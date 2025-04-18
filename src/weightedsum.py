from gurobipy import *
import criteria
import printing

class WeightedSumOptimiser(object):
    def __init__(self, pool, cycles, weights_list):
        self.model = Model()
        self.pool = pool
        self.cycles = cycles
        self.weights = weights_list
        
    def _exchanges_in_optimal_solution(self, items):
            return [item for item in items if item.mip_var.X > 0.5]
    
    def _add_chosen_objectives(self, constraint_list, cycles, altruists):
        final_constraints = []

        for constraint in constraint_list:
            if constraint == "MAX_TWO_CYCLES":
                final_constraints.append([cycle.mip_var * criteria.MaxTwoCycles().cycle_val(cycle) for cycle in cycles])
                final_constraints.append([altruist.mip_unmatched * criteria.MaxTwoCycles().altruist_val() for altruist in altruists])
            elif constraint == "MAX_SIZE":
                final_constraints.append([cycle.mip_var * criteria.MaxSize().cycle_val(cycle) for cycle in cycles])
                final_constraints.append([altruist.mip_unmatched * criteria.MaxSize().altruist_val() for altruist in altruists])
            elif constraint == "MAX_BACKARCS":
                final_constraints.append([cycle.mip_var * criteria.MaxBackarcs().cycle_val(cycle) for cycle in cycles])
                final_constraints.append([altruist.mip_unmatched * criteria.MaxBackarcs().altruist_val() for altruist in altruists])
            elif constraint == "MIN_THREE_CYCLES":
                final_constraints.append([cycle.mip_var * criteria.MinThreeCycles().cycle_val(cycle) for cycle in cycles])
                final_constraints.append([altruist.mip_unmatched * criteria.MinThreeCycles().altruist_val() for altruist in altruists])
            elif constraint == "MAX_WEIGHT":
                final_constraints.append([cycle.mip_var * criteria.MaxOverallWeight().cycle_val(cycle) for cycle in cycles])
                final_constraints.append([altruist.mip_unmatched * criteria.MaxOverallWeight().altruist_val() for altruist in altruists])
        return final_constraints

        
    def _add_mip_vars_and_constraints(self, pool):
        
        for cycle in self.cycles:
            cycle.mip_var = self.model.addVar(vtype=GRB.BINARY, name='cycle' + str(cycle.index))
        self.model.update()

        # this also adds the corresponding cycle mip var to the altruists too!
        for cycle in self.cycles:
            for node in cycle.donor_patient_nodes:
                node.patient.mip_vars.append(cycle.mip_var) 
                node.donor.mip_vars.append(cycle.mip_var) 
                
        for node in pool.donor_patient_nodes:
            self.model.addConstr(quicksum(node.patient.mip_vars) <= 1)
            self.model.addConstr(quicksum(node.donor.mip_vars) <= 1)
        self.model.update()

        for altruist in pool.altruists:
            altruist.mip_unmatched = self.model.addVar(vtype=GRB.BINARY, name=f'unmatched_altruist_{altruist.id}')

        # setting the multi-objective method to 0 = weighted sum 
        # setting to 1 = hierarchical
        self.model.setParam(GRB.Param.MultiObjMethod, 0) 
        self.model.update()

    def optimise(self, pool, constraint_list):
        self.model.setParam('OutputFlag', 0)
        self._add_mip_vars_and_constraints(pool)
        # paper has constraint s.t. where altruist mip var is 1 if they are unmatched
        # and 0 if they are matched in a cycle so they are not double counted
        # altruist can be added to create a dpd chain, or donate to the deceased donor pool
        for altruist in pool.altruists:
            # first find all cycles that contain this altruistic donor
            cycles_with_altruist = []
            for cycle in self.cycles:
                if any(node.donor.id == altruist.id and node.is_altruist for node in cycle.donor_patient_nodes):
                    cycles_with_altruist.append(cycle)
            
            self.model.addConstr(
                altruist.mip_unmatched + quicksum(cycle.mip_var for cycle in cycles_with_altruist) == 1,
                name=f'altruist_constraint_{altruist.id}')

        self.model.ModelSense = GRB.MAXIMIZE 
        self.model.update()

        final_constraints = self._add_chosen_objectives(constraint_list, self.cycles, pool.altruists)

        for i in range(len(final_constraints)):
            if constraint_list[i//2] == "MIN_THREE_CYCLES":
                self.model.setObjectiveN(-quicksum(final_constraints[i]), index=i, priority=0, name=f"{constraint_list[i//2]}_{i}")    
            else:
                self.model.setObjectiveN(quicksum(final_constraints[i]), index=i, priority=0, name=f"{constraint_list[i//2]}_{i}")     
        self.model.update()
        
        for i in range(0, self.model.NumObj//2):
            self.model.Params.ObjNumber = 2 * i
            self.model.ObjNWeight = self.weights[i]
            self.model.Params.ObjNumber = (2 * i) + 1
            self.model.ObjNWeight = self.weights[i]

        self.model.update()
        self.model.optimize()
        assert self.model.Status == GRB.Status.OPTIMAL, "Model did not find an optimal solution."
        optimal_cycles = self._exchanges_in_optimal_solution(self.cycles)
        
        all_selected_cycles = printing.write_solution_obj_values(self.model, self.cycles, "./output/weighted_sum_solution_obj_values.txt")

        return optimal_cycles, all_selected_cycles

    # this function was for testing the pool's find cycles function was correct
    def run_gurobi_cycle_finder(self, donor_patient_nodes):
        edges = []
        for node in donor_patient_nodes:
            u = (node.donor.id, node.patient.id)
            for e in node.out_edges:
                target_node = e.donor_recipient_node
                v = (target_node.donor.id, int(target_node.patient.id))
                edges.append((u, v))

        var_edges = self.model.addVars(edges, vtype=GRB.BINARY, name="edge")
        
        for u, v in edges:
            # making sure the reverse edge exists
            if (v, u) in edges:
                self.model.addConstr(var_edges[u, v] == var_edges[v, u], name=f"{u}_{v}_two_cycle")

        self.model.setObjective(quicksum(var_edges[u, v] for u, v in edges if (v, u) in edges), GRB.MAXIMIZE)
        self.model.optimize()

        seen = set()
        two_cycles_list = []

        # finding 2-cycles
        for u, v in edges:
            if (u, v) in edges and (v, u) in edges:
                # > 0.5 means edge has been selected
                # check both to and back have been selected                
                if var_edges[u, v].X > 0.5 and var_edges[v, u].X > 0.5:
                    curr_set = frozenset((u, v))
                    if curr_set not in seen:
                        seen.add(curr_set)
                        two_cycles_list.append((u, v))  

        three_cycles = []
        for u, v in edges:
            for w in donor_patient_nodes:
                w_id = (w.donor.id, w.patient.id)
                if (v, w_id) in edges and (w_id, u) in edges:
                    three_cycles.append((u, v, w_id))

        for (u, v, w) in three_cycles:
            self.model.addConstr(var_edges[u, v] + var_edges[v, w] + var_edges[w, u] == 3, name=f"{u}_{v}_{w}_three_cycle")

        self.model.setObjective(
            quicksum(var_edges[u, v] + var_edges[v, w] + var_edges[w, u] for (u, v, w) in three_cycles) / 3,
            GRB.MAXIMIZE
        )
        
        self.model.optimize()

        seen = set()
        three_cycles_list = []

        # finding 3-cycles
        for (u, v, w) in three_cycles:
            curr_set = frozenset((u, v, w))
            if curr_set not in seen:
                seen.add(curr_set)
                if var_edges[u, v].X > 0.5 and var_edges[v, w].X > 0.5 and var_edges[w, u].X > 0.5:
                    three_cycles_list.append((u, v, w)) 

        return two_cycles_list, three_cycles_list

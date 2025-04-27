from gurobipy import *
import criteria
import printing

class WeightedSumOptimiser(object):
    def __init__(self, pool, cycles, weights_list, test=False):
        self.model = Model()
        self.pool = pool
        self.cycles = cycles
        self.test = test
        self.weights = weights_list


    def _exchanges_in_optimal_solution(self, items):
            return [item for item in items if item.mip_var.X > 0.5]
    
    def _add_chosen_objectives(self, constraint_list, cycles, altruists):
        final_constraints = []

        for constraint in constraint_list:
            if constraint == "MAX_TWO_CYCLES":
                final_constraints.append([cycle.mip_var * criteria.MaxTwoCycles().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxTwoCycles().altruist_val() for altruist in altruists])
            elif constraint == "MAX_SIZE":
                final_constraints.append([cycle.mip_var * criteria.MaxSize().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxSize().altruist_val() / 10 for altruist in altruists])
            elif constraint == "MAX_BACKARCS":
                final_constraints.append([cycle.mip_var * criteria.MaxBackarcs().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxBackarcs().altruist_val() for altruist in altruists])
            elif constraint == "MIN_THREE_CYCLES":
                final_constraints.append([cycle.mip_var * criteria.MinThreeCycles().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MinThreeCycles().altruist_val() for altruist in altruists])
            elif constraint == "MAX_WEIGHT":
                final_constraints.append([cycle.mip_var * criteria.MaxOverallScore().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxOverallScore().altruist_val() / 1000 for altruist in altruists])
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

        # paper has constraint s.t. where altruist mip var is 1 if they are unmatched
        # and 0 if they are matched in a cycle so they are not double counted
        # altruist can be added to create a dpd chain, or donate to the deceased donor pool
        for altruist in pool.altruists:
            altruist.mip_unmatched = self.model.addVar(vtype=GRB.BINARY, name=f'unmatched_altruist_{altruist.id}')
            altruist.mip_vars.append(altruist.mip_unmatched)
        
        for node in pool.donor_patient_nodes:
            if node.is_altruist:
                self.model.addConstr(quicksum(node.donor.mip_vars) == 1)
            else:
                self.model.addConstr(quicksum(node.donor.mip_vars) <= 1)
            self.model.addConstr(quicksum(node.patient.mip_vars) <= 1)       
        # setting the multi-objective method to 1 = hierarchical
        # setting to 0 = weighted sum 
        self.model.setParam(GRB.Param.MultiObjMethod, 0) 
        self.model.update()

    def optimise(self, pool, constraint_list):
        self.model.setParam('OutputFlag', 0)
        self._add_mip_vars_and_constraints(pool)

        self.model.ModelSense = GRB.MAXIMIZE 
        self.model.update()

        final_constraints = self._add_chosen_objectives(constraint_list, self.cycles, pool.altruists)

        for i in range(len(final_constraints)):
            if constraint_list[i] == "MIN_THREE_CYCLES":
                self.model.setObjectiveN(-quicksum(final_constraints[i]), index=i, priority=0, name=f"{constraint_list[i]}_{i}")    
            else:
                self.model.setObjectiveN(quicksum(final_constraints[i]), index=i, priority=0, name=f"{constraint_list[i]}_{i}")     
        self.model.update()
        
        for i in range(0, self.model.NumObj):
            self.model.Params.ObjNumber = i
            self.model.ObjNWeight = self.weights[i]

        self.model.update()
        self.model.optimize()
        assert self.model.Status == GRB.Status.OPTIMAL, "Model did not find an optimal solution."
        optimal_cycles = self._exchanges_in_optimal_solution(self.cycles)
        
        all_selected_cycles = printing.write_solution_obj_values(self.model, self.cycles, "./output/weighted_sum_solution_obj_values.txt")

        return optimal_cycles, all_selected_cycles

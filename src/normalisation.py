from gurobipy import *
import criteria
import printing

class Normaliser(object):
    def __init__(self, pool, cycles):
        self.model = Model()
        self.pool = pool
        self.cycles = cycles

    def _exchanges_in_optimal_solution(self, items):
            return [item for item in items if item.mip_var.X > 0.5]
    
    def _add_chosen_objective(self, constraint, cycles, altruists):
        if constraint == "MAX_TWO_CYCLES":
            final_constraint = [cycle.mip_var * criteria.MaxTwoCycles().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxTwoCycles().altruist_val() for altruist in altruists]
        elif constraint == "MAX_SIZE":
            final_constraint = [cycle.mip_var * criteria.MaxSize().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxSize().altruist_val() for altruist in altruists]
        elif constraint == "MAX_BACKARCS":
            final_constraint = [cycle.mip_var * criteria.MaxBackarcs().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxBackarcs().altruist_val() for altruist in altruists]
        elif constraint == "MIN_THREE_CYCLES":
            final_constraint = [cycle.mip_var * criteria.MinThreeCycles().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MinThreeCycles().altruist_val() for altruist in altruists]
        elif constraint == "MAX_WEIGHT":
            final_constraint = [cycle.mip_var * criteria.MaxOverallWeight().cycle_val(cycle) for cycle in cycles] + [altruist.mip_unmatched * criteria.MaxOverallWeight().altruist_val() for altruist in altruists]
        return final_constraint

        
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
        self.model.setParam(GRB.Param.MultiObjMethod, 1) 
        self.model.update()
    
    def find_max_values(self, pool, constraint_list):
        max_values = {}
        for constraint in constraint_list:
            max_values[constraint] = self._optimise(pool, constraint)
        return max_values

    def _optimise(self, pool, constraint):

        self.model.setParam('OutputFlag', 0)
        self._add_mip_vars_and_constraints(pool)

        self.model.ModelSense = GRB.MAXIMIZE 

        final_constraint = self._add_chosen_objective(constraint, self.cycles, pool.altruists)
        if constraint == "MIN_THREE_CYCLES":
            self.model.setObjective(-quicksum(final_constraint))    
        else:
            self.model.setObjective(quicksum(final_constraint))     

        self.model.update()
        self.model.optimize()
        assert self.model.Status == GRB.Status.OPTIMAL, "Model did not find an optimal solution."        

        return self.model.ObjVal
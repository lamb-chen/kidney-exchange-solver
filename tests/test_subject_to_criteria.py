import unittest
from src import reader as r
from src import hierarchical
from src import johnsons

class TestSubjectToCriteria(unittest.TestCase):

    def test_subject_to_max_two_cycles(self):
        filename = "tests/datasets/test_max_cycles.json"
        reader = r.JSONReader()
        pool = reader.read_json(filename)
        cycles, _ = johnsons.johnsons(pool.donor_patient_nodes, 3)
        g_solver = hierarchical.HierarchicalOptimiser(pool=pool, cycles=cycles, test=True)
        constraint_list = ["MAX_TWO_CYCLES", "MAX_SIZE"]
        optimal_cycles = g_solver.optimise(pool, constraint_list)
        self.assertEqual(len(optimal_cycles[0].donor_patient_nodes), 3)
        
if __name__ == '__main__':
    unittest.main()
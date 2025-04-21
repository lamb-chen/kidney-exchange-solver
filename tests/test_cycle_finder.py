import unittest
from src import reader as r
from src import hierarchical
from src import johnsons
import copy 
from src import simple

class TestCycleFinder(unittest.TestCase):

    # def test_cycle_finder(self):
    #     filename = "tests/datasets/test_cycle_count_before.json"
    #     reader = r.JSONReader()
    #     pool_before = reader.read_json(filename)
    #     before_cycles, _ = johnsons.johnsons(pool_before.donor_patient_nodes, 3)
    #     before_n_cycles = len(before_cycles)

    #     filename = "tests/datasets/test_cycle_count_after.json"
    #     pool_after = reader.read_json(filename)
    #     after_cycles, _ = johnsons.johnsons(pool_after.donor_patient_nodes, 3)
    #     after_n_cycles = len(after_cycles)
    #     self.assertEqual(before_n_cycles + 1, after_n_cycles)

    def test_cycle_finder_with_gurobi(self):
        # filename = "tests/datasets/test_cycle_count_before.json"
        # filename = "tests/datasets/test_example.json"
        filename = "tests/datasets/cycles.json"
        # filename = "tests/datasets/input-file.json"
        reader = r.JSONReader()
        pool = reader.read_json(filename)
        # pool_copy = reader.read_json(filename)
        # cycles, _ = johnsons.johnsons(pool.donor_patient_nodes, 3)
        cycles = simple.find_simple_cycles(pool.donor_patient_nodes, 3)
        # cycles = pool.identify_cycles(3)
        # cycles = pool.create_cycles_objects(3)
        # pool.all_cycles = cycles
        g_solver = hierarchical.HierarchicalOptimiser(pool=pool, cycles=cycles, test=True)
        two_cycles_list = g_solver.gurobi_find_two_cycles(pool.donor_patient_nodes)
        three_cycles_list = g_solver.gurobi_find_three_cycles(pool.donor_patient_nodes)
        total_cycle_count = len(two_cycles_list) + len(three_cycles_list)
        self.assertEqual(total_cycle_count, len(cycles))

if __name__ == '__main__':
    unittest.main()
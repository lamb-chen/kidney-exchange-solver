import unittest
from src import reader as r
from src import hierarchical
from src import printing
from src import simple

class TestAltruistCycleFinder(unittest.TestCase):

    def test_altruist_cycle_found(self):
        filename = "tests/datasets/test_example.json"
        reader = r.JSONReader()
        pool = reader.read_json(filename)
        cycles = simple.find_simple_cycles(pool.donor_patient_nodes, 3)
        self.assertEqual(len(cycles), 9)

    def test_altruist_included(self):
        filename = "tests/datasets/test_example.json"
        reader = r.JSONReader()
        pool = reader.read_json(filename)
        cycles = simple.find_simple_cycles(pool.donor_patient_nodes, 3)
        g_solver = hierarchical.HierarchicalOptimiser(pool=pool, cycles=cycles, test=True)
        constraint_list = ["MAX_SIZE"]
        optimal_cycles = g_solver.optimise(pool, constraint_list)
        print(optimal_cycles)
        printing.print_cycles(optimal_cycles)
        n_transplants = sum(len(cycle.donor_patient_nodes) for cycle in optimal_cycles)
        self.assertEqual(7, n_transplants)
    
    def test_altruist_split_1(self):
        filename = "tests/datasets/test_altruist_split_1.json"
        reader = r.JSONReader()
        pool = reader.read_json(filename)
        cycles = simple.find_simple_cycles(pool.donor_patient_nodes, 3)
        g_solver = hierarchical.HierarchicalOptimiser(pool=pool, cycles=cycles, test=True)
        constraint_list = ["MAX_SIZE"]
        optimal_cycles = g_solver.optimise(pool, constraint_list)
        self.assertEqual(len(optimal_cycles), 1)

    def test_altruist_split_2(self):
        filename = "tests/datasets/test_altruist_split_2.json"
        reader = r.JSONReader()
        pool = reader.read_json(filename)
        cycles = simple.find_simple_cycles(pool.donor_patient_nodes, 3)
        g_solver = hierarchical.HierarchicalOptimiser(pool=pool, cycles=cycles, test=True)
        constraint_list = ["MAX_SIZE"]
        optimal_cycles = g_solver.optimise(pool, constraint_list)
        self.assertEqual(len(optimal_cycles), 2)

if __name__ == '__main__':
    unittest.main()
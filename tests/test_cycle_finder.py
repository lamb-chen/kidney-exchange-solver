import unittest
from src import reader as r
from src import hierarchical
from src import simple

class TestCycleFinder(unittest.TestCase):

    def test_cycle_finder(self):
        filename = "tests/datasets/test_cycle_count_before.json"
        reader = r.JSONReader()
        pool_before = reader.read_json(filename)
        before_cycles = simple.find_simple_cycles(pool_before.donor_patient_nodes, 3)
        before_n_cycles = len(before_cycles)

        filename = "tests/datasets/test_cycle_count_after.json"
        pool_after = reader.read_json(filename)
        after_cycles = simple.find_simple_cycles(pool_after.donor_patient_nodes, 3)
        after_n_cycles = len(after_cycles)
        self.assertEqual(before_n_cycles + 1, after_n_cycles)

if __name__ == '__main__':
    unittest.main()
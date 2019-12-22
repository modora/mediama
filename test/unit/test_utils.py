import unittest
from pathlib import Path

import mediama.utils as utils

# A trivial test suite!!
class TestGetProjectRoot(unittest.TestCase):
    def test_function(self):
        expected = Path(__file__).parent.parent.parent
        result = utils.get_project_root()
        self.assertEqual(expected, result)

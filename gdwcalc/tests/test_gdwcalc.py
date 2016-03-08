# -*- coding: utf-8 -*-
"""
<insert 1-line description here>

Created on Tue Mar  8 13:03:32 2016

@author: dthor

Usage:
    module_name.py

Options:
    -h --help           # Show this screen.
    --version           # Show version.

"""

import unittest

from .. import GDWCalc

class TestDummy(unittest.TestCase):
    def test_dummy(self):
        self.assertTrue(True)


class TestPairwise(unittest.TestCase):
    def test_pairwise(self):
        a = [1, 2, 3, 4, 5]
        expected = [(1, 2), (2, 3), (3, 4), (4, 5)]
        result = list(GDWCalc.pairwise(a))
        self.assertEqual(result, expected)


if __name__ == "__main__":
    unittest.main(verbosity=2)

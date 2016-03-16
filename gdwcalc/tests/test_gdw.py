# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 14:01:24 2014

@name:          test_gdw.py
@vers:          0.1
@author:        dthor
@created:       Tue Jun 17 14:01:24 2014
@modified:      Tue Jun 17 14:01:24 2014
@descr:         Unit Testing for gdwcalc.gdw module
"""

import unittest
from .. import gdw


class TestWaferClass(unittest.TestCase):
    """
    """
    def test_invalid_x_offset_raises_typeerror(self):
        wafer = gdw.Wafer((1, 1), (0, 0))

        invalid_entries = (
                           # wrong value
                           "hello",
                           # wrong type
                           {"a": 3},
                           (1, ),
                           # not a single item
                           ("a", 1),
                           (-3, "a"),
                           )

        for item in invalid_entries:
            with self.subTest(invalid_value=item):
                with self.assertRaises(TypeError):
                    wafer.x_offset = item

    def test_invalid_y_offset_raises_typeerror(self):
        wafer = gdw.Wafer((1, 1), (0, 0))

        invalid_entries = (
                           # wrong value
                           "hello",
                           # wrong type
                           {"a": 3},
                           (1, ),
                           # not a single item
                           ("a", 1),
                           (-3, "a"),
                           )

        for item in invalid_entries:
            with self.subTest(invalid_value=item):
                with self.assertRaises(TypeError):
                    wafer.y_offset = item

    def test_invalid_center_offset_raises_typeerror(self):
        wafer = gdw.Wafer((1, 1), (0, 0))

        invalid_entries = (
                           # not lists or tuples
                           "hello",
                           123,
                           # correct length, but mixed or invalid entries
                           ("a", 1),
                           (-3, "a"),
                           # incorrect length
                           ("even", "even", "even"),
                           (1, 2, 3, 4),
                           (1, ),
                           )

        for item in invalid_entries:
            with self.subTest(invalid_value=item):
                with self.assertRaises(TypeError):
                    wafer.center_offset = item


class TestDieClass(unittest.TestCase):
    """
    """
    def test_cant_add_attribute(self):
        die = gdw.Die(1, 1, 1, 1, 1)
        with self.assertRaises(AttributeError):
            die.new_attribute = 1


class TestMaxDistSquared(unittest.TestCase):
    """
    """
    #                center coord,  box size,       expected value
    known_values = (
                    ((0, 0),        (2, 2),          2),
                    ((0, 0),        (6, 8),          25),
                    ((0, 0),        (2, 36),         325),
                    ((0, 0),        (0, 0),          0),
                    ((0.5, 0.5),    (1, 1),          2),
                    ((0, 0),        (3.14, 2.718),   4.311781),
                    ((0, -10),      (3.14, 2.718),   131.491781),
                    ((-10, 0),      (3.14, 2.718),   135.711781),
                    ((-10, -10),    (3.14, 2.718),   262.891781),
                    ((0, 10),       (3.14, 2.718),   131.491781),
                    ((10, 0),       (3.14, 2.718),   135.711781),
                    ((10, 10),      (3.14, 2.718),   262.891781),
                    ((100000, 100000), (2, 2),       20000400002),
                    ((1000, 0),     (100, 0.00001),  1102500),
                    )

    def test_known_values(self):
        for center, size, expected in self.known_values:
            with self.subTest(center=center, size=size):
                result = gdw.max_dist_sqrd(center, size)
                self.assertAlmostEqual(result, expected)


class TestFlatLocation(unittest.TestCase):
    """
    """
    known_values = (
                    (50,     -23.7056196),
                    (75,     -35.8164473),
                    (100,    -47.2857008),
                    (125,    -58.7765897),
                    (150,    -69.2707550),
                    (35,     -17.5),
                    (120,    -60),
                    (237.68, -118.84),
                    )

    def test_known_values(self):
        for dia, expected in self.known_values:
            with self.subTest(diameter=dia):
                result = gdw.flat_location(dia)
                self.assertAlmostEqual(result, expected)

    def test_invalid_input_raises_typeerror(self):
        with self.assertRaises(TypeError):
            gdw.flat_location('hello')


class TestGDWCalculation(unittest.TestCase):
    known_values = {
    # name:   (((die_xy,      dia, offset_xy,      excl, scribe_excl, expected
    "ints":   (((5, 5),       150, ('even', 'even'), 5,     5),       546),
    "floats": (((5.0, 5.0),   150, ('even', 'even'), 5,     5),       546),
    "t01":    (((3.34, 3.16), 100, ('even', 'even'), 5,     5),       548),
    "t02-1":  (((2.43, 3.30), 150, ('even', 'odd'),  5,     4.5),     1814),
    "t02-2":  (((2.43, 3.30), 150, ('even', 'even'), 5,     4.5),     1794),
    "t02-3":  (((2.43, 3.30), 150, ('odd', 'odd'),   5,     4.5),     1800),
    "t02-4":  (((2.43, 3.30), 150, ('odd', 'even'),  5,     4.5),     1804),
    "t03":    (((4.34, 6.44), 150, ('even', 'even'), 5,     5),       484),
    "t04":    (((1, 1),       150, ('even', 'even'), 5,     5),       14902),
    "t05":    (((1, 1),       200, ('odd', 'even'),  5,     15),      27435),
    "t06":    (((2.9, 3.3),   150, (-1.65, 2.95),    4.5,   4.5),     1529),
    "t07":    (((2.69, 1.65), 150, (1.345, 2.1),     4.5,   4.5),     3346),
    "t08":    (((4.4, 5.02),  150, (0, -0.2),        4.5,   4.5),     648),
    }

    def test_known_values(self):
        for k, (v, expected) in self.known_values.items():
            with self.subTest(test_name=k):
                gdw_list = gdw.gdw(*v)
                # count only die that are probed
                result = sum(1 for x in gdw_list[0] if x[4] == 'probe')
                self.assertEqual(result, expected)


@unittest.skip("tested function not completed yet")
class TestDieToRadius(unittest.TestCase):
    """
    """
    def test_known_values(self):
        pass



if __name__ == "__main__":
    unittest.main(verbosity=2)

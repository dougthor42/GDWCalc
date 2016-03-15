# -*- coding: utf-8 -*-
"""
Created on Tue Jun 17 14:01:24 2014

@name:          test_gdw.py
@vers:          0.1
@author:        dthor
@created:       Tue Jun 17 14:01:24 2014
@modified:      Tue Jun 17 14:01:24 2014
@descr:         Unit Testing for douglib.gdw module
"""

from __future__ import print_function, division
import unittest
import os.path
from .. import gdw


REF_DATA_PATH = os.path.join(os.path.dirname(os.path.realpath(__file__)),
                             "reference_data",
                             )


class GDW(unittest.TestCase):
    """ Unit Testing of the gross die per wafer algorithm """
    # (die_xy, dia, (offset_x, offset_y), excl, fss_excl, expected_result)
    mdh25 = ((3.34, 3.16), 100, ('even', 'even'), 5, 5, 548)
    mdh26_std = ((2.43, 3.30), 150, ('even', 'odd'), 5, 4.5, 1814)
    mdh26_ee = ((2.43, 3.30), 150, ('even', 'even'), 5, 4.5, 1794)
    mdh26_oo = ((2.43, 3.30), 150, ('odd', 'odd'), 5, 4.5, 1800)
    mdh26_oe = ((2.43, 3.30), 150, ('odd', 'even'), 5, 4.5, 1804)
    mdh27 = ((4.34, 6.44), 150, ('even', 'even'), 5, 5, 484)
    floats = ((5.0, 5.0), 150, ('even', 'even'), 5, 5, 546)
    ints = ((5, 5), 150, ('even', 'even'), 5, 5, 546)
    kv_1 = ((1, 1), 150, ('even', 'even'), 5, 5, 14902)
    kv_2 = ((1, 1), 200, ('odd', 'even'), 5, 15, 27435)

    known_values = (floats,
                    ints,
                    mdh25,
                    mdh26_std,
                    mdh26_ee,
                    mdh26_oo,
                    mdh26_oe,
                    mdh27,
                    kv_1,
                    kv_2,
                    )

    def test_known_values(self):
        """ Known-value testing for GDW calculation """
        for die_xy, dia, center, excl, fss_excl, exp_res in self.known_values:
            gdw_list = gdw.gdw(die_xy,
                               dia,
                               center,
                               excl,
                               fss_excl,
                               )
            # count only die that are probed
            result = sum(1 for x in gdw_list[0] if x[4] == 'probe')
            self.assertEqual(exp_res, result)


@unittest.skip("demonstrating skipping")
def check_wafer_map():
    import douglib.wafer_map
    # Test the wafer map stuff
    data = []
    file_path = r"X:\WinPython27\projects\douglib\test_data\wafer_map.csv"
    with open(file_path) as of:
        for line in of:
            data.append(tuple([float(i) for i in line.strip().split(',')]))

    douglib.wafer_map.plot_wafer_map(data,
                                     plot_range=(0, 75),
                                     wafer=(150, 5, 5),
                                     center_rc=(24, 31.5),
                                     )


if __name__ == "__main__":
    unittest.main(exit=False, verbosity=2)

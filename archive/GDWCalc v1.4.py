# -*- coding: utf-8 -*-
"""
@name:              GDWCalc.py
@vers:              1.4
@author:            Douglas Thor
@created:           2013-04-19
@modified:          2013-10-08
@descr:             Calcualtes Gross Die per Wafer (GDW), accounting for
                    wafer flat, edge exclusion, and front-side-scribe (FSS)
                    exclusion (also called flat exclusion).

                    Returns nothing.

                    Prints out the Offset Type (Odd or Even) and the GDW, as
                    well as where die were lost (edge, flat, FSS)

"""

from __future__ import print_function
import douglib.prompts as prompts
import douglib.gdw as gdw


# Defined by SEMI M1-0302
__version__ = "1.4"
__released__ = "2014-07-14"


def printHeader():
    print()
    print("++++++++++++++++++++++++++++++")
    print("GDWCalc v%s" % __version__)
    print("Released %s" % __released__)
    print("++++++++++++++++++++++++++++++")
    print("")


def main():
    printHeader()
    die_xy, dia, excl, fss = prompts.wafer_info()
    print("")

    probeList, center_xy = gdw.maxGDW(die_xy, dia, excl, fss)

    if prompts.plot():
        coord_list = [(i[0], i[1], i[4])
                      for i in probeList]
        gdw.plotGDW(coord_list, die_xy, dia, excl, fss, center_xy)

    raw_input("Press Enter to close this window.")


if __name__ == "__main__":
    main()

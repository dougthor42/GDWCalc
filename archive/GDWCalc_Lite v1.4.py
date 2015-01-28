# -*- coding: utf-8 -*-
"""
@name:              GDWCalc_Lite.py
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
import math


# Defined by SEMI M1-0302
FLAT_LENGTHS = {50: 15.88, 75: 22.22, 100: 32.5, 125: 42.5, 150: 57.5}
PROG_VERS = "1.4"
REL_DATE = "2014-02-26"


def round_to_multiple(x, multiple):
    return int(multiple * round(float(x)/multiple))


def max_dist(center, size):
    """
    Calcualtes the largest distance from the origin for a rectangle of
    size (x, y), where the center of the rectangle's coordinates are known.
    If the rectangle's center is in the Q1, then the upper-right corner is
    the farthest away from the origin. If in Q2, then the upper-left corner
    is farthest away. Etc.
    Returns the magnitude of the largest distance.
    """
    halfX = size[0]/2.
    halfY = size[1]/2.
    if center[0] < 0:
        halfX = -halfX
    if center[1] < 0:
        halfY = -halfY
    dist = math.sqrt((center[0] + halfX)**2 + (center[1] + halfY)**2)
    return dist


def dieSizePrompt():
    while True:
        try:
            dieX = float(raw_input("Die X size (mm): "))
            if dieX > 1000 or dieX <= 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid entry. Please enter a number between 0 and 1000.")

    while True:
        try:
            dieY = float(raw_input("Die Y size (mm): "))
            if dieY > 1000 or dieY <= 0:
                raise ValueError
            break
        except ValueError:
            print("Invalid entry. Please enter a number between 0 and 1000.")
    return (dieX, dieY)


def waferSizePrompt():
    while True:
        default = 150.0
        dia = raw_input("Wafer diameter (mm) [%dmm]: " % default)
        if dia == "":
            dia = float(default)
            print("Using default value of %dmm." % default)
            break
        else:
            try:
                dia = float(dia)
                if dia <= 0 or dia > 500:
                    raise ValueError
                break
            except ValueError:
                print("Invalid entry. Please enter a number between 0 and 500.")
    return dia


def exclSizePrompt():
    while True:
        default = 5.0
        exclSize = raw_input("Exclusion ring width (mm) [%dmm]: " % default)
        if exclSize == "":
            exclSize = float(default)
            print("Using default value of %dmm." % default)
            break
        else:
            try:
                exclSize = float(exclSize)
                if exclSize < 0:
                    raise ValueError
                break
            except ValueError:
                print("Invalid entry. Please enter a number greater than 0.")
    return exclSize


def FSSExclPrompt():
    """ Prompts user for Front-Side Scribe Exclusion width. Also called Flat
    Exclusion """
    while True:
        default = 5.0
        FSSExcl = raw_input("Front Side Scribe (Flat) Exclusion (mm) [%dmm]: " % default)
        if FSSExcl == "":
            FSSExcl = float(default)
            print("Using default value of %dmm." % default)
            break
        else:
            try:
                FSSExcl = float(FSSExcl)
                if FSSExcl < 0:
                    raise ValueError
                break
            except ValueError:
                print("Invalid entry. Please enter a number greater than 0.")
    return FSSExcl


def gdw(dieSize, dia, centerType, excl, FSS_EXCLUSION):
    """
    Calculates Gross Die per Wafer (GDW) for a given dieSize (X, Y),
    wafer diameter dia, centerType (xType, yType), and exclusion width (mm).

    Returns a list of tuples (X, Y, XCoord, YCoord, dieStatus)
    """
    origin = (0, 0)
    dieX = dieSize[0]
    dieY = dieSize[1]
    rad = 0.5 * dia

    # assume that the reticle center is the wafer center
    dieCenter = list(origin)

    if centerType[0] == "even":
        # offset the dieCenter by 1/2 the die size, X direction
        dieCenter[0] = 0.5 * dieX
    if centerType[1] == "even":
        # offset the dieCenter by 1/2 the die size, Y direction
        dieCenter[1] = 0.5 * dieY

    # find out how many die we can fit on the wafer
    nX = int(math.ceil(dia/dieX))
    nY = int(math.ceil(dia/dieY))

    # If we're centered on the wafer, we need to add one to the axis count
    if centerType[0] == "odd":
        nX += 1
    if centerType[1] == "odd":
        nY += 1

    # make a list of (x, y) center coordinate pairs
    centers = []
    for i in range(nX):
        for j in range(nY):
            centers.append(((i-nX/2) * dieX + dieCenter[0],
                            (j-nY/2) * dieY + dieCenter[1]))

    if dia in FLAT_LENGTHS:
        # A flat is defined, so we draw it.
        flatSize = FLAT_LENGTHS[dia]
        x = flatSize/2
        y = -math.sqrt(rad**2 - x**2)
    else:
        # A flat is not defined so...
        y = -rad

    yExcl = y + FSS_EXCLUSION

    # Take only those that are within the wafer radius
    dieList = []
    #n = 0
    #updateValue = round_to_multiple(len(centers) // 100, 100)
    #listLen = len(centers)
    #print("Calculating GDW:")
    for coord in centers:
        #if n % updateValue == 0:
        #    progress_bar(n, listLen)
        newCoords = (coord[0] - dieX/2, coord[1] - dieY/2)
        if max_dist(coord, dieSize) > rad:
            # it's off the wafer
            status = "wafer"
        elif coord[1] - dieY/2 < y:
            # it's off the flat
            status = "flat"
        elif max_dist(coord, dieSize) > (rad - excl):
            # it's outside of the exclusion
            status = "excl"
        elif coord[1] - dieY/2 < yExcl:
            # it's ouside the flat exclusion
            status = "flatExcl"
        else:
            # it's a good die, add it to the list
            status = "probe"
        # need to figure out how to get true RC numbers
        dieList.append(("X Col", "Y Row", newCoords[0], newCoords[1], status))
        #n += 1
    #progress_bar(n, listLen)
    #print("")

    return dieList


def maxGDW(dieSize, dia, excl, fssExcl):
    # list of available die shifts
    ds = [("odd", "odd"),
          ("odd", "even"),
          ("even", "odd"),
          ("even", "even")]
    j = (0, "")
    probeList = []
    for shift in ds:
        probeCount = 0
        edgeCount = 0
        flatCount = 0
        flatExclCount = 0
        dieList = gdw(dieSize, dia, shift, excl, fssExcl)
        for die in dieList:
            if die[-1] == "probe":
                probeCount += 1
            elif die[-1] == "excl":
                edgeCount += 1
            elif die[-1] == "flat":
                flatCount += 1
            elif die[-1] == "flatExcl":
                flatExclCount += 1

        #print(shift, probeCount)
        if probeCount > j[0]:
            j = (probeCount, shift, edgeCount, flatCount, flatExclCount)
            probeList = dieList

    print("")
    print("----------------------------------")
    print("Maximum GDW: %d" % j[0])
    print("Offsets:\tX (Col): %s\tY (Row): %s\n" % (j[1][0], j[1][1]))

    print("Die lost to Edge Exclusion: %d" % j[2])
    print("Die Lost to Wafer Flat: %d" % j[3])
    print("Die Lost to Front-Side Scribe Exclusion: %d" % j[4])
    print("----------------------------------")

    return probeList


def printHeader():
    print("++++++++++++++++++++++++++++++")
    print("GDWCalc v%s" % PROG_VERS)
    print("Released %s" % REL_DATE)
    print("++++++++++++++++++++++++++++++")
    print("")


def main():
    printHeader()
    dieXY = dieSizePrompt()
    dia = waferSizePrompt()
    excl = exclSizePrompt()
    FSS_Width = FSSExclPrompt()
    print("")

    maxGDW(dieXY, dia, excl, FSS_Width)

    raw_input("Press Enter to close this window.")


if __name__ == "__main__":
    main()

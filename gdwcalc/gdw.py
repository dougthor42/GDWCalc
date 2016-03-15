# -*- coding: utf-8 -*-
"""
Created on Mon Aug 26 11:02:21 2013

@author: dthor

A library holding common subroutines and classes that I've created.
Remember PEP8 Style Guides:
Classes are CamelCase (MyClassName)
functions are lowercase with underscores (my_function)
CONSTANTS are UPPERCASE with underscores (MAX_CONSTANT)
"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
import math
import os
import warnings

# Third-Party
import wafer_map.wm_app as wm_app


# ---------------------------------------------------------------------------
### Constants
# ---------------------------------------------------------------------------
# Defined by SEMI M1-0302
FLAT_LENGTHS = {50: 15.88, 75: 22.22, 100: 32.5, 125: 42.5, 150: 57.5}


# ---------------------------------------------------------------------------
### Classes
# ---------------------------------------------------------------------------
class Wafer(object):
    """
    """
    def __init__(self, die_xy, center_offset,
                 dia=150, excl=4.5, flat_excl=4.5, scribe_y=70.2):
        self._die_xy = die_xy
        self._center_offset = center_offset
        self._dia = dia
        self._excl = excl
        self._flat_excl = flat_excl
        self._scribe_y = scribe_y

        self._flat_y = flat_location(self.dia)
        self._center_grid = None

    @property
    def dia(self):
        return self._dia

    @dia.setter
    def dia(self, value):
        self._dia = value

    @property
    def rad(self):
        return self.dia / 2

    @property
    def excl(self):
        return self._excl

    @excl.setter
    def excl(self, value):
        self._excl = value

    @property
    def flat_excl(self):
        return self._flat_excl

    @property
    def excl_rad_sqrd(self):
        return (self.dia/2)**2 + (self.excl**2) - (self.dia * self.excl)

    @property
    def die_xy(self):
        return self._die_xy

    @die_xy.setter
    def die_xy(self, value):
        raise NotImplementedError

    @property
    def die_x(self):
        return self.die_xy[0]

    @property
    def die_y(self):
        return self.die_xy[1]

    @property
    def flat_y(self):
        return self._flat_y

    @property
    def grid_max_x(self):
        return 2 * int(math.ceil(self.dia / self.die_x))

    @property
    def grid_max_y(self):
        return 2 * int(math.ceil(self.dia / self.die_y))

    @property
    def grid_max_xy(self):
        return (self.grid_max_x, self.grid_max_y)

    @property
    def x_offset(self):
        return self._x_offset

    @x_offset.setter
    def x_offset(self, value):
        if value not in ("even", "odd") and not isinstance(value, (float, int)):
            err_str = "Invalid value: `{}`. Value must be 'odd', 'even', or a number."
            raise TypeError(err_str.format(value))
        self._x_offset = value

    @property
    def y_offset(self):
        return self._y_offset

    @y_offset.setter
    def y_offset(self, value):
        if value not in ("even", "odd") and not isinstance(value, (float, int)):
            err_str = "Invalid value: `{}`. Value must be 'odd', 'even', or a number."
            raise TypeError(err_str.format(value))
        self._y_offset = value

    @property
    def center_offset(self):
        return (self.x_offset, self.y_offset)

    @center_offset.setter
    def center_offset(self, value):
        if isinstance(value, (list, tuple)) and len(value) == 2:
            self.x_offset, self.y_offset = value
        else:
            raise TypeError("value must be a list or tuple of length 2.")

    @property
    def grid_center_x(self):
        return self.grid_max_x/2 + self.x_offset

    @property
    def grid_center_y(self):
        return self.grid_max_y/2 + self.y_offset

    @property
    def grid_center_xy(self):
        return (self.grid_center_x, self.grid_center_y)


class Die(object):
    """
    """
    def __init__(self, x_grid, y_grid, x_coord, y_coord, state):
        self.x_grid = x_grid
        self.y_grid = y_grid
        self.x_coord = x_coord
        self.y_coord = y_coord
        self.state = state


# ---------------------------------------------------------------------------
### Functions
# ---------------------------------------------------------------------------
def max_dist_sqrd(center, size):
    """
    Calculates the squared distance from the orgin (0, 0) to the
    farthest corner of a rectangle.

    Does not take the square of the distance for the sake of speed.

    If the rectangle's center is in the Q1, then the upper-right corner is
    the farthest away from the origin. If in Q2, then the upper-left corner
    is farthest away. Etc.

    Returns the magnitude of the largest distance.

    Used primarily for calculating if a die has any part outside of wafer's
    edge exclusion.

    Parameters:
    -----------
    center : tuple of length 2, numerics
        (x, y) tuple defining the rectangle's center coordinates

    size : tuple of length 2
        (x, y) tuple that defines the size of the rectangle.

    Returns:
    --------
    dist : numeric
        The distance from the origin (0, 0) to the farthest corner of the
        rectangle.

    See Also:
    ---------
    max_dist :
        Calculates the distance from the orgin (0, 0) to the
        farthest corner of a rectangle.
    """
    half_x = size[0]/2.
    half_y = size[1]/2.
    if center[0] < 0:
        half_x = -half_x
    if center[1] < 0:
        half_y = -half_y
    dist = (center[0] + half_x)**2 + (center[1] + half_y)**2
    return dist


def flat_location(dia):
    """
    Returns the flat's y location wrt to wafer center for a given diameter.

    Parameters:
    -----------
    dia : int or float
        The wafer diameter in mm.

    Returns:
    --------
    flat_y : float
        The flat Y location with respect to the wafer center.
    """
    flat_y = -dia/2     # assume wafer edge at first
    if dia in FLAT_LENGTHS:
        # A flat is defined by SEMI M1-0302, so we calcualte where it is
        flat_y = -math.sqrt((dia/2)**2 - (FLAT_LENGTHS[dia] * 0.5)**2)

    return flat_y


def gdw(die_size, dia, center_offset=('odd', 'odd'), excl=5, flat_excl=5):
    """
    Calculates Gross Die per Wafer (GDW) for a given die_size,
    wafer diameter, center_offset, and exclusion width (mm).

    Returns a list of tuples ``(x_grid, y_grid, x_coord, y_coord, die_status)``

    Parameters:
    -----------
    die_size : list or tuple of numerics, length 2
        The die (x, y) size in mm.

    dia : int or float
        The wafer diameter in mm.

    center_offset : list or tuple of length 2.
        (x, y) offset in mm from the die origin (lower-left corner).
        Alternatively, may be set to ('odd', 'odd'), ('odd', even'),
        ('even', 'odd'), or ('even', 'even')

    excl : into or float
        The wafer-edge exclusion distance in mm.

    flat_excl : int or float
        The flat exclusion distance in mm.

    Returns:
    --------
    grid_points : list of tuples
        The list of die that cover the wafer. Each die is defined by
        a tuple of ``(x_grid, y_grid, x_coord, y_coord, die_status)``.

    grid_center_xy : tuple of length 2
        The wafer center in die grid coordinates.

    Notes:
    ------
    + xCol and yRow are 1 indexed
    + Possible values for `die_status` are::

        'wafer', 'flat', 'excl', 'flatExcl', 'probe'
    """

    wafer = Wafer(die_size, center_offset, dia, excl, flat_excl)

    wafer.x_offset = 0
    wafer.y_offset = 0
    if center_offset[0] == "even":
        # offset the dieCenter by 1/2 the die size, X direction
        wafer.x_offset = 0.5
    if center_offset[1] == "even":
        # offset the dieCenter by 1/2 the die size, Y direction
        wafer.y_offset = 0.5

    # convert the fixed offset to a die %age
    if not all(i in ('odd', 'even') for i in center_offset):
        wafer.x_offset = center_offset[1] / wafer.die_x
        wafer.y_offset = center_offset[0] / wafer.die_y

    # This could be more efficient
    grid_points = []
    for _x in range(1, wafer.grid_max_x):
        for _y in range(1, wafer.grid_max_y):
            coord_die_center_x = wafer.die_x * (_x - wafer.grid_center_x)
            # we have to reverse the y coord, hence why it's
            # ``wafer.grid_center_y - _y`` and not ``_y - wafer.grid_center_y``
            coord_die_center_y = wafer.die_y * (wafer.grid_center_y - _y)
            coord_die_center = (coord_die_center_x, coord_die_center_y)
            center_rad_sqrd = coord_die_center_x**2 + coord_die_center_y**2
            die_max_sqrd = max_dist_sqrd(coord_die_center, wafer.die_xy)
            coord_lower_left_x = coord_die_center_x - wafer.die_x/2
            coord_lower_left_y = coord_die_center_y - wafer.die_y/2
#            coord_lower_left = (coord_lower_left_x, coord_lower_left_y)

            if die_max_sqrd > wafer.rad**2:
                # it's off the wafer, don't add to list.
                status = "wafer"
                continue
            elif coord_lower_left_y < wafer.flat_y:
                # it's off the flat
                status = "flat"
            elif die_max_sqrd > wafer.excl_rad_sqrd:
                # it's outside of the exclusion
                status = "excl"
            elif coord_lower_left_y < (wafer.flat_y + wafer.flat_excl):
                # it's ouside the flat exclusion
                status = "flatExcl"
            else:
                # it's a good die, add it to the list
                status = "probe"

            grid_points.append((_x,
                                _y,
                                coord_lower_left_x,
                                coord_lower_left_y,
                                status,
                                ))

    return (grid_points, wafer.grid_center_xy)


def gdw_fo(die_size, dia, fo, excl=5, flat_excl=5):
    """
    Calculates Gross Die per Wafer (GDW) for a given die_size (X, Y),
    wafer diameter dia, center fixed offset (fo), and exclusion width (mm).

    Returns a list of tuples (xCol, yRow, xCoord, yCoord, dieStatus)

    xCol and yRow are 1 indexed

    values for dieStatus are"
    DIE_STATUS = [wafer, flat, excl, flatExcl, probe]
    """
    warnings.warn("Use `gdw` function instead", PendingDeprecationWarning)
    return gdw(die_size, dia, fo, excl, flat_excl)


def maxGDW(die_size, dia, excl, fssExcl):
    """

    returns list of tuples of (xCol, yRow, xCoord, yCoord, dieStatus)
    xCol and yRow are 1 indexed.

    Parameters:
    -----------
    die_size : tuple
        Tuple of (die_x, die_y) sizes. Values are floats in mm.

    dia : int?
        The wafer diameter in mm.

    excl : float
        The edge exclusion in mm.

    fssExcl : float
        The flat exclusion in mm.

    Returns:
    --------
    (probeList, centerXY)

    probeList : list of tuples
        A list of 5-tuples: (xCol, yRow, xCoord, yCoord, dieStatus)

    gridCenter : tuple
        A 2-tuple of (grid_x, grid_y) center coordinates.

        **TODO: Confirm that this is (X, Y) and not (R, C)**
    """

    # list of available die shifts in XY pairs
    ds = [("odd", "odd"),
          ("odd", "even"),
          ("even", "odd"),
          ("even", "even")]
    #ds = [("even", "odd")]
    j = (0, "")
    probeList = []
    for shift in ds:
        probeCount = 0
        edgeCount = 0
        flatCount = 0
        flatExclCount = 0
        dieList, grid_center = gdw(die_size, dia, shift, excl, fssExcl)
        for die in dieList:
            if die[-1] == "probe":
                probeCount += 1
            elif die[-1] == "excl":
                edgeCount += 1
            elif die[-1] == "flat":
                flatCount += 1
            elif die[-1] == "flatExcl":
                flatExclCount += 1

        print(shift, probeCount)
        if probeCount > j[0]:
            j = (probeCount, shift, edgeCount, flatCount, flatExclCount)
            probeList = dieList
            gridCenter = grid_center

    SUMMARY_STRING = """
    ----------------------------------
    Maximum GDW: {max_gdw} (X: {max_gdw_type_x}, Y: {max_gdw_type_y})

    Die lost to Edge Exclusion: {lost_edge}
    Die Lost to Wafer Flat: {lost_flat}
    Die Lost to Front-Side Scribe Exclusion: {lost_fss}
    ----------------------------------
    """

    print(SUMMARY_STRING.format(max_gdw=j[0],
                                max_gdw_type_x=j[1][0],
                                max_gdw_type_y=j[1][1],
                                lost_edge=j[2],
                                lost_flat=j[3],
                                lost_fss=j[4]))

    return (probeList, gridCenter)


def plotGDW(dieList, die_size, dia, excl, fssExcl, grid_center):
    """
    Plots up a wafer map of dieList, coloring based on the bin the die
    die belongs to.

    Uses my xw Code

    dieList is a list of tuples (xCol, yRow, xCoord, yCoord, dieStatus) where
    xCol and yRow are 1-indexed and dieStatus is a psudo-enum of:
        ["probe", "flat", "excl", "flatExcl", "wafer"]
        (as defined by the gdw routine)
    die size is a tuple of (x_size, y_size) and is in mm.
    dia, excl, and fssExcl are in mm.
    """
    wm_app.WaferMapApp(dieList,
                       die_size,
                       grid_center,
                       dia,
                       excl,
                       fssExcl,
                       data_type='discrete'
                       )


def gen_mask_file(probeList, maskName, dieXY, dia):
    """
    Generates a text file that can be read by the LabVIEW OWT program.

    probeList should only contain die that are fully on the wafer. Die that
    are within the edxlucion zones but still fully on the wafer *are*
    included.

    probeList is what's returned from maxGDW, so it's a list of
    (xCol, yRow, xCoord, yCoord, dieStatus) tuples
    """

    # 1. Create the file
    # 2. Add the header
    # 3. Append only the "probe" die to the die list.
    # 4. Finalize the file.
    path = os.path.join("\\\\hydrogen\\engineering\\\
Software\\LabView\\OWT\\masks", maskName + ".ini")
    print("Saving mask file data to:")
    print(path)

    # this defines where (1, 1) actually is.
    # TODO: Verify that "- 2" works for all cases
    edge_R = min({i[1] for i in probeList if i[4] == 'excl'}) - 2
    edge_C = min({i[0] for i in probeList if i[4] == 'excl'}) - 2
    print("min(edge_R) = {}    min(edge_C) = {}".format(edge_R, edge_C))

    # Adjust the original data to the origin
    for _i, _ in enumerate(probeList):
        probeList[_i] = list(probeList[_i])
        probeList[_i][0] -= edge_C
        probeList[_i][1] -= edge_R
        probeList[_i] = tuple(probeList[_i])

    nRC = (max({i[1] for i in probeList}) + 1,
           max({i[0] for i in probeList}) + 1)
    print("nRC = {}".format(nRC))

    # create a list of every die
    allDie = []
    for row in range(1, nRC[0] + 1):        # Need +1 b/c end pt omitted
        for col in range(1, nRC[1] + 1):    # Need +1 b/c end pt omitted
            allDie.append((row, col))

    # Note: I need list() so that I make copies of the data. Without it,
    # all these things would be pointing to the same allDie object.
    TestAllList = list(allDie)
    edgeList = list(allDie)
    everyList = list(allDie)
    die_to_probe = []

    # This algorithm is crap, but it works.
    # Create the exclusion list to add to the OWT file.
    # NOTE: I SWITCH FROM XY to RC HERE!
    for item in probeList:
        _rc = (item[1], item[0])
        _state = item[4]
        try:
            if _state == "probe":
                TestAllList.remove(_rc)
                die_to_probe.append(_rc)
            if _state in ("excl", "flatExcl", "probe"):
                everyList.remove(_rc)
            if _state in ("excl", "flatExcl"):
                edgeList.remove(_rc)
        except ValueError:
            print(_rc, _state)
            raise

    # Determine the starting RC - this will be the min row, min column that
    # as a "probe" value. However, since the GDW algorithm now puts the
    # origin somewhere far off the wafer, we need to adjust the values a bit.
    minR = min(i[0] for i in die_to_probe)
    minC = min(i[1] for i in die_to_probe if i[0] == minR)
    startRC = (minR, minC)
    print("Landing Die: {}".format(startRC))

    TestAllString = ''.join(["%s,%s; " % (i[0], i[1]) for i in TestAllList])
    edgeString = ''.join(["%s,%s; " % (i[0], i[1]) for i in edgeList])
    everyString = ''.join(["%s,%s; " % (i[0], i[1]) for i in everyList])

    homeRC = (1, 1)                         # Static value

    with open(path, 'w') as openf:
        openf.write("[Mask]\n")
        openf.write("Mask = \"%s\"\n" % maskName)
        openf.write("Die X = %f\n" % dieXY[0])
        openf.write("Die Y = %f\n" % dieXY[1])
        openf.write("Flat = 0\n")                   # always 0
        openf.write("\n")
        openf.write("[%dmm]\n" % dia)
        openf.write("Rows = %d\n" % nRC[0])
        openf.write("Cols = %d\n" % nRC[1])
        openf.write("Home Row = %d\n" % homeRC[0])
        openf.write("Home Col = %d\n" % homeRC[1])
        openf.write("Start Row = %d\n" % startRC[0])
        openf.write("Start Col = %d\n" % startRC[1])
        openf.write("Every = \"" + everyString[:-2] + "\"\n")
        openf.write("TestAll = \"" + TestAllString[:-2] + "\"\n")
        openf.write("Edge Inking = \"" + edgeString[:-2] + "\"\n")
        openf.write("\n[Devices]\n")
        openf.write("PCM = \"0.2,0,0,,T\"\n")


def die_to_radius(rc_coord, die_size):
    """ attempts to determine the die's XY location from the rc_coord

    We'll need to find out which die is the center of the wafer. The issue is
    that we don't use any negative row column coordinates. If we're just doing
    MDH26 then I already know that the wafer center is between columns 32 and
    33 and is the middle of row 24...
    """
    center_xy = (32.5, 24)
    die_x = die_size[0] * (rc_coord[1] - center_xy[0])
    die_y = die_size[1] * (rc_coord[0] - center_xy[1])
    radius = math.sqrt(die_x**2 + die_y**2)
    return radius


def example_gdw_calc():
    print("Running example GDW Calculation...")
    die_size = (5.02, 8.49)
    dia = 150
    excl = 4.5
    fssExcl = 4.5
    dielist, grid_center = maxGDW(die_size, dia, excl, fssExcl)
    grid_center = (30.5, 27.5)
    grid_center = (14.3386, 8.5589)
    coord_list = [(i[0]+grid_center[0], i[1]+grid_center[1], i[4])
                  for i in dielist]

    plotGDW(coord_list, die_size, dia, excl, fssExcl, grid_center)
    print(dielist[1])
    import douglib.prompts as prompts
    if prompts.y_n("Generate OWT Map File? "):
        gen_mask_file(dielist, "MDH00", die_size, dia)

if __name__ == "__main__":
    print("This file is not meant to be run as a module.")

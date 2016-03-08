# -*- coding: utf-8 -*-
# pylint: disable=W0201
"""
@name:              GDWCalc.py
@author:            Douglas Thor
@created:           2013-04-19
@descr:             Calcualtes Gross Die per Wafer (GDW), accounting for
                    wafer flat, edge exclusion, and front-side-scribe (FSS)
                    exclusion (also called flat exclusion).

                    Returns nothing.

                    Prints out the Offset Type (Odd or Even) and the GDW, as
                    well as where die were lost (edge, flat, FSS)

"""
# ---------------------------------------------------------------------------
### Imports
# ---------------------------------------------------------------------------
# Standard Library
from __future__ import print_function
import itertools
import math
import os

# Third Party
import douglib.gdw as gdw
import numpy as np
import wafer_map.wm_core as wm_core
import wafer_map.wm_info as wm_info
import wx
import wx.lib.plot as wxplot

# Package / Application
try:
    # Imports used for unittests
#    from . import sibling_module
    from . import (__version__,
                   __released__,
                   )
except (SystemError, ValueError):
    try:
        # Imports used by Spyder
#        import sibling_module
        from __init__ import (__version__,
                              __released__,
                              )
    except ImportError:
         # Imports used by cx_freeze
#        from package import sibling_module
        from gdwcalc import (__version__,
                             __released__,
                             )


# TODO: Recode maxGDW to to include 'print' statements?

TITLE_TEXT = "GDWCalc v{}   Released {}".format(__version__,
                                                __released__)
INSTRUCTION_TEXT = """
Keyboard Shortcuts:
Enter\tCalculate GDW
Home\tZoom to fit
C\tToggle centerlines
O\tToggle wafer outline
L\tToggle legend
CTRL+Q\tExit

Click on wafer map to
zoom (mouse wheel) and
pan (middle-click + drag)"""


class MainApp(object):
    """ Main App Object """
    def __init__(self):
        self.app = wx.App()
        self.frame = MainFrame()
        self.frame.Show()
        self.app.MainLoop()


class MainFrame(wx.Frame):
    """ Main Frame """
    def __init__(self):
        wx.Frame.__init__(self,
                          None,
                          title=TITLE_TEXT,
                          size=(1400, 820),
                          )
        self.init_ui()

    def init_ui(self):
        """ Init the UI components """
        self.menu_bar = wx.MenuBar()

        self._create_menus()
        self._create_menu_items()
        self._add_menu_items()
        self._add_menus()
        self._bind_events()

        # Initialize default states
        self.mv_outline.Check()
        self.mv_crosshairs.Check()

        # Set the MenuBar and create a status bar (easy thanks to wx.Frame)
        self.SetMenuBar(self.menu_bar)
        self.CreateStatusBar()

        self.panel = MainPanel(self)

    def _create_menus(self):
        """ Create each menu for the menu bar """
        self.mfile = wx.Menu()
        self.medit = wx.Menu()
        self.mview = wx.Menu()
        self.mopts = wx.Menu()

    def _create_menu_items(self):
        """ Create each item for each menu """
        self.mf_close = wx.MenuItem(self.mfile,
                                    wx.ID_ANY,
                                    "&Close\tCtrl+Q",
                                    "TestItem",
                                    )

        self.me_calc = wx.MenuItem(self.medit,
                                   wx.ID_ANY,
                                   "&Calculate\tEnter",
                                   "Calculate Gross Die per Wafer",
                                   )

        self.mv_zoomfit = wx.MenuItem(self.mview,
                                      wx.ID_ANY,
                                      "Zoom &Fit\tHome",
                                      "Zoom to Fit",
                                      )
        self.mv_crosshairs = wx.MenuItem(self.mview,
                                         wx.ID_ANY,
                                         "Crosshairs\tC",
                                         "Show or hide the crosshairs",
                                         wx.ITEM_CHECK,
                                         )
        self.mv_outline = wx.MenuItem(self.mview,
                                      wx.ID_ANY,
                                      "Wafer Outline\tO",
                                      "Show or hide the wafer outline",
                                      wx.ITEM_CHECK,
                                      )

    def _add_menu_items(self):
        """ Appends MenuItems to each menu """
        self.mfile.Append(self.mf_close)
        self.medit.Append(self.me_calc)
        self.mview.Append(self.mv_zoomfit)
        self.mview.AppendSeparator()
        self.mview.Append(self.mv_crosshairs)
        self.mview.Append(self.mv_outline)

    def _add_menus(self):
        """ Appends each menu to the menu bar """
        self.menu_bar.Append(self.mfile, "&File")
        self.menu_bar.Append(self.medit, "&Edit")
        self.menu_bar.Append(self.mview, "&View")

    def _bind_events(self):
        """ Binds events to varoius MenuItems """
        self.Bind(wx.EVT_MENU, self.on_quit, self.mf_close)
        self.Bind(wx.EVT_MENU, self.on_calc, self.me_calc)
        self.Bind(wx.EVT_MENU, self.zoom_fit, self.mv_zoomfit)
        self.Bind(wx.EVT_MENU, self.toggle_crosshairs, self.mv_crosshairs)
        self.Bind(wx.EVT_MENU, self.toggle_outline, self.mv_outline)

    def on_quit(self, event):
        """ Actions for the quit event """
        self.Close(True)

    def on_calc(self, event):
        """ Action for Calc event """
        self.panel.on_calc_gdw(event)

    def zoom_fit(self, event):
        """ Call the WaferMapPanel.zoom_fill() method """
        print("Frame Event!")
        self.panel.wafer_map.zoom_fill()

    def toggle_crosshairs(self, event):
        """ Call the WaferMapPanel toggle_crosshairs() method """
        self.panel.wafer_map.toggle_crosshairs()

    def toggle_outline(self, event):
        """ Call the WaferMapPanel.toggle_outline() method """
        self.panel.wafer_map.toggle_outline()


class MainPanel(wx.Panel):
    """ Main Panel. Contains parameters and the map """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        probe_list, self.center_xy = gdw.maxGDW((5, 5), 150, 5, 5)
        self.coord_list = [(i[0], i[1], i[4]) for i in probe_list]

        self.wafer_info = wm_info.WaferInfo((5, 5), self.center_xy)
        self.die_xy = self.wafer_info.die_size
        self.dia = self.wafer_info.dia

        self.init_ui()

    def init_ui(self):
        """ Create the UI """

        # Die X Size
        self.x_lbl = wx.StaticText(self, label="X Size (mm)")
        self.x_input = wx.TextCtrl(self, wx.ID_ANY, "5", size=(50, -1))

        # Die Y Size
        self.y_lbl = wx.StaticText(self, label="Y Size (mm)")
        self.y_input = wx.TextCtrl(self, wx.ID_ANY, "5", size=(50, -1))

        # Wafer Diameter
        self.dia_lbl = wx.StaticText(self, label="Wafer Diameter (mm)")
        self.dia_input = wx.TextCtrl(self, wx.ID_ANY, "150", size=(50, -1))

        # Edge Exclusion
        self.ee_lbl = wx.StaticText(self, label="Edge Exlusion (mm)")
        self.ee_input = wx.TextCtrl(self, wx.ID_ANY, "5", size=(50, -1))

        # Flat Exclusion
        self.fe_lbl = wx.StaticText(self, label="Flat Exclusion (mm)")
        self.fe_input = wx.TextCtrl(self, wx.ID_ANY, "5", size=(50, -1))

        # Fixed Offsets
        self.fo_chk = wx.CheckBox(self, label="Fixed Offsets")
        self.x_fo_lbl = wx.StaticText(self, label="X Offset (mm)")
        self.x_fo_input = wx.TextCtrl(self, wx.ID_ANY, "0", size=(50, -1))
        self.y_fo_lbl = wx.StaticText(self, label="Y Offset (mm)")
        self.y_fo_input = wx.TextCtrl(self, wx.ID_ANY, "0", size=(50, -1))

        # Force First Die Coord
        self.fdc_chk = wx.CheckBox(self, label="Force 1st Die Coord")
        self.x_fdc_lbl = wx.StaticText(self, label="X (Column) Coord")
        self.x_fdc_input = wx.TextCtrl(self, wx.ID_ANY, "0", size=(50, -1))
        self.y_fdc_lbl = wx.StaticText(self, label="Y (Row) Coord")
        self.y_fdc_input = wx.TextCtrl(self, wx.ID_ANY, "0", size=(50, -1))

        # Calculate Button
        self.calc_button = wx.Button(self, label="Calculate")
        self.Bind(wx.EVT_BUTTON, self.on_calc_gdw, self.calc_button)

        self.gen_mask_button = wx.Button(self, label="Generate Mask File")
        self.Bind(wx.EVT_BUTTON, self.on_gen_mask, self.gen_mask_button)

        # Actual Wafer Map
        legend_values = ["flat",
                         "excl",
                         "probe",
                         "flatExcl",
                         ]
        self.wafer_map = wm_core.WaferMapPanel(self,
                                               self.coord_list,
                                               self.wafer_info,
                                               data_type='discrete',
                                               plot_die_centers=True,
                                               discrete_legend_values=legend_values
                                               )

        # Radius Histograms
        radius_sqrd_data = list(
           (self.wafer_info.die_size[0] * (self.wafer_info.center_xy[0] - die[0]))**2
           + (self.wafer_info.die_size[1] * (self.wafer_info.center_xy[1] - die[1]))**2
           for die in self.coord_list)
        radius_data = list(math.sqrt(item) for item in radius_sqrd_data)
        self.histograms = RadiusPlots(self, radius_data)

        # Result Info
        self.gdw_lbl = wx.StaticText(self, label="Gross Die per Wafer:")
        self.gdw_result = wx.StaticText(self, label="0")

        self.ee_loss_lbl = wx.StaticText(self,
                                         label="Die lost to Edge Exclusion:")

        self.ee_loss_result = wx.StaticText(self, label="0")

        self.flat_loss_lbl = wx.StaticText(self,
                                           label="Die Lost to Wafer Flat:")
        self.flat_loss_result = wx.StaticText(self, label="0")

        self.fe_loss_lbl = wx.StaticText(self,
                                         label="Die Lost to Flat Exclusion:")
        self.fe_loss_result = wx.StaticText(self, label="0")

        # Center Info
        self.shape_lbl = wx.StaticText(self, label="Center Offsets:")
        self.shape_x_label = wx.StaticText(self, label="X (Column):")
        self.shape_x_result = wx.StaticText(self, label="0 (odd)")
        self.shape_y_lbl = wx.StaticText(self, label="Y (Row):")
        self.shape_y_result = wx.StaticText(self, label="0 (odd)")

        self.center_lbl = wx.StaticText(self, label="Center Coords:")
        self.center_x_lbl = wx.StaticText(self, label="X (Column):")
        self.center_x_result = wx.StaticText(self, label="0")
        self.center_y_lbl = wx.StaticText(self, label="Y (Row):")
        self.center_y_result = wx.StaticText(self, label="0")

        # Instructions:
        self.instructions = wx.StaticText(self, label=INSTRUCTION_TEXT)

        # Set the Layout
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.fgs_inputs = wx.FlexGridSizer(rows=13, cols=2, vgap=0, hgap=0)
        self.fgs_inputs.AddMany([self.x_lbl, self.x_input,
                                 self.y_lbl, self.y_input,
                                 self.dia_lbl, self.dia_input,
                                 self.ee_lbl, self.ee_input,
                                 self.fe_lbl, self.fe_input,
                                 (-1, 10), (-1, -1),
                                 self.fo_chk, (-1, -1),
                                 self.x_fo_lbl, self.x_fo_input,
                                 self.y_fo_lbl, self.y_fo_input,
                                 (-1, 10), (-1, -1),
                                 self.fdc_chk, (-1, -1),
                                 self.x_fdc_lbl, self.x_fdc_input,
                                 self.y_fdc_lbl, self.y_fdc_input,
                                 ])

        self.fgs_results = wx.FlexGridSizer(rows=13, cols=2, vgap=0, hgap=10)

        # Add items to the results layout
        self.fgs_results.AddMany([self.gdw_lbl, self.gdw_result,
                                  (-1, 10), (-1, 10),
                                  self.ee_loss_lbl, self.ee_loss_result,
                                  self.flat_loss_lbl, self.flat_loss_result,
                                  self.fe_loss_lbl, self.fe_loss_result,
                                  (-1, 10), (-1, 10),
                                  self.shape_lbl, (-1, -1),
                                  self.shape_x_label, self.shape_x_result,
                                  self.shape_y_lbl, self.shape_y_result,
                                  (-1, 10), (-1, 10),
                                  self.center_lbl, (-1, -1),
                                  self.center_x_lbl, self.center_x_result,
                                  self.center_y_lbl, self.center_y_result,
                                  ])
        self.vbox.Add(self.fgs_inputs, 0, wx.EXPAND)
        self.vbox.Add((-1, 10), 0, wx.EXPAND)
        self.vbox.Add(self.calc_button, 0, wx.EXPAND)
        self.vbox.Add((-1, 10), 0, wx.EXPAND)
        self.vbox.Add(self.gen_mask_button, 0, wx.EXPAND)
        self.vbox.Add((-1, 10), 0, wx.EXPAND)
        self.vbox.Add(self.fgs_results, 0, wx.EXPAND)
        self.vbox.Add(self.instructions, 0, wx.EXPAND)
        self.hbox.Add(self.vbox, 0, wx.EXPAND)
        self.hbox.Add((20, -1), 0, wx.EXPAND)
        self.hbox.Add(self.wafer_map, 2, wx.EXPAND)
        self.hbox.Add(self.histograms, 1, wx.EXPAND)

        self.SetSizer(self.hbox)

    def on_calc_gdw(self, event):
        """ Performs the GDW Calculation on button click """
        print("Button Pressed")

        self.die_x = float(self.x_input.Value)
        self.die_y = float(self.y_input.Value)
        self.die_xy = (self.die_x, self.die_y)
        self.dia = int(self.dia_input.Value)
        self.ee = float(self.ee_input.Value)
        self.fe = float(self.fe_input.Value)
        self.fo_bool = bool(self.fo_chk.Value)
        self.x_fo = float(self.x_fo_input.Value)
        self.y_fo = float(self.y_fo_input.Value)
        self.fo = (self.x_fo, self.y_fo)
        self.grid_offset = (0, 0)

        # If using fixed offsets, call other function.
        if self.fo_bool:
            probe_list, self.center_xy = gdw.gdw_fo(self.die_xy,
                                                    self.dia,
                                                    self.fo,
                                                    self.ee,
                                                    self.fe,
                                                    )

        else:
            probe_list, self.center_xy = gdw.maxGDW(self.die_xy,
                                                    self.dia,
                                                    self.ee,
                                                    self.fe,
                                                    )
        self.coord_list = [(i[0], i[1], i[4]) for i in probe_list]

        # If using a forced starting die (top-left), adjust coords
        if self.fdc_chk.Value:
            # Gind the topmost then leftmost probed die.
            min_y = min({c[1] for c in self.coord_list if c[2] == "probe"})
            min_x = min([c[0] for c in self.coord_list
                         if c[2] == "probe" and c[1] == min_y])

            # Calculate the delta
            delta_x = min_x - int(self.x_fdc_input.Value)
            delta_y = min_y - int(self.y_fdc_input.Value)

            self.grid_offset = (delta_x, delta_y)

            # Update the coord list and the center xy location.
            self.coord_list = [(i[0] - delta_x,
                                i[1] - delta_y,
                                i[2]) for i in self.coord_list]

            self.center_xy = (self.center_xy[0] - delta_x,
                              self.center_xy[1] - delta_y)

        # Calculate the Die Counts
        # TODO: Update gdw.maxGDW to return these values instead
        self.gdw = 0
        self.flat_loss = 0
        self.ee_loss = 0
        self.fe_loss = 0

        # TODO: This isn't pythonic at all, but I'm ~~in a rush~~ lazy
        for rcd in self.coord_list:
            if rcd[2] == 'probe':
                self.gdw += 1
            elif rcd[2] == 'flat':
                self.flat_loss += 1
            elif rcd[2] == 'excl':
                self.ee_loss += 1
            elif rcd[2] == 'flatExcl':
                self.fe_loss += 1
            else:
                raise KeyError("Invalid dieStatus value")

        self.wafer_info = wm_info.WaferInfo(self.die_xy,
                                            self.center_xy,
                                            self.dia,
                                            self.ee,
                                            self.fe)

        # All these things just so that I can update the map...
        self.wafer_map.canvas.InitAll()
        self.wafer_map._clear_canvas()
        self.wafer_map.die_size = self.die_xy
        self.wafer_map.xyd = self.coord_list
        self.wafer_map.wafer_info = self.wafer_info
        self.wafer_map.grid_center = self.center_xy
        self.wafer_map.xyd_dict = wm_core.xyd_to_dict(self.coord_list)
        self.wafer_map._create_legend()
        self.wafer_map.draw_die()
        self.wafer_map.draw_die_center()
        self.wafer_map.draw_wafer_objects()
        self.wafer_map.zoom_fill()

        # Calcualte new radius data
        radius_sqrd_data = list(
           (self.wafer_info.die_size[0] * (self.wafer_info.center_xy[0] - die[0]))**2
           + (self.wafer_info.die_size[1] * (self.wafer_info.center_xy[1] - die[1]))**2
           for die in self.coord_list)
        new_radius_data = list(math.sqrt(item) for item in radius_sqrd_data)
        self.histograms.update(new_radius_data)

        self.gdw_result.SetLabel(str(self.gdw))
        self.ee_loss_result.SetLabel(str(self.ee_loss))
        self.flat_loss_result.SetLabel(str(self.flat_loss))
        self.fe_loss_result.SetLabel(str(self.fe_loss))

        self.x_offset = self.center_xy[0] % 1
        if self.x_offset == 0:
            self.x_offset = "0 (odd)".format(self.x_offset)
        else:
            self.x_offset = "0.5 (even)".format(self.x_offset)
        self.shape_x_result.SetLabel(str(self.x_offset))

        self.y_offset = self.center_xy[1] % 1
        if self.y_offset == 0:
            self.y_offset = "0 (odd)".format(self.y_offset)
        else:
            self.y_offset = "0.5 (even)".format(self.y_offset)
        self.shape_y_result.SetLabel(str(self.y_offset))

        self.center_x_result.SetLabel(str(self.center_xy[0]))
        self.center_y_result.SetLabel(str(self.center_xy[1]))

        # Update the screen
        self.Refresh()
        self.Update()

    def on_gen_mask(self, event):
        """ Handle the gen_mask event """
        mask = "MDH00"
        statusbar = self.parent.StatusBar

        try:
            gen_mask_file(self.coord_list, mask,
                          self.die_xy, self.dia, self.fdc_chk.Value)
        except Exception as err:
            print(err)
            statusbar.SetStatusText("Error: {}".format(err))
            raise
        statusbar.SetStatusText("Mask saved to '{}'".format(mask))



class RadiusPlots(wx.Panel):
    """ A container for the two radius histograms """
    def __init__(self, parent, radius_data):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.radius_data = radius_data
        self._init_ui()

        self._bind_events()

    def _init_ui(self):
        """ """
        # create the items
        self.lin_binspec = range(0, 81, 5)

        # bins of equal area, area = 2000 mm^2
        self.eq_area_binspec = [0, 25.2313, 35.6825, 43.7019,
                                50.4627, 56.419, 61.8039,
                                66.7558, 71.365, 75.694]

        self.radius_plot = Histogram(self,
                                     self.radius_data,
                                     self.lin_binspec,
                                     "Bin Size = 5mm",
                                     "Radius (mm)",
                                     )
        self.eq_area_plot = Histogram(self,
                                      self.radius_data,
                                      self.eq_area_binspec,
                                      "BinSize = 2000 mm^2",
                                      "Radius (mm)",
                                      )

        # Create the layout manager
        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.radius_plot, 1, wx.EXPAND)
        self.vbox.Add(self.eq_area_plot, 1, wx.EXPAND)
        self.SetSizer(self.vbox)

    def _bind_events(self):
        """ """
        pass

    def update(self, data):
        """ Updates the two radius plots """
        self.radius_plot.update(data, self.lin_binspec)
        self.eq_area_plot.update(data, self.eq_area_binspec)


def pairwise(iterable):
    "s -> (s0,s1), (s1,s2), (s2, s3), ..."
    a, b = itertools.tee(iterable)
    next(b, None)
    return zip(a, b)


class Histogram(wxplot.PlotCanvas):
    """
    A homebrewed histogram plot

    data must be a 1d list or tuple of floats or integers.

    binspec must be a 1d list or tuple of floats or integers.

    binspec defines the bin cutoff points
    For example, binspec = [0, 1, 2, 3, 4] would result in 6 bins:
        x < 0
        0 <= x < 1
        1 <= x < 2
        3 <= x < 3
        3 <= x < 4
        x >= 4

    """
    def __init__(self, parent, data, binspec,
                 title="Histogram", x_label="Bin", y_label="Count"):
        wxplot.PlotCanvas.__init__(self, parent)
        self.parent = parent
        self.data = data
        self.binspec = binspec
        self.hist_data = None
        self.title = title
        self.x_label = x_label
        self.y_label = y_label

#        self._init_data()

#        self._init_ui()
        self.update(self.data, self.binspec)

    def _init_ui(self):
        pass

    def _init_data(self):
        pass

    def update(self, data, binspec):
        self.Clear()

        # other stuff uses numpy so I can too.
        hist, edges = np.histogram(data, binspec)

        bars = []
        for n, (count, (low, high)) in enumerate(zip(hist, pairwise(edges))):

            pts = [(low, 0), (low, count)]
            ln = wxplot.PolyLine(pts,
                                 colour='blue',
                                 width=3,
                                 )
            bars.append(ln)

            # hack to get things to look like a "bar"...
            pts2 = [(high, 0), (high, count)]
            ln2 = wxplot.PolyLine(pts2,
                                  colour='blue',
                                  width=3,
                                  )
            bars.append(ln2)
            pts3 = [(low, count), (high, count)]
            ln3 = wxplot.PolyLine(pts3,
                                  colour='blue',
                                  width=3,
                                  )
            bars.append(ln3)

        bars = [wxplot.PolyHistogram(hist, edges)]

        plot = wxplot.PlotGraphics(bars,
                                   title=self.title,
                                   xLabel=self.x_label,
                                   yLabel=self.y_label,
                                   )

        self.XSpec = (0, 75)

        self.EnableGrid = True
        self.Draw(plot)


def gen_mask_file(probe_list, mask_name, die_xy, dia, fixed_start_coord=False):
    """
    Generates a text file that can be read by the LabVIEW OWT program.

    probe_list should only contain die that are fully on the wafer. Die that
    are within the edxlucion zones but still fully on the wafer *are*
    included.

    probe_list is what's returned from maxGDW, so it's a list of
    (xCol, yRow, xCoord, yCoord, dieStatus) tuples
    """

    # 1. Create the file
    # 2. Add the header
    # 3. Append only the "probe" die to the die list.
    # 4. Finalize the file.
    path = os.path.join("\\\\hydrogen\\engineering\\\
Software\\LabView\\OWT\\masks", mask_name + ".ini")
    print("Saving mask file data to:")
    print(path)

    # Auto-calculate the edge row and column
    if not fixed_start_coord:
        # Adjust the original data to the origin
        # this defines where (1, 1) actually is.
        # TODO: Verify that "- 2" works for all cases
        edge_row = min({i[1] for i in probe_list if i[2] == 'excl'}) - 2
        edge_col = min({i[0] for i in probe_list if i[2] == 'excl'}) - 2
        print("edge_row = {}  edge_col = {}".format(edge_row, edge_col))

        for _i, _ in enumerate(probe_list):
            probe_list[_i] = list(probe_list[_i])
            probe_list[_i][0] -= edge_col
            probe_list[_i][1] -= edge_row
            probe_list[_i] = tuple(probe_list[_i])

    n_rc = (max({i[1] for i in probe_list}) + 1,
            max({i[0] for i in probe_list}) + 1)
    print("n_rc = {}".format(n_rc))

    # create a list of every die
    all_die = []
    for row in range(1, n_rc[0] + 1):        # Need +1 b/c end pt omitted
        for col in range(1, n_rc[1] + 1):    # Need +1 b/c end pt omitted
            all_die.append((row, col))

    # Note: I need list() so that I make copies of the data. Without it,
    # all these things would be pointing to the same all_die object.
    test_all_list = list(all_die)
    edge_list = list(all_die)
    every_list = list(all_die)
    die_to_probe = []

    # This algorithm is crap, but it works.
    # Create the exclusion list to add to the OWT file.
    # NOTE: I SWITCH FROM XY to RC HERE!
    for item in probe_list:
        _rc = (item[1], item[0])
        _state = item[2]
        try:
            if _state == "probe":
                test_all_list.remove(_rc)
                die_to_probe.append(_rc)
            if _state in ("excl", "flatExcl", "probe"):
                every_list.remove(_rc)
            if _state in ("excl", "flatExcl"):
                edge_list.remove(_rc)
        except ValueError:
#            print(_rc, _state)
#            raise
            continue

    # Determine the starting RC - this will be the min row, min column that
    # as a "probe" value. However, since the GDW algorithm now puts the
    # origin somewhere far off the wafer, we need to adjust the values a bit.
    min_row = min(i[0] for i in die_to_probe)
    min_col = min(i[1] for i in die_to_probe if i[0] == min_row)
    start_rc = (min_row, min_col)
    print("Landing Die: {}".format(start_rc))

    test_all_string = ''.join(["%s,%s; " % (i[0], i[1]) for i in test_all_list])
    edge_string = ''.join(["%s,%s; " % (i[0], i[1]) for i in edge_list])
    every_string = ''.join(["%s,%s; " % (i[0], i[1]) for i in every_list])

    home_rc = (1, 1)                         # Static value

    with open(path, 'w') as openf:
        openf.write("[Mask]\n")
        openf.write("Mask = \"%s\"\n" % mask_name)
        openf.write("Die X = %f\n" % die_xy[0])
        openf.write("Die Y = %f\n" % die_xy[1])
        openf.write("Flat = 0\n")                   # always 0
        openf.write("\n")
        openf.write("[%dmm]\n" % dia)
        openf.write("Rows = %d\n" % n_rc[0])
        openf.write("Cols = %d\n" % n_rc[1])
        openf.write("Home Row = %d\n" % home_rc[0])
        openf.write("Home Col = %d\n" % home_rc[1])
        openf.write("Start Row = %d\n" % start_rc[0])
        openf.write("Start Col = %d\n" % start_rc[1])
        openf.write("Every = \"" + every_string[:-2] + "\"\n")
        openf.write("TestAll = \"" + test_all_string[:-2] + "\"\n")
        openf.write("Edge Inking = \"" + edge_string[:-2] + "\"\n")
        openf.write("\n[Devices]\n")
        openf.write("PCM = \"0.2,0,0,,T\"\n")


def main():
    """ Main Code """
    MainApp()


if __name__ == "__main__":
    main()

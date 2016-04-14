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

# Third Party
import numpy as np
import wafer_map.wm_core as wm_core
import wafer_map.wm_info as wm_info
import wafer_map.wm_legend as wm_legend
import wx
import wx.lib.plot as wxplot

# Package / Application
try:
    # Imports used for unittests
    from . import gdw
    from . import (__version__,
                   __released__,
                   )
except (SystemError, ValueError):
    try:
        # Imports used by Spyder
        import gdw
        from __init__ import (__version__,
                              __released__,
                              )
    except ImportError:
         # Imports used by cx_freeze
        from gdwcalc import gdw
        from gdwcalc import (__version__,
                             __released__,
                             )


# TODO: Recode maxGDW to to include 'print' statements?

TITLE_TEXT = "GDWCalc v{}   Released {}".format(__version__,
                                                __released__)
INSTRUCTION_TEXT = """\
Keyboard Shortcuts:
Enter\tCalculate GDW
Home\tZoom to fit
C\tToggle centerlines
O\tToggle wafer outline
G\tToggle die grid lines
CTRL+Q\tExit

Click on wafer map to
zoom (mouse wheel) and
pan (middle-click + drag)"""


# ---------------------------------------------------------------------------
### Application Classes
# ---------------------------------------------------------------------------
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
        self.mv_gridlines.Check()

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
        self.mv_gridlines = wx.MenuItem(self.mview,
                                        wx.ID_ANY,
                                        "Die Grid\tG",
                                        "Show or hide the die grid lines",
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
        self.mview.Append(self.mv_gridlines)

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
        self.Bind(wx.EVT_MENU, self.toggle_gridlines, self.mv_gridlines)

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

    def toggle_gridlines(self, event):
        """ Call the WaferMapPanel.toggle_die_gridlines() method """
        self.panel.wafer_map.toggle_die_gridlines()

        # Hack to get center lines to always be on top
        if self.mv_gridlines.IsChecked():
            self.panel.wafer_map.toggle_crosshairs()
            self.panel.wafer_map.toggle_crosshairs()


# ---------------------------------------------------------------------------
### SubPanels
# ---------------------------------------------------------------------------
class XYTextCtrl(wx.Panel):
    """
    SubPanel for an XY input.

    Contains a 25px spacer, a LabeledTextCtrl, a stretch spacer, and a
    second LabeledTextCtrl in a horizontal pattern.

    Parameters:
    -----------
    parent : ``wx.Panel`` or ``wx.Frame`` object
        The parent panel or frame.
    x_default : str, optional
        The initial value for the X control.
    y_default : str, optional
        The initial value for the Y control.

    Public Properties:
    ------------------
    x_value, y_value : str
        Get or set the wx.TextCtrl value

    Layout:
    -------
    ::

        +-----------------------------+
        |   X: [____]        Y: [____]|
        +-----------------------------+
    """
    def __init__(self, parent, x_default="", y_default=""):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.x_default = x_default
        self.y_default = y_default

        self._init_ui()

    def _init_ui(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.x_ctrl = LabeledTextCtrl(self, "X:", self.x_default)
        self.y_ctrl = LabeledTextCtrl(self, "Y:", self.y_default)

        self.hbox.AddSpacer(25)
        self.hbox.Add(self.x_ctrl, 0, wx.ALIGN_CENTER_VERTICAL)
        self.hbox.AddStretchSpacer()
        self.hbox.Add(self.y_ctrl, 0, wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.hbox)

    @property
    def x_value(self):
        return self.x_ctrl.Value

    @x_value.setter
    def x_value(self, val):
        # ChangeValue does not fire wxECT_TEXT event; SetValue does.
        self.x_ctrl.ChangeValue(val)

    @property
    def y_value(self):
        return self.y_ctrl.Value

    @y_value.setter
    def y_value(self, val):
        # ChangeValue does not fire wxECT_TEXT event; SetValue does.
        self.y_ctrl.ChangeValue(val)


class LabeledTextCtrl(wx.Panel):
    """
    Generic labeled wx.TextCtrl.

    Parameters:
    -----------
    parent : ``wx.Panel`` or ``wx.Frame`` object
        The parent panel or frame.
    label : str, optional
        The label to display next to the ``wx.TextCtrl``.
    default : str, optional
        The initial value for the ``wx.TextCtrl``.

    Public Properties:
    ------------------
    value : str
        Get or set the wx.TextCtrl value

    Layout:
    -------
    ::

        +-------------------------+
        |label<5px><stretch>[____]|
        +-------------------------+
    """
    def __init__(self, parent, label="", default=""):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.label = label
        self.default = default

        self._init_ui()

    def _init_ui(self):
        # TODO: what to do if label is empty?
        self.text = wx.StaticText(self, label=self.label)
        self.ctrl = wx.TextCtrl(self, wx.ID_ANY, self.default, size=(50, -1))

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.hbox.Add(self.text, 0, wx.ALIGN_CENTER_VERTICAL)
        self.hbox.AddSpacer(5)
        self.hbox.AddStretchSpacer()
        self.hbox.Add(self.ctrl, 0, wx.ALIGN_CENTER_VERTICAL)

        self.SetSizer(self.hbox)

    @property
    def value(self):
        return self.ctrl.Value

    @value.setter
    def value(self, val):
        self.ctrl.Value = val

    # Make it easier for people used to wxPython's CamelCase
    Value = value


class LabeledXYCtrl(wx.Panel):
    """
    A XYTextCtrl with a label to the top-left.

    Parameters:
    -----------
    parent : ``wx.Panel`` or ``wx.Frame`` object
        The parent panel or frame.
    label : str, optional
        The label for the XY group.
    x_default : str, optional
        The initial X value
    y_default : str, optional
        The initial Y value

    Public Properties:
    ------------------
    x_value, y_value : str
        Get or set the wx.TextCtrl value

    Layout:
    -------
    ::

        +-------------------------+
        |label                    |
        |   X: [____]     Y:[____]|
        +-------------------------+
    """
    def __init__(self, parent, label="", x_default="", y_default=""):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.label = label
        self.x_default = x_default
        self.y_default = y_default

        self._init_ui()

    def _init_ui(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.text = wx.StaticText(self, label=self.label)

        self.ctrls = XYTextCtrl(self, self.x_default, self.y_default)

        self.vbox.Add(self.text)
        self.vbox.Add(self.ctrls, 0, wx.EXPAND)

        self.SetSizer(self.vbox)

    @property
    def x_value(self):
        return self.ctrls.x_ctrl.Value

    @x_value.setter
    def x_value(self, val):
        # ChangeValue does not fire wxECT_TEXT event; SetValue does.
        self.ctrls.x_ctrl.ChangeValue(val)

    @property
    def y_value(self):
        return self.ctrls.y_ctrl.Value

    @y_value.setter
    def y_value(self, val):
        # ChangeValue does not fire wxECT_TEXT event; SetValue does.
        self.ctrls.y_ctrl.ChangeValue(val)


class CheckedXYCtrl(wx.Panel):
    """
    A XYTextCtrl with a Checkbox to the top-left.

    Parameters:
    -----------
    parent : ``wx.Panel`` or ``wx.Frame`` object
        The parent panel or frame.
    label : str, optional
        The label for the checkbox.
    x_default : str, optional
        The initial X value
    y_default : str, optional
        The initial Y value

    Public Properties:
    ------------------
    x_value, y_value : str
        Get or set the wx.TextCtrl value
    checked : bool
        Get or set the checkbox value.

    Layout:
    -------
    ::

        +--------------------------+
        |[] label                  |
        |   X: [____]     Y: [____]|
        +--------------------------+
    """
    def __init__(self, parent, label="", x_default="", y_default=""):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.label = label
        self.x_default = x_default
        self.y_default = y_default

        self._init_ui()

    def _init_ui(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.chk_ctrl = wx.CheckBox(self, label=self.label)

        self.ctrls = XYTextCtrl(self, self.x_default, self.y_default)

        self.vbox.Add(self.chk_ctrl)
        self.vbox.Add(self.ctrls, 0, wx.EXPAND)

        self.SetSizer(self.vbox)

    @property
    def checked(self):
        return self.chk_ctrl.IsChecked()

    @checked.setter
    def checked(self, val):
        if val not in (True, False):
            raise TypeError("Value must be a boolean: `True` or `False`")
        self.chk_ctrl.SetValue(val)

    @property
    def x_value(self):
        return self.ctrls.x_ctrl.Value

    @x_value.setter
    def x_value(self, val):
        # ChangeValue does not fire wxECT_TEXT event; SetValue does.
        self.ctrls.x_ctrl.ChangeValue(val)

    @property
    def y_value(self):
        return self.ctrls.y_ctrl.Value

    @y_value.setter
    def y_value(self, val):
        # ChangeValue does not fire wxECT_TEXT event; SetValue does.
        self.ctrls.y_ctrl.ChangeValue(val)


class CheckedTextCtrl(wx.Panel):
    """
    A labeled TextCtrl with a Checkbox to the top-left.

    Parameters:
    -----------
    parent : ``wx.Panel`` or ``wx.Frame`` object
        The parent panel or frame.
    check_label : str, optional
        The label for the checkbox.
    ctrl_label : str, optional
        The label for the ``wx.TextCtrl``
    default : str, optional
        The initial value of the ``wx.TextCtrl``

    Public Properties:
    ------------------
    value : str
        Get or set the ``wx.TextCtrl`` value
    checked : bool
        Get or set the checkbox value.

    Layout:
    -------
    ::

        +----------------------------+
        |[] check_label              |
        |    ctrl_label:       [____]|
        +----------------------------+
    """
    def __init__(self, parent, check_label="", ctrl_label="", default=""):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.check_label = check_label
        self.ctrl_label = ctrl_label
        self.default = default

        self._init_ui()

    def _init_ui(self):
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        self.chk_ctrl = wx.CheckBox(self, label=self.check_label)

        self.ctrl = LabeledTextCtrl(self, self.ctrl_label, self.default)

        self.hbox.AddSpacer(25)
        self.hbox.Add(self.ctrl, 1, wx.EXPAND)

        self.vbox.Add(self.chk_ctrl)
        self.vbox.Add(self.hbox, 0, wx.EXPAND)

        self.SetSizer(self.vbox)

    @property
    def checked(self):
        return self.chk_ctrl.IsChecked()

    @checked.setter
    def checked(self, val):
        self.chk_ctrl.SetValue(val)

    @property
    def value(self):
        return self.ctrl.Value

    @value.setter
    def value(self, val):
        self.ctrl.ChangeValue(val)


class StaticTextResult(wx.Panel):
    """
    A labeled wx.StaticText with value getters and setters

    Parameters:
    -----------
    parent : ``wx.Panel`` or ``wx.Frame`` object
        The parent panel or frame.
    label : str, optional
        The label to display
    default : str, optional
        The initial value to display

    Public Properties:
    ------------------
    value : str
        Get or set the displayed value

    Layout:
    -------
    ::

        +----------------------------+
        |label                  value|
        +----------------------------+
    """
    def __init__(self, parent, label, default):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.label = label
        self.default = default

        self._init_ui()

    def _init_ui(self):
        self.lbl = wx.StaticText(self, label=self.label)
        self._value = wx.StaticText(self, label=self.default,
                                    style=wx.ALIGN_RIGHT|wx.ST_NO_AUTORESIZE)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

        self.hbox.Add(self.lbl, 0)
        self.hbox.AddStretchSpacer()
        self.hbox.Add(self._value, 1)

        self.SetSizer(self.hbox)

    @property
    def value(self):
        return self._value.GetLabel()

    @value.setter
    def value(self, val):
        if isinstance(val, (float, int)):
            val = "{:>.8g}".format(val)
        elif isinstance(val, str):
            pass
        else:
            raise TypeError("Value must be a string, int, or float")

        self._value.SetLabel(val)


class StaticXYTextResult(wx.Panel):
    """
    Not used.
    """
    def __init__(self, parent, x_default, y_default):
        wx.Panel.__init__(self, parent)
        self.parent = parent
        self.x_default = x_default
        self.y_default = y_default

        self._init_ui()

    def _init_ui(self):
        self._x_value = StaticTextResult(self, "X (col):", self.x_default)
        self._y_value = StaticTextResult(self, "Y (row):", self.y_default)

        self.hbox = wx.BoxSizer(wx.HORIZONTAL)

#        self.hbox.AddSpacer(10)
#        self.hbox.AddStretchSpacer()
        self.hbox.Add(self._x_value, 0, wx.EXPAND)
#        self.hbox.AddSpacer(10)
        self.hbox.Add(self._y_value, 0, wx.EXPAND)

        self.SetSizer(self.hbox)

    @property
    def x_value(self):
        return self._x_value.GetLabel()

    @x_value.setter
    def x_value(self, val):
        self._x_value.SetLabel(val)

    @property
    def y_value(self):
        return self._y_value.GetLabel()

    @y_value.setter
    def y_value(self, val):
        self._y_value.SetLabel(val)


class ResultPanel(wx.Panel):
    """
    The entire results panel.
    """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        self.gdw_result = StaticTextResult(self,
                                           "Gross Die per Wafer:",
                                           "0",
                                           )
        self.ee_loss_result = StaticTextResult(self,
                                               "Die lost to Edge Exclusion:",
                                               "0",
                                               )
        self.flat_loss_result = StaticTextResult(self,
                                                 "Die Lost to Wafer Flat:",
                                                 "0",
                                                 )
        self.fe_loss_result = StaticTextResult(self,
                                                 "Die Lost to Flat Exclusion:",
                                                 "0",
                                                 )
        self.scribe_loss_result = StaticTextResult(self,
                                                 "Die Lost to Scribe Exclusion:",
                                                 "0",
                                                 )

        self.shape_x_result = StaticTextResult(self,
                                               "Center X (Column) Offset:",
                                               "0 (odd)")
        self.shape_y_result = StaticTextResult(self,
                                               "Center Y (Row) Offset:",
                                               "0 (odd)")

        self.center_x_result = StaticTextResult(self, "Center X Coord:", "0")
        self.center_y_result = StaticTextResult(self, "Center Y Coord:", "0")

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.gdw_result, 0, wx.EXPAND)
        self.vbox.Add(self.ee_loss_result, 0, wx.EXPAND)
        self.vbox.Add(self.flat_loss_result, 0, wx.EXPAND)
        self.vbox.Add(self.fe_loss_result, 0, wx.EXPAND)
        self.vbox.Add(self.scribe_loss_result, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.shape_x_result, 0, wx.EXPAND)
        self.vbox.Add(self.shape_y_result, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.center_x_result, 0, wx.EXPAND)
        self.vbox.Add(self.center_y_result, 0, wx.EXPAND)

        self.SetSizer(self.vbox)


class InputPanel(wx.Panel):
    """ Main input panel """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        self._init_ui()

    def _init_ui(self):
        self.size_input = LabeledXYCtrl(self, "Die Size (mm):", "5", "5")
        self.dia_input = LabeledTextCtrl(self, "Diameter (mm)", "150")
        self.ee_input = LabeledTextCtrl(self, "Edge Exclusion (mm)", "5")
        self.fe_input = LabeledTextCtrl(self, "Flat Exclusion (mm)", "5")
        self.fo_ctrl = CheckedXYCtrl(self,
                                     "Force Fixed Offsets? (mm):",
                                     "0",
                                     "0",
                                     )
        self.fdc_ctrl = CheckedXYCtrl(self, "Force 1st Die Coord?", "0", "0")
        self.scribe_loc_ctrl = CheckedTextCtrl(self,
                                               "Use the Aizu Scribe Location?",
                                               "Y Coord (mm)",
                                               "70.2",
                                               )

        self.vbox = wx.BoxSizer(wx.VERTICAL)
        self.vbox.Add(self.size_input, 0, wx.EXPAND)
        self.vbox.Add(self.dia_input, 0, wx.EXPAND)
        self.vbox.Add(self.ee_input, 0, wx.EXPAND)
        self.vbox.Add(self.fe_input, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.fo_ctrl, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.fdc_ctrl, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.scribe_loc_ctrl, 0, wx.EXPAND)

        self.SetSizer(self.vbox)


# ---------------------------------------------------------------------------
### Main UI Panel
# ---------------------------------------------------------------------------
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
        self.input_panel = InputPanel(self)

        # Calculate Button
        self.calc_button = wx.Button(self, label="Calculate")
        self.Bind(wx.EVT_BUTTON, self.on_calc_gdw, self.calc_button)

        self.gen_mask_button = wx.Button(self, label="Generate Mask File")
        self.Bind(wx.EVT_BUTTON, self.on_gen_mask, self.gen_mask_button)

        # Actual Wafer Map
        legend_values = [
                         "flat",
                         "excl",
                         "probe",
                         "flatExcl",
                         "scribe",
                         ]
        legend_colors = [
                         wx.Colour(191, 0, 0),
                         wx.Colour(0, 191, 191),
                         wx.Colour(95, 191, 0),
                         wx.Colour(95, 0, 191),
                         wx.Colour(152, 191, 0),
                         ]
        self.wafer_map = wm_core.WaferMapPanel(self,
                                               self.coord_list,
                                               self.wafer_info,
                                               data_type='discrete',
                                               plot_die_centers=False,
                                               show_die_gridlines=True,
                                               discrete_legend_values=legend_values
                                               )

        # Hack until I raise the legend colors up to WaferMapPanel constructor.
#        self.wafer_map.legend = wm_legend.DiscreteLegend(self.wafer_map,
#                                                         legend_values,
#                                                         legend_colors,
#                                                         )
#
#        self.wafer_map.toggle_legend()
#        self.wafer_map.toggle_legend()

        # Radius Histograms
        radius_sqrd_data = list(
           (self.wafer_info.die_size[0] * (self.wafer_info.center_xy[0] - die[0]))**2
           + (self.wafer_info.die_size[1] * (self.wafer_info.center_xy[1] - die[1]))**2
           for die in self.coord_list)
        radius_data = list(math.sqrt(item) for item in radius_sqrd_data)
        self.histograms = RadiusPlots(self, radius_data)

        # Result Info
        self.results = ResultPanel(self)

        # Instructions:
        self.instructions = wx.StaticText(self, label=INSTRUCTION_TEXT)

        # Set the Layout
        self.hbox = wx.BoxSizer(wx.HORIZONTAL)
        self.vbox = wx.BoxSizer(wx.VERTICAL)

        # Add items to the vertical side-bar box.
        self.vbox.Add(self.input_panel, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.calc_button, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.gen_mask_button, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.results, 0, wx.EXPAND)
        self.vbox.AddSpacer(10)
        self.vbox.Add(self.instructions, 0, wx.EXPAND)

        # Add items to the main horizontal box sizer.
        self.hbox.AddSpacer(2)
        self.hbox.Add(self.vbox, 0, wx.EXPAND)
        self.hbox.AddSpacer(20)
        self.hbox.Add(self.wafer_map, 2, wx.EXPAND)
        self.hbox.Add(self.histograms, 1, wx.EXPAND)

        self.SetSizer(self.hbox)

    def on_calc_gdw(self, event):
        """ Performs the GDW Calculation on button click """
        print("Button Pressed")

        self.die_x = float(self.input_panel.size_input.x_value)
        self.die_y = float(self.input_panel.size_input.y_value)
        self.die_xy = (self.die_x, self.die_y)
        self.dia = int(self.input_panel.dia_input.Value)
        self.ee = float(self.input_panel.ee_input.Value)
        self.fe = float(self.input_panel.fe_input.Value)
        self.fo_bool = bool(self.input_panel.fo_ctrl.checked)
        self.x_fo = float(self.input_panel.fo_ctrl.x_value)
        self.y_fo = float(self.input_panel.fo_ctrl.y_value)
        self.fo = (self.x_fo, self.y_fo)
        self.grid_offset = (0, 0)
        self.north_limit = float(self.input_panel.scribe_loc_ctrl.value)

        if not self.input_panel.scribe_loc_ctrl.checked:
            self.north_limit = None

        # If using fixed offsets, call other function.
        if self.fo_bool:
            probe_list, self.center_xy = gdw.gdw(self.die_xy,
                                                 self.dia,
                                                 self.fo,
                                                 self.ee,
                                                 self.fe,
                                                 self.north_limit
                                                 )

        else:
            probe_list, self.center_xy = gdw.maxGDW(self.die_xy,
                                                    self.dia,
                                                    self.ee,
                                                    self.fe,
                                                    self.north_limit
                                                    )
        self.coord_list = [(i[0], i[1], i[4]) for i in probe_list]

        # If using a forced starting die (top-left), adjust coords
        if self.input_panel.fdc_ctrl.checked:
            # Gind the topmost then leftmost probed die.
            min_y = min({c[1] for c in self.coord_list if c[2] == "probe"})
            min_x = min([c[0] for c in self.coord_list
                         if c[2] == "probe" and c[1] == min_y])

            # Calculate the delta
            delta_x = min_x - int(self.input_panel.fdc_ctrl.x_value)
            delta_y = min_y - int(self.input_panel.fdc_ctrl.y_value)

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
        self.scribe_loss = 0

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
            elif rcd[2] == 'scribe':
                self.scribe_loss += 1
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

        self.results.gdw_result.value = self.gdw
        self.results.ee_loss_result.value = self.ee_loss
        self.results.flat_loss_result.value = self.flat_loss
        self.results.fe_loss_result.value = self.fe_loss
        self.results.scribe_loss_result.value = self.scribe_loss

        self.x_offset = self.center_xy[0] % 1
        if self.x_offset == 0:
            self.x_offset = "0 (odd)".format(self.x_offset)
        else:
            self.x_offset = "0.5 (even)".format(self.x_offset)
        self.results.shape_x_result.value = self.x_offset

        self.y_offset = self.center_xy[1] % 1
        if self.y_offset == 0:
            self.y_offset = "0 (odd)".format(self.y_offset)
        else:
            self.y_offset = "0.5 (even)".format(self.y_offset)
        self.results.shape_y_result.value = self.y_offset

        self.results.center_x_result.value = self.center_xy[0]
        self.results.center_y_result.value = self.center_xy[1]

        # Update the screen
        self.Refresh()
        self.Update()

    def on_gen_mask(self, event):
        """ Handle the gen_mask event """
        mask = "MDH00"
        statusbar = self.parent.StatusBar

        try:
            gdw.gen_mask_file(self.coord_list, mask,
                              self.die_xy, self.dia, self.fdc_ctrl.checked)
        except Exception as err:
            print(err)
            statusbar.SetStatusText("Error: {}".format(err))
            raise
        statusbar.SetStatusText("Mask saved to '{}'".format(mask))


# ---------------------------------------------------------------------------
### Plotting Panels
# ---------------------------------------------------------------------------
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


def main():
    """ Main Code """
    MainApp()


if __name__ == "__main__":
    main()

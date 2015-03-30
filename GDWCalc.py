# -*- coding: utf-8 -*-
# pylint: disable=W0201
"""
@name:              GDWCalc.py
@vers:              1.5
@author:            Douglas Thor
@created:           2013-04-19
@modified:          2015-01-27
@descr:             Calcualtes Gross Die per Wafer (GDW), accounting for
                    wafer flat, edge exclusion, and front-side-scribe (FSS)
                    exclusion (also called flat exclusion).

                    Returns nothing.

                    Prints out the Offset Type (Odd or Even) and the GDW, as
                    well as where die were lost (edge, flat, FSS)

"""

from __future__ import print_function
import douglib.gdw as gdw
import wafer_map.wm_core as wm_core
import wafer_map.wm_info as wm_info
import wx


# Defined by SEMI M1-0302
__version__ = "1.5.1"
__released__ = "2015-01-27"
# TODO: Recode maxGDW to to include 'print' statements?
# TODO: add "Save" button which outputs data


INSTRUCTION_TEXT = """
Keyboard Shortcuts:
Enter\tCalculate GDW
Home\tZoom to fit
C\tToggle centerlines
O\tToggle wafer outline
L\tToggle legend
CTRL+C\tExit

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
                          title="GDWCalc v1.5.3",
                          size=(1000, 700),
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

    def _add_menu_items(self):
        """ Appends MenuItems to each menu """
        self.mfile.AppendItem(self.mf_close)
        self.medit.AppendItem(self.me_calc)

    def _add_menus(self):
        """ Appends each menu to the menu bar """
        self.menu_bar.Append(self.mfile, "&File")
        self.menu_bar.Append(self.medit, "&Edit")

    def _bind_events(self):
        """ Binds events to varoius MenuItems """
        self.Bind(wx.EVT_MENU, self.on_quit, self.mf_close)
        self.Bind(wx.EVT_MENU, self.on_calc, self.me_calc)

    def on_quit(self, event):
        """ Actions for the quit event """
        self.Close(True)

    def on_calc(self, event):
        """ Action for Calc event """
        self.panel.calc_gdw(event)


class MainPanel(wx.Panel):
    """ Main Panel. Contains parameters and the map """
    def __init__(self, parent):
        wx.Panel.__init__(self, parent)
        self.parent = parent

        probe_list, self.center_xy = gdw.maxGDW((5, 5), 150, 5, 5)
        self.coord_list = [(i[0], i[1], i[4]) for i in probe_list]

        self.wafer_info = wm_info.WaferInfo((5, 5), self.center_xy)

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

        # Calculate Button
        self.calc_button = wx.Button(self, label="Calculate")
        self.Bind(wx.EVT_BUTTON, self.calc_gdw, self.calc_button)

        # Actual Wafer Map
        legend_values = [
                         "flat",
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
        self.fgs_inputs = wx.FlexGridSizer(rows=8, cols=2)
        self.fgs_inputs.AddMany([self.x_lbl, self.x_input,
                                 self.y_lbl, self.y_input,
                                 self.dia_lbl, self.dia_input,
                                 self.ee_lbl, self.ee_input,
                                 self.fe_lbl, self.fe_input,
                                 self.fo_chk, (-1, -1),
                                 self.x_fo_lbl, self.x_fo_input,
                                 self.y_fo_lbl, self.y_fo_input,
                                 ])

        self.fgs_results = wx.FlexGridSizer(rows=13, cols=2, hgap=10)

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
        self.vbox.Add((-1, 20), 0, wx.EXPAND)
        self.vbox.Add(self.calc_button, 0, wx.EXPAND)
        self.vbox.Add((-1, 20), 0, wx.EXPAND)
        self.vbox.Add(self.fgs_results, 0, wx.EXPAND)
        self.vbox.Add(self.instructions, 0, wx.EXPAND)
        self.hbox.Add(self.vbox, 0, wx.EXPAND)
        self.hbox.Add((20, -1), 0, wx.EXPAND)
        self.hbox.Add(self.wafer_map, 1, wx.EXPAND)

        self.SetSizer(self.hbox)

    def calc_gdw(self, event):
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

        # Calculate the Die Counts
        # TODO: Update gdw.maxGDW to return these values instead
        self.gdw = 0
        self.flat_loss = 0
        self.ee_loss = 0
        self.fe_loss = 0

        # TODO: This isn't pythonic at all, but I'm in a rush
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
        self.wafer_map.xyd_dict = self.wafer_map.xyd_to_dict(self.coord_list)
        self.wafer_map._create_legend()
        self.wafer_map.draw_die()
        self.wafer_map.draw_die_center()
        self.wafer_map.draw_wafer_objects()
        self.wafer_map.zoom_fill()

        self.Refresh()
        self.Update()

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


def main():
    """ Main Code """
    MainApp()


if __name__ == "__main__":
    main()

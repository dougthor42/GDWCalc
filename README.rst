==========
GDWCalc
==========

A gross die per wafer (GDW) calculator.

Plots up a wafer map of rectangular die based on the die size, wafer diameter,
and exclusion zones. Die are colored by their status (good to probe, crosses
edge exclusion, crosses flat exclusion, or falls off due to the wafer flat.

Knows about SEMI SPEC M1-0302 which defines wafer flat sizes.


Changelog:
----------
v1.5.6 : 2015-09-16
  - Added ability to set the 1st die coordinates.

v1.5.5 : 2015-08-25
  - Added ability to export map as an OWT mask file.
  - Renamed some variables to match my coding style.

v1.5.4 : 2015-08-05
  - Updated build method, no changes to program.

v1.5.3 : 2015-03-30
  - Fixed issue where plot colors would change if 0 die were lost for
    a given category
  - Die centers will now plot by default
  - Added option to plot and calculate GDW using a fixed offset rather than
    having the program find an optimal offset.

v1.5.2 : 2015-01-28
  - Fixed bug in douglib.gdw.gdw() where die were incorrectly labeled as
    flat-exclusion or wafer-flat.
  - First release with changelog.
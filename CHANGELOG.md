# Changelog:

## v1.7.3 (2017-02-20)
+ Updated CI.

## v1.7.2 - TBD
+ Moved `gdw` to separate package
+ Fixed typos

## v1.7.1 - 2016-04-21
+ Fixed issue where mask file generation would not work.
  [GL #4](http://gitlab.tph.local/dthor/GDWCalc/issues/4)
+ Edge and Flat exclusion now defaults to 4.5mm

## v1.7.0 - 2016-04-14
+ Massive UI refactoring.
+ Slight change in UI organization
+ Added option to exclude a top-side scribe exclusion.
+ Removed all requirements on `douglib`.
+ CI updates and fixes
+ Factored out gross die per wafer calculations into separate module
+ Documentation updates.

## v1.6.1 - 2016-03-08
+ Executable is now built using Python 3.4 and wxPython Phoenix

## v1.6.0 - 2015-11-11
+ Added keyboard shortcuts for wafer map:
    + Home: zoom fill
    + o: toggle wafer outline on/off
    + c: toggle wafer center crosshairs on/off
+ Added histograms of # die by Radius (mm) and by equal-area (2000mm^2)

## v1.5.7 - 2015-10-30
+ Updated wafer_map to version 1.0.11. This adds a display for radius to
  the status bar.

## v1.5.6 - 2015-09-16
+ Added ability to set the 1st die coordinates.

## v1.5.5 - 2015-08-25
+ Added ability to export map as an OWT mask file.
+ Renamed some variables to match my coding style.

## v1.5.4 - 2015-08-05
+ Updated build method, no changes to program.

## v1.5.3 - 2015-03-30
+ Fixed issue where plot colors would change if 0 die were lost for
  a given category
+ Die centers will now plot by default
+ Added option to plot and calculate GDW using a fixed offset rather than
  having the program find an optimal offset.

## v1.5.2 - 2015-01-28
+ Fixed bug in douglib.gdw.gdw() where die were incorrectly labeled as
  flat-exclusion or wafer-flat.
+ First release with changelog.

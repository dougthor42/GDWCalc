# -*- coding: utf-8 -*-
# Let's start with some default (for me) imports...

from cx_Freeze import setup, Executable

# Process the includes, excludes and packages first
includes = []
excludes = ['_gtkagg', '_tkagg', 'bsddb', 'curses', 'email', 'pywin.debugger',
            'pywin.debugger.dbgcon', 'pywin.dialogs', 'tcl',
            'Tkconstants', 'Tkinter', 'scipy', 'pil']
packages = []
path = []

# This is a place where the user custom code may go. You can do almost
# whatever you want, even modify the data_files, includes and friends
# here as long as they have the same variable name that the setup call
# below is expecting.

# No custom code added

# The setup for cx_Freeze is different from py2exe. Here I am going to
# use the Python class Executable from cx_Freeze

GUI2Exe_Target_1 = Executable(
    # what to build
    script="GDWCalc v1.5.5.py",
    initScript=None,
    base='Win32GUI',
    targetDir=r"dist",
    targetName="GDWCalc v1.5.5.exe",
    compress=True,
    copyDependentFiles=True,
    appendScriptToExe=False,
    appendScriptToLibrary=False,
    icon=None
    )

# That's serious now: we have all (or almost all) the options cx_Freeze
# supports. I put them all even if some of them are usually defaulted
# and not used. Some of them I didn't even know about.

setup(
    version="1.5.5",
    description="A calculator for gross die per wafer (GDW)",
    author="Douglas Thor",
    name="GDWCalc",
    options={"build_exe": {"includes": includes,
                           "excludes": excludes,
                           "packages": packages,
                           "path": path
                           }
             },
    executables=[GUI2Exe_Target_1]
    )

# This is a place where any post-compile code may go.
# You can add as much code as you want, which can be used, for example,
# to clean up your folders or to do some particular post-compilation
# actions.

# No post-compilation code added


# And we are done. That's a setup script :-D

# -*- coding: utf-8 -*-
"""
@name:          build.py
@vers:          0.1
@author:        dthor

Usage:
    build.py
    build.py (-h | --help)
    build.py --version

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""

from __future__ import print_function
import subprocess
from docopt import docopt
from os import walk
import os.path as osp
import zipfile

__author__ = "Douglas Thor"
__version__ = "v0.1.0"

EXCLUDED_MODULES = ["_gtkagg",
                    "_tkagg",
                    "bsddb",
                    "curses",
                    "email",
                    "pywin.debugger",
                    "pywin.debugger.dbgcon",
                    "pywin.dialogs",
                    "tcl",
                    "Tkconstants",
                    "Tkinter",
                    "scipy",
                    "pil",
                    ]
EX_MOD_STR = ",".join(EXCLUDED_MODULES)

CALL_STR = ['cxfreeze.bat', "GDWCalc.py",
            '--target-dir', "dist\GDWCalc v1.5.3",
            "-s", "--compress",
            "--base-name", "Win32GUI",
            "--exclude-modules", EX_MOD_STR,
            ]


def zipdir(path, zipfile):
    """ Zips a directory """
    for root, dirs, files in walk(path):
        for fname in files:
            zipfile.write(osp.join(root, fname))

print("--------------------------------")
print("-----Starting Build Process-----")
print("--------------------------------")
print("subprocess.call(%s)" % CALL_STR)
subprocess.call(CALL_STR)
print("--------------------------------")
print("---------Build Complete---------")
print("--------------------------------\n")

print("Bundling into .zip file...")
args = docopt(__doc__, version=__version__)
#folder = args['PATH']
folder = "dist\GDWCalc v1.5.3"

zipname = osp.split(folder)[1] + '.zip'
zippath = osp.join(osp.split(folder)[0], zipname)
print(zipname)
print(zippath)

zipf = zipfile.ZipFile(zippath, 'w')
zipdir(folder, zipf)
zipf.close()
print("Complete")

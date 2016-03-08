# -*- coding: utf-8 -*-
"""
setup.py file for GDWCalc.

@author: dthor
"""
### #------------------------------------------------------------------------
### Imports
### #------------------------------------------------------------------------
# Standard Library
from setuptools import setup, find_packages
import logging

# Third Party

# Package / Application
from gdwcalc import (__version__,
                     __project_url__,
                     __project_name__,
                     __description__,
                     __long_descr__,
                     )

# turn off logging if we're going to build a distribution
logging.disable(logging.CRITICAL)

setup(
    name=__project_name__,
    version=__version__,
    description=__description__,
    long_description=__long_descr__,
    packages=find_packages(),
    author="Douglas Thor",
    url=__project_url__,
    classifiers=[
        "Development Status :: 4 - Beta",
        "Environment :: Win32 (MS Windows)",
        "Environment :: X11 Applications",
        "Environment :: MacOS X",
        "Intended Audience :: End Users/Desktop",
        "License :: OSI Approved :: GNU General Public License v2 (GPLv2)",
        "Operating System :: Microsoft :: Windows",
        "Operating System :: MacOS :: MacOS X",
        "Operating System :: POSIX :: Linux",
        "Programming Language :: Python :: 3.4",
        "Programming Language :: Python :: 3 :: Only",
        "Programming Language :: Python :: Implementation :: CPython",
        "Topic :: Utilities",
        ],
    requires=["wxPython",
              "douglib",
              "wafer_map"
              ],
)

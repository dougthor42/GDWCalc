# -*- coding: utf-8 -*-
"""
@name:          bundle.py
@vers:          0.1.0
@author:        dthor
@created:       Wed Jan 28 15:38:26 2015
@descr:         Bundles the files created by build.bat into a .zip file.

Usage:
    bundle.py PATH

Options:
    -h --help           # Show this screen.
    --version           # Show version.
"""

from __future__ import print_function, division
from __future__ import absolute_import
#from __future__ import unicode_literals

from docopt import docopt
from os import walk
import os.path as osp
import zipfile

__author__ = "Douglas Thor"
__version__ = "v0.1.0"


def zipdir(path, zipfile):
    """ Zips a directory """
    for root, dirs, files in walk(path):
        for fname in files:
            zipfile.write(osp.join(root, fname))


def main():
    """ Main Code """
    args = docopt(__doc__, version=__version__)
    folder = args['PATH']

    zipname = osp.split(folder)[1] + '.zip'
    zippath = osp.join(osp.split(folder)[0], zipname)
    print(zipname)
    print(zippath)

    zipf = zipfile.ZipFile(zippath, 'w')
    zipdir(folder, zipf)
    zipf.close()


if __name__ == "__main__":
    main()

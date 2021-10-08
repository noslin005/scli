from __future__ import absolute_import
from app import cli

import os
import sys

__author__ = "Nilson Lopes"
__copyright__ = "Copyright 2020, Source Code Corporation"
__version__ = "0.1.0"
__email__ = "nlopes@sourcecode.com"


if __package__ == '':
    path = os.path.dirname(os.path.dirname(__file__))
    sys.path.insert(0, path)


if __name__ == '__main__':
    sys.exit(cli.main())

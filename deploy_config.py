# -*- coding: utf-8 -*-
import os

PYTHON_VERSION = '3.4'
PYTHON_ENV_MODULE = 'venv'

if 'SYSTEMDRIVE' in os.environ:
    PYTHON_PATH = os.path.join(os.environ['SYSTEMDRIVE'] + os.path.sep, 'python34', 'python.exe')


#!/bin/bash
export PYTHONPATH=/core/TD/PPlib:/core/Linux/Lib/PythonLib:/core/TD/sg4th/src:/core/TD/shotgunAPI/python-api-master:$PYTHONPATH
export PATH=/core/Linux/APPZ/Python/2.7/bin:$PATH
export LD_LIBRARY_PATH=/core/Linux/APPZ/Python/2.7/lib:$LD_LIBRARY_PATH

/core/Linux/APPZ/Python/2.7/bin/python2.7 /core/Linux/APPZ/shell/nimby/nimby_checker.py

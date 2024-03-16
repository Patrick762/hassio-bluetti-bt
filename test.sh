#!/bin/sh

# Execute unittests of python library
python3 -m unittest discover -s tests -p "*_test.py"

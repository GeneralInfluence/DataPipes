#!/bin/bash
python setup.py sdist bdist_wheel
git commit -am '"'$1'"'
git push origin master

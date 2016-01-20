#!/bin/bash

echo "------------------------------------"
echo "Cleaning workspace"
echo "------------------------------------"

# TODO JT 2014-02-13 - Should clean the workspace
rm -rf src/build
rm -rf *.dmg
rm -rf *.tar.gz
rm -f src/VERSION.py
rm -rf src/peachyprinter/VERSION.py
rm -f version.properties 

echo "------------------------------------"
echo "Extracting Git Revision Number"
echo "------------------------------------"

SEMANTIC=`cat symantic.version`

function trim() { echo $1; }

if [ -z $GIT_HOME ]; then
  if [ -f "/usr/local/bin/git" ]; then
    export GIT_HOME=/usr/local/bin/git
  elif [ -f "/usr/bin/git" ]; then
    export GIT_HOME=/usr/bin/git
  elif [ -f "/bin/git" ]; then
    export GIT_HOME=/bin/git
  else
    echo "Could not find git."
    exit 1
  fi
fi

export GIT_REV_COUNT_RAW=`$GIT_HOME log --pretty=oneline | wc -l`
export GIT_REV_COUNT=`trim $GIT_REV_COUNT_RAW`
export GIT_REV=`$GIT_HOME rev-parse HEAD`

VERSION=$SEMANTIC.$TAG$GIT_REV_COUNT
echo "Version: $VERSION"
echo "# THIS IS A GENERATED FILE " > version.properties
echo "version='$VERSION'" >> version.properties
echo "revision='$GIT_REV'" >> version.properties
echo "Git Revision Number is $GIT_REV_COUNT"
cp version.properties src/peachyprinter/VERSION.py
cp version.properties src/VERSION.py


echo "------------------------------------"
echo "Running Setup"
echo "------------------------------------"
source ./setup_mac.sh
if [ $? != 0 ]; then
    echo "FAILED SETUP ABORTING"
    exit 55
fi

echo "------------------------------------"
echo "Running Tests"
echo "------------------------------------"

python -m pip install mock==1.0.1
python test/test-all.py

if [ $? != 0 ]; then
    echo "FAILED TESTS ABORTING"
    exit 55
fi
cd src
python setup.py sdist

if [ $? != 0 ]; then
    echo "FAILED PACKAGING ABORTING"
    exit 56
fi
cd ..

mv src/dist/PeachyPrinterToolsAPI*.tar.gz .

if [ $? != 0 ]; then
    echo "FAILED MOVE PACKAGE ABORTING"
    exit 57
fi
echo "------------------------------------"
echo "COMPLETE SUCCESS"
echo "------------------------------------"

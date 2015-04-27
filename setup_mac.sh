#!/bin/bash

echo "----Checking for already running Virtual Environment----"
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Deactivitate the existing virtual enviroment before running this script."
    echo "This can be done with the \"deactivate\" command."
    exit 53 
fi

echo "----Checking for Pip----"
command -v pip 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "Pip not available, you should be prompted for install:"
    sudo easy_install pip
    if [ $? != 0 ]; then
        echo "FAILURE: Pip failed installing"
        WILL_FAIL=11
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: Pip failed installing"
    fi
fi


echo "----Checking for virtualenv----"
command -v virtualenv 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "virtualenv not available, you should be prompted for install:"
    sudo pip install virtualenv
    if [ $? != 0 ]; then
        echo "FAILURE: virtualenv failed installing"
        WILL_FAIL=12
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: virtualenv failed installing"
    fi
fi

echo "----Checking for and create a virtual environment----"
CREATE_VENV="TRUE"
if [ -d "venv" ]; then
    while true; do
    read -p "Do you wish remove and re-install this environment?" yn
    case $yn in
        [Yy]* ) rm -rf venv && CREATE_VENV="TRUE"; break;;
        [Nn]* ) CREATE_VENV="FALSE"; break;;
        * ) echo "Please answer yes or no.";;
    esac
    done
fi
if [ $CREATE_VENV == "TRUE" ]; then
    virtualenv venv
    if [ $? != 0 ]; then
        echo "Virutal environment failed"
        exit 59
    fi
fi
source venv/bin/activate
if [[ "$VIRTUAL_ENV" == "" ]]; then
    echo "FAILURE: Virutal environment creation failed"
    exit 666
fi

echo "----Setting up virtual environment----"
SETUP_TMP="setup_tmp"
WILL_FAIL=0
FAIL_REASONS=""
export CFLAGS=-Qunused-arguments
export CPPFLAGS=-Qunused-arguments

echo "--------Setting up numpy----"
python -c"import numpy" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "Numpy not available adding"
    pip install -U --force numpy
    if [ $? != 0 ]; then
        echo "FAILURE: Numpy failed installing"
        WILL_FAIL=1
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: Numpy failed installing"
    fi
fi

echo "--------Setting up mock----"
python -c"import mock" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "mock not available adding"
    pip install -U mock
    if [ $? != 0 ]; then
        echo "FAILURE: mock failed installing"
        WILL_FAIL=2
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: mock failed installing"
    fi
fi

echo "--------Setting up pyserial----"
python -c"import pyserial" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "pyserial not available adding"
    pip install -U pyserial
    if [ $? != 0 ]; then
        echo "FAILURE: pyserial failed installing"
        WILL_FAIL=2
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: pyserial failed installing"
    fi
fi

echo "--------Setting up libusb1----"
python -c"import libusb1" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "libusb1 not available adding"
    pip install -U libusb1
    if [ $? != 0 ]; then
        echo "FAILURE: libusb1 failed installing"
        WILL_FAIL=2
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: libusb1 failed installing"
    fi
fi

echo "--------Setting up protobuf----"
python -c"import protobuf" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "protobuf not available adding"
    pip install -U protobuf
    if [ $? != 0 ]; then
        echo "FAILURE: protobuf failed installing"
        WILL_FAIL=2
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: protobuf failed installing"
    fi
fi

echo "--------Applying work around to googles protobuf library----"
touch venv/lib/python2.7/site-packages/google/__init__.py
python -m compileall venv/lib/python2.7/site-packages/google/

echo ""
echo "-----------------------------------"
echo "Enviroment setup complete and seemingly successful."
echo "You can start the enviroment with the command\"source venv/bin/activate\""

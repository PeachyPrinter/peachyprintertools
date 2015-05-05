#!/bin/bash

echo "----Checking for already running Virtual Environment----"
if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Deactivitate the existing virtual enviroment before running this script."
    echo "This can be done with the \"deactivate\" command."
    exit 53 
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
if [ ! -d "venv" ]; then
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
export CFLAGS=-Qunused-arguments
export CPPFLAGS=-Qunused-arguments

echo "--------Install requirements---------"
pip install -r requirements.txt

echo "--------Applying work around to googles protobuf library----"
touch venv/lib/python2.7/site-packages/google/__init__.py
python -m compileall venv/lib/python2.7/site-packages/google/

echo ""
echo "-----------------------------------"
echo "Enviroment setup complete and seemingly successful."
echo "You can start the enviroment with the command\"source venv/bin/activate\""

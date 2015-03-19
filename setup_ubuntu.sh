#!/bin/bash
usage() { echo "Usage: $0 -c{clean}" 1>&2; exit 1; }

while getopts "ch?:" opt; do
    case "${opt}" in
        c)
            clean="TRUE"
            ;;
        h)
            usage
            ;;
        ?)
            usage
            ;;
    esac
done


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
    sudo apt-get install python-pip
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
    sudo apt-get install python-virtualenv
    if [ $? != 0 ]; then
        echo "FAILURE: virtualenv failed installing"
        WILL_FAIL=12
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: virtualenv failed installing"
    fi
fi


echo "----Checking for and create a virtual environment----"
CREATE_VENV="TRUE"
if [ -d "venv" ]; then
    if [ "$clean" == "TRUE" ]; then
        rm -rf venv && CREATE_VENV="TRUE"
    else
        CREATE_VENV="FALSE"
    fi
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

echo "--------Setting up protobuf----"
python -c"import protobuf" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "protobuf not available adding"
    pip install -U protobuf
    if [ $? != 0 ]; then
        echo "FAILURE: protobuf failed installing"
        WILL_FAIL=1
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: protobuf failed installing"
    fi
fi

echo "--------Setting up pyserial----"
python -c"import pyserial" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "pyserial not available adding"
    pip install -U pyserial
    if [ $? != 0 ]; then
        echo "FAILURE: pyserial failed installing"
        WILL_FAIL=1
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: pyserial failed installing"
    fi
fi

echo "--------Setting up mock----"
python -c"import mock" 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "mock not available adding"
    pip install -U mock
    if [ $? != 0 ]; then
        echo "FAILURE: mock failed installing"
        WILL_FAIL=1
        FAIL_REASONS="$FAIL_REASONS\nFAILURE: mock failed installing"
    fi
fi


if [ $WILL_FAIL != 0 ]; then
    echo "Enviroment setup failed. Summary:"
    echo -e $FAIL_REASONS
    exit $WILL_FAIL
fi

echo ""
echo "-----------------------------------"
echo "Enviroment setup complete and seemingly successful."
echo "You can start the enviroment with the command\"source venv/bin/activate\""

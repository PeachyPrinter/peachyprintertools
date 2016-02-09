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

if [[ "$VIRTUAL_ENV" != "" ]]; then
    echo "Deactivitate the existing virtual enviroment before running this script."
    echo "This can be done with the \"deactivate\" command."
    exit 53 
fi

command -v pip 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "Pip not available"
    exit 555
fi

command -v virtualenv 2>&1 >/dev/null
if [ $? != 0 ]; then
    echo "virtualenv not available"
    exit 444
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


echo "--------Install requirements---------"
pip install -r requirements.txt
if [ $? != 0 ]; then
    echo "Pip install or requirements failed"
    exit 59
fi

echo ""
echo "-----------------------------------"
echo "Enviroment setup complete and seemingly successful."
echo "You can start the enviroment with the command\"source venv/bin/activate\""

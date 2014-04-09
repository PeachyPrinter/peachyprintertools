#!/bin/sh
#This is development helper tool to continuosly run the test suite.

FORMAT=$(echo -e "\033[1;33m%w%f\033[0m written")
while inotifywait -qre close_write --format "$FORMAT" .
do
    find . -name "*.pyc" -exec rm -rf {} \;
    python "$@"
done
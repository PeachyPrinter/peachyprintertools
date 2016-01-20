@echo off

SET PYTHON_PATH=c:\Python27_64

echo ------------------------------------
echo Cleaning workspace
echo ------------------------------------

del /Q *.msi
rmdir /S /Q src\build
rmdir /S /Q src\PeachyPrinterToolsAPI.egg-info
rmdir /S /Q src\dist
REM TODO JT 2014-02-04 - Should clean the workspace

echo ------------------------------------
echo Extracting Git Revision Number
echo ------------------------------------

set SEMANTIC=0.0.1
set /p SEMANTIC=<symantic.version
IF NOT DEFINED GIT_HOME (
  git --version
  IF "%ERRORLEVEL%" == "0" (
    set GIT_HOME=git
  ) ELSE (
    echo "Could not find git."
    pause
    EXIT /B 1
  )
)

for /f "delims=" %%A in ('%GIT_HOME% rev-list HEAD --count') do set "GIT_REV_COUNT=%%A"
for /f "delims=" %%A in ('%GIT_HOME% rev-parse HEAD') do set "GIT_REV=%%A"

set VERSION=%SEMANTIC%.%GIT_REV_COUNT%
echo Version: %VERSION%
echo # THIS IS A GENERATED FILE  > version.properties
echo version='%VERSION%' >> version.properties
echo revision='%GIT_REV%' >> version.properties
echo Git Revision Number is %GIT_REV_COUNT%
copy version.properties src\peachyprinter\VERSION.py
copy version.properties src\VERSION.py

echo ------------------------------------
echo Downlaoding and installing dependancies
echo ------------------------------------
call setup_windows.bat

cd src

echo ------------------------------------
echo Running Tests
echo ------------------------------------
set PYTHONPATH=%PYTHONPATH%;src
%PYTHON_PATH%\python ..\test\test-all.py

IF NOT "%ERRORLEVEL%" == "0" (
    echo "FAILED TESTS ABORTING"
    EXIT /B 2
)


echo ------------------------------------
echo Create Peachy Tools Api
echo ------------------------------------

%PYTHON_PATH%\python setup.py sdist
IF NOT "%ERRORLEVEL%" == "0" (
    echo "FAILED PACKAGING ABORTING"
    cd ..
    EXIT /B 3
)

cd ..

echo ------------------------------------
echo Moving file
echo ------------------------------------

move src\dist\*.zip .

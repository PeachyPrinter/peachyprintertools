@echo off

echo ------------------------------------
echo Cleaning workspace
echo ------------------------------------

del *.msi
rmdir /s src\build
REM TODO JT 2014-02-04 - Should clean the workspace

echo ------------------------------------
echo Extracting Git Revision Number
echo ------------------------------------

set SEMANTIC=0.0.1
set /p SEMANTIC=<symantic.version
IF NOT DEFINED GIT_HOME (
  git --version
  IF ERRORLEVEL 0 (
    set GIT_HOME=git
  ) ELSE (
    echo Could not find git.
    pause
    REM exit 1
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
copy version.properties src\VERSION.py


echo ------------------------------------
echo Running Tests
echo ------------------------------------

python test/test-all.py
IF NOT ERRORLEVEL 0 (
    echo FAILED TESTS ABORTING
    exit 1
)


echo ------------------------------------
echo Create Peachy Tools Application
echo ------------------------------------

cd src
python setup.py bdist_msi
IF NOT ERRORLEVEL 0 (
    echo FAILED TESTS ABORTING
    exit 1
)
cd ..
move src\build\*.msi .

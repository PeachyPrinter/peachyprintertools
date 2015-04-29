@ECHO OFF

REM "Virtual env not used on windows for now."

call pip install -r requirements.txt
call python build_dep.py






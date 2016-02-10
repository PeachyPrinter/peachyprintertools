@ECHO OFF

call python -m pip install --upgrade setuptools==19.2

call python -m pip install -r requirements.txt
IF NOT "%ERRORLEVEL%" == "0" (
    ECHO FAILURE: Requirements install failed
    EXIT /B 99
)






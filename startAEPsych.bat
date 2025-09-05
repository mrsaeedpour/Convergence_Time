 @echo off
echo Attempting to activate virtual environment...
call conda activate base

if %errorlevel%==0 (
    echo Virtual environment activated successfully.
) else (
    echo Error: Failed to activate virtual environment!
    pause
    goto end
)
echo Starting AEPsych server...
rem start the server
aepsych_server --port 5555 --ip 127.0.0.1 --db %1
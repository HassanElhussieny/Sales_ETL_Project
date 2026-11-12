@echo off

REM Run the Sales ETL pipeline.
REM All paths are relative to this file's folder (%~dp0), so the project
REM works wherever it is cloned - including from Windows Task Scheduler.

REM Change to the project directory (the folder containing this file)
cd /d "%~dp0"

REM Activate the project's virtual environment if it exists
if exist "venv\Scripts\activate.bat" (
    call "venv\Scripts\activate.bat"
) else (
    echo [WARN] venv not found in "%~dp0" - using the Python on PATH.
)

REM Run the pipeline
python scripts\pipeline.py
set "EXIT_CODE=%ERRORLEVEL%"

REM Keep window open for 5 seconds so you can see the result
timeout /t 5

exit /b %EXIT_CODE%

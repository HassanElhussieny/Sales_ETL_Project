@echo off

REM Activate virtual environment
call C:\Users\LENOVO.SXT605\Desktop\Data_Analytics_project\venv\Scripts\activate.bat

REM Change to project directory
cd /d C:\Users\LENOVO.SXT605\Desktop\Data_Analytics_project

REM Run the pipeline
python scripts\pipeline.py

REM Keep window open for 5 seconds so you can see the result
timeout /t 5

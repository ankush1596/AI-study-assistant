
@echo off
cd /d "%~dp0"

echo Starting AI Study Assistant...
echo Project folder: %CD%

if not exist "app.py" (
    echo ERROR: app.py is missing from this folder.
    pause
    exit /b 1
)

if exist "..\.venv\Scripts\python.exe" (
    "..\.venv\Scripts\python.exe" app.py
) else (
    python app.py
)

pause

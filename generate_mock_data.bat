@echo off
REM Karui-Search Mock Data Generation Script
REM Run this from the project root directory

echo Starting Karui-Search Mock Data Generation...
echo.

REM Change to the project directory
cd /d "%~dp0"

REM Run the Python script
python scripts/generate_mock_data.py

REM Check if the script was successful
if %ERRORLEVEL% EQU 0 (
    echo.
    echo ✅ Mock data generation completed successfully!
    echo Check src/frontend/src/data/ for updated files.
) else (
    echo.
    echo ❌ Mock data generation failed. Check the logs above.
)

REM Keep window open to see results
pause
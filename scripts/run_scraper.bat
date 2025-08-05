@echo off
echo ================================
echo    KARUI-SEARCH SCRAPER (FULL)
echo ================================
echo.
echo This runs the full generate_mock_data.py script
echo which automatically saves to src/frontend/src/data/
echo.
echo WARNING: This may take 10+ minutes due to
echo Royal Resort processing 174 properties.
echo.
echo For faster options, use:
echo   - run_scraper_fast.bat (2-3 minutes)
echo   - run_scraper_balanced.bat (3-5 minutes)
echo.
set /p confirm="Continue with full scrape? (Y/N): "

if /i "%confirm%"=="Y" (
    cd /d "C:\Users\dougc\git\karuisearch"
    echo.
    echo Starting full property scraping...
    python scripts\generate_mock_data.py
    
    echo.
    echo ================================
    echo Full scraping completed!
    echo Results saved to:
    echo   src\frontend\src\data\mockProperties.json
    echo   src\frontend\src\data\mockWeeklyData.json
    echo ================================
) else (
    echo.
    echo Scraping cancelled.
)

echo.
pause
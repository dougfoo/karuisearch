@echo off
echo ================================================
echo     KARUI-SEARCH BALANCED SCRAPER
echo     Target: 10 properties from each site
echo ================================================
echo.
echo This will scrape:
echo   - Mitsui no Mori: up to 10 properties
echo   - Royal Resort: up to 10 properties  
echo   - Besso Navi: up to 10 properties
echo.
echo Choose output format:
echo   1. Regular JSON output (balanced_scrape_results.json)
echo   2. Mock data format (src/frontend/src/data/)
echo.
set /p choice="Enter choice (1 or 2): "

cd /d "C:\Users\dougc\git\karuisearch\scripts"

if "%choice%"=="2" (
    echo.
    echo Running with --writemock flag...
    echo Estimated time: 3-5 minutes
    python run_scraper_balanced.py --writemock
    echo ================================================
    echo Balanced scraping completed!
    echo Mock data saved to: src/frontend/src/data/
    echo ================================================
) else (
    echo.
    echo Running with regular output...
    echo Estimated time: 3-5 minutes
    python run_scraper_balanced.py
    echo ================================================
    echo Balanced scraping completed!
    echo Results saved to: balanced_scrape_results.json
    echo ================================================
)

echo.
pause
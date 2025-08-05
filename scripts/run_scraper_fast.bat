@echo off
echo ================================================
echo     KARUI-SEARCH FAST SCRAPER
echo     Quick test of all 3 sites
echo ================================================
echo.
echo This will test:
echo   - Mitsui no Mori: all available properties
echo   - Royal Resort: first 3 properties (demo)
echo   - Besso Navi: all available properties
echo.
echo Choose output format:
echo   1. Regular JSON output (fast_scrape_results.json)
echo   2. Mock data format (src/frontend/src/data/)
echo.
set /p choice="Enter choice (1 or 2): "

cd /d "C:\Users\dougc\git\karuisearch\scripts"

if "%choice%"=="2" (
    echo.
    echo Running with --writemock flag...
    python run_scraper_fast.py --writemock
    echo ================================================
    echo Fast scraping completed!
    echo Mock data saved to: src/frontend/src/data/
    echo ================================================
) else (
    echo.
    echo Running with regular output...
    python run_scraper_fast.py
    echo ================================================
    echo Fast scraping completed!
    echo Results saved to: fast_scrape_results.json
    echo ================================================
)

echo.
pause
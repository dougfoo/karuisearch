@echo off
echo ================================================
echo     KARUI-SEARCH FAST SCRAPER (MOCK MODE)
echo     Output: src/frontend/src/data/
echo ================================================
echo.
echo This will test all 3 sites and save to mock data format:
echo   - Mitsui no Mori: all available properties
echo   - Royal Resort: first 3 properties (demo)
echo   - Besso Navi: all available properties
echo.
echo Output files:
echo   - src/frontend/src/data/mockProperties.json
echo   - src/frontend/src/data/mockWeeklyData.json
echo.
echo Estimated time: 2-3 minutes
echo.
pause

cd /d "C:\Users\dougc\git\karuisearch"
python run_scraper_fast.py --writemock

echo.
echo ================================================
echo Fast scraping completed!
echo Mock data saved to: src/frontend/src/data/
echo ================================================
echo.
pause
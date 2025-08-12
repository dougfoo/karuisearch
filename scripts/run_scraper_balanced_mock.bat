@echo off
echo ================================================
echo   KARUI-SEARCH BALANCED SCRAPER (MOCK MODE)
echo   Target: 10 properties per site
echo   Output: src/frontend/src/data/
echo ================================================
echo.
echo This will scrape and save to mock data format:
echo   - Mitsui no Mori: up to 10 properties
echo   - Royal Resort: up to 10 properties  
echo   - Besso Navi: up to 10 properties
echo   - Resort Innovation: up to 10 properties
echo   - Tokyu Resort: up to 10 properties
echo   - Seibu Real Estate: up to 10 properties
echo   - Resort Home: up to 10 properties
echo.
echo Output files:
echo   - src/frontend/src/data/mockProperties.json
echo   - src/frontend/src/data/mockWeeklyData.json
echo.
echo Estimated time: 5-8 minutes
echo.
pause

cd /d "C:\Users\dougc\git\karuisearch\scripts"
python run_scraper_balanced.py --writemock

echo.
echo ================================================
echo Balanced scraping completed!
echo Mock data saved to: src/frontend/src/data/
echo ================================================
echo.
pause
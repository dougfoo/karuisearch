@echo off
echo ================================================
echo   ROYAL RESORT ONLY SCRAPER - PHASE 1 TEST
echo   Testing browser crash fixes
echo   Output: src/frontend/src/data/
echo ================================================
echo.
echo This will test Royal Resort extraction with:
echo   - Browser stability improvements
echo   - Crash recovery system
echo   - Optimized extraction methods
echo   - Direct save to frontend mock data
echo.
echo Output files:
echo   - src/frontend/src/data/mockProperties.json
echo   - src/frontend/src/data/mockWeeklyData.json
echo.
echo Testing 3 properties max for stability
echo.
pause

cd /d "%~dp0"
python run_royal_resort_only.py

echo.
echo ================================================
echo Royal Resort test completed!
echo Check frontend at http://localhost:3001
echo ================================================
echo.
pause
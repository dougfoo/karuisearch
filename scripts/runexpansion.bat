@echo off
echo Starting Karuizawa Real Estate Expansion Test...
echo Testing 5 new sites with small samples
echo.

cd /d "%~dp0\.."
python -m src.scrapers.expansion_test_scrapers

echo.
echo Expansion test completed!
pause
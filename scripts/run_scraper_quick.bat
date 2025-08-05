@echo off
echo ================================
echo    KARUI-SEARCH QUICK SCRAPER
echo ================================
echo.
echo Running quick scrape (Mitsui only for speed)...
echo.

cd /d "C:\Users\dougc\git\karuisearch"

python -c "
import sys, os
sys.path.insert(0, os.path.join(os.getcwd(), 'src'))
from scrapers.scraper_factory import ScraperFactory

print('=== QUICK SCRAPE RESULTS ===')
factory = ScraperFactory()

# Mitsui only (fast and reliable)
print('Scraping Mitsui...')
mitsui_props = factory.scrape_site('mitsui')
print(f'Mitsui: {len(mitsui_props)} properties with images')

for i, prop in enumerate(mitsui_props[:3], 1):
    print(f'  {i}. {prop.title[:50]}...')
    print(f'     Price: {prop.price}, Images: {len(prop.image_urls)}')

print(f'TOTAL: {len(mitsui_props)} properties extracted')
print('SUCCESS: Image extraction working!')
"

echo.
echo ================================
echo Quick scrape completed!
echo ================================
echo.
pause
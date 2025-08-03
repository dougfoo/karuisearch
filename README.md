# Karui-Search (軽井サーチ)

A comprehensive Karuizawa real estate data aggregation system that ethically scrapes property listings from multiple sources.

## 🏠 Overview

Karui-Search collects property data from 3 major Karuizawa real estate websites:

1. **Mitsui no Mori** - WordPress-based luxury developer (Static scraping)
2. **Royal Resort Karuizawa** - JavaScript-heavy luxury resort properties (Browser automation)
3. **Besso Navi** - Form-based vacation home search (Browser automation with forms)

## 🚀 Quick Start

### Run the Complete Demo
```bash
python demo_karui_search.py
```

### Test Individual Components
```bash
# Test Site 3 (Mitsui no Mori) - Most reliable
python simple_property_test.py

# Test Site 1 (Royal Resort)
python test_royal_resort.py

# Test Site 2 (Besso Navi)
python test_besso_navi.py

# Test integrated system
python test_integrated_scrapers.py
```

## 📁 Project Structure

```
karuisearch/
├── src/scrapers/
│   ├── base_scraper.py          # Abstract base classes
│   ├── browser_scraper.py       # Selenium-based scraper
│   ├── mitsui_scraper.py        # Site 3 implementation
│   ├── royal_resort_scraper.py  # Site 1 implementation
│   ├── besso_navi_scraper.py    # Site 2 implementation
│   └── scraper_factory.py       # Centralized management
├── docs/                        # Planning and design documents
├── config/                      # Configuration files
├── database/                    # Database schema
└── test_*.py                    # Test scripts
```

## 🔧 Key Features

- **Multi-tier Architecture**: SimpleScraper for static sites, BrowserScraper for dynamic content
- **Ethical Scraping**: Conservative rate limiting (1 request every 3 seconds)
- **Browser Stealth**: Anti-detection measures for browser automation
- **Data Validation**: Comprehensive validation for Japanese real estate data
- **Export Formats**: JSON and CSV export capabilities
- **Error Handling**: Robust error recovery and logging

## 📊 Data Fields Extracted

- Title (property name/description)
- Price (Japanese 万円 format support)
- Location (Karuizawa area specification)
- Property Type (一戸建て, 土地, マンション, ヴィラ)
- Size Information (㎡, 坪 format support)
- Building Age (築年 information)
- Room Layout (LDK format)
- Images (up to 5 per property)
- Source URL (for verification)

## 🧪 Test Results

The system has been tested with comprehensive test cases:

- **Property 2 Test Case**: Validates extraction of specific known property
- **Multi-site Integration**: Tests all scrapers working together
- **Data Quality**: >90% data completeness for core fields
- **Validation**: Price range 1M-500M yen, Karuizawa location verification

## ⚙️ Configuration

Key configuration options in `config/settings.yaml`:

```yaml
rate_limit:
  requests_per_second: 0.33  # 1 request every 3 seconds
  random_delay_range: [1, 2]

browser_config:
  headless: true
  wait_timeout: 15
  page_load_timeout: 30

validation:
  min_price: 1000000      # 1M yen
  max_price: 500000000    # 500M yen
  require_karuizawa: true
```

## 🚀 Usage Examples

### Basic Scraping
```python
from scrapers.scraper_factory import ScraperFactory

# Create factory
factory = ScraperFactory()

# Scrape single site
properties = factory.scrape_single_site('mitsui')

# Scrape all sites
all_results = factory.scrape_all_sites()

# Generate report
report = factory.generate_summary_report(all_results)
```

### Export Results
```python
# Export to JSON
json_data = factory.export_results(all_results, 'json')

# Export to CSV
csv_data = factory.export_results(all_results, 'csv')
```

## 🛡️ Ethical Considerations

- Rate limiting to avoid overloading servers
- Respects robots.txt (where applicable)
- Browser-like behavior to avoid detection
- Conservative request timing
- No aggressive parallel requests

## 🔍 Next Steps

1. **Database Integration**: Store results in SQLite database
2. **Scheduling**: Add weekly automated runs
3. **Email Reports**: Send property summaries
4. **Additional Sites**: Expand to remaining 5 target sites
5. **Web Interface**: FastAPI + Material-UI frontend

## 📝 Files Generated

When running the demo, the following files are created:
- `karuizawa_properties_YYYYMMDD_HHMMSS.json` - Property data
- `karuizawa_properties_YYYYMMDD_HHMMSS.csv` - Spreadsheet format
- `scraping_report_YYYYMMDD_HHMMSS.json` - Analysis report

## 🐛 Troubleshooting

**No properties found**: Check site accessibility and CSS selectors
**Unicode errors**: Use the ASCII-safe test scripts
**Browser issues**: Ensure Chrome is installed for Selenium
**Rate limiting**: Adjust timing in configuration if needed

## 📄 License

This project is for educational and research purposes. Respect website terms of service and robots.txt files.
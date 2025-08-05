# 📁 KARUI-SEARCH PROJECT STRUCTURE (Updated)

## 🚀 **Root Directory** (Clean & Organized)

```
karuisearch/
├── 📋 CLAUDE.md                     # Project instructions for AI
├── 📋 README.md                     # Main project documentation  
├── 📋 ARCHITECTURE.md               # System architecture
├── 📋 CHANGELOG.md                  # Version history
├── 📋 SCRAPER_MACROS_GUIDE.md      # Scraper usage guide
├── 📋 UPDATED_PROJECT_STRUCTURE.md  # This file
├── 🔧 package.json                  # Node.js dependencies (root)
├── 🔧 requirements.txt              # Python dependencies
├── 📁 config/                       # Configuration files
├── 📁 database/                     # Database schemas
├── 📁 docs/                         # Documentation
├── 📁 scripts/                      # 🆕 ALL EXECUTABLE FILES HERE
├── 📁 src/                          # Source code (scrapers, frontend, utils)
└── 📁 node_modules/                 # Node dependencies (root)
```

## 📁 **Scripts Directory** (All Executables)

```
scripts/
├── 📄 README.md                      # Scripts documentation
├── 🐍 generate_mock_data.py          # Main data generation script
├── 🪟 generate_mock_data.bat         # Windows batch for above

├── 🚀 **Fast Scrapers** (2-3 minutes)
│   ├── 🐍 run_scraper_fast.py        # Python script
│   ├── 🪟 run_scraper_fast.bat       # Interactive batch
│   └── 🪟 run_scraper_fast_mock.bat  # Direct mock output

├── ⚖️ **Balanced Scrapers** (3-5 minutes, 10 props/site)
│   ├── 🐍 run_scraper_balanced.py    # Python script  
│   ├── 🪟 run_scraper_balanced.bat   # Interactive batch
│   └── 🪟 run_scraper_balanced_mock.bat # Direct mock output

├── 🔧 **Other Scrapers**
│   ├── 🪟 run_scraper.bat            # Full scraping (10+ min)
│   ├── 🪟 run_scraper_quick.bat      # Mitsui only (30s)
│   └── 🐍 run_quick_scrape.py        # Quick test script

├── 🧪 **Test & Debug Scripts**
│   ├── 🐍 test_*.py                  # Various test scripts
│   ├── 🐍 debug_*.py                 # Debug utilities
│   ├── 🐍 simple_*.py                # Simple test scripts
│   └── 🐍 demo_karui_search.py       # Demo script

└── 📊 **Data & Logs**
    ├── 📄 *.csv                      # Test results
    └── 📄 scraping.log               # Log files
```

## 📁 **Source Code Structure**

```
src/
├── 🕷️ **scrapers/** (Web Scraping Engine)
│   ├── 🐍 base_scraper.py           # Abstract base classes
│   ├── 🐍 browser_scraper.py        # Selenium browser automation  
│   ├── 🐍 scraper_factory.py        # Scraper factory pattern
│   ├── 🐍 mitsui_scraper.py         # Mitsui no Mori (✅ Working)
│   ├── 🐍 royal_resort_scraper.py   # Royal Resort (✅ Working)
│   ├── 🐍 besso_navi_scraper.py     # Besso Navi browser version
│   └── 🐍 besso_navi_http_scraper.py # Besso Navi HTTP version (✅ Fixed)

├── 🛠️ **utils/** (Utilities)
│   └── 🐍 titleGenerator.py         # Property title generation

└── 🌐 **frontend/** (React Application)
    ├── 📄 index.html                # Entry point
    ├── 🔧 package.json              # Frontend dependencies
    ├── 🔧 vite.config.ts            # Vite configuration
    ├── 🔧 tsconfig.json             # TypeScript config
    └── src/
        ├── 📄 App.tsx               # Main app component
        ├── 📄 main.tsx              # React entry
        ├── 📁 components/           # UI components
        ├── 📁 pages/                # Page components  
        ├── 📁 data/                 # Mock data (JSON files)
        ├── 📁 services/             # API services
        ├── 📁 types/                # TypeScript types
        ├── 📁 utils/                # Frontend utilities
        ├── 📁 hooks/                # React hooks
        └── 📁 i18n/                 # Internationalization
```

## 🎯 **Key Changes Made**

### ✅ **File Organization**
- **Moved ALL executable files** to `scripts/` directory
- **Updated all import paths** to use `../src/` 
- **Fixed all batch file paths** to run from scripts directory
- **Maintained clean root** with only documentation and config

### ✅ **Path Updates**
- Python scripts: `sys.path.append(os.path.join(os.path.dirname(__file__), '..', 'src'))`
- Mock output: `os.path.join("..", "src", "frontend", "src", "data")`
- Batch files: `cd /d "C:\Users\dougc\git\karuisearch\scripts"`

### ✅ **Maintained Functionality**
- All scrapers still work correctly
- `--writemock` flag still outputs to frontend data directory
- Batch files run from their new location
- Import paths correctly resolve to source code

## 🚀 **How to Use**

### **From Root Directory:**
```bash
# Navigate to scripts
cd scripts

# Run any scraper
./run_scraper_fast_mock.bat
python generate_mock_data.py
```

### **Direct Execution:**
```bash
# Double-click any .bat file in scripts/ folder
# They will automatically set correct working directory
```

## 📊 **Current Status**

| Component | Status | Location |
|-----------|--------|----------|
| **All Scrapers** | ✅ Working | `scripts/` |
| **Mock Data Generation** | ✅ Working | `scripts/generate_mock_data.py` |
| **Batch Macros** | ✅ Updated | `scripts/*.bat` |
| **Frontend Integration** | ✅ Working | `src/frontend/src/data/` |
| **Image Extraction** | ✅ Fixed | All scrapers extracting images |

## 🎉 **Benefits of New Structure**

- **🧹 Clean root directory** - Only docs and config at top level
- **📁 Organized scripts** - All executables in one place  
- **🔄 Easy execution** - Double-click any batch file
- **🛠️ Developer friendly** - Clear separation of concerns
- **📦 Maintainable** - Easy to find and update scripts

**Your project is now perfectly organized and all scrapers are working with full image extraction!** 🚀
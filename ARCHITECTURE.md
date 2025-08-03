# Karui-Search Architecture

## Overview
Karui-Search (軽井サーチ) is a real estate data aggregation system that collects property listings from multiple Karuizawa real estate websites, stores them locally, and provides weekly summaries with links to original sources.

## System Architecture

### Core Components

```
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Web Scrapers  │───▶│  Data Pipeline  │───▶│   Database      │
│                 │    │                 │    │                 │
│ • Site A        │    │ • Validation    │    │ • Properties    │
│ • Site B        │    │ • Deduplication │    │ • Sources       │
│ • Site C        │    │ • Normalization │    │ • Reports       │
└─────────────────┘    └─────────────────┘    └─────────────────┘
                                │
                                ▼
┌─────────────────┐    ┌─────────────────┐    ┌─────────────────┐
│   Scheduler     │───▶│   Web API       │───▶│  Frontend UI    │
│                 │    │                 │    │                 │
│ • Scraping Jobs │    │ • FastAPI       │    │ • React + MUI   │
│ • Report Gen    │    │ • REST Endpoints│    │ • Property Grid │
│ • Cleanup       │    │ • Data Export   │    │ • Weekly Reports│
└─────────────────┘    └─────────────────┘    └─────────────────┘
```

### Data Flow

1. **Collection Phase**
   - Scheduled scrapers fetch data from configured real estate websites
   - Raw HTML is parsed and structured data extracted
   - Data validation and cleaning applied

2. **Processing Phase**
   - Duplicate detection across sources
   - Data normalization (price formats, area measurements)
   - Image URL collection and validation

3. **Storage Phase**
   - Cleaned data stored in local database
   - Source tracking and last-updated timestamps
   - Historical data preservation

4. **Presentation Phase**
   - Weekly report generation
   - Web interface for browsing properties
   - Export functionality for data analysis

## Technology Stack

### Backend
- **Language**: Python 3.11+
- **Web Framework**: FastAPI
- **Database**: SQLite with direct SQL queries
- **Scraping**: Beautiful Soup 4 + Requests
- **Scheduling**: APScheduler
- **Data Processing**: Pandas

### Frontend
- **Framework**: React 18
- **UI Library**: Material-UI (MUI) v5
- **State Management**: React Query + React Context
- **Build Tool**: Vite
- **Language**: TypeScript

### Infrastructure
- **Containerization**: Docker
- **Reverse Proxy**: Nginx
- **Environment Management**: Docker Compose

## Directory Structure

```
karui-search/
├── src/
│   ├── scrapers/
│   │   ├── __init__.py
│   │   ├── base_scraper.py
│   │   ├── site_a_scraper.py
│   │   └── scraper_factory.py
│   ├── database/
│   │   ├── __init__.py
│   │   ├── connection.py
│   │   └── queries.py
│   ├── api/
│   │   ├── __init__.py
│   │   ├── main.py
│   │   ├── routes/
│   │   └── schemas/
│   ├── frontend/
│   │   ├── src/
│   │   ├── public/
│   │   ├── package.json
│   │   └── vite.config.ts
│   ├── scheduler/
│   │   ├── __init__.py
│   │   ├── jobs.py
│   │   └── scheduler.py
│   └── utils/
│       ├── __init__.py
│       ├── data_processor.py
│       └── validators.py
├── config/
│   ├── settings.yaml
│   ├── scraping_rules.yaml
│   └── database.yaml
├── docs/
│   ├── FEATURES.md
│   ├── SCRAPING_TARGETS.md
│   └── API.md
├── tests/
│   ├── unit/
│   ├── integration/
│   └── conftest.py
├── docker/
│   ├── Dockerfile.backend
│   ├── Dockerfile.frontend
│   └── docker-compose.yml
├── database/
│   ├── schema.sql
│   └── seed_data.sql
├── requirements.txt
├── package.json
├── README.md
└── .env.example
```

## Design Principles

### Modularity
- Each scraper is independent and configurable
- Simple database layer with direct SQL access
- API and frontend loosely coupled

### Scalability
- Horizontal scaling through containerization
- Database partitioning for large datasets
- Caching layer for frequently accessed data

### Reliability
- Robust error handling and retry mechanisms
- Data validation at multiple layers
- Graceful degradation when sources are unavailable

### Maintainability
- Clear separation of concerns
- Comprehensive testing coverage
- Detailed logging and monitoring

## Security Considerations

- Rate limiting to respect website ToS
- Data sanitization for XSS prevention
- Secure configuration management
- Regular dependency updates

## Future Enhancements

- Machine learning for price trend analysis
- Mobile app development
- Real-time notifications for new listings
- Integration with mapping services
- Multi-language support (Japanese/English)
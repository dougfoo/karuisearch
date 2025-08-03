# CLAUDE.md

This file provides guidance to Claude Code (claude.ai/code) when working with code in this repository.

## Project Overview

Karui-Search (軽井サーチ) is a real estate data aggregation system that collects property listings from multiple Karuizawa real estate websites, stores them locally, and provides weekly summaries. The name combines Japanese "karui" (light) with "search" as a pun on Karuizawa.

## Architecture

This is a modular system with clear separation between:
- **Web Scrapers**: Independent, configurable scrapers for different real estate sites (SUUMO, At Home, Homes.co.jp)
- **Data Pipeline**: Validation, deduplication, and normalization of scraped data
- **Database Layer**: SQLite for development, PostgreSQL for production with SQLAlchemy ORM
- **Web API**: FastAPI backend with REST endpoints
- **Frontend**: React 18 + Material-UI (MUI) v5 for clean Japanese design aesthetics
- **Scheduler**: APScheduler for automated scraping and report generation

## Technology Stack

### Backend
- Python 3.11+ with FastAPI
- SQLite with direct SQL queries for simplicity
- Beautiful Soup 4 + Requests for web scraping
- APScheduler for automated tasks
- Pandas for data processing

### Frontend
- React 18 with TypeScript
- Material-UI (MUI) v5 for component library
- React Query for server state management
- Vite as build tool

### Infrastructure
- Docker for containerization
- Docker Compose for orchestration

## Configuration Management

The system uses YAML-based configuration in `config/settings.yaml` with environment variable substitution (${VAR_NAME} syntax). Key configuration areas:
- Database settings (development/production)
- Scraping parameters (rate limits, schedules, target sites)
- Frontend theming and display options
- Logging and monitoring settings

## Data Flow

1. **Collection**: Scheduled scrapers extract data from real estate websites
2. **Processing**: Data validation, deduplication, and normalization
3. **Storage**: Cleaned data stored with source tracking and timestamps
4. **Presentation**: Weekly reports and web interface for browsing

## Scraping Strategy

Target websites are configured with specific rate limits and scraping rules:
- SUUMO: 2 requests/second (priority 1)
- At Home: 1 request/second (priority 2) 
- Homes.co.jp: 2 requests/second (priority 3)

Scrapers respect robots.txt, implement retry logic, and include deduplication across sources.

## Development Notes

### Database Schema
Properties are stored with standardized fields (price in yen, size in sqm) and include source attribution. Uses simple SQLite with direct SQL queries for maximum simplicity. The system tracks property history and supports multiple property types (house, apartment, land, vacation home).

### Material-UI Integration
The frontend uses Material-UI for consistent Japanese design aesthetics, with configurable theming, responsive design, and internationalization support for Japanese/English text.

### Ethical Scraping
Rate limiting is enforced per site, user agents are properly identified, and the system respects terms of service. Data processing includes validation rules and anonymization options.

## Directory Structure Focus

- `src/scrapers/`: Site-specific scraping logic with base classes
- `src/database/`: Models, connections, and migrations
- `src/api/`: FastAPI routes and schemas
- `src/frontend/`: React application with MUI components
- `src/scheduler/`: Automated job management
- `config/`: YAML configuration files
- `docs/`: Feature specifications and scraping targets
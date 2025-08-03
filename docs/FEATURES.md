# Karui-Search Features Specification

## Core Features

### 1. Multi-Source Data Collection
**Description**: Automated scraping of real estate listings from multiple Karuizawa property websites.

**Requirements**:
- Support for at least 3-5 major real estate websites
- Configurable scraping rules per website
- Respect robots.txt and rate limiting
- Handle different page structures and data formats
- Capture: property title, price, location, size, description, images, contact info

**User Stories**:
- As a user, I want the system to automatically collect new listings so I don't have to manually check multiple websites
- As a user, I want the system to handle different website formats seamlessly

### 2. Local Database Storage
**Description**: Persistent local storage of property data with metadata tracking.

**Requirements**:
- SQLite database for development, PostgreSQL for production
- Track data sources and collection timestamps
- Maintain historical data for trend analysis
- Handle duplicate detection across sources
- Support for property images and metadata

**User Stories**:
- As a user, I want all collected data stored locally so I can access it offline
- As a user, I want historical data preserved so I can track market trends

### 3. Weekly Summary Reports
**Description**: Automated generation of weekly property summaries with new listings.

**Requirements**:
- Generate weekly reports every Sunday evening
- Include new properties from the past week
- Sort by price, size, or location
- Include thumbnail images and key details
- Provide direct links to original listings
- Export options (HTML, PDF, JSON)

**User Stories**:
- As a user, I want weekly summaries so I can quickly review new properties
- As a user, I want links to original listings so I can get detailed information

### 4. Web Interface
**Description**: Clean, responsive web interface built with React and Material-UI.

**Requirements**:
- Property grid/list view with sorting and filtering
- Search functionality (by location, price range, size)
- Detailed property view with image gallery
- Weekly report viewing and navigation
- Mobile-responsive design
- Japanese and English text support

**User Stories**:
- As a user, I want a clean interface to browse properties
- As a user, I want to filter and search properties by my criteria
- As a user, I want the interface to work well on my phone

### 5. Data Processing Pipeline
**Description**: Robust data cleaning, validation, and normalization.

**Requirements**:
- Price normalization (handle different currencies/formats)
- Area measurement standardization (tsubo, sqm, etc.)
- Address standardization and geocoding
- Image URL validation and downloading
- Duplicate detection across sources
- Data quality scoring

**User Stories**:
- As a user, I want consistent data formats so I can easily compare properties
- As a user, I want duplicates removed so I don't see the same property multiple times

## Advanced Features (Future Releases)

### 6. Price Trend Analysis
**Description**: Historical price tracking and trend visualization.

**Requirements**:
- Price history graphs for individual properties
- Market trend analysis for different areas
- Price prediction algorithms
- Comparative market analysis

### 7. Notification System
**Description**: Real-time alerts for new properties matching user criteria.

**Requirements**:
- Email notifications for new listings
- Custom search criteria and alerts
- Price drop notifications
- Mobile push notifications

### 8. Property Comparison
**Description**: Side-by-side comparison of multiple properties.

**Requirements**:
- Compare up to 3-4 properties simultaneously
- Highlight differences and similarities
- Save comparison sessions
- Export comparison reports

### 9. Mapping Integration
**Description**: Interactive maps showing property locations.

**Requirements**:
- Google Maps or OpenStreetMap integration
- Property markers with popup details
- Distance calculations to amenities
- Area boundary overlays

### 10. Data Export and API
**Description**: Programmatic access to collected data.

**Requirements**:
- RESTful API for data access
- CSV/JSON export functionality
- Webhook support for real-time updates
- Rate limiting and authentication

## Technical Requirements

### Performance
- Page load times under 2 seconds
- Scraping jobs complete within 30 minutes
- Support for 10,000+ property records
- Responsive design for mobile devices

### Reliability
- 99% uptime for web interface
- Graceful handling of website changes
- Automatic retry mechanisms for failed scrapes
- Data backup and recovery procedures

### Security
- Input validation and sanitization
- Secure configuration management
- Rate limiting to respect website ToS
- Regular security updates

### Usability
- Intuitive navigation and search
- Japanese language support
- Accessible design (WCAG 2.1 AA)
- Clear error messages and help text

## Integration Requirements

### External Services
- Email service for notifications (SendGrid, SES)
- Image storage and CDN (optional)
- Geocoding service for address standardization
- Backup storage (cloud or local)

### Development Tools
- Docker for containerization
- Git for version control
- CI/CD pipeline for automated testing
- Monitoring and logging (optional)

## Data Model

### Property Entity
```
- id (unique identifier)
- title (property title)
- price (standardized price)
- location (address/area)
- size (standardized area)
- property_type (house, apartment, land)
- description (full description)
- images (array of image URLs)
- source_url (original listing URL)
- source_website (website identifier)
- date_first_seen (when first scraped)
- date_last_updated (last modification)
- status (active, sold, removed)
```

### Source Entity
```
- id (unique identifier)
- name (website name)
- url (base URL)
- scraping_rules (JSON configuration)
- last_scraped (timestamp)
- status (active, inactive, error)
- rate_limit (requests per minute)
```

### Report Entity
```
- id (unique identifier)
- week_start (start date of week)
- week_end (end date of week)
- property_count (number of new properties)
- generated_at (timestamp)
- file_path (path to generated report)
```
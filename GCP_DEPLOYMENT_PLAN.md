# Karui-Search Google Cloud Platform Deployment Plan

## Executive Summary

This document outlines a comprehensive plan to migrate the Karui-Search real estate aggregation system from local development to a production-ready Google Cloud Platform deployment with persistent cloud database storage for long-term property data tracking.

**Key Objectives:**
- Deploy Karui-Search on GCP with 99.9% uptime
- Migrate from SQLite to Cloud SQL PostgreSQL for scalability
- Implement automated scraping with Cloud Scheduler
- Enable long-term property data storage and historical tracking
- Create cost-effective architecture (~$70/month)

## Current System Analysis

### Existing Architecture
- **Backend**: Python 3.11+ with FastAPI
- **Database**: SQLite with comprehensive schema (properties, sources, scraping_jobs, etc.)
- **Scrapers**: 3 active scrapers (Mitsui, Royal Resort, Besso Navi)
- **Frontend**: React 18 + Material-UI
- **Containerization**: Docker-ready

### Current Data Volume
- 12 sample properties from mock data
- Weekly reports with property tracking
- Image URL collection and validation
- Historical price change tracking

## Phase 1: Infrastructure Setup (Weeks 1-2)

### 1.1 Core GCP Services

#### Compute Engine Instance
```yaml
Instance Configuration:
  - Machine Type: e2-standard-2 (2 vCPU, 8GB RAM)
  - OS: Ubuntu 20.04 LTS
  - Boot Disk: 50GB SSD
  - Region: asia-northeast1 (Tokyo) for optimal Japan scraping
  - Estimated Cost: ~$35/month
```

#### Cloud SQL PostgreSQL
```yaml
Database Configuration:
  - Instance: db-n1-standard-1 (1 vCPU, 3.75GB RAM)
  - Storage: 20GB SSD (auto-expanding)
  - Backup: Automated daily backups
  - High Availability: Regional persistent disk
  - Estimated Cost: ~$25/month
```

#### Cloud Storage Buckets
```yaml
Storage Buckets:
  - karui-search-images: Property images and media
  - karui-search-backups: Database and system backups
  - karui-search-reports: Generated weekly reports
  - Estimated Cost: ~$2/month
```

### 1.2 Network & Security

#### VPC Network Setup
- Private subnet for database and internal services
- Cloud NAT for outbound scraping traffic
- Firewall rules for HTTPS (443) and SSH (22)
- Internal load balancer for API traffic

#### Identity & Access Management (IAM)
- Service accounts for each component
- Principle of least privilege access
- API keys for external integrations

## Phase 2: Database Migration (Weeks 2-3)

### 2.1 Schema Migration

#### PostgreSQL Schema Conversion
```sql
-- Convert existing SQLite schema to PostgreSQL
-- Key changes:
-- - AUTOINCREMENT → SERIAL
-- - PRAGMA foreign_keys → Native FK support
-- - Enhanced indexing for property searches
-- - JSONB columns for flexible data storage

CREATE TABLE properties (
    id SERIAL PRIMARY KEY,
    title VARCHAR(500) NOT NULL,
    price VARCHAR(100) NOT NULL,
    location VARCHAR(500) NOT NULL,
    property_type VARCHAR(50),
    size_info VARCHAR(200),
    building_age VARCHAR(100),
    source_url VARCHAR(1000) NOT NULL,
    scraped_date DATE NOT NULL,
    description TEXT,
    image_urls JSONB,  -- Enhanced JSON support
    rooms VARCHAR(50),
    source_id INTEGER REFERENCES sources(id),
    source_property_id VARCHAR(100),
    is_active BOOLEAN DEFAULT TRUE,
    date_first_seen TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
    date_last_updated TIMESTAMP DEFAULT CURRENT_TIMESTAMP
);

-- Add full-text search capabilities
CREATE INDEX properties_search_idx ON properties 
USING GIN (to_tsvector('japanese', title || ' ' || COALESCE(description, '')));
```

#### Data Migration Script
```python
# migration_script.py
import sqlite3
import psycopg2
from google.cloud.sql.connector import connector
import os

def migrate_properties_data():
    # Connect to existing SQLite
    sqlite_conn = sqlite3.connect('database/karui_search.db')
    
    # Connect to Cloud SQL PostgreSQL
    pg_conn = connector.connect(
        instance_connection_name=os.environ['CLOUD_SQL_CONNECTION_NAME'],
        driver="pg8000",
        user=os.environ['DB_USER'],
        password=os.environ['DB_PASSWORD'],
        db=os.environ['DB_NAME']
    )
    
    # Migrate data with proper type conversion
    migrate_sources(sqlite_conn, pg_conn)
    migrate_properties(sqlite_conn, pg_conn)
    migrate_scraping_jobs(sqlite_conn, pg_conn)
```

### 2.2 Connection Management

#### Cloud SQL Proxy Setup
```yaml
# cloud-sql-proxy deployment
apiVersion: apps/v1
kind: Deployment
metadata:
  name: cloud-sql-proxy
spec:
  replicas: 1
  template:
    spec:
      containers:
      - name: cloud-sql-proxy
        image: gcr.io/cloudsql-docker/gce-proxy:1.33.2
        command:
          - "/cloud_sql_proxy"
          - "-instances=PROJECT_ID:REGION:INSTANCE_NAME=tcp:5432"
```

## Phase 3: Application Deployment (Weeks 3-5)

### 3.1 Containerization

#### Backend Dockerfile Optimization
```dockerfile
FROM python:3.11-slim

WORKDIR /app

# Install system dependencies for web scraping
RUN apt-get update && apt-get install -y \
    chromium-browser \
    chromium-chromedriver \
    && rm -rf /var/lib/apt/lists/*

# Install Python dependencies
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application code
COPY src/ ./src/
COPY config/ ./config/

# Set environment variables
ENV PYTHONPATH=/app
ENV CHROME_BIN=/usr/bin/chromium-browser
ENV CHROMEDRIVER_PATH=/usr/bin/chromedriver

EXPOSE 8000

CMD ["uvicorn", "src.api.main:app", "--host", "0.0.0.0", "--port", "8000"]
```

#### Frontend Production Build
```dockerfile
FROM node:18-alpine AS builder

WORKDIR /app
COPY src/frontend/package*.json ./
RUN npm ci --only=production

COPY src/frontend/ .
RUN npm run build

FROM nginx:alpine
COPY --from=builder /app/dist /usr/share/nginx/html
COPY nginx.conf /etc/nginx/nginx.conf
EXPOSE 80
```

### 3.2 Google Container Registry

#### Container Build & Deploy Pipeline
```bash
# Build and push containers
gcloud builds submit --tag gcr.io/PROJECT_ID/karui-search-backend:latest src/
gcloud builds submit --tag gcr.io/PROJECT_ID/karui-search-frontend:latest src/frontend/

# Deploy to Compute Engine
gcloud compute instances create-with-container karui-search-instance \
    --container-image gcr.io/PROJECT_ID/karui-search-backend:latest \
    --zone asia-northeast1-a \
    --machine-type e2-standard-2
```

### 3.3 Environment Configuration

#### Production Environment Variables
```bash
# Database
export CLOUD_SQL_CONNECTION_NAME="project:region:instance"
export DB_HOST="127.0.0.1"
export DB_PORT="5432"
export DB_NAME="karui_search"
export DB_USER="postgres"
export DB_PASSWORD="secure_password"

# Scraping Configuration
export SCRAPING_ENABLED="true"
export RATE_LIMIT_REQUESTS_PER_SECOND="0.33"
export MAX_CONCURRENT_SCRAPERS="1"

# Storage
export GCS_BUCKET_IMAGES="karui-search-images"
export GCS_BUCKET_REPORTS="karui-search-reports"

# Monitoring
export ENABLE_LOGGING="true"
export LOG_LEVEL="INFO"
```

## Phase 4: Automation & Scheduling (Weeks 5-6)

### 4.1 Cloud Scheduler Configuration

#### Automated Scraping Jobs
```yaml
# Daily scraping job
gcloud scheduler jobs create http daily-scraping \
    --schedule="0 6 * * *" \
    --uri="https://karui-search.example.com/api/scrape/all" \
    --http-method=POST \
    --headers="Authorization=Bearer ${API_TOKEN}" \
    --time-zone="Asia/Tokyo"

# Weekly report generation
gcloud scheduler jobs create http weekly-reports \
    --schedule="0 9 * * 1" \
    --uri="https://karui-search.example.com/api/reports/generate" \
    --http-method=POST \
    --time-zone="Asia/Tokyo"
```

#### Backup Automation
```yaml
# Daily database backup
gcloud scheduler jobs create http daily-backup \
    --schedule="0 2 * * *" \
    --uri="https://karui-search.example.com/api/admin/backup" \
    --http-method=POST
```

### 4.2 Cloud Functions for Event Processing

#### Property Change Notifications
```python
# functions/property_notifications.py
import functions_framework
from google.cloud import pubsub_v1

@functions_framework.cloud_event
def process_property_changes(cloud_event):
    """Process property changes and send notifications"""
    
    # Parse property change data
    property_data = cloud_event.data
    
    # Check for significant changes (price drops >10%)
    if detect_significant_change(property_data):
        send_notification(property_data)
    
    # Update historical tracking
    update_property_history(property_data)
```

## Phase 5: Long-term Data Strategy (Weeks 6-8)

### 5.1 BigQuery Integration

#### Data Warehouse Setup
```sql
-- BigQuery dataset for historical analysis
CREATE SCHEMA karui_search_analytics;

-- Property trends table
CREATE TABLE karui_search_analytics.property_trends (
    property_id STRING,
    scraped_date DATE,
    price_value NUMERIC,
    location_normalized STRING,
    property_type STRING,
    size_sqm NUMERIC,
    days_on_market INTEGER,
    price_per_sqm NUMERIC
)
PARTITION BY scraped_date
CLUSTER BY location_normalized, property_type;
```

#### Daily ETL Pipeline
```python
# etl/daily_sync.py
from google.cloud import bigquery
import pandas as pd

def sync_daily_properties():
    """Sync daily property data to BigQuery for analysis"""
    
    # Extract from Cloud SQL
    properties_df = extract_daily_properties()
    
    # Transform and normalize data
    transformed_df = transform_property_data(properties_df)
    
    # Load to BigQuery
    client = bigquery.Client()
    table_id = "project.karui_search_analytics.property_trends"
    
    job_config = bigquery.LoadJobConfig(
        write_disposition="WRITE_APPEND"
    )
    
    job = client.load_table_from_dataframe(
        transformed_df, table_id, job_config=job_config
    )
```

### 5.2 Data Retention & Archival

#### Storage Lifecycle Policies
```yaml
# Cloud Storage lifecycle configuration
lifecycle:
  rule:
  - action:
      type: SetStorageClass
      storageClass: NEARLINE
    condition:
      age: 30
      matches_storage_class: STANDARD
  - action:
      type: SetStorageClass
      storageClass: COLDLINE
    condition:
      age: 365
      matches_storage_class: NEARLINE
```

## Security & Compliance

### 5.3 Security Hardening

#### Network Security
- Private IP addresses for all internal services
- Cloud Armor for DDoS protection
- SSL/TLS certificates via Cloud Load Balancer
- VPC firewall rules restricting access

#### Data Protection
- Encryption at rest for Cloud SQL and Cloud Storage
- Encryption in transit via HTTPS/TLS
- Regular security scanning with Cloud Security Scanner
- Backup encryption with customer-managed keys

#### Access Control
```yaml
# IAM roles and permissions
roles:
  - name: karui-search-scraper
    permissions:
      - cloudsql.instances.connect
      - storage.objects.create
      - logging.logEntries.create
  
  - name: karui-search-admin
    permissions:
      - cloudsql.instances.admin
      - compute.instances.admin
      - storage.buckets.admin
```

## Monitoring & Observability

### 6.1 Cloud Monitoring Setup

#### Key Metrics
```yaml
monitoring_metrics:
  - name: "Scraping Success Rate"
    threshold: "> 95%"
    alert_policy: "email + slack"
  
  - name: "Database Connection Pool"
    threshold: "< 80% utilization"
    alert_policy: "email"
  
  - name: "API Response Time"
    threshold: "< 2 seconds p95"
    alert_policy: "slack"
  
  - name: "Daily Property Count"
    threshold: "> 10 new properties/day"
    alert_policy: "dashboard"
```

#### Log Aggregation
```python
# logging/structured_logging.py
import logging
from google.cloud import logging as cloud_logging

def setup_cloud_logging():
    """Setup structured logging for Cloud Operations"""
    client = cloud_logging.Client()
    client.setup_logging()
    
    # Custom formatter for scraping logs
    formatter = logging.Formatter(
        '{"timestamp": "%(asctime)s", "level": "%(levelname)s", '
        '"scraper": "%(name)s", "message": "%(message)s", '
        '"properties_found": %(properties_count)s}'
    )
```

## Cost Analysis & Optimization

### 7.1 Monthly Cost Breakdown

| Service | Configuration | Monthly Cost (USD) |
|---------|---------------|-------------------|
| Compute Engine | e2-standard-2 | $35 |
| Cloud SQL PostgreSQL | db-n1-standard-1 | $25 |
| Cloud Storage | 100GB | $2 |
| Cloud Scheduler | 10 jobs | $1 |
| Load Balancer | Regional | $3 |
| BigQuery | 10GB/month | $2 |
| Monitoring & Logging | Standard | $2 |
| **Total Estimated** | | **~$70/month** |

### 7.2 Cost Optimization Strategies

#### Compute Optimization
- Use preemptible instances for development
- Implement auto-scaling based on scraping schedule
- Schedule instance stop/start for non-24/7 workloads

#### Storage Optimization
- Implement image compression before Cloud Storage upload
- Use lifecycle policies to move old data to cheaper storage classes
- Regular cleanup of temporary files and logs

## Implementation Timeline

### Week 1-2: Infrastructure Foundation
- [ ] Set up GCP project and billing
- [ ] Create VPC network and subnets
- [ ] Deploy Cloud SQL PostgreSQL instance
- [ ] Configure Cloud Storage buckets
- [ ] Set up IAM roles and service accounts

### Week 3-4: Database Migration
- [ ] Convert SQLite schema to PostgreSQL
- [ ] Create data migration scripts
- [ ] Test database connectivity from Compute Engine
- [ ] Migrate existing property data
- [ ] Validate data integrity

### Week 5-6: Application Deployment
- [ ] Build and push container images to GCR
- [ ] Deploy backend application to Compute Engine
- [ ] Configure environment variables and secrets
- [ ] Deploy frontend with Cloud CDN
- [ ] Set up domain and SSL certificates

### Week 7-8: Automation & Testing
- [ ] Configure Cloud Scheduler for automated scraping
- [ ] Set up BigQuery for historical data analysis
- [ ] Implement monitoring and alerting
- [ ] Perform load testing and optimization
- [ ] Create backup and disaster recovery procedures

## Success Criteria

### Technical Metrics
- 99.9% uptime for web application
- < 2 second API response times
- > 95% scraping success rate
- Zero data loss during migration
- < 5 minute recovery time from failures

### Business Metrics
- Successfully track 100+ properties across 3 sites
- Generate accurate weekly reports
- Maintain 6+ months of historical data
- Enable trend analysis and price tracking
- Support future expansion to additional scraping sources

## Risk Mitigation

### Technical Risks
- **Database Migration**: Comprehensive testing with rollback plan
- **Scraping Stability**: Robust error handling and retry mechanisms
- **Cost Overruns**: Budget alerts and resource monitoring
- **Data Loss**: Multiple backup strategies and testing

### Operational Risks
- **Site Changes**: Monitoring for scraper failures with alerts
- **Rate Limiting**: Respectful scraping with configurable delays
- **Compliance**: Regular review of website terms of service
- **Security**: Regular security audits and updates

## Future Enhancements

### Phase 2 Features (Months 3-6)
- Machine learning for price prediction
- Real-time notifications via WebSocket
- Mobile app development
- Advanced analytics dashboard
- Multi-language support (Japanese/English)

### Phase 3 Scaling (Months 6-12)
- Kubernetes deployment for auto-scaling
- Multiple region deployment
- Advanced caching with Cloud Memorystore
- API rate limiting for external users
- Marketplace integration

## Conclusion

This comprehensive GCP deployment plan transforms Karui-Search from a local development tool into a production-ready, scalable cloud application with persistent data storage. The phased approach ensures systematic migration with minimal risk while establishing a foundation for long-term growth and feature enhancement.

The estimated monthly cost of $70 provides excellent value for a fully managed, scalable property tracking system with historical data analysis capabilities. The architecture supports future expansion while maintaining reliability and security best practices.

## Next Steps

1. **Approve Budget**: Confirm $70/month operational budget
2. **GCP Account Setup**: Create project and enable required APIs
3. **Begin Phase 1**: Infrastructure setup and network configuration
4. **Schedule Reviews**: Weekly progress reviews during 8-week implementation

---

*Document Version: 1.0*  
*Last Updated: 2025-08-04*  
*Author: Claude AI Assistant*  
*Project: Karui-Search GCP Migration*
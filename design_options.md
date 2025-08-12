# Google Cloud Hosting Options for Karuizawa Real Estate Site

## Overview

This document outlines three hosting options for deploying the Karuizawa real estate application on Google Cloud Platform, with weekly data updates and cost optimization in mind.

## Option 1: Ultra-Budget (~$0-2/month)

### Architecture
- **Frontend**: Cloud Storage static hosting
- **Backend**: Cloud Functions (HTTP triggered)
- **Database**: Cloud Storage (JSON files)
- **Scheduling**: Cloud Scheduler
- **CDN**: Cloud CDN (optional)

### Components
```
User Browser → Cloud CDN → Cloud Storage (React App)
                    ↓
Cloud Scheduler → Cloud Functions → Cloud Storage (JSON Data)
```

### Implementation
- React app built and deployed to Cloud Storage bucket
- Weekly scraping via Cloud Functions triggered by Cloud Scheduler
- Data stored as JSON files in Cloud Storage
- Simple, serverless architecture

### Cost Breakdown
- **Cloud Storage**: ~$0.50/month (1GB data + requests)
- **Cloud Functions**: ~$0.25/month (weekly execution)
- **Cloud Scheduler**: ~$0.10/month (4 jobs/month)
- **Cloud CDN**: ~$0.25/month (optional, low traffic)
- **Total**: **$0.60-1.10/month**

### Pros
- Extremely low cost
- Simple deployment
- No database management
- Fast static site performance

### Cons
- Limited scalability
- Manual data management
- No real-time updates
- Basic search/filtering capabilities

---

## Option 2: Hybrid (~$3-8/month) **[RECOMMENDED]**

### Architecture
- **Frontend**: Firebase Hosting
- **Backend**: Cloud Functions
- **Database**: Firestore (NoSQL)
- **Scheduling**: Cloud Scheduler
- **Authentication**: Firebase Auth (future)

### Components
```
User Browser → Firebase Hosting (React App)
                    ↓
Cloud Scheduler → Cloud Functions → Firestore
                                        ↑
                                   React App (real-time)
```

### Implementation
- React app deployed to Firebase Hosting
- Firestore for structured property data with change tracking
- Cloud Functions for weekly scraping and data processing
- Real-time updates when properties change
- Built-in analytics and monitoring

### Cost Breakdown
- **Firebase Hosting**: ~$0.25/month (1GB bandwidth)
- **Firestore**: ~$2-4/month (storage + reads/writes)
- **Cloud Functions**: ~$1/month (weekly scraping + API calls)
- **Cloud Scheduler**: ~$0.10/month
- **Firebase features**: ~$0.50/month (analytics, etc.)
- **Total**: **$3.85-5.85/month**

### Pros
- Real-time data updates
- Structured data with change tracking
- Built-in monitoring and analytics
- Easy scaling for future features
- Integrated Google Cloud ecosystem

### Cons
- Slightly higher cost
- More complex setup
- Database query limits

---

## Option 3: Full-Stack (~$10-15/month)

### Architecture
- **Frontend**: Firebase Hosting
- **Backend**: Cloud Run (containerized)
- **Database**: Cloud SQL (PostgreSQL)
- **Scheduling**: Cloud Scheduler
- **Caching**: Memorystore (Redis)

### Components
```
User Browser → Firebase Hosting → Cloud Run API → Cloud SQL
                                      ↓
Cloud Scheduler → Cloud Run (Scrapers) → Cloud SQL
                                      ↓
                                 Memorystore (Cache)
```

### Implementation
- React SPA on Firebase Hosting
- FastAPI backend containerized on Cloud Run
- PostgreSQL database for complex queries and relationships
- Redis caching for performance
- Full REST API with advanced filtering

### Cost Breakdown
- **Firebase Hosting**: ~$0.25/month
- **Cloud Run**: ~$3-5/month (always-on minimum instances)
- **Cloud SQL**: ~$7/month (micro instance)
- **Memorystore**: ~$2/month (basic Redis)
- **Cloud Scheduler**: ~$0.10/month
- **Total**: **$12.35-14.35/month**

### Pros
- Full relational database capabilities
- High performance with caching
- Advanced querying and analytics
- Production-ready scalability
- Complete control over backend logic

### Cons
- Highest cost
- Most complex setup and maintenance
- Overkill for current requirements

---

## Recommendation: Option 2 (Hybrid)

**Why Option 2 is ideal:**

1. **Cost-Effective**: At $3-8/month, it's affordable while providing real-time capabilities
2. **Change Tracking**: Firestore enables proper property change detection and history
3. **Real-Time Updates**: Users see new properties immediately after weekly scraping
4. **Integrated Ecosystem**: Firebase/Google Cloud services work seamlessly together
5. **Future-Proof**: Easy to add authentication, notifications, and other features
6. **Analytics**: Built-in user analytics and monitoring
7. **Scalability**: Can handle increased traffic and data without major changes

## Implementation Timeline

### Phase 1: Setup (Week 1)
- Create Google Cloud project
- Set up Firebase Hosting and Firestore
- Configure Cloud Functions and Scheduler

### Phase 2: Migration (Week 2)
- Migrate existing property data to Firestore
- Refactor React app for Firestore integration
- Deploy frontend to Firebase Hosting

### Phase 3: Automation (Week 3)
- Set up weekly scraping Cloud Functions
- Implement change detection and notifications
- Configure monitoring and alerts

### Phase 4: Enhancement (Week 4)
- Add advanced filtering and search
- Implement property favorites/watchlist
- Set up email notifications for new properties

## Technical Requirements

### Firestore Schema
```javascript
// Properties Collection
{
  id: "prop_123",
  title: "Luxury Villa in Karuizawa",
  price: "¥50,000,000",
  location: "Old Karuizawa",
  propertyType: "Villa",
  images: ["url1", "url2"],
  source: "mitsui",
  dateAdded: "2025-08-11",
  lastModified: "2025-08-11",
  isActive: true,
  changeHistory: [...]
}

// Weekly Reports Collection
{
  weekOf: "2025-08-11",
  totalProperties: 45,
  newProperties: 3,
  priceChanges: 2,
  summary: "..."
}
```

### Cloud Functions
- `weeklyPropertyScraper`: Runs every Sunday at 2 AM JST
- `propertyChangeDetector`: Compares new data with existing
- `weeklyReportGenerator`: Creates summary reports
- `propertyAPI`: Serves data to React frontend

## Monitoring & Alerts

### Metrics to Track
- Weekly scraping success/failure rates
- Number of new properties found
- Price changes and trends
- User engagement on frontend
- API response times
- Database query performance

### Alerts
- Failed scraping runs
- Unusual property count changes
- High error rates
- Approaching quota limits

---

*Last Updated: August 11, 2025*
*Status: Ready for Implementation*
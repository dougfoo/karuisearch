# UI Prototype Development Plan

## Overview
Create a functional React + Material-UI prototype using dummy JSON data to demonstrate the Karui-Search interface design before building the actual backend integration.

## Phase 1: Project Setup & Foundation (1-2 days)

### 1.1 Frontend Project Initialization
- Create React app structure: `src/frontend/`
- Set up Vite + TypeScript + Material-UI
- Configure i18next for Japanese/English translation
- Set up React Router for navigation
- Install dependencies from existing package.json

### 1.2 Dummy Data Creation
**Create realistic JSON mock data files:**

**`src/frontend/data/mockProperties.json`** - Sample property data matching our V1 schema:
```json
[
  {
    "id": "prop_001",
    "title": "軽井沢町大字軽井沢の新築別荘",
    "price": "¥58,000,000",
    "location": "長野県北佐久郡軽井沢町大字軽井沢",
    "property_type": "別荘",
    "size_info": "土地:250㎡ 建物:180㎡",
    "building_age": "新築",
    "description": "軽井沢の静かな別荘地に建つ新築別荘です...",
    "image_urls": ["https://via.placeholder.com/400x300", "..."],
    "rooms": "4LDK+S",
    "source_url": "https://www.royal-resort.co.jp/property/001",
    "scraped_date": "2024-01-15",
    "date_first_seen": "2024-01-15T10:30:00Z"
  }
  // 50+ sample properties with varied data
]
```

**`src/frontend/data/mockWeeklyData.json`** - Weekly reports:
```json
{
  "week_start": "2024-01-15",
  "week_end": "2024-01-21", 
  "total_new": 15,
  "price_changes": {
    "increases": 3,
    "decreases": 2
  },
  "properties": [/* subset of mockProperties */]
}
```

### 1.3 Theme & i18n Setup
- Custom Material-UI theme with Japanese aesthetics
- Translation files (ja.json, en.json) for UI labels
- Smart translation utilities for property data

## Phase 2: Core Components (2-3 days)

### 2.1 Base Components
**Layout Components:**
- `AppShell` - Main app container with navigation
- `Header` - Navigation bar with language toggle
- `Sidebar` - Filter panel for desktop
- `FilterDrawer` - Mobile filter drawer

**Property Components:**
- `PropertyCard` - Core property display component
- `PropertyGrid` - Responsive grid layout
- `PropertyDetail` - Modal/page for detailed view
- `ImageGallery` - Property photo carousel

### 2.2 Core Features Implementation
**Navigation & Routing:**
- Home page (`/`) 
- Weekly properties (`/weekly`)
- All listings (`/listings`)
- Property detail (`/property/:id`)

**Data Management:**
- Mock API service using JSON files
- React Query for state management
- Filter/sort/search functionality
- Pagination logic

## Phase 3: Page Implementation (2-3 days)

### 3.1 Weekly Properties Page
- Week navigation (previous/next)
- Property count summary with price change indicators
- Filterable property grid
- Weekly statistics display

### 3.2 All Listings Page  
- Complete property database view
- Advanced filtering sidebar:
  - Property type toggles
  - Price range slider (¥1M - ¥500M)
  - Area checkboxes (旧軽井沢, 新軽井沢, etc.)
  - Building age categories
  - Keyword search
- Multiple sorting options
- Pagination (20 properties per page)

### 3.3 Property Detail View
- Full property information display
- Image gallery with thumbnails
- Price history chart (if available)
- Source attribution with external links
- Related properties suggestions

## Phase 4: Japanese UX & Polish (1-2 days)

### 4.1 Japanese Localization
- Proper Japanese number formatting (万円 display)
- Tsubo/sqm dual measurements
- Japanese date formatting
- Cultural color choices and spacing

### 4.2 Mobile Optimization
- Touch-friendly interactions
- Swipe gestures for navigation
- Responsive breakpoints
- Bottom sheet modals for mobile

### 4.3 Performance & UX
- Skeleton loading states
- Progressive image loading
- Smooth animations
- Error boundaries

## Phase 5: Demo Features (1 day)

### 5.1 Interactive Features
- Language toggle (JP ⇄ EN)
- Search functionality
- Filter persistence
- Favorite properties (local storage)

### 5.2 Demo Data Scenarios
- Properties with price changes
- Mixed property types and ages
- Various image counts and quality
- Properties from different sources

## Directory Structure
```
src/frontend/
├── components/
│   ├── layout/
│   │   ├── AppShell.tsx
│   │   ├── Header.tsx
│   │   └── Sidebar.tsx
│   ├── property/
│   │   ├── PropertyCard.tsx
│   │   ├── PropertyGrid.tsx
│   │   ├── PropertyDetail.tsx
│   │   └── ImageGallery.tsx
│   └── ui/
│       ├── FilterControls.tsx
│       └── LoadingStates.tsx
├── pages/
│   ├── HomePage.tsx
│   ├── WeeklyPage.tsx
│   ├── ListingsPage.tsx
│   └── PropertyDetailPage.tsx
├── data/
│   ├── mockProperties.json
│   ├── mockWeeklyData.json
│   └── mockSources.json
├── services/
│   ├── mockApi.ts
│   └── translations.ts
├── hooks/
│   ├── useProperties.ts
│   └── useFilters.ts
├── utils/
│   ├── formatting.ts
│   └── translations.ts
└── i18n/
    ├── ja.json
    └── en.json
```

## Technology Choices
- **State Management**: React Query (TanStack Query) - Excellent for caching, background updates, and API integration
- **Styling**: Material-UI v5 with custom Japanese-inspired theme
- **Routing**: React Router v6 for navigation
- **Internationalization**: react-i18next for bilingual support
- **Build Tool**: Vite for fast development and builds

## Success Criteria
- ✅ Fully functional bilingual interface
- ✅ All major pages working with mock data
- ✅ Responsive design (mobile + desktop)
- ✅ Japanese number/date formatting
- ✅ Filter, sort, search functionality
- ✅ Material-UI design system implemented
- ✅ Performance optimized (smooth interactions)

## Deliverables
1. Working React prototype deployable via `npm run dev`
2. Comprehensive mock data covering various scenarios
3. Complete component library ready for backend integration
4. Documentation for component props and usage patterns

This prototype will validate our UI design and provide a foundation for backend integration later.
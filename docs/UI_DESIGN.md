# Karui-Search UI Design Documentation

## Weekly New Properties Interface

### Overview
The weekly new properties interface is the core user-facing feature of Karui-Search, designed to showcase newly discovered real estate listings in a clean, Material-UI based interface with Japanese design aesthetics and bilingual support.

### Design Goals
- **Clean Japanese Aesthetic**: Minimal, uncluttered design following Japanese design principles
- **Bilingual Support**: Japanese primary with English fallback
- **Mobile-First**: Responsive design optimized for mobile viewing
- **Quick Scanning**: Users can rapidly review new properties with key details visible
- **Source Attribution**: Clear indication of property source with direct links

## Component Architecture

### 1. WeeklyPropertiesPage (Main Container)
**Responsibilities:**
- Week range navigation (previous/next week buttons)
- Property count summary display
- Filter controls (property type, price range)
- Integration with PropertyGrid component
- Loading states and error handling

**Key Features:**
- Week selector with Japanese date formatting
- "今週の物件" (This Week's Properties) heading
- Quick statistics: "新着 15件" (15 New Properties)
- Sort options: 価格順 (by price), 面積順 (by area), 追加日順 (by date added)

### 2. PropertyCard Component (Core Display Element)

#### Visual Layout
```
┌─────────────────────────────────────┐
│ [Property Image]            [Type]  │
│                             Badge   │
│ ¥58,000,000  📈 +¥2M (先週より)       │
│ 軽井沢町大字軽井沢                      │
│                                     │
│ 土地: 200㎡  建物: 150㎡               │
│ 築15年  4LDK                        │
│                                     │
│ 🆕 発見日: 1月15日                    │
│ [Source: Royal Resort] [元サイトを見る] │
└─────────────────────────────────────┘
```

#### Essential Data Display
**Always Visible:**
- **Property Image**: Primary image with 300px thumbnail, fallback placeholder
- **Price**: Formatted in yen (¥12,500,000) with proper Japanese number formatting
- **Price Changes**: Visual indicator for price increases/decreases since discovery
- **Location**: Address within Karuizawa (軽井沢町〇〇)
- **Property Type Badge**: 一戸建て/マンション/土地/別荘
- **Discovery Date**: When property was first found by scraper
- **Source Attribution**: Clear source website identification

**Conditional Display:**
- **Building Age**: 築15年 (for houses/apartments) or 新築 (new construction)
- **Size Information**: 土地:200㎡ 建物:150㎡ (land and building areas)
- **Room Layout**: 3LDK, 4SLDK format for apartments/houses
- **Construction Details**: 木造/鉄骨造 (when available)

#### Material-UI Components
- `Card` with elevation=2 for subtle shadow
- `CardMedia` for property images (aspect ratio 16:9)
- `CardContent` with consistent Typography hierarchy
- `Chip` components for property type and source
- `Button` variant="outlined" for "元サイトを見る" (View Original)

### 3. PropertyGrid Component

#### Responsive Layout
- **Desktop (≥1200px)**: 3 columns with 24px gaps
- **Tablet (768-1199px)**: 2 columns with 16px gaps  
- **Mobile (<768px)**: 1 column with 8px gaps

#### Grid Features
- Infinite scroll or pagination (configurable)
- Skeleton loading placeholders during data fetch
- Empty state with helpful message
- Sort controls in AppBar

## Material-UI Theme Configuration

### Color Palette
```javascript
const theme = createTheme({
  palette: {
    primary: { main: '#1976d2' }, // Blue
    secondary: { main: '#dc004e' }, // Red accent
    background: { 
      default: '#fafafa',
      paper: '#ffffff'
    }
  }
});
```

### Typography Scale
- **h4**: Page title "今週の新着物件"
- **h6**: Property titles
- **body1**: Price display (larger, emphasized)
- **body2**: Location and details
- **caption**: Source attribution and metadata

### Japanese Localization Standards

#### Price Formatting
```javascript
// Examples:
¥5,800,000 (5.8M yen)
¥125,000,000 (125M yen)
¥1,200万円 (preserve original format when available)

// Price change indicators:
📈 +¥2,000,000 (値上がり)    // Green text for increases
📉 -¥1,500,000 (値下がり)    // Red text for decreases
= 価格変更なし                // Gray text for no change
```

#### Discovery Date Formatting
```javascript
// Discovery date examples:
🆕 発見日: 1月15日            // This month
🆕 発見日: 12/28              // Previous month (same year)
🆕 発見日: 2023/12/15         // Previous year
🆕 発見日: 3日前              // Relative format (3 days ago)
```

#### Area Display
```javascript
// Standard format:
土地: 200㎡  建物: 150㎡
敷地: 300坪  (when in tsubo)
延床面積: 120㎡
```

#### Building Age Categories
```javascript
新築 (0-2 years)    // Green chip
築浅 (3-20 years)   // Blue chip  
築古 (20+ years)    // Gray chip
```

#### Property Type Labels
```javascript
一戸建て (House)
マンション (Apartment/Condo)
土地 (Land)
別荘 (Vacation Home)
```

## User Experience Features

### Navigation Components
```
┌─────────────────────────────────────┐
│ ← 先週  |  今週の新着物件  |  来週 →   │
│    (Last Week)    (This Week)   (Next Week) │
│                                     │
│ 2024年1月1日 - 1月7日                │
│ 新着物件: 15件                       │
└─────────────────────────────────────┘
```

### Filter Controls
- Property type chips (toggleable)
- Price range slider with yen formatting
- Sort dropdown: 追加日順/価格昇順/価格降順/面積順

### Loading States
- Skeleton cards during initial load
- Progressive image loading with blur-up effect
- Shimmer animation for text placeholders

### Mobile Optimizations

#### Touch Interactions
- Card tap expands to show full details
- Swipe gestures for week navigation
- Large touch targets (44px minimum)

#### Mobile-Specific Features
- Sticky header with week navigation
- Collapsible filter panel
- Bottom sheet for property details
- Optimized image sizes for mobile bandwidth

## Implementation Guidelines

### Performance Considerations
- Lazy loading for images outside viewport
- Virtualized scrolling for large property lists
- React.memo for PropertyCard to prevent unnecessary re-renders
- Debounced search and filter inputs

### Accessibility Features
- ARIA labels for all interactive elements
- Keyboard navigation support
- High contrast mode compatibility
- Screen reader optimized content structure

### Error Handling
- Graceful image fallbacks
- Network error recovery
- Empty state illustrations
- Retry mechanisms for failed requests

## Development Steps

### Phase 1: Core Components
1. Create PropertyCard component with basic layout
2. Implement PropertyGrid with responsive design
3. Add Material-UI theming and Japanese typography
4. Test with mock data

### Phase 2: Data Integration
1. Connect to backend API endpoints
2. Implement price change tracking and display
3. Add discovery date formatting and display
4. Implement loading states and error handling
5. Add real property data rendering
6. Test with various data scenarios

### Phase 3: Enhanced Features
1. Add week navigation functionality
2. Implement filtering and sorting
3. Add mobile-specific optimizations
4. Performance testing and optimization

### Phase 4: Polish
1. Japanese localization refinements
2. Accessibility improvements
3. Animation and micro-interactions
4. Cross-browser testing

## Technical Specifications

### Required Material-UI Components
```javascript
import {
  Card, CardMedia, CardContent, CardActions,
  Typography, Chip, Button, Grid,
  Skeleton, AppBar, Toolbar,
  IconButton, Menu, MenuItem
} from '@mui/material';
```

### Custom Hooks Needed
- `useWeeklyProperties(weekStart)` - Fetch property data
- `usePropertyFilters()` - Filter state management
- `useJapaneseFormatting()` - Yen/area formatting utilities

### API Endpoints
- `GET /api/properties/weekly?week=YYYY-MM-DD` - Weekly property data with price history
- `GET /api/properties/{id}` - Individual property details
- `GET /api/properties/{id}/price-history` - Price change history for property
- `GET /api/weeks/available` - Available week ranges

### Enhanced Data Model
```javascript
// Property object with new fields:
{
  id: "prop_123",
  title: "軽井沢の別荘",
  price: "¥58,000,000",
  price_history: [
    { date: "2024-01-15", price: "¥58,000,000" },
    { date: "2024-01-08", price: "¥56,000,000" }
  ],
  date_first_seen: "2024-01-15T10:30:00Z",
  price_change: {
    amount: "+¥2,000,000",
    percentage: "+3.6%",
    direction: "increase", // "increase" | "decrease" | "none"
    since_date: "2024-01-08"
  },
  // ... other existing fields
}
```

This design specification provides the foundation for implementing a clean, user-friendly interface that effectively showcases Karuizawa real estate properties while maintaining Japanese design sensibilities and ensuring excellent mobile usability.
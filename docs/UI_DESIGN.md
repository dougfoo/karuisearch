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

## Page Structure & Navigation

### Site Navigation
```
ホーム (Home) → 今週の新着 (This Week's New)
              → 全物件一覧 (All Listings) 
              → 週間レポート (Weekly Reports)
```

## Internationalization Strategy

### UI-Level Translation Approach
**Store original Japanese data, translate interface elements and labels**

#### Data Storage (Preserve Original)
```yaml
# Keep original Japanese property data intact
title: "軽井沢町大字軽井沢の新築別荘"
location: "長野県北佐久郡軽井沢町"  
property_type: "別荘"
size_info: "土地:200㎡ 建物:150㎡"
building_age: "築15年"
description: "軽井沢の静かな別荘地に建つ新築別荘です..."
```

#### Smart Translation Functions
```javascript
// Contextual property data translation
const translatePropertyType = (originalType, locale) => {
  const translations = {
    "一戸建て": { en: "Single-Family House" },
    "別荘": { en: "Vacation Home" },
    "土地": { en: "Land" },
    "マンション": { en: "Apartment/Condo" }
  };
  return locale === 'en' ? translations[originalType]?.en : originalType;
};

const translateSizeInfo = (sizeInfo, locale) => {
  if (locale === 'en') {
    return sizeInfo
      .replace('土地:', 'Land: ')
      .replace('建物:', 'Building: ')
      .replace('㎡', ' sqm')
      .replace('坪', ' tsubo');
  }
  return sizeInfo;
};
```

#### i18n Configuration (React i18next)
```javascript
// Translation files
// ja.json
{
  "nav.home": "ホーム",
  "nav.weekly": "今週の新着",
  "nav.all_listings": "全物件一覧",
  "property.type": "物件種別",
  "filter.price": "価格帯",
  "sort.by_date": "追加日順",
  "area.old_karuizawa": "旧軽井沢"
}

// en.json  
{
  "nav.home": "Home",
  "nav.weekly": "This Week's New",
  "nav.all_listings": "All Listings",
  "property.type": "Property Type",
  "filter.price": "Price Range", 
  "sort.by_date": "By Date Added",
  "area.old_karuizawa": "Old Karuizawa"
}
```

#### Implementation Benefits
- ✅ **Data Integrity**: Original Japanese preserved
- ✅ **Real-time Language Switching**: Instant UI translation
- ✅ **Cost Effective**: No translation API costs during scraping
- ✅ **Flexibility**: Easy to add new languages later
- ✅ **Context Aware**: Smart translations based on property context

## Component Architecture

### 1. All Listings Page (新規追加)
**URL**: `/listings` - Complete property database with advanced filtering

#### Page Layout
```
┌─────────────────────────────────────────────────────────┐
│ [≡] 軽井サーチ | All Listings    [🔍] [JP/EN] [👤]      │
├─────────────────────────────────────────────────────────┤
│ 📊 全物件一覧 | All Properties                          │
│ 合計: 1,247件  更新: 2024/01/15                         │
│                                                         │
│ [一戸建て] [土地] [別荘] [マンション]  🔍 [検索...]      │
│ 並び順: [追加日順 ▼] [価格安い順] [価格高い順] [面積順]   │
├─────────────────────────────────────────────────────────┤
│ ┌─ Filters ─┐ ┌─ Property Grid ─────────────────────┐   │
│ │💰 価格帯    │ │ [Property Cards - same as weekly] │   │
│ │📍 エリア    │ │ - Sortable by date_listed         │   │
│ │📐 面積     │ │ - Sortable by price               │   │ 
│ │🏠 築年数    │ │ - Filterable by property_type     │   │
│ │🔍 キーワード │ │ - Pagination (20 per page)       │   │
│ └───────────┘ └─────────────────────────────────────┘   │
└─────────────────────────────────────────────────────────┘
```

#### Key Features
- **Complete Database View**: All scraped properties, not just weekly
- **Advanced Sorting**: Date listed, price (low→high, high→low), area size  
- **Multi-Filter System**: Property type, price range, area, building age
- **Search Functionality**: Keyword search across titles and descriptions
- **Pagination**: Handle large datasets efficiently
- **Persistent Filters**: Remember user preferences

### 2. WeeklyPropertiesPage (Main Container)
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

## Enhanced User Experience Features

### Improved Navigation Components
```
┌─────────────────────────────────────────────────────────┐
│ [≡]  軽井サーチ | Karui-Search     [🔍] [JP/EN] [👤]    │
├─────────────────────────────────────────────────────────┤
│ ← 先週  |  📅 今週の新着物件 (1/1-1/7)  |  来週 →      │
│                                                         │
│ 🆕 新着: 15件  📈 値上がり: 3件  📉 値下がり: 2件        │
│                                                         │
│ [全て] [一戸建て] [土地] [別荘]   並び順: [追加日順 ▼]    │
└─────────────────────────────────────────────────────────┘
```

### Advanced Filter System
#### Filter Drawer (Mobile) / Sidebar (Desktop)
```
┌─────────────────────────────────────┐
│ 🔍 検索・フィルター                   │
├─────────────────────────────────────┤
│ 🏷️ 物件種別                          │
│ ☑️ 一戸建て (8)  ☑️ 土地 (5)         │
│ ☐ マンション (2) ☐ 別荘 (3)           │
│                                     │
│ 💰 価格帯                            │
│ [----●----●----] ¥1,000万-¥8,000万  │
│                                     │
│ 📐 敷地面積                          │
│ [--●----------] 200㎡以上            │
│                                     │
│ 🏠 築年数                            │
│ ⚪ 指定なし ⚪ 新築 ⚪ 築10年以内       │
│                                     │
│ 📍 エリア                            │
│ ☑️ 旧軽井沢 (6)  ☐ 新軽井沢 (4)       │
│ ☐ 中軽井沢 (3)   ☐ 南軽井沢 (2)       │
│                                     │
│ [フィルターをクリア] [検索]            │
└─────────────────────────────────────┘
```

### Enhanced Property Detail Modal
```
┌─────────────────────────────────────────────────────────┐
│ [×]  軽井沢町大字軽井沢の新築別荘               [❤️] [📤] │
├─────────────────────────────────────────────────────────┤
│ [< 🖼️ Image Gallery (5/8) >]                          │
│                                                         │
│ 💰 ¥58,000,000  📈 +¥2,000,000 (先週より)               │
│ 📍 長野県北佐久郡軽井沢町大字軽井沢                      │
│                                                         │
│ ┌─ 基本情報 ─────────────┬─ 詳細情報 ─────────────┐      │
│ │🏠 種別: 別荘            │📐 敷地: 250㎡ (75.7坪) │      │
│ │🆕 築年: 新築 (2024年)   │🏘️ 建物: 180㎡ (54.5坪) │      │
│ │🚪 間取り: 4LDK+S       │🏗️ 構造: 木造2階建て    │      │
│ │🚗 駐車場: 2台分        │⚡ 設備: オール電化      │      │
│ └─────────────────────────┴─────────────────────────┘      │
│                                                         │
│ 📝 物件説明                                              │
│ 軽井沢の静かな別荘地に建つ新築別荘です。自然豊かな...    │
│                                                         │
│ 🚉 アクセス: 軽井沢駅まで車で8分                         │
│ 🏪 周辺: スーパー(車5分)、病院(車10分)                   │
│                                                         │
│ ┌─────────────────────────────────────────────────────┐  │
│ │ 📊 価格履歴                                          │  │
│ │ 2024/01/15: ¥58,000,000 (現在)                     │  │
│ │ 2024/01/08: ¥56,000,000 (+¥2,000,000)             │  │
│ └─────────────────────────────────────────────────────┘  │
│                                                         │
│ 🔗 元サイト: Royal Resort  [元サイトで見る]              │
│ 🆕 発見日: 2024年1月15日                                │
│                                                         │
│ [問い合わせ] [お気に入り] [共有] [類似物件を見る]        │
└─────────────────────────────────────────────────────────┘
```

### Loading States
- Skeleton cards during initial load
- Progressive image loading with blur-up effect
- Shimmer animation for text placeholders

### Japanese UX Patterns & Cultural Considerations

#### Number and Currency Display
```javascript
// Japanese number formatting patterns
¥5,800万円     // Traditional Japanese (万 = 10,000)
¥58,000,000    // Western format for clarity
58百万円       // Alternative million format

// Area measurements (dual display)
土地: 200㎡ (60.5坪)  // Both metric and traditional tsubo
建物: 150㎡ (45.4坪)  // Users expect both formats
```

#### Typography Hierarchy (Japanese-First)
- **Primary text**: Japanese with fallback fonts
- **Furigana support**: For difficult kanji readings
- **Mixed script handling**: Japanese + English + Numbers
- **Vertical text option**: For traditional layouts

#### Color Psychology (Japanese Context)
```javascript
const japaneseColors = {
  // 縁起の良い色 (Auspicious colors)
  prosperity: '#B8860B',    // Gold - wealth, prosperity
  nature: '#228B22',        // Green - growth, harmony
  stability: '#8B4513',     // Brown - earth, stability
  purity: '#F8F8FF',        // White - cleanliness, new beginnings
  
  // Warning colors (culturally appropriate)
  caution: '#FF4500',       // Orange-red (not pure red)
  attention: '#FFD700',     // Gold for important info
}
```

#### Information Hierarchy (Japanese Real Estate)
1. **Price** (最重要) - Largest, most prominent
2. **Location** - Specific address details important
3. **Size** - Both land and building areas
4. **Age/Condition** - Critical for Japanese buyers
5. **Access** - Station distance, transportation
6. **Surrounding area** - Schools, shopping, medical

### Mobile Optimizations

#### Touch Interactions
- **Card tap**: Expands to show full details
- **Long press**: Quick preview with key info
- **Swipe gestures**: Week navigation (left/right)
- **Pull to refresh**: Update current week data
- **Double tap**: Zoom into property images

#### Mobile-Specific Features
- **Sticky header**: Week navigation always visible  
- **Floating filter button**: Quick access to filters
- **Bottom sheet modals**: For property details
- **Progressive loading**: Images load as needed
- **Offline indicators**: Show cached vs live data

#### Japanese Mobile Patterns
- **QR code integration**: For easy sharing
- **Map integration**: Quick access to location
- **Station distance**: Prominent display for commuters
- **Bookmark system**: Save favorite properties

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
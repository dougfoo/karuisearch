/**
 * Type definitions for Karui-Search property data
 * Matches our simplified V1 database schema
 */

export interface Property {
  id: string;
  title: string;
  price: string; // Keep original format: "¥58,000,000", "5,800万円"
  location: string; // Address/area as displayed on site
  property_type?: string; // "別荘", "一戸建て", "土地", etc.
  size_info?: string; // "土地:200㎡ 建物:150㎡"
  building_age?: string; // "築15年", "新築", "平成20年建築"
  description?: string;
  image_urls?: string[]; // Max 5 images
  rooms?: string; // "3LDK", "4SLDK"
  source_url: string;
  scraped_date: string; // ISO date string
  date_first_seen: string; // ISO datetime string
  
  // Optional computed fields for UI
  price_change?: PriceChange;
  is_new?: boolean; // Added this week
  is_featured?: boolean;
  isFavorite?: boolean; // User favorite status
}

export interface PriceChange {
  amount: string; // "+¥2,000,000", "-¥1,500,000"
  percentage: string; // "+3.6%", "-2.1%"
  direction: 'increase' | 'decrease' | 'none';
  since_date: string;
}

export interface PropertySource {
  id: string;
  name: string;
  base_url: string;
  display_name: string; // "Royal Resort", "Besso Navi"
  is_active: boolean;
}

export interface WeeklyReport {
  week_start: string; // ISO date
  week_end: string; // ISO date
  total_new: number;
  price_changes: {
    increases: number;
    decreases: number;
  };
  properties: Property[];
  generated_at: string; // ISO datetime
}

export interface PropertyFilters {
  property_types: string[];
  price_range: {
    min: number;
    max: number;
  };
  areas: string[];
  building_age_categories: string[];
  keyword: string;
  has_images: boolean;
}

export interface SortOption {
  key: string;
  label: string;
  label_en: string;
  direction: 'asc' | 'desc';
}

export interface PaginationInfo {
  page: number;
  per_page: number;
  total: number;
  total_pages: number;
}

// API Response types
export interface PropertiesResponse {
  properties: Property[];
  pagination: PaginationInfo;
  filters_applied: PropertyFilters;
}

export interface PropertyDetailResponse extends Property {
  related_properties: Property[];
  price_history: Array<{
    date: string;
    price: string;
  }>;
}

// UI State types
export interface UIState {
  theme: 'light' | 'dark';
  language: 'ja' | 'en';
  sidebar_open: boolean;
  loading: boolean;
  error: string | null;
}

export interface PropertyCardProps {
  property: Property;
  onClick?: (property: Property) => void;
  showPriceChange?: boolean;
  compact?: boolean;
}

export interface PropertyGridProps {
  properties: Property[];
  loading?: boolean;
  error?: string | null;
  onPropertyClick?: (property: Property) => void;
  emptyMessage?: string;
}
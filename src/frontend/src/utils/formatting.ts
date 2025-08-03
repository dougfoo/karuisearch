/**
 * Formatting utilities for Japanese real estate data
 * Handles currency, numbers, dates, and property-specific formatting
 */

import { logger } from './logger';

// Japanese number formatting utilities
export const formatPrice = (price: string | number, locale: string = 'ja'): string => {
  // If price is already a formatted string, return as-is
  if (typeof price === 'string' && price.includes('¥')) {
    return price;
  }
  
  const numericPrice = typeof price === 'string' ? parseFloat(price.replace(/[^\d]/g, '')) : price;
  
  if (isNaN(numericPrice)) {
    logger.warn('Invalid price format', {
      component: 'formatting',
      action: 'format_price',
      metadata: { price, locale }
    });
    return typeof price === 'string' ? price : '¥0';
  }
  
  if (locale === 'ja') {
    // Japanese formatting with 万円/億円
    if (numericPrice >= 100000000) { // 1億円以上
      const oku = numericPrice / 100000000;
      return `¥${oku.toFixed(oku % 1 === 0 ? 0 : 1)}億円`;
    } else if (numericPrice >= 10000) { // 1万円以上
      const man = numericPrice / 10000;
      return `¥${man.toFixed(man % 1 === 0 ? 0 : 0)}万円`;
    } else {
      return `¥${numericPrice.toLocaleString('ja-JP')}`;
    }
  } else {
    // English formatting
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(numericPrice);
  }
};

// Parse price from string to number
export const parsePrice = (priceString: string): number => {
  if (!priceString) return 0;
  
  // Handle Japanese format (万円, 億円)
  if (priceString.includes('万円')) {
    const match = priceString.match(/¥?([0-9,]+(?:\.[0-9]+)?)万円/);
    if (match) {
      return parseFloat(match[1].replace(/,/g, '')) * 10000;
    }
  }
  
  if (priceString.includes('億円')) {
    const match = priceString.match(/¥?([0-9,]+(?:\.[0-9]+)?)億円/);
    if (match) {
      return parseFloat(match[1].replace(/,/g, '')) * 100000000;
    }
  }
  
  // Handle regular number format
  const numbers = priceString.replace(/[^\d]/g, '');
  return parseInt(numbers, 10) || 0;
};

// Format area/size information
export const formatSizeInfo = (sizeInfo: string, locale: string = 'ja'): string => {
  if (!sizeInfo || locale === 'ja') {
    return sizeInfo;
  }
  
  // Translate to English
  return sizeInfo
    .replace('土地:', 'Land: ')
    .replace('建物:', 'Building: ')
    .replace('専有面積:', 'Area: ')
    .replace('延床面積:', 'Total Floor Area: ')
    .replace('㎡', ' sqm')
    .replace('坪', ' tsubo');
};

// Format building age
export const formatBuildingAge = (buildingAge: string, locale: string = 'ja'): string => {
  if (!buildingAge || locale === 'ja') {
    return buildingAge;
  }
  
  // Translate common age terms
  const ageTranslations: Record<string, string> = {
    '新築': 'New Construction',
    '築浅': 'Recently Built',
  };
  
  // Handle "築X年" format
  const yearMatch = buildingAge.match(/築(\d+)年/);
  if (yearMatch) {
    const years = parseInt(yearMatch[1], 10);
    return years === 1 ? '1 year old' : `${years} years old`;
  }
  
  // Handle era format (平成XX年, 令和XX年)
  if (buildingAge.includes('平成') || buildingAge.includes('令和')) {
    return `Built in ${buildingAge}`;
  }
  
  return ageTranslations[buildingAge] || buildingAge;
};

// Format property type
export const formatPropertyType = (propertyType: string, locale: string = 'ja'): string => {
  if (!propertyType || locale === 'ja') {
    return propertyType;
  }
  
  const typeTranslations: Record<string, string> = {
    '一戸建て': 'Single-Family House',
    '別荘': 'Vacation Home',
    '土地': 'Land',
    'マンション': 'Apartment/Condo',
    'リゾートマンション': 'Resort Condominium',
  };
  
  return typeTranslations[propertyType] || propertyType;
};

// Format location/address
export const formatLocation = (location: string, locale: string = 'ja'): string => {
  if (!location || locale === 'ja') {
    return location;
  }
  
  // Translate location parts to English
  let translated = location
    .replace('長野県北佐久郡軽井沢町', 'Karuizawa, Kitasaku District, Nagano Prefecture ')
    .replace('軽井沢町', 'Karuizawa ')
    .replace('旧軽井沢', 'Old Karuizawa')
    .replace('新軽井沢', 'New Karuizawa')
    .replace('中軽井沢', 'Central Karuizawa')
    .replace('南軽井沢', 'South Karuizawa')
    .replace('追分', 'Oiwake')
    .replace('長倉', 'Nagakura')
    .replace('発地', 'Hatchi')
    .replace('大字', '');
  
  // Clean up extra spaces
  return translated.replace(/\s+/g, ' ').trim();
};

// Format date in Japanese style
export const formatDate = (dateString: string, locale: string = 'ja'): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  
  if (isNaN(date.getTime())) {
    logger.warn('Invalid date format', {
      component: 'formatting',
      action: 'format_date',
      metadata: { dateString, locale }
    });
    return dateString;
  }
  
  if (locale === 'ja') {
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'numeric',
      day: 'numeric',
    });
  } else {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'short',
      day: 'numeric',
    });
  }
};

// Format relative date (e.g., "3 days ago")
export const formatRelativeDate = (dateString: string, locale: string = 'ja'): string => {
  if (!dateString) return '';
  
  const date = new Date(dateString);
  const now = new Date();
  const diffMs = now.getTime() - date.getTime();
  const diffDays = Math.floor(diffMs / (1000 * 60 * 60 * 24));
  
  if (diffDays === 0) {
    return locale === 'ja' ? '今日' : 'Today';
  } else if (diffDays === 1) {
    return locale === 'ja' ? '昨日' : 'Yesterday';
  } else if (diffDays < 7) {
    return locale === 'ja' ? `${diffDays}日前` : `${diffDays} days ago`;
  } else if (diffDays < 30) {
    const weeks = Math.floor(diffDays / 7);
    return locale === 'ja' ? `${weeks}週間前` : `${weeks} week${weeks > 1 ? 's' : ''} ago`;
  } else {
    return formatDate(dateString, locale);
  }
};

// Format price change
export const formatPriceChange = (priceChange: {
  amount: string;
  percentage: string;
  direction: 'increase' | 'decrease' | 'none';
}, locale: string = 'ja'): string => {
  if (!priceChange || priceChange.direction === 'none') {
    return locale === 'ja' ? '価格変更なし' : 'No change';
  }
  
  const { amount, percentage, direction } = priceChange;
  
  if (locale === 'ja') {
    const directionText = direction === 'increase' ? '値上がり' : '値下がり';
    return `${amount} (${percentage}) ${directionText}`;
  } else {
    const directionText = direction === 'increase' ? 'increase' : 'decrease';
    return `${amount} (${percentage}) ${directionText}`;
  }
};

// Truncate text with ellipsis
export const truncateText = (text: string, maxLength: number): string => {
  if (!text || text.length <= maxLength) {
    return text;
  }
  
  return text.substring(0, maxLength) + '...';
};

// Extract number from string
export const extractNumber = (str: string): number => {
  if (!str) return 0;
  
  const match = str.match(/[\d,]+/);
  if (match) {
    return parseInt(match[0].replace(/,/g, ''), 10);
  }
  
  return 0;
};

// Format number with locale
export const formatNumber = (num: number, locale: string = 'ja'): string => {
  if (locale === 'ja') {
    return num.toLocaleString('ja-JP');
  } else {
    return num.toLocaleString('en-US');
  }
};

// Validate and clean image URL
export const cleanImageUrl = (url: string): string => {
  if (!url) return '';
  
  // Remove any extra spaces or special characters
  const cleaned = url.trim();
  
  // Validate URL format
  try {
    new URL(cleaned);
    return cleaned;
  } catch {
    logger.warn('Invalid image URL', {
      component: 'formatting',
      action: 'clean_image_url',
      metadata: { url: cleaned }
    });
    return '';
  }
};

// Get display text for empty values
export const getEmptyText = (locale: string = 'ja'): string => {
  return locale === 'ja' ? '情報なし' : 'Not available';
};
/**
 * Internationalization configuration for Karui-Search
 * Supports Japanese (primary) and English languages
 */

import i18n from 'i18next';
import { initReactI18next } from 'react-i18next';
import LanguageDetector from 'i18next-browser-languagedetector';

import jaTranslations from './ja.json';
import enTranslations from './en.json';
import { logger } from '../utils/logger';

// Translation resources
const resources = {
  ja: {
    translation: jaTranslations,
  },
  en: {
    translation: enTranslations,
  },
};

// Language detection configuration
const detectionOptions = {
  // Detection order
  order: [
    'localStorage',   // Check localStorage first
    'navigator',      // Then browser language
    'htmlTag',        // Then HTML lang attribute
    'path',           // Then URL path
    'subdomain',      // Then subdomain
  ],
  
  // Cache user language
  caches: ['localStorage'],
  
  // Don't cache on these paths
  excludeCacheFor: ['cimode'],
  
  // Check for supported languages only
  checkWhitelist: true,
};

// Initialize i18next
i18n
  .use(LanguageDetector)
  .use(initReactI18next)
  .init({
    resources,
    
    // Language settings
    fallbackLng: 'ja',           // Default to Japanese
    supportedLngs: ['ja', 'en'], // Supported languages
    load: 'languageOnly',        // Don't load country-specific variants
    
    // Detection settings
    detection: detectionOptions,
    
    // Interpolation settings
    interpolation: {
      escapeValue: false,        // React already does escaping
      formatSeparator: ',',
      format: (value, format, lng) => {
        // Custom formatting for numbers and dates
        if (format === 'currency') {
          return formatCurrency(value, lng || 'ja');
        }
        if (format === 'number') {
          return formatNumber(value, lng || 'ja');
        }
        if (format === 'date') {
          return formatDate(value, lng || 'ja');
        }
        return value;
      },
    },
    
    // Namespace settings
    defaultNS: 'translation',
    ns: ['translation'],
    
    // Debug settings
    debug: import.meta.env.DEV,
    
    // React settings
    react: {
      useSuspense: false,
    },
    
    // Pluralization
    pluralSeparator: '_',
    contextSeparator: '_',
    
    // Performance
    parseMissingKeyHandler: (key) => {
      logger.warn('Missing translation key', {
        component: 'i18n',
        action: 'missing_key',
        metadata: { key, language: i18n.language }
      });
      return key;
    },
  });

// Custom formatting functions
function formatCurrency(value: number, language: string): string {
  if (language === 'ja') {
    // Japanese currency formatting
    if (value >= 100000000) { // 1億円以上
      return `¥${(value / 100000000).toFixed(1)}億円`;
    } else if (value >= 10000) { // 1万円以上
      return `¥${(value / 10000).toFixed(0)}万円`;
    } else {
      return `¥${value.toLocaleString('ja-JP')}`;
    }
  } else {
    // English currency formatting
    return new Intl.NumberFormat('en-US', {
      style: 'currency',
      currency: 'JPY',
      minimumFractionDigits: 0,
      maximumFractionDigits: 0,
    }).format(value);
  }
}

function formatNumber(value: number, language: string): string {
  if (language === 'ja') {
    return value.toLocaleString('ja-JP');
  } else {
    return value.toLocaleString('en-US');
  }
}

function formatDate(value: string | Date, language: string): string {
  const date = new Date(value);
  
  if (language === 'ja') {
    return date.toLocaleDateString('ja-JP', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  } else {
    return date.toLocaleDateString('en-US', {
      year: 'numeric',
      month: 'long',
      day: 'numeric',
    });
  }
}

// Property data translation utilities
export const translatePropertyType = (originalType: string, targetLang: string): string => {
  const translations: Record<string, Record<string, string>> = {
    '一戸建て': { en: 'Single-Family House' },
    '別荘': { en: 'Vacation Home' },
    '土地': { en: 'Land' },
    'マンション': { en: 'Apartment/Condo' },
  };
  
  if (targetLang === 'ja') {
    return originalType;
  }
  
  return translations[originalType]?.[targetLang] || originalType;
};

export const translateSizeInfo = (sizeInfo: string, targetLang: string): string => {
  if (targetLang === 'ja') {
    return sizeInfo;
  }
  
  return sizeInfo
    .replace('土地:', 'Land: ')
    .replace('建物:', 'Building: ')
    .replace('専有面積:', 'Area: ')
    .replace('㎡', ' sqm')
    .replace('坪', ' tsubo');
};

export const translateBuildingAge = (buildingAge: string, targetLang: string): string => {
  if (targetLang === 'ja') {
    return buildingAge;
  }
  
  const ageTranslations: Record<string, string> = {
    '新築': 'New Construction',
    '築浅': 'Recently Built',
  };
  
  // Handle "築X年" format
  const yearMatch = buildingAge.match(/築(\d+)年/);
  if (yearMatch) {
    return `${yearMatch[1]} years old`;
  }
  
  return ageTranslations[buildingAge] || buildingAge;
};

export const translateLocation = (location: string, targetLang: string): string => {
  if (targetLang === 'ja') {
    return location;
  }
  
  return location
    .replace('長野県北佐久郡軽井沢町', 'Karuizawa, Kitasaku District, Nagano Prefecture ')
    .replace('軽井沢町', 'Karuizawa ')
    .replace('旧軽井沢', 'Old Karuizawa')
    .replace('新軽井沢', 'New Karuizawa')
    .replace('中軽井沢', 'Central Karuizawa')
    .replace('南軽井沢', 'South Karuizawa')
    .replace('追分', 'Oiwake')
    .replace('長倉', 'Nagakura')
    .replace('発地', 'Hatchi');
};

// Event listeners for language changes
i18n.on('languageChanged', (lng) => {
  logger.languageChanged(i18n.language, lng);
  
  // Update HTML lang attribute
  document.documentElement.lang = lng;
  
  // Update document title
  const appTitle = i18n.t('app.title');
  document.title = appTitle;
});

// Log initialization
logger.info('i18n initialized', {
  component: 'i18n',
  action: 'initialized',
  metadata: {
    language: i18n.language,
    supportedLanguages: ['ja', 'en'],
    detectedLanguage: i18n.language,
  }
});

export default i18n;
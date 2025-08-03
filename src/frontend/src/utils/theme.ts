/**
 * Material-UI theme configuration with Japanese aesthetics
 * Optimized for Karuizawa real estate application
 */

import { createTheme, ThemeOptions } from '@mui/material/styles';
import { logger } from './logger';

// Japanese-inspired color palette
const colors = {
  // Primary: Forest Green (軽井沢の森)
  primary: {
    main: '#2E7D32',    // Deep forest green
    light: '#66BB6A',   // Light green
    dark: '#1B5E20',    // Dark forest
    contrastText: '#ffffff',
  },
  
  // Secondary: Mountain Earth (山の土)
  secondary: {
    main: '#5D4037',    // Warm brown
    light: '#8D6E63',   // Light brown
    dark: '#3E2723',    // Dark brown
    contrastText: '#ffffff',
  },
  
  // Accent colors for specific use cases
  accent: {
    blue: '#1976D2',     // Clear sky blue
    warm: '#FF8F00',     // Autumn orange
    neutral: '#616161',  // Charcoal grey
    success: '#4CAF50',  // Success green
    warning: '#FF9800',  // Warning orange
    error: '#F44336',    // Error red
  },
  
  // Japanese aesthetic colors (縁起の良い色)
  japanese: {
    prosperity: '#B8860B',  // Gold - wealth, prosperity
    nature: '#228B22',      // Green - growth, harmony
    stability: '#8B4513',   // Brown - earth, stability
    purity: '#F8F8FF',      // White - cleanliness, new beginnings
    elegance: '#2F4F4F',    // Dark slate gray - sophistication
  }
};

// Typography configuration with Japanese font support
const typography: ThemeOptions['typography'] = {
  fontFamily: [
    'Noto Sans JP',
    'Roboto',
    'Hiragino Sans',
    'ヒラギノ角ゴ Pro W3',
    'Hiragino Kaku Gothic Pro',
    'メイリオ',
    'Meiryo',
    'MS Pゴシック',
    'sans-serif'
  ].join(','),
  
  // Japanese text hierarchy
  h1: {
    fontSize: '2.5rem',
    fontWeight: 300,
    lineHeight: 1.2,
    letterSpacing: '-0.01562em',
  },
  h2: {
    fontSize: '2rem',
    fontWeight: 400,
    lineHeight: 1.3,
    letterSpacing: '-0.00833em',
  },
  h3: {
    fontSize: '1.5rem',
    fontWeight: 500,
    lineHeight: 1.4,
    letterSpacing: '0em',
  },
  h4: {
    fontSize: '1.25rem',
    fontWeight: 500,
    lineHeight: 1.4,
    letterSpacing: '0.00735em',
  },
  h5: {
    fontSize: '1.125rem',
    fontWeight: 500,
    lineHeight: 1.5,
    letterSpacing: '0em',
  },
  h6: {
    fontSize: '1rem',
    fontWeight: 500,
    lineHeight: 1.5,
    letterSpacing: '0.0075em',
  },
  
  // Body text optimized for Japanese readability
  body1: {
    fontSize: '1rem',
    lineHeight: 1.6,
    letterSpacing: '0.00938em',
  },
  body2: {
    fontSize: '0.875rem',
    lineHeight: 1.5,
    letterSpacing: '0.01071em',
  },
  
  // UI elements
  button: {
    fontSize: '0.875rem',
    fontWeight: 500,
    lineHeight: 1.75,
    letterSpacing: '0.02857em',
    textTransform: 'none', // Preserve Japanese text case
  },
  caption: {
    fontSize: '0.75rem',
    lineHeight: 1.5,
    letterSpacing: '0.03333em',
  },
  overline: {
    fontSize: '0.75rem',
    fontWeight: 500,
    lineHeight: 2,
    letterSpacing: '0.08333em',
    textTransform: 'none',
  },
};

// Component style overrides for Japanese UX
const components: ThemeOptions['components'] = {
  // Card styling for property cards
  MuiCard: {
    styleOverrides: {
      root: {
        borderRadius: 12,
        boxShadow: '0 2px 8px rgba(0,0,0,0.1)',
        transition: 'all 0.3s ease-in-out',
        '&:hover': {
          boxShadow: '0 4px 16px rgba(0,0,0,0.15)',
          transform: 'translateY(-2px)',
        },
      },
    },
  },
  
  // Button styling
  MuiButton: {
    styleOverrides: {
      root: {
        borderRadius: 8,
        padding: '8px 16px',
        textTransform: 'none',
        fontSize: '0.875rem',
        fontWeight: 500,
      },
      contained: {
        boxShadow: '0 2px 4px rgba(0,0,0,0.1)',
        '&:hover': {
          boxShadow: '0 4px 8px rgba(0,0,0,0.15)',
        },
      },
    },
  },
  
  // Chip styling for property types
  MuiChip: {
    styleOverrides: {
      root: {
        borderRadius: 16,
        fontSize: '0.75rem',
      },
    },
  },
  
  // Input styling
  MuiTextField: {
    styleOverrides: {
      root: {
        '& .MuiOutlinedInput-root': {
          borderRadius: 8,
        },
      },
    },
  },
  
  // Paper styling
  MuiPaper: {
    styleOverrides: {
      root: {
        borderRadius: 12,
      },
    },
  },
  
  // AppBar styling
  MuiAppBar: {
    styleOverrides: {
      root: {
        boxShadow: '0 1px 3px rgba(0,0,0,0.1)',
      },
    },
  },
};

// Breakpoints for responsive design
const breakpoints = {
  values: {
    xs: 0,      // Mobile phones
    sm: 600,    // Tablets
    md: 900,    // Small laptops
    lg: 1200,   // Desktops
    xl: 1536,   // Large screens
  },
};

// Spacing configuration
const spacing = 8; // 8px base unit

// Create the main theme
export const createAppTheme = (mode: 'light' | 'dark' = 'light') => {
  const isDark = mode === 'dark';
  
  const theme = createTheme({
    palette: {
      mode,
      primary: colors.primary,
      secondary: colors.secondary,
      background: {
        default: isDark ? '#121212' : '#fafafa',
        paper: isDark ? '#1e1e1e' : '#ffffff',
      },
      text: {
        primary: isDark ? '#ffffff' : '#212121',
        secondary: isDark ? '#b3b3b3' : '#666666',
      },
      divider: isDark ? '#333333' : '#e0e0e0',
      error: {
        main: colors.accent.error,
      },
      warning: {
        main: colors.accent.warning,
      },
      success: {
        main: colors.accent.success,
      },
    },
    typography,
    components,
    breakpoints,
    spacing,
    
    // Custom theme extensions
    custom: {
      colors: {
        ...colors,
        // Property type colors
        propertyTypes: {
          house: colors.primary.main,     // 一戸建て
          apartment: colors.accent.blue,  // マンション
          land: colors.accent.warm,       // 土地
          vacation: colors.secondary.main, // 別荘
        },
        // Price change indicators
        priceChange: {
          increase: colors.accent.success,
          decrease: colors.accent.error,
          neutral: colors.accent.neutral,
        },
      },
      // Japanese-specific styling
      japanese: {
        cardSpacing: 16,
        borderRadius: {
          small: 8,
          medium: 12,
          large: 16,
        },
        shadows: {
          light: '0 2px 8px rgba(0,0,0,0.1)',
          medium: '0 4px 16px rgba(0,0,0,0.15)',
          heavy: '0 8px 32px rgba(0,0,0,0.2)',
        },
      },
    },
  });
  
  logger.debug('Theme created', {
    component: 'theme',
    action: 'theme_created',
    metadata: { mode, colors: Object.keys(colors) }
  });
  
  return theme;
};

// Default light theme
export const lightTheme = createAppTheme('light');

// Dark theme for future use
export const darkTheme = createAppTheme('dark');

// Theme utilities
export const getPropertyTypeColor = (type: string, theme: any) => {
  const typeMap: Record<string, string> = {
    '一戸建て': theme.custom.colors.propertyTypes.house,
    'マンション': theme.custom.colors.propertyTypes.apartment,
    '土地': theme.custom.colors.propertyTypes.land,
    '別荘': theme.custom.colors.propertyTypes.vacation,
  };
  
  return typeMap[type] || theme.palette.primary.main;
};

export const getPriceChangeColor = (direction: string, theme: any) => {
  const directionMap: Record<string, string> = {
    increase: theme.custom.colors.priceChange.increase,
    decrease: theme.custom.colors.priceChange.decrease,
    none: theme.custom.colors.priceChange.neutral,
  };
  
  return directionMap[direction] || theme.custom.colors.priceChange.neutral;
};

// Export default theme
export default lightTheme;
/**
 * PropertyGrid Component
 * Responsive grid layout for displaying property cards
 * Handles loading states, empty states, and pagination
 */

import React from 'react';
import {
  Grid,
  Box,
  Typography,
  Alert,
  Button,
  Container,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import { Refresh as RefreshIcon } from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { Property, PropertyGridProps } from '@types/property';
import PropertyCard, { PropertyCardSkeleton } from './PropertyCard';
import { logger } from '@utils/logger';

const PropertyGrid: React.FC<PropertyGridProps> = ({
  properties,
  loading = false,
  error = null,
  onPropertyClick,
  emptyMessage,
}) => {
  const theme = useTheme();
  const { t } = useTranslation();
  
  // Responsive breakpoints
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));
  const isTablet = useMediaQuery(theme.breakpoints.down('md'));

  // Determine grid spacing based on screen size
  const getGridSpacing = () => {
    if (isMobile) return 2;
    if (isTablet) return 3;
    return 4;
  };

  // Determine number of skeleton cards to show
  const getSkeletonCount = () => {
    if (isMobile) return 2;
    if (isTablet) return 4;
    return 6;
  };

  // Handle property card click
  const handlePropertyClick = (property: Property) => {
    logger.propertyViewed(property.id, 'grid_click');
    if (onPropertyClick) {
      onPropertyClick(property);
    }
  };

  // Handle retry action
  const handleRetry = () => {
    logger.userInteraction('PropertyGrid', 'retry_click');
    // In a real app, this would trigger a refetch
    window.location.reload();
  };

  // Log grid render
  React.useEffect(() => {
    if (!loading && !error) {
      logger.debug('PropertyGrid rendered', {
        component: 'PropertyGrid',
        action: 'grid_rendered',
        metadata: {
          propertyCount: properties.length,
          screenSize: isMobile ? 'mobile' : isTablet ? 'tablet' : 'desktop'
        }
      });
    }
  }, [properties.length, loading, error, isMobile, isTablet]);

  // Error state
  if (error && !loading) {
    return (
      <Container maxWidth="md" sx={{ py: 4 }}>
        <Alert 
          severity="error" 
          action={
            <Button 
              color="inherit" 
              size="small" 
              onClick={handleRetry}
              startIcon={<RefreshIcon />}
            >
              {t('common.retry')}
            </Button>
          }
        >
          <Typography variant="h6" gutterBottom>
            {t('error.general')}
          </Typography>
          <Typography variant="body2">
            {error}
          </Typography>
        </Alert>
      </Container>
    );
  }

  // Loading state
  if (loading) {
    return (
      <Container maxWidth="lg" sx={{ py: 2 }}>
        <Grid container spacing={getGridSpacing()}>
          {Array.from({ length: getSkeletonCount() }).map((_, index) => (
            <Grid item xs={12} sm={6} md={4} lg={3} key={`skeleton-${index}`}>
              <PropertyCardSkeleton compact={isMobile} />
            </Grid>
          ))}
        </Grid>
      </Container>
    );
  }

  // Empty state
  if (!properties || properties.length === 0) {
    return (
      <Container maxWidth="md" sx={{ py: 8, textAlign: 'center' }}>
        <Box>
          <Typography variant="h5" color="text.secondary" gutterBottom>
            {emptyMessage || t('listings.noResults')}
          </Typography>
          <Typography variant="body1" color="text.secondary" sx={{ mb: 3 }}>
            {t('listings.refineSearch')}
          </Typography>
          <Button 
            variant="outlined" 
            onClick={handleRetry}
            startIcon={<RefreshIcon />}
          >
            {t('common.retry')}
          </Button>
        </Box>
      </Container>
    );
  }

  // Main grid display
  return (
    <Container maxWidth="lg" sx={{ py: 2 }}>
      <Grid container spacing={getGridSpacing()}>
        {properties.map((property) => (
          <Grid 
            item 
            xs={12} 
            sm={6} 
            md={4} 
            lg={3} 
            key={property.id}
            sx={{
              // Ensure consistent grid item heights
              '& .MuiCard-root': {
                height: '100%',
              }
            }}
          >
            <PropertyCard
              property={property}
              onClick={handlePropertyClick}
              showPriceChange={true}
              compact={isMobile}
            />
          </Grid>
        ))}
      </Grid>

      {/* Grid performance metrics for development */}
      {import.meta.env.DEV && (
        <Box sx={{ mt: 2, p: 1, bgcolor: 'grey.100', borderRadius: 1 }}>
          <Typography variant="caption" color="text.secondary">
            Debug: {properties.length} properties rendered • 
            Grid: {isMobile ? '1' : isTablet ? '2' : '3-4'} columns • 
            Spacing: {getGridSpacing()}px
          </Typography>
        </Box>
      )}
    </Container>
  );
};

export default PropertyGrid;
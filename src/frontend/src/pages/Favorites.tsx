/**
 * Favorites Page Component
 * Displays user's saved favorite properties
 * Allows removal of favorites and navigation to property details
 */

import React from 'react';
import {
  Box,
  Container,
  Typography,
  Button,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  Favorite as FavoriteIcon,
  ArrowBack as ArrowBackIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { useFavorites } from '@services/queries';
import PropertyGrid from '@components/property/PropertyGrid';
import { LoadingSpinner, EmptyState, ErrorState } from '@components/ui/LoadingStates';
import { logger } from '@utils/logger';

const Favorites: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('sm'));

  // Data query
  const {
    data: favoriteProperties = [],
    isLoading,
    error,
    refetch,
  } = useFavorites();

  // Event handlers
  const handleBack = () => {
    navigate(-1);
    logger.userInteraction('Favorites', 'back_click');
  };

  const handlePropertyClick = (property: any) => {
    navigate(`/property/${property.id}`);
    logger.userInteraction('Favorites', 'property_click', {
      propertyId: property.id
    });
  };

  const handleBrowseProperties = () => {
    navigate('/listings');
    logger.userInteraction('Favorites', 'browse_properties_click');
  };

  // Log page view
  React.useEffect(() => {
    logger.pageView('Favorites', {
      favoriteCount: favoriteProperties.length
    });
  }, [favoriteProperties.length]);

  // Handle error state
  if (error && !isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ErrorState
          message={error.message}
          onRetry={() => refetch()}
        />
      </Container>
    );
  }

  return (
    <Box data-testid="favorites-page">
      {/* Page Header */}
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <Box display="flex" alignItems="center" mb={4}>
          <Button
            startIcon={<ArrowBackIcon />}
            onClick={handleBack}
            sx={{ mr: 2 }}
          >
            {t('common.back')}
          </Button>
          
          <Box>
            <Box display="flex" alignItems="center" gap={1} mb={1}>
              <FavoriteIcon color="error" />
              <Typography variant="h4" component="h1" sx={{ fontWeight: 700 }}>
                {t('favorites.title')}
              </Typography>
            </Box>
            <Typography variant="body1" color="text.secondary">
              {isLoading 
                ? t('common.loading') 
                : t('favorites.description', { count: favoriteProperties.length })
              }
            </Typography>
          </Box>
        </Box>

        {/* Loading State */}
        {isLoading ? (
          <LoadingSpinner message={t('favorites.loading')} />
        ) : favoriteProperties.length === 0 ? (
          /* Empty State */
          <EmptyState
            type="favorite"
            title={t('favorites.emptyState.title')}
            description={t('favorites.emptyState.description')}
            action={{
              label: t('favorites.emptyState.action'),
              onClick: handleBrowseProperties,
            }}
          />
        ) : (
          /* Favorites Grid */
          <>
            {/* Results Summary */}
            <Box 
              display="flex" 
              justifyContent="space-between" 
              alignItems="center" 
              mb={3}
              sx={{
                p: 2,
                backgroundColor: theme.palette.background.paper,
                borderRadius: 1,
                border: `1px solid ${theme.palette.divider}`,
              }}
            >
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {t('favorites.resultsCount', { count: favoriteProperties.length })}
              </Typography>
              
              <Button
                variant="outlined"
                onClick={handleBrowseProperties}
                size={isMobile ? 'small' : 'medium'}
              >
                {t('favorites.browseMore')}
              </Button>
            </Box>

            <PropertyGrid
              properties={favoriteProperties}
              loading={isLoading}
              error={error?.message || null}
              onPropertyClick={handlePropertyClick}
              emptyMessage={t('favorites.noResults')}
            />
          </>
        )}
      </Container>
    </Box>
  );
};

export default Favorites;
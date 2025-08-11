/**
 * All Listings Page Component
 * Comprehensive property search and browsing interface
 * Features advanced filtering, sorting, and pagination
 */

import React, { useState, useCallback, useMemo } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Button,
  Fab,
  Badge,
  useTheme,
  useMediaQuery,
  Drawer,
} from '@mui/material';
import {
  FilterList as FilterListIcon,
  Tune as TuneIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { PropertyFilters } from '@types/property';
import { useProperties } from '@services/queries';
import PropertyGrid from '@components/property/PropertyGrid';
import FilterControls from '@components/ui/FilterControls';
import { LoadingSpinner, EmptyState, ErrorState } from '@components/ui/LoadingStates';
import { logger } from '@utils/logger';

const AllListings: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // UI State
  const [mobileFiltersOpen, setMobileFiltersOpen] = useState(false);

  // Filter state with more comprehensive defaults
  const [filters, setFilters] = useState<PropertyFilters>({
    searchTerm: '',
    propertyTypes: [],
    locations: [],
    priceRange: { min: 0, max: 500000000 },
    sortBy: 'date_desc',
    page: 1,
    pageSize: 24,
  });

  // Data query
  const {
    data: properties = [],
    isLoading,
    error,
    refetch,
  } = useProperties(filters);

  // Memoized active filter count for performance
  const activeFilterCount = useMemo(() => {
    let count = 0;
    if (filters.searchTerm?.trim()) count++;
    if (filters.propertyTypes && filters.propertyTypes.length > 0) count++;
    if (filters.locations && filters.locations.length > 0) count++;
    if (filters.priceRange && (filters.priceRange.min > 0 || filters.priceRange.max < 500000000)) count++;
    if (filters.sortBy && filters.sortBy !== 'date_desc') count++;
    return count;
  }, [filters]);

  // Event handlers
  const handleFiltersChange = useCallback((newFilters: PropertyFilters) => {
    setFilters(prev => ({
      ...prev,
      ...newFilters,
      page: 1, // Reset to first page when filters change
    }));
    logger.userInteraction('AllListings', 'filters_change', {
      activeFilters: Object.keys(newFilters).length
    });
  }, []);

  const handleClearFilters = useCallback(() => {
    setFilters({
      searchTerm: '',
      propertyTypes: [],
      locations: [],
      priceRange: { min: 0, max: 500000000 },
      sortBy: 'date_desc',
      page: 1,
      pageSize: 24,
    });
    setMobileFiltersOpen(false);
    logger.userInteraction('AllListings', 'clear_all_filters');
  }, []);

  const handlePropertyClick = useCallback((property: any) => {
    navigate(`/property/${property.id}`);
    logger.userInteraction('AllListings', 'property_click', {
      propertyId: property.id
    });
  }, [navigate]);

  const handleLoadMore = useCallback(() => {
    setFilters(prev => ({
      ...prev,
      pageSize: (prev.pageSize || 24) + 24
    }));
    logger.userInteraction('AllListings', 'load_more', {
      newPageSize: (filters.pageSize || 24) + 24
    });
  }, [filters.pageSize]);

  const handleMobileFiltersToggle = useCallback(() => {
    setMobileFiltersOpen(prev => !prev);
    logger.userInteraction('AllListings', 'mobile_filters_toggle', {
      isOpen: !mobileFiltersOpen
    });
  }, [mobileFiltersOpen]);

  // Log page view
  React.useEffect(() => {
    logger.pageView('AllListings', {
      totalProperties: properties.length,
      activeFilterCount,
      hasSearch: !!filters.searchTerm?.trim()
    });
  }, [properties.length, activeFilterCount, filters.searchTerm]);

  // Handle error state
  if (error && !isLoading) {
    return (
      <Container maxWidth="xl" sx={{ py: 2 }}>
        <ErrorState
          message={error.message}
          onRetry={() => refetch()}
        />
      </Container>
    );
  }

  const hasMoreToLoad = properties.length >= (filters.pageSize || 24);

  return (
    <Box data-testid="all-listings-page">
      {/* Page Header */}
      <Container maxWidth="xl" sx={{ py: 2 }}>
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={4}>
          <Box>
            <Typography variant="h4" component="h1" gutterBottom sx={{ fontWeight: 700 }}>
              {t('allListings.title')}
            </Typography>
            <Typography variant="body1" color="text.secondary">
              {t('allListings.description')}
            </Typography>
          </Box>

        </Box>

        {/* Desktop Filters - Top Row */}
        {!isMobile && (
          <FilterControls
            filters={filters}
            onFiltersChange={handleFiltersChange}
            onClear={handleClearFilters}
            resultsCount={properties.length}
            loading={isLoading}
          />
        )}

        {/* Results Header */}
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
            {isLoading 
              ? t('common.loading')
              : t('allListings.resultsCount', { count: properties.length })
            }
          </Typography>

          {/* Active Filters Indicator */}
          {activeFilterCount > 0 && (
            <Badge badgeContent={activeFilterCount} color="primary">
              <TuneIcon color="action" />
            </Badge>
          )}
        </Box>

        {/* Loading State */}
        {isLoading && properties.length === 0 ? (
          <LoadingSpinner message={t('common.loadingProperties')} />
        ) : properties.length === 0 ? (
          /* Empty State */
          <EmptyState
            type="search"
            title={t('allListings.emptyState.title')}
            description={t('allListings.emptyState.description')}
            action={{
              label: t('allListings.emptyState.action'),
              onClick: handleClearFilters,
            }}
          />
        ) : (
          /* Properties Display */
          <>
            <PropertyGrid
              properties={properties}
              loading={isLoading}
              error={error?.message || null}
              onPropertyClick={handlePropertyClick}
              emptyMessage={t('allListings.noResults')}
            />

            {/* Load More Button */}
            {hasMoreToLoad && (
              <Box textAlign="center" sx={{ mt: 4 }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={handleLoadMore}
                  disabled={isLoading}
                  sx={{ minWidth: 200 }}
                >
                  {isLoading 
                    ? t('common.loading')
                    : t('allListings.loadMore')
                  }
                </Button>
              </Box>
            )}

            {/* End of Results Indicator */}
            {!hasMoreToLoad && properties.length > 0 && (
              <Box 
                textAlign="center" 
                sx={{ 
                  mt: 4, 
                  py: 2, 
                  color: 'text.secondary',
                  borderTop: `1px solid ${theme.palette.divider}`,
                }}
              >
                <Typography variant="body2">
                  {t('allListings.endOfResults', { count: properties.length })}
                </Typography>
              </Box>
            )}
          </>
        )}
      </Container>

      {/* Mobile Filter FAB */}
      {isMobile && (
        <Fab
          color="primary"
          aria-label={t('allListings.openFilters')}
          onClick={handleMobileFiltersToggle}
          sx={{
            position: 'fixed',
            bottom: 16,
            right: 16,
            zIndex: theme.zIndex.speedDial,
          }}
        >
          <Badge badgeContent={activeFilterCount} color="error">
            <FilterListIcon />
          </Badge>
        </Fab>
      )}

      {/* Mobile Filter Drawer */}
      {isMobile && (
        <Drawer
          anchor="bottom"
          open={mobileFiltersOpen}
          onClose={handleMobileFiltersToggle}
          PaperProps={{
            sx: {
              maxHeight: '80vh',
              borderTopLeftRadius: theme.spacing(2),
              borderTopRightRadius: theme.spacing(2),
            },
          }}
        >
          <Box sx={{ p: 2 }}>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              {t('allListings.filters')}
            </Typography>
            <FilterControls
              filters={filters}
              onFiltersChange={(newFilters) => {
                handleFiltersChange(newFilters);
                setMobileFiltersOpen(false);
              }}
              onClear={() => {
                handleClearFilters();
                setMobileFiltersOpen(false);
              }}
              resultsCount={properties.length}
              loading={isLoading}
            />
          </Box>
        </Drawer>
      )}
    </Box>
  );
};

export default AllListings;
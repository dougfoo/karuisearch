/**
 * Home Page Component
 * Main landing page with property search, filters, and grid display
 * Features Japanese real estate search experience
 */

import React, { useState, useMemo } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  useTheme,
  useMediaQuery,
} from '@mui/material';
import {
  TrendingUp as TrendingUpIcon,
  CalendarToday as CalendarTodayIcon,
  Home as HomeIcon,
  Visibility as VisibilityIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { PropertyFilters } from '@types/property';
import { useProperties, useWeeklyReport } from '@services/queries';
import PropertyGrid from '@components/property/PropertyGrid';
import FilterControls from '@components/ui/FilterControls';
import { LoadingSpinner, EmptyState, ErrorState } from '@components/ui/LoadingStates';
import { logger } from '@utils/logger';

const Home: React.FC = () => {
  const theme = useTheme();
  const { t } = useTranslation();
  const navigate = useNavigate();
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // Filter state
  const [filters, setFilters] = useState<PropertyFilters>({
    searchTerm: '',
    propertyTypes: [],
    locations: [],
    priceRange: { min: 0, max: 500000000 },
    sortBy: 'date_desc',
    page: 1,
    pageSize: 12,
  });

  // Data queries
  const {
    data: properties = [],
    isLoading: propertiesLoading,
    error: propertiesError,
    refetch: refetchProperties,
  } = useProperties(filters);

  const {
    data: weeklyReport,
    isLoading: weeklyLoading,
  } = useWeeklyReport(0);

  // Memoized stats for performance
  const stats = useMemo(() => {
    if (!properties.length && !weeklyReport) return null;

    const totalProperties = properties.length;
    const newThisWeek = weeklyReport?.summary.totalListings || 0;
    const averagePrice = weeklyReport?.summary.averagePrice || 0;
    
    // Calculate property type distribution
    const typeDistribution = properties.reduce((acc, property) => {
      if (property.property_type) {
        acc[property.property_type] = (acc[property.property_type] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    return {
      totalProperties,
      newThisWeek,
      averagePrice,
      mostCommonType: Object.entries(typeDistribution).sort(([,a], [,b]) => b - a)[0]?.[0],
    };
  }, [properties, weeklyReport]);

  // Event handlers
  const handleFiltersChange = (newFilters: PropertyFilters) => {
    setFilters(newFilters);
    logger.userInteraction('Home', 'filters_change', {
      filtersChanged: Object.keys(newFilters).length
    });
  };

  const handleClearFilters = () => {
    setFilters({
      searchTerm: '',
      propertyTypes: [],
      locations: [],
      priceRange: { min: 0, max: 500000000 },
      sortBy: 'date_desc',
      page: 1,
      pageSize: 12,
    });
    logger.userInteraction('Home', 'clear_filters');
  };

  const handlePropertyClick = (property: any) => {
    navigate(`/property/${property.id}`);
    logger.userInteraction('Home', 'property_click', {
      propertyId: property.id
    });
  };

  const handleViewWeeklyReport = () => {
    navigate('/weekly');
    logger.userInteraction('Home', 'view_weekly_report');
  };

  const handleViewAllListings = () => {
    navigate('/listings');
    logger.userInteraction('Home', 'view_all_listings');
  };

  // Log page view
  React.useEffect(() => {
    logger.pageView('Home', {
      totalProperties: properties.length,
      hasFilters: Object.values(filters).some(value => 
        Array.isArray(value) ? value.length > 0 : 
        typeof value === 'object' ? Object.values(value).some(v => v !== 0 && v !== 500000000) :
        value !== '' && value !== 'date_desc' && value !== 1 && value !== 12
      )
    });
  }, [properties.length]);

  // Handle error state
  if (propertiesError && !propertiesLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <ErrorState
          message={propertiesError.message}
          onRetry={() => refetchProperties()}
        />
      </Container>
    );
  }

  return (
    <Box data-testid="home-page">
      {/* Hero Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          py: { xs: 4, md: 6 },
          mb: 4,
        }}
      >
        <Container maxWidth="lg">
          <Typography
            variant={isMobile ? 'h4' : 'h3'}
            component="h1"
            gutterBottom
            sx={{ fontWeight: 700, textAlign: 'center' }}
          >
            {t('home.hero.title')}
          </Typography>
          <Typography
            variant="h6"
            sx={{
              textAlign: 'center',
              opacity: 0.9,
              maxWidth: 600,
              mx: 'auto',
              mb: 4,
            }}
          >
            {t('home.hero.subtitle')}
          </Typography>

          {/* Quick Stats */}
          {stats && (
            <Grid container spacing={2} justifyContent="center">
              <Grid item xs={6} sm={3}>
                <Card sx={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'white' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <HomeIcon sx={{ fontSize: 32, mb: 1 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {stats.totalProperties}
                    </Typography>
                    <Typography variant="caption">
                      {t('home.stats.totalProperties')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              <Grid item xs={6} sm={3}>
                <Card sx={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'white' }}>
                  <CardContent sx={{ textAlign: 'center', py: 2 }}>
                    <CalendarTodayIcon sx={{ fontSize: 32, mb: 1 }} />
                    <Typography variant="h6" sx={{ fontWeight: 600 }}>
                      {stats.newThisWeek}
                    </Typography>
                    <Typography variant="caption">
                      {t('home.stats.newThisWeek')}
                    </Typography>
                  </CardContent>
                </Card>
              </Grid>
              {!isMobile && (
                <>
                  <Grid item xs={6} sm={3}>
                    <Card sx={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'white' }}>
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <TrendingUpIcon sx={{ fontSize: 32, mb: 1 }} />
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          ¥{Math.round(stats.averagePrice / 10000)}万
                        </Typography>
                        <Typography variant="caption">
                          {t('home.stats.averagePrice')}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                  <Grid item xs={6} sm={3}>
                    <Card sx={{ backgroundColor: 'rgba(255,255,255,0.1)', color: 'white' }}>
                      <CardContent sx={{ textAlign: 'center', py: 2 }}>
                        <VisibilityIcon sx={{ fontSize: 32, mb: 1 }} />
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {stats.mostCommonType}
                        </Typography>
                        <Typography variant="caption">
                          {t('home.stats.popularType')}
                        </Typography>
                      </CardContent>
                    </Card>
                  </Grid>
                </>
              )}
            </Grid>
          )}
        </Container>
      </Box>

      {/* Main Content */}
      <Container maxWidth="xl">
        <Grid container spacing={2}>
          {/* Filters */}
          <Grid item xs={12}>
            <FilterControls
              filters={filters}
              onFiltersChange={handleFiltersChange}
              onClear={handleClearFilters}
              resultsCount={properties.length}
              loading={propertiesLoading}
            />
          </Grid>

          {/* Quick Action Cards */}
          <Grid item xs={12}>
            <Grid container spacing={2} sx={{ mb: 3 }}>
              <Grid item xs={12} sm={6}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': { transform: 'translateY(-2px)' },
                  }}
                  onClick={handleViewWeeklyReport}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={2}>
                      <CalendarTodayIcon color="primary" />
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {t('home.quickActions.weeklyReport')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {t('home.quickActions.weeklyReportDesc')}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
              
              <Grid item xs={12} sm={6}>
                <Card
                  sx={{
                    cursor: 'pointer',
                    transition: 'transform 0.2s',
                    '&:hover': { transform: 'translateY(-2px)' },
                  }}
                  onClick={handleViewAllListings}
                >
                  <CardContent>
                    <Box display="flex" alignItems="center" gap={2}>
                      <HomeIcon color="primary" />
                      <Box>
                        <Typography variant="h6" sx={{ fontWeight: 600 }}>
                          {t('home.quickActions.allListings')}
                        </Typography>
                        <Typography variant="body2" color="text.secondary">
                          {t('home.quickActions.allListingsDesc')}
                        </Typography>
                      </Box>
                    </Box>
                  </CardContent>
                </Card>
              </Grid>
            </Grid>
          </Grid>

          {/* Properties Grid */}
          <Grid item xs={12}>
            {propertiesLoading ? (
              <LoadingSpinner message={t('common.loadingProperties')} />
            ) : properties.length === 0 ? (
              <EmptyState
                type="search"
                title={t('home.emptyState.title')}
                description={t('home.emptyState.description')}
                action={{
                  label: t('home.emptyState.action'),
                  onClick: handleClearFilters,
                }}
              />
            ) : (
              <PropertyGrid
                properties={properties}
                loading={propertiesLoading}
                error={propertiesError?.message || null}
                onPropertyClick={handlePropertyClick}
                emptyMessage={t('home.noResults')}
              />
            )}
          </Grid>

          {/* Load More Button */}
          {properties.length > 0 && properties.length >= (filters.pageSize || 12) && (
            <Grid item xs={12}>
              <Box textAlign="center" sx={{ mt: 4 }}>
                <Button
                  variant="outlined"
                  size="large"
                  onClick={() => {
                    setFilters(prev => ({
                      ...prev,
                      pageSize: (prev.pageSize || 12) + 12
                    }));
                    logger.userInteraction('Home', 'load_more');
                  }}
                  disabled={propertiesLoading}
                >
                  {t('home.loadMore')}
                </Button>
              </Box>
            </Grid>
          )}
        </Grid>
      </Container>
    </Box>
  );
};

export default Home;
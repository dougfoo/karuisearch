/**
 * Weekly Report Page Component
 * Displays weekly property market summary with statistics and new listings
 * Features Japanese business report aesthetics with charts and insights
 */

import React, { useState } from 'react';
import {
  Box,
  Container,
  Typography,
  Grid,
  Card,
  CardContent,
  Button,
  IconButton,
  Chip,
  Divider,
  useTheme,
  useMediaQuery,
  Paper,
  Table,
  TableBody,
  TableCell,
  TableContainer,
  TableHead,
  TableRow,
} from '@mui/material';
import {
  CalendarTodayIcon,
  TrendingUpIcon,
  TrendingDownIcon,
  HomeIcon,
  LocationOnIcon,
  ArrowBackIcon,
  ArrowForwardIcon,
  ShareIcon,
  PictureAsPdfIcon,
  InsightsIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate } from 'react-router-dom';

import { useWeeklyReport } from '@services/queries';
import PropertyGrid from '@components/property/PropertyGrid';
import { LoadingSpinner, EmptyState, ErrorState } from '@components/ui/LoadingStates';
import { formatPrice, formatDate, formatRelativeDate } from '@utils/formatting';
import { logger } from '@utils/logger';

const WeeklyReport: React.FC = () => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const locale = i18n.language;
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  const [weekOffset, setWeekOffset] = useState(0);

  // Data query
  const {
    data: weeklyReport,
    isLoading,
    error,
    refetch,
  } = useWeeklyReport(weekOffset);

  // Navigation handlers
  const handlePreviousWeek = () => {
    setWeekOffset(prev => prev + 1);
    logger.userInteraction('WeeklyReport', 'previous_week', {
      newWeekOffset: weekOffset + 1
    });
  };

  const handleNextWeek = () => {
    if (weekOffset > 0) {
      setWeekOffset(prev => prev - 1);
      logger.userInteraction('WeeklyReport', 'next_week', {
        newWeekOffset: weekOffset - 1
      });
    }
  };

  const handlePropertyClick = (property: any) => {
    navigate(`/property/${property.id}`);
    logger.userInteraction('WeeklyReport', 'property_click', {
      propertyId: property.id
    });
  };

  const handleShareReport = () => {
    logger.userInteraction('WeeklyReport', 'share_report', {
      weekOffset
    });
    // TODO: Implement share functionality
  };

  const handleExportPdf = () => {
    logger.userInteraction('WeeklyReport', 'export_pdf', {
      weekOffset
    });
    // TODO: Implement PDF export
  };

  // Log page view
  React.useEffect(() => {
    logger.pageView('WeeklyReport', {
      weekOffset,
      reportDate: weeklyReport?.weekStartDate
    });
  }, [weekOffset, weeklyReport]);

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

  // Handle loading state
  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LoadingSpinner message={t('loading.weeklyReport')} />
      </Container>
    );
  }

  if (!weeklyReport) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <EmptyState
          title={t('weeklyReport.noData')}
          description={t('weeklyReport.noDataDesc')}
        />
      </Container>
    );
  }

  const { newListings, summary, weekStartDate, weekEndDate } = weeklyReport;
  const weekStart = new Date(weekStartDate);
  const weekEnd = new Date(weekEndDate);

  return (
    <Box data-testid="weekly-report-page">
      {/* Header Section */}
      <Box
        sx={{
          background: `linear-gradient(135deg, ${theme.palette.primary.main} 0%, ${theme.palette.primary.dark} 100%)`,
          color: 'white',
          py: { xs: 3, md: 4 },
          mb: 4,
        }}
      >
        <Container maxWidth="lg">
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography
              variant={isMobile ? 'h5' : 'h4'}
              component="h1"
              sx={{ fontWeight: 700 }}
            >
              {t('weeklyReport.title')}
            </Typography>
            
            <Box display="flex" gap={1}>
              <IconButton
                color="inherit"
                onClick={handleShareReport}
                aria-label={t('common.share')}
              >
                <ShareIcon />
              </IconButton>
              <IconButton
                color="inherit"
                onClick={handleExportPdf}
                aria-label={t('weeklyReport.exportPdf')}
              >
                <PictureAsPdfIcon />
              </IconButton>
            </Box>
          </Box>

          {/* Week Navigation */}
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
            <Button
              variant="outlined"
              startIcon={<ArrowBackIcon />}
              onClick={handlePreviousWeek}
              sx={{ 
                color: 'white', 
                borderColor: 'rgba(255,255,255,0.3)',
                '&:hover': { borderColor: 'white' }
              }}
            >
              {t('weeklyReport.previousWeek')}
            </Button>

            <Box textAlign="center">
              <Typography variant="h6" sx={{ fontWeight: 600 }}>
                {formatDate(weekStartDate, locale)} - {formatDate(weekEndDate, locale)}
              </Typography>
              <Typography variant="body2" sx={{ opacity: 0.8 }}>
                {weekOffset === 0 
                  ? t('weeklyReport.thisWeek') 
                  : t('weeklyReport.weeksAgo', { count: weekOffset })
                }
              </Typography>
            </Box>

            <Button
              variant="outlined"
              endIcon={<ArrowForwardIcon />}
              onClick={handleNextWeek}
              disabled={weekOffset === 0}
              sx={{ 
                color: 'white', 
                borderColor: 'rgba(255,255,255,0.3)',
                '&:hover': { borderColor: 'white' },
                '&:disabled': { 
                  color: 'rgba(255,255,255,0.5)',
                  borderColor: 'rgba(255,255,255,0.2)'
                }
              }}
            >
              {t('weeklyReport.nextWeek')}
            </Button>
          </Box>
        </Container>
      </Box>

      <Container maxWidth="lg">
        {/* Summary Statistics */}
        <Grid container spacing={3} sx={{ mb: 4 }}>
          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <HomeIcon sx={{ fontSize: 40, color: theme.palette.primary.main, mb: 1 }} />
                <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.primary.main }}>
                  {summary.totalListings}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('weeklyReport.stats.newListings')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <TrendingUpIcon sx={{ fontSize: 40, color: theme.palette.success.main, mb: 1 }} />
                <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.success.main }}>
                  {formatPrice(summary.averagePrice, locale)}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('weeklyReport.stats.averagePrice')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <LocationOnIcon sx={{ fontSize: 40, color: theme.palette.info.main, mb: 1 }} />
                <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.info.main }}>
                  {Object.keys(summary.propertyTypes).length}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('weeklyReport.stats.propertyTypes')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>

          <Grid item xs={12} sm={6} md={3}>
            <Card sx={{ height: '100%' }}>
              <CardContent sx={{ textAlign: 'center' }}>
                <InsightsIcon sx={{ fontSize: 40, color: theme.palette.warning.main, mb: 1 }} />
                <Typography variant="h4" sx={{ fontWeight: 700, color: theme.palette.warning.main }}>
                  {Math.round((summary.totalListings / 7) * 10) / 10}
                </Typography>
                <Typography variant="body2" color="text.secondary">
                  {t('weeklyReport.stats.dailyAverage')}
                </Typography>
              </CardContent>
            </Card>
          </Grid>
        </Grid>

        {/* Property Type Distribution */}
        {Object.keys(summary.propertyTypes).length > 0 && (
          <Card sx={{ mb: 4 }}>
            <CardContent>
              <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                {t('weeklyReport.propertyTypeDistribution')}
              </Typography>
              <Grid container spacing={2}>
                {Object.entries(summary.propertyTypes).map(([type, count]) => (
                  <Grid item xs={6} sm={4} md={3} key={type}>
                    <Box
                      sx={{
                        p: 2,
                        border: `1px solid ${theme.palette.divider}`,
                        borderRadius: 1,
                        textAlign: 'center',
                      }}
                    >
                      <Typography variant="h5" sx={{ fontWeight: 600, color: theme.palette.primary.main }}>
                        {count}
                      </Typography>
                      <Typography variant="body2" color="text.secondary">
                        {t(`propertyTypes.${type}`, type)}
                      </Typography>
                    </Box>
                  </Grid>
                ))}
              </Grid>
            </CardContent>
          </Card>
        )}

        {/* Price Range Distribution */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              {t('weeklyReport.priceDistribution')}
            </Typography>
            <TableContainer component={Paper} variant="outlined">
              <Table size="small">
                <TableHead>
                  <TableRow>
                    <TableCell>{t('weeklyReport.priceRange')}</TableCell>
                    <TableCell align="right">{t('weeklyReport.properties')}</TableCell>
                    <TableCell align="right">{t('weeklyReport.percentage')}</TableCell>
                  </TableRow>
                </TableHead>
                <TableBody>
                  {Object.entries(summary.priceRanges).map(([range, count]) => {
                    const percentage = summary.totalListings > 0 
                      ? Math.round((count / summary.totalListings) * 100) 
                      : 0;
                    
                    return (
                      <TableRow key={range}>
                        <TableCell>
                          {t(`weeklyReport.priceRanges.${range}`, range)}
                        </TableCell>
                        <TableCell align="right">{count}</TableCell>
                        <TableCell align="right">{percentage}%</TableCell>
                      </TableRow>
                    );
                  })}
                </TableBody>
              </Table>
            </TableContainer>
          </CardContent>
        </Card>

        {/* New Listings Section */}
        <Box sx={{ mb: 4 }}>
          <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
            <Typography variant="h5" sx={{ fontWeight: 600 }}>
              {t('weeklyReport.newListings')} ({newListings.length})
            </Typography>
            
            {newListings.length > 0 && (
              <Button
                variant="outlined"
                onClick={() => navigate('/listings')}
              >
                {t('weeklyReport.viewAllListings')}
              </Button>
            )}
          </Box>

          {newListings.length > 0 ? (
            <PropertyGrid
              properties={newListings}
              loading={isLoading}
              error={error?.message || null}
              onPropertyClick={handlePropertyClick}
              emptyMessage={t('weeklyReport.noNewListings')}
            />
          ) : (
            <EmptyState
              type="search"
              title={t('weeklyReport.noNewListings')}
              description={t('weeklyReport.noNewListingsDesc')}
            />
          )}
        </Box>

        {/* Weekly Insights */}
        <Card sx={{ mb: 4 }}>
          <CardContent>
            <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
              {t('weeklyReport.insights')}
            </Typography>
            <Box sx={{ mt: 2 }}>
              {summary.totalListings > 0 ? (
                <Box>
                  <Typography variant="body1" paragraph>
                    {t('weeklyReport.insightSummary', {
                      count: summary.totalListings,
                      averagePrice: formatPrice(summary.averagePrice, locale),
                      topType: Object.entries(summary.propertyTypes).sort(([,a], [,b]) => b - a)[0]?.[0] || ''
                    })}
                  </Typography>
                  
                  {summary.totalListings > 10 && (
                    <Chip
                      icon={<TrendingUpIcon />}
                      label={t('weeklyReport.highActivity')}
                      color="success"
                      variant="outlined"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  )}
                  
                  {summary.averagePrice > 80000000 && (
                    <Chip
                      icon={<TrendingUpIcon />}
                      label={t('weeklyReport.premiumMarket')}
                      color="primary"
                      variant="outlined"
                      sx={{ mr: 1, mb: 1 }}
                    />
                  )}
                </Box>
              ) : (
                <Typography variant="body1" color="text.secondary">
                  {t('weeklyReport.noInsights')}
                </Typography>
              )}
            </Box>
          </CardContent>
        </Card>
      </Container>
    </Box>
  );
};

export default WeeklyReport;
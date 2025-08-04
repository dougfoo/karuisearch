/**
 * Property Detail Page Component
 * Comprehensive property view with images, details, and contact options
 * Features Japanese real estate detail page aesthetics and functionality
 */

import React, { useState, useEffect } from 'react';
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
  Paper,
  List,
  ListItem,
  ListItemIcon,
  ListItemText,
  ImageList,
  ImageListItem,
  Dialog,
  DialogContent,
  useTheme,
  useMediaQuery,
  Breadcrumbs,
  Link,
  Fab,
  Skeleton,
} from '@mui/material';
import {
  ArrowBack as ArrowBackIcon,
  Favorite as FavoriteIcon,
  FavoriteBorder as FavoriteBorderIcon,
  Share as ShareIcon,
  Print as PrintIcon,
  LocationOn as LocationOnIcon,
  Home as HomeIcon,
  CalendarToday as CalendarTodayIcon,
  SquareFoot as SquareFootIcon,
  TrendingUp as TrendingUpIcon,
  TrendingDown as TrendingDownIcon,
  Phone as PhoneIcon,
  Email as EmailIcon,
  Launch as LaunchIcon,
  Close as CloseIcon,
  NavigateNext as NavigateNextIcon,
  NavigateBefore as NavigateBeforeIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';
import { useNavigate, useParams } from 'react-router-dom';

import { useProperty, useToggleFavorite } from '@services/queries';
import { LoadingSpinner, EmptyState, ErrorState } from '@components/ui/LoadingStates';
import {
  formatPrice,
  formatDate,
  formatRelativeDate,
  formatSizeInfo,
  formatBuildingAge,
  formatPropertyType,
  formatLocation,
  formatPriceChange,
} from '@utils/formatting';
import { logger } from '@utils/logger';

const PropertyDetail: React.FC = () => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const navigate = useNavigate();
  const { id } = useParams<{ id: string }>();
  const locale = i18n.language;
  const isMobile = useMediaQuery(theme.breakpoints.down('md'));

  // UI State
  const [selectedImageIndex, setSelectedImageIndex] = useState(0);
  const [imageDialogOpen, setImageDialogOpen] = useState(false);
  const [isFavorite, setIsFavorite] = useState(false);

  // Data queries
  const {
    data: property,
    isLoading,
    error,
    refetch,
  } = useProperty(id || '');

  const toggleFavoriteMutation = useToggleFavorite();

  // Get source name from URL
  const getSourceName = (sourceUrl: string) => {
    if (sourceUrl.includes('mitsuinomori.co.jp')) return '三井の森';
    if (sourceUrl.includes('royal-resort.co.jp')) return 'Royal Resort';
    if (sourceUrl.includes('besso-navi.com')) return 'Besso Navi';
    return t('property.source');
  };

  // Event handlers
  const handleBack = () => {
    navigate(-1);
    logger.userInteraction('PropertyDetail', 'back_navigation', {
      propertyId: id
    });
  };

  const handleFavoriteToggle = async () => {
    if (!property) return;
    
    try {
      const newFavoriteStatus = await toggleFavoriteMutation.mutateAsync(property.id);
      setIsFavorite(newFavoriteStatus);
      logger.userInteraction('PropertyDetail', 'favorite_toggle', {
        propertyId: property.id,
        isFavorite: newFavoriteStatus
      });
    } catch (error) {
      logger.error('Favorite toggle failed', {
        component: 'PropertyDetail',
        action: 'favorite_toggle_error',
        error: error.message,
        metadata: { propertyId: property.id }
      });
    }
  };

  const handleShare = () => {
    if (navigator.share) {
      navigator.share({
        title: property?.title,
        text: `${property?.title} - ${formatPrice(property?.price || '', locale)}`,
        url: window.location.href,
      });
    } else {
      // Fallback to clipboard
      navigator.clipboard.writeText(window.location.href);
    }
    logger.userInteraction('PropertyDetail', 'share', {
      propertyId: id,
      method: navigator.share ? 'native' : 'clipboard'
    });
  };

  const handlePrint = () => {
    window.print();
    logger.userInteraction('PropertyDetail', 'print', {
      propertyId: id
    });
  };

  const handleImageClick = (index: number) => {
    setSelectedImageIndex(index);
    setImageDialogOpen(true);
    logger.userInteraction('PropertyDetail', 'image_view', {
      propertyId: id,
      imageIndex: index
    });
  };

  const handleExternalLink = () => {
    if (property?.source_url) {
      window.open(property.source_url, '_blank', 'noopener,noreferrer');
      logger.userInteraction('PropertyDetail', 'external_link', {
        propertyId: id,
        sourceUrl: property.source_url
      });
    }
  };

  const handleContactInquiry = (method: 'phone' | 'email') => {
    logger.userInteraction('PropertyDetail', 'contact_inquiry', {
      propertyId: id,
      method
    });
    // TODO: Implement contact functionality
  };

  // Log page view
  useEffect(() => {
    if (property) {
      logger.pageView('PropertyDetail', {
        propertyId: property.id,
        propertyType: property.property_type,
        price: property.price,
        location: property.location
      });
    }
  }, [property]);

  // Handle loading state
  if (isLoading) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <LoadingSpinner message={t('loading.details')} />
      </Container>
    );
  }

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

  // Handle not found
  if (!property) {
    return (
      <Container maxWidth="lg" sx={{ py: 4 }}>
        <EmptyState
          title={t('propertyDetail.notFound')}
          description={t('propertyDetail.notFoundDesc')}
          action={{
            label: t('propertyDetail.backToListings'),
            onClick: () => navigate('/listings'),
          }}
        />
      </Container>
    );
  }

  const images = property.image_urls || [];
  const hasImages = images.length > 0;

  return (
    <Box data-testid="property-detail-page">
      {/* Mobile Back Button */}
      {isMobile && (
        <Fab
          color="primary"
          aria-label={t('common.back')}
          onClick={handleBack}
          sx={{
            position: 'fixed',
            top: 16,
            left: 16,
            zIndex: theme.zIndex.speedDial,
          }}
        >
          <ArrowBackIcon />
        </Fab>
      )}

      <Container maxWidth="lg" sx={{ py: { xs: 2, md: 4 } }}>
        {/* Breadcrumbs */}
        {!isMobile && (
          <Breadcrumbs
            separator={<NavigateNextIcon fontSize="small" />}
            sx={{ mb: 3 }}
          >
            <Link
              color="inherit"
              href="/"
              onClick={(e) => {
                e.preventDefault();
                navigate('/');
              }}
              sx={{ cursor: 'pointer' }}
            >
              {t('navigation.home')}
            </Link>
            <Link
              color="inherit"
              href="/listings"
              onClick={(e) => {
                e.preventDefault();
                navigate('/listings');
              }}
              sx={{ cursor: 'pointer' }}
            >
              {t('navigation.allListings')}
            </Link>
            <Typography color="text.primary">
              {property.title}
            </Typography>
          </Breadcrumbs>
        )}

        {/* Header Actions */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={3}>
          {!isMobile && (
            <Button
              startIcon={<ArrowBackIcon />}
              onClick={handleBack}
              variant="outlined"
            >
              {t('common.back')}
            </Button>
          )}
          
          <Box display="flex" gap={1}>
            <IconButton
              onClick={handleFavoriteToggle}
              color={isFavorite ? 'error' : 'default'}
              aria-label={t('common.favorite')}
            >
              {isFavorite ? <FavoriteIcon /> : <FavoriteBorderIcon />}
            </IconButton>
            
            <IconButton
              onClick={handleShare}
              aria-label={t('common.share')}
            >
              <ShareIcon />
            </IconButton>
            
            <IconButton
              onClick={handlePrint}
              aria-label={t('propertyDetail.print')}
            >
              <PrintIcon />
            </IconButton>
          </Box>
        </Box>

        <Grid container spacing={4}>
          {/* Left Column - Images and Details */}
          <Grid item xs={12} md={8}>
            {/* Property Images */}
            {hasImages ? (
              <Card sx={{ mb: 3 }}>
                <Box sx={{ position: 'relative' }}>
                  {/* Main Image */}
                  <Box
                    component="img"
                    src={images[selectedImageIndex]}
                    alt={property.title}
                    sx={{
                      width: '100%',
                      height: { xs: 250, md: 400 },
                      objectFit: 'cover',
                      cursor: 'pointer',
                    }}
                    onClick={() => handleImageClick(selectedImageIndex)}
                  />
                  
                  {/* Image Counter */}
                  {images.length > 1 && (
                    <Chip
                      label={`${selectedImageIndex + 1} / ${images.length}`}
                      sx={{
                        position: 'absolute',
                        top: 16,
                        right: 16,
                        backgroundColor: 'rgba(0,0,0,0.7)',
                        color: 'white',
                      }}
                    />
                  )}

                  {/* Navigation Arrows */}
                  {images.length > 1 && (
                    <>
                      <IconButton
                        sx={{
                          position: 'absolute',
                          left: 16,
                          top: '50%',
                          transform: 'translateY(-50%)',
                          backgroundColor: 'rgba(0,0,0,0.5)',
                          color: 'white',
                          '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' },
                        }}
                        onClick={() => setSelectedImageIndex(
                          selectedImageIndex > 0 ? selectedImageIndex - 1 : images.length - 1
                        )}
                      >
                        <NavigateBeforeIcon />
                      </IconButton>
                      
                      <IconButton
                        sx={{
                          position: 'absolute',
                          right: 16,
                          top: '50%',
                          transform: 'translateY(-50%)',
                          backgroundColor: 'rgba(0,0,0,0.5)',
                          color: 'white',
                          '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' },
                        }}
                        onClick={() => setSelectedImageIndex(
                          selectedImageIndex < images.length - 1 ? selectedImageIndex + 1 : 0
                        )}
                      >
                        <NavigateNextIcon />
                      </IconButton>
                    </>
                  )}
                </Box>

                {/* Thumbnail Strip */}
                {images.length > 1 && (
                  <Box sx={{ p: 2 }}>
                    <ImageList cols={Math.min(images.length, isMobile ? 4 : 6)} rowHeight={80}>
                      {images.map((image, index) => (
                        <ImageListItem
                          key={index}
                          sx={{
                            cursor: 'pointer',
                            border: selectedImageIndex === index 
                              ? `2px solid ${theme.palette.primary.main}` 
                              : '2px solid transparent',
                            borderRadius: 1,
                            overflow: 'hidden',
                          }}
                          onClick={() => setSelectedImageIndex(index)}
                        >
                          <img
                            src={image}
                            alt={`${property.title} ${index + 1}`}
                            style={{ objectFit: 'cover', width: '100%', height: '100%' }}
                          />
                        </ImageListItem>
                      ))}
                    </ImageList>
                  </Box>
                )}
              </Card>
            ) : (
              <Card sx={{ mb: 3 }}>
                <Box
                  sx={{
                    height: { xs: 250, md: 400 },
                    display: 'flex',
                    alignItems: 'center',
                    justifyContent: 'center',
                    backgroundColor: theme.palette.grey[100],
                    color: theme.palette.grey[500],
                  }}
                >
                  <HomeIcon sx={{ fontSize: 64, mr: 2 }} />
                  <Typography variant="h6">
                    {t('common.noImage')}
                  </Typography>
                </Box>
              </Card>
            )}

            {/* Property Details */}
            <Card>
              <CardContent>
                <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                  {t('propertyDetail.details')}
                </Typography>
                
                <List disablePadding>
                  {/* Property Type */}
                  {property.property_type && (
                    <ListItem disablePadding sx={{ py: 1 }}>
                      <ListItemIcon>
                        <HomeIcon color="action" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('property.type')}
                        secondary={formatPropertyType(property.property_type, locale)}
                      />
                    </ListItem>
                  )}

                  {/* Location */}
                  <ListItem disablePadding sx={{ py: 1 }}>
                    <ListItemIcon>
                      <LocationOnIcon color="action" />
                    </ListItemIcon>
                    <ListItemText
                      primary={t('property.location')}
                      secondary={formatLocation(property.location, locale)}
                    />
                  </ListItem>

                  {/* Size Info */}
                  {property.size_info && (
                    <ListItem disablePadding sx={{ py: 1 }}>
                      <ListItemIcon>
                        <SquareFootIcon color="action" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('property.size')}
                        secondary={formatSizeInfo(property.size_info, locale)}
                      />
                    </ListItem>
                  )}

                  {/* Building Age */}
                  {property.building_age && (
                    <ListItem disablePadding sx={{ py: 1 }}>
                      <ListItemIcon>
                        <CalendarTodayIcon color="action" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('property.age')}
                        secondary={formatBuildingAge(property.building_age, locale)}
                      />
                    </ListItem>
                  )}

                  {/* Rooms */}
                  {property.rooms && (
                    <ListItem disablePadding sx={{ py: 1 }}>
                      <ListItemIcon>
                        <HomeIcon color="action" />
                      </ListItemIcon>
                      <ListItemText
                        primary={t('property.rooms')}
                        secondary={property.rooms}
                      />
                    </ListItem>
                  )}
                </List>
              </CardContent>
            </Card>

            {/* Description */}
            {property.description && (
              <Card sx={{ mt: 3 }}>
                <CardContent>
                  <Typography variant="h6" gutterBottom sx={{ fontWeight: 600 }}>
                    {t('property.description')}
                  </Typography>
                  <Typography variant="body1" sx={{ lineHeight: 1.7 }}>
                    {property.description}
                  </Typography>
                </CardContent>
              </Card>
            )}
          </Grid>

          {/* Right Column - Sidebar */}
          <Grid item xs={12} md={4}>
            {/* Price Card */}
            <Card sx={{ mb: 3, position: 'sticky', top: 24 }}>
              <CardContent>
                {/* Property Type Badge */}
                {property.property_type && (
                  <Box sx={{ mb: 2 }}>
                    <Chip
                      label={formatPropertyType(property.property_type, locale)}
                      color="primary"
                      variant="outlined"
                    />
                    {property.is_new && (
                      <Chip
                        label={t('property.newListing')}
                        color="error"
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    )}
                    {property.is_featured && (
                      <Chip
                        label={t('property.featured')}
                        color="warning"
                        size="small"
                        sx={{ ml: 1 }}
                      />
                    )}
                  </Box>
                )}

                {/* Title */}
                <Typography variant="h5" gutterBottom sx={{ fontWeight: 700 }}>
                  {property.title}
                </Typography>

                {/* Price */}
                <Typography
                  variant="h4"
                  color="primary"
                  gutterBottom
                  sx={{ fontWeight: 700 }}
                >
                  {formatPrice(property.price, locale)}
                </Typography>

                {/* Price Change */}
                {property.price_change && property.price_change.direction !== 'none' && (
                  <Box display="flex" alignItems="center" gap={1} sx={{ mb: 2 }}>
                    {property.price_change.direction === 'increase' ? (
                      <TrendingUpIcon color="success" />
                    ) : (
                      <TrendingDownIcon color="error" />
                    )}
                    <Typography
                      variant="body2"
                      color={property.price_change.direction === 'increase' ? 'success.main' : 'error.main'}
                    >
                      {formatPriceChange(property.price_change, locale)}
                    </Typography>
                  </Box>
                )}

                <Divider sx={{ my: 2 }} />

                {/* Date Information */}
                <Box sx={{ mb: 2 }}>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {t('property.dateAdded')}: {formatRelativeDate(property.date_first_seen, locale)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary" gutterBottom>
                    {t('property.lastUpdated')}: {formatDate(property.scraped_date, locale)}
                  </Typography>
                  <Typography variant="body2" color="text.secondary">
                    {t('property.source')}: {getSourceName(property.source_url)}
                  </Typography>
                </Box>

                <Divider sx={{ my: 2 }} />

                {/* Action Buttons */}
                <Box sx={{ display: 'flex', flexDirection: 'column', gap: 2 }}>
                  <Button
                    variant="contained"
                    size="large"
                    startIcon={<PhoneIcon />}
                    onClick={() => handleContactInquiry('phone')}
                    fullWidth
                  >
                    {t('propertyDetail.contactPhone')}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    size="large"
                    startIcon={<EmailIcon />}
                    onClick={() => handleContactInquiry('email')}
                    fullWidth
                  >
                    {t('propertyDetail.contactEmail')}
                  </Button>
                  
                  <Button
                    variant="outlined"
                    startIcon={<LaunchIcon />}
                    onClick={handleExternalLink}
                    fullWidth
                  >
                    {t('common.viewOriginal')}
                  </Button>
                </Box>
              </CardContent>
            </Card>
          </Grid>
        </Grid>
      </Container>

      {/* Image Gallery Dialog */}
      <Dialog
        open={imageDialogOpen}
        onClose={() => setImageDialogOpen(false)}
        maxWidth="lg"
        fullWidth
        PaperProps={{
          sx: { backgroundColor: 'black' }
        }}
      >
        <DialogContent sx={{ p: 0, position: 'relative' }}>
          <IconButton
            onClick={() => setImageDialogOpen(false)}
            sx={{
              position: 'absolute',
              top: 16,
              right: 16,
              color: 'white',
              backgroundColor: 'rgba(0,0,0,0.5)',
              '&:hover': { backgroundColor: 'rgba(0,0,0,0.7)' },
              zIndex: 1,
            }}
          >
            <CloseIcon />
          </IconButton>
          
          {hasImages && (
            <Box
              component="img"
              src={images[selectedImageIndex]}
              alt={property.title}
              sx={{
                width: '100%',
                height: 'auto',
                maxHeight: '80vh',
                objectFit: 'contain',
              }}
            />
          )}
        </DialogContent>
      </Dialog>
    </Box>
  );
};

export default PropertyDetail;
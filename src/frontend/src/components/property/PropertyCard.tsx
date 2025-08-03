/**
 * PropertyCard Component
 * Core property display component with Japanese design aesthetics
 * Supports both compact and full layouts
 */

import React from 'react';
import {
  Card,
  CardContent,
  CardMedia,
  CardActions,
  Typography,
  Button,
  Chip,
  Box,
  IconButton,
  Skeleton,
  useTheme,
} from '@mui/material';
import {
  FavoriteIcon,
  ShareIcon,
  LocationOnIcon,
  HomeIcon,
  CalendarTodayIcon,
  TrendingUpIcon,
  TrendingDownIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { Property, PropertyCardProps } from '@types/property';
import {
  formatPrice,
  formatSizeInfo,
  formatBuildingAge,
  formatPropertyType,
  formatLocation,
  formatRelativeDate,
  formatPriceChange,
  truncateText,
  cleanImageUrl,
  getEmptyText,
} from '@utils/formatting';
import { logger } from '@utils/logger';

const PropertyCard: React.FC<PropertyCardProps> = ({
  property,
  onClick,
  showPriceChange = true,
  compact = false,
}) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const locale = i18n.language;

  // Handle card click
  const handleCardClick = () => {
    if (onClick) {
      logger.propertyViewed(property.id, 'card_click');
      onClick(property);
    }
  };

  // Handle external link click
  const handleExternalClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    logger.userInteraction('PropertyCard', 'external_link_click', {
      propertyId: property.id,
      sourceUrl: property.source_url
    });
    window.open(property.source_url, '_blank', 'noopener,noreferrer');
  };

  // Handle favorite toggle
  const handleFavoriteClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    logger.userInteraction('PropertyCard', 'favorite_toggle', {
      propertyId: property.id
    });
    // TODO: Implement favorite functionality
  };

  // Handle share click
  const handleShareClick = (e: React.MouseEvent) => {
    e.stopPropagation();
    logger.userInteraction('PropertyCard', 'share_click', {
      propertyId: property.id
    });
    // TODO: Implement share functionality
  };

  // Get primary image with fallback
  const primaryImage = property.image_urls && property.image_urls.length > 0
    ? cleanImageUrl(property.image_urls[0])
    : '';

  // Get property type color
  const getPropertyTypeColor = (type: string) => {
    const colorMap: Record<string, string> = {
      '一戸建て': theme.palette.primary.main,
      'マンション': theme.palette.info.main,
      '土地': theme.palette.warning.main,
      '別荘': theme.palette.secondary.main,
    };
    return colorMap[type] || theme.palette.grey[500];
  };

  // Get price change icon and color
  const getPriceChangeDisplay = () => {
    if (!property.price_change || property.price_change.direction === 'none') {
      return null;
    }

    const { direction } = property.price_change;
    const isIncrease = direction === 'increase';
    const color = isIncrease ? theme.palette.success.main : theme.palette.error.main;
    const Icon = isIncrease ? TrendingUpIcon : TrendingDownIcon;

    return (
      <Box display="flex" alignItems="center" gap={0.5} color={color}>
        <Icon fontSize="small" />
        <Typography variant="caption" color="inherit">
          {formatPriceChange(property.price_change, locale)}
        </Typography>
      </Box>
    );
  };

  return (
    <Card
      sx={{
        height: compact ? 200 : 400,
        display: 'flex',
        flexDirection: 'column',
        cursor: onClick ? 'pointer' : 'default',
        transition: 'all 0.3s ease-in-out',
        position: 'relative',
        '&:hover': onClick ? {
          transform: 'translateY(-2px)',
          boxShadow: theme.shadows[8],
        } : {},
      }}
      onClick={handleCardClick}
      data-testid={`property-card-${property.id}`}
    >
      {/* Property Image */}
      <CardMedia
        component="img"
        height={compact ? 120 : 200}
        image={primaryImage || `https://via.placeholder.com/400x300/cccccc/666666?text=${encodeURIComponent(t('common.noImage'))}`}
        alt={property.title}
        sx={{
          objectFit: 'cover',
          backgroundColor: theme.palette.grey[200],
        }}
        onError={(e) => {
          logger.warn('Image load error', {
            component: 'PropertyCard',
            action: 'image_error',
            metadata: { propertyId: property.id, imageUrl: primaryImage }
          });
          // Set fallback image
          (e.target as HTMLImageElement).src = `https://via.placeholder.com/400x300/cccccc/666666?text=${encodeURIComponent(t('common.noImage'))}`;
        }}
      />

      {/* Property Type Badge */}
      {property.property_type && (
        <Chip
          label={formatPropertyType(property.property_type, locale)}
          size="small"
          sx={{
            position: 'absolute',
            top: 8,
            right: 8,
            backgroundColor: getPropertyTypeColor(property.property_type),
            color: 'white',
            fontWeight: 500,
          }}
        />
      )}

      {/* New Listing Badge */}
      {property.is_new && (
        <Chip
          label={t('property.newListing')}
          size="small"
          color="error"
          sx={{
            position: 'absolute',
            top: 8,
            left: 8,
            fontWeight: 500,
          }}
        />
      )}

      {/* Card Content */}
      <CardContent sx={{ flexGrow: 1, padding: compact ? 1 : 2 }}>
        {/* Property Title */}
        <Typography
          variant={compact ? "subtitle2" : "h6"}
          component="h3"
          gutterBottom
          sx={{
            fontWeight: 500,
            overflow: 'hidden',
            textOverflow: 'ellipsis',
            display: '-webkit-box',
            WebkitLineClamp: compact ? 1 : 2,
            WebkitBoxOrient: 'vertical',
            lineHeight: 1.4,
          }}
        >
          {truncateText(property.title, compact ? 40 : 80)}
        </Typography>

        {/* Price */}
        <Typography
          variant={compact ? "h6" : "h5"}
          color="primary"
          gutterBottom
          sx={{ fontWeight: 600 }}
        >
          {formatPrice(property.price, locale)}
        </Typography>

        {/* Price Change */}
        {showPriceChange && property.price_change && (
          <Box sx={{ mb: 1 }}>
            {getPriceChangeDisplay()}
          </Box>
        )}

        {/* Location */}
        <Box display="flex" alignItems="center" gap={0.5} mb={1}>
          <LocationOnIcon fontSize="small" color="action" />
          <Typography variant="body2" color="text.secondary" noWrap>
            {formatLocation(property.location, locale)}
          </Typography>
        </Box>

        {/* Size Info */}
        {property.size_info && (
          <Box display="flex" alignItems="center" gap={0.5} mb={1}>
            <HomeIcon fontSize="small" color="action" />
            <Typography variant="body2" color="text.secondary">
              {formatSizeInfo(property.size_info, locale)}
            </Typography>
          </Box>
        )}

        {/* Building Age and Rooms */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={1}>
          {property.building_age && (
            <Typography variant="body2" color="text.secondary">
              {formatBuildingAge(property.building_age, locale)}
            </Typography>
          )}
          {property.rooms && (
            <Typography variant="body2" color="text.secondary">
              {property.rooms}
            </Typography>
          )}
        </Box>

        {/* Date Added */}
        {!compact && (
          <Box display="flex" alignItems="center" gap={0.5} mt={1}>
            <CalendarTodayIcon fontSize="small" color="action" />
            <Typography variant="caption" color="text.secondary">
              {t('property.dateAdded')}: {formatRelativeDate(property.date_first_seen, locale)}
            </Typography>
          </Box>
        )}
      </CardContent>

      {/* Card Actions */}
      <CardActions sx={{ padding: compact ? 1 : 2, paddingTop: 0 }}>
        <Button
          size="small"
          variant="outlined"
          onClick={handleExternalClick}
          sx={{ flexGrow: 1 }}
        >
          {t('common.viewOriginal')}
        </Button>
        
        <IconButton
          size="small"
          onClick={handleFavoriteClick}
          color="default"
          aria-label={t('common.favorite')}
        >
          <FavoriteIcon />
        </IconButton>
        
        <IconButton
          size="small"
          onClick={handleShareClick}
          color="default"
          aria-label={t('common.share')}
        >
          <ShareIcon />
        </IconButton>
      </CardActions>
    </Card>
  );
};

// Loading skeleton component
export const PropertyCardSkeleton: React.FC<{ compact?: boolean }> = ({ compact = false }) => (
  <Card sx={{ height: compact ? 200 : 400, display: 'flex', flexDirection: 'column' }}>
    <Skeleton variant="rectangular" height={compact ? 120 : 200} />
    <CardContent sx={{ flexGrow: 1 }}>
      <Skeleton variant="text" width="60%" height={compact ? 20 : 24} />
      <Skeleton variant="text" width="40%" height={compact ? 28 : 32} sx={{ mb: 1 }} />
      <Skeleton variant="text" width="80%" height={16} />
      <Skeleton variant="text" width="70%" height={16} />
      <Skeleton variant="text" width="50%" height={16} />
    </CardContent>
    <CardActions>
      <Skeleton variant="rectangular" width={100} height={32} />
      <Skeleton variant="circular" width={32} height={32} />
      <Skeleton variant="circular" width={32} height={32} />
    </CardActions>
  </Card>
);

export default PropertyCard;
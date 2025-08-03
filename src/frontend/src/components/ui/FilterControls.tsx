/**
 * FilterControls Component
 * Property search and filter controls with Japanese UX patterns
 * Includes price range, location, property type, and advanced filters
 */

import React, { useState } from 'react';
import {
  Box,
  Card,
  CardContent,
  Typography,
  TextField,
  Select,
  MenuItem,
  FormControl,
  InputLabel,
  Slider,
  Chip,
  Button,
  Accordion,
  AccordionSummary,
  AccordionDetails,
  Grid,
  InputAdornment,
  useTheme,
  SelectChangeEvent,
} from '@mui/material';
import {
  ExpandMoreIcon,
  SearchIcon,
  ClearIcon,
  TuneIcon,
} from '@mui/icons-material';
import { useTranslation } from 'react-i18next';

import { PropertyFilters } from '@types/property';
import { formatPrice } from '@utils/formatting';
import { logger } from '@utils/logger';

interface FilterControlsProps {
  filters: PropertyFilters;
  onFiltersChange: (filters: PropertyFilters) => void;
  onClear: () => void;
  resultsCount?: number;
  loading?: boolean;
}

const FilterControls: React.FC<FilterControlsProps> = ({
  filters,
  onFiltersChange,
  onClear,
  resultsCount = 0,
  loading = false,
}) => {
  const theme = useTheme();
  const { t, i18n } = useTranslation();
  const locale = i18n.language;
  
  const [advancedOpen, setAdvancedOpen] = useState(false);

  // Price range presets in yen
  const priceRanges = [
    { label: t('filters.priceRanges.under30m'), min: 0, max: 30000000 },
    { label: t('filters.priceRanges.30to50m'), min: 30000000, max: 50000000 },
    { label: t('filters.priceRanges.50to100m'), min: 50000000, max: 100000000 },
    { label: t('filters.priceRanges.100to200m'), min: 100000000, max: 200000000 },
    { label: t('filters.priceRanges.over200m'), min: 200000000, max: 999999999 },
  ];

  // Property types
  const propertyTypes = [
    { value: '一戸建て', label: t('propertyTypes.house') },
    { value: '別荘', label: t('propertyTypes.vacation') },
    { value: 'マンション', label: t('propertyTypes.apartment') },
    { value: '土地', label: t('propertyTypes.land') },
  ];

  // Karuizawa areas
  const locations = [
    { value: '旧軽井沢', label: t('locations.oldKaruizawa') },
    { value: '新軽井沢', label: t('locations.newKaruizawa') },
    { value: '中軽井沢', label: t('locations.centralKaruizawa') },
    { value: '南軽井沢', label: t('locations.southKaruizawa') },
    { value: '追分', label: t('locations.oiwake') },
    { value: '長倉', label: t('locations.nagakura') },
    { value: '発地', label: t('locations.hatchi') },
  ];

  const handleSearchChange = (value: string) => {
    onFiltersChange({ ...filters, searchTerm: value });
    logger.userInteraction('FilterControls', 'search_change', {
      hasSearchTerm: value.length > 0
    });
  };

  const handlePropertyTypeChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value as string[];
    onFiltersChange({ ...filters, propertyTypes: value });
    logger.userInteraction('FilterControls', 'property_type_change', {
      selectedTypes: value.length
    });
  };

  const handleLocationChange = (event: SelectChangeEvent<string[]>) => {
    const value = event.target.value as string[];
    onFiltersChange({ ...filters, locations: value });
    logger.userInteraction('FilterControls', 'location_change', {
      selectedLocations: value.length
    });
  };

  const handlePriceRangeChange = (event: Event, newValue: number | number[]) => {
    const [min, max] = newValue as number[];
    onFiltersChange({
      ...filters,
      priceRange: { min, max }
    });
    logger.userInteraction('FilterControls', 'price_range_change', {
      minPrice: min,
      maxPrice: max
    });
  };

  const handleSortChange = (event: SelectChangeEvent<string>) => {
    const value = event.target.value;
    onFiltersChange({ ...filters, sortBy: value });
    logger.userInteraction('FilterControls', 'sort_change', {
      sortBy: value
    });
  };

  const handlePricePresetClick = (min: number, max: number) => {
    onFiltersChange({
      ...filters,
      priceRange: { min, max }
    });
    logger.userInteraction('FilterControls', 'price_preset_click', {
      presetMin: min,
      presetMax: max
    });
  };

  const handleClear = () => {
    onClear();
    setAdvancedOpen(false);
    logger.userInteraction('FilterControls', 'clear_filters');
  };

  const getActiveFilterCount = () => {
    let count = 0;
    if (filters.searchTerm) count++;
    if (filters.propertyTypes && filters.propertyTypes.length > 0) count++;
    if (filters.locations && filters.locations.length > 0) count++;
    if (filters.priceRange && (filters.priceRange.min > 0 || filters.priceRange.max < 999999999)) count++;
    if (filters.sortBy && filters.sortBy !== 'date_desc') count++;
    return count;
  };

  const activeFilterCount = getActiveFilterCount();

  return (
    <Card sx={{ mb: 3 }} data-testid="filter-controls">
      <CardContent>
        {/* Header */}
        <Box display="flex" justifyContent="space-between" alignItems="center" mb={2}>
          <Typography variant="h6" sx={{ fontWeight: 600 }}>
            {t('filters.title')}
          </Typography>
          <Box display="flex" gap={1} alignItems="center">
            {resultsCount > 0 && (
              <Typography variant="body2" color="text.secondary">
                {t('filters.resultsCount', { count: resultsCount })}
              </Typography>
            )}
            {activeFilterCount > 0 && (
              <Button
                size="small"
                onClick={handleClear}
                startIcon={<ClearIcon />}
                disabled={loading}
              >
                {t('filters.clear')} ({activeFilterCount})
              </Button>
            )}
          </Box>
        </Box>

        {/* Search Bar */}
        <TextField
          fullWidth
          variant="outlined"
          placeholder={t('search.placeholder')}
          value={filters.searchTerm || ''}
          onChange={(e) => handleSearchChange(e.target.value)}
          InputProps={{
            startAdornment: (
              <InputAdornment position="start">
                <SearchIcon color="action" />
              </InputAdornment>
            ),
          }}
          sx={{ mb: 2 }}
          disabled={loading}
        />

        {/* Quick Filters */}
        <Grid container spacing={2} sx={{ mb: 2 }}>
          {/* Property Type */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>{t('filters.propertyType')}</InputLabel>
              <Select
                multiple
                value={filters.propertyTypes || []}
                onChange={handlePropertyTypeChange}
                disabled={loading}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(selected as string[]).map((value) => (
                      <Chip
                        key={value}
                        label={propertyTypes.find(t => t.value === value)?.label || value}
                        size="small"
                      />
                    ))}
                  </Box>
                )}
              >
                {propertyTypes.map((type) => (
                  <MenuItem key={type.value} value={type.value}>
                    {type.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Location */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>{t('filters.location')}</InputLabel>
              <Select
                multiple
                value={filters.locations || []}
                onChange={handleLocationChange}
                disabled={loading}
                renderValue={(selected) => (
                  <Box sx={{ display: 'flex', flexWrap: 'wrap', gap: 0.5 }}>
                    {(selected as string[]).map((value) => (
                      <Chip
                        key={value}
                        label={locations.find(l => l.value === value)?.label || value}
                        size="small"
                      />
                    ))}
                  </Box>
                )}
              >
                {locations.map((location) => (
                  <MenuItem key={location.value} value={location.value}>
                    {location.label}
                  </MenuItem>
                ))}
              </Select>
            </FormControl>
          </Grid>

          {/* Sort */}
          <Grid item xs={12} sm={6} md={3}>
            <FormControl fullWidth size="small">
              <InputLabel>{t('filters.sortBy')}</InputLabel>
              <Select
                value={filters.sortBy || 'date_desc'}
                onChange={handleSortChange}
                disabled={loading}
              >
                <MenuItem value="date_desc">{t('filters.sortOptions.newest')}</MenuItem>
                <MenuItem value="date_asc">{t('filters.sortOptions.oldest')}</MenuItem>
                <MenuItem value="price_desc">{t('filters.sortOptions.priceHigh')}</MenuItem>
                <MenuItem value="price_asc">{t('filters.sortOptions.priceLow')}</MenuItem>
              </Select>
            </FormControl>
          </Grid>

          {/* Advanced Toggle */}
          <Grid item xs={12} sm={6} md={3}>
            <Button
              fullWidth
              variant={advancedOpen ? "contained" : "outlined"}
              onClick={() => setAdvancedOpen(!advancedOpen)}
              startIcon={<TuneIcon />}
              sx={{ height: '40px' }}
              disabled={loading}
            >
              {t('filters.advanced')}
            </Button>
          </Grid>
        </Grid>

        {/* Advanced Filters */}
        <Accordion expanded={advancedOpen} onChange={() => setAdvancedOpen(!advancedOpen)}>
          <AccordionSummary sx={{ display: 'none' }}>
          </AccordionSummary>
          <AccordionDetails sx={{ pt: 0 }}>
            {/* Price Range */}
            <Box sx={{ mb: 3 }}>
              <Typography variant="subtitle2" gutterBottom>
                {t('filters.priceRange')}
              </Typography>
              
              {/* Price Presets */}
              <Box sx={{ mb: 2, display: 'flex', flexWrap: 'wrap', gap: 1 }}>
                {priceRanges.map((range, index) => (
                  <Chip
                    key={index}
                    label={range.label}
                    onClick={() => handlePricePresetClick(range.min, range.max)}
                    variant={
                      filters.priceRange?.min === range.min && filters.priceRange?.max === range.max
                        ? "filled"
                        : "outlined"
                    }
                    color="primary"
                    clickable
                    size="small"
                  />
                ))}
              </Box>

              {/* Price Slider */}
              <Box sx={{ px: 2 }}>
                <Slider
                  value={[
                    filters.priceRange?.min || 0,
                    filters.priceRange?.max || 500000000
                  ]}
                  onChange={handlePriceRangeChange}
                  valueLabelDisplay="auto"
                  valueLabelFormat={(value) => formatPrice(value, locale)}
                  min={0}
                  max={500000000}
                  step={1000000}
                  marks={[
                    { value: 0, label: '¥0' },
                    { value: 100000000, label: '¥1億' },
                    { value: 300000000, label: '¥3億' },
                    { value: 500000000, label: '¥5億' },
                  ]}
                  disabled={loading}
                />
              </Box>

              <Box display="flex" justifyContent="space-between" sx={{ mt: 1 }}>
                <Typography variant="caption" color="text.secondary">
                  {t('filters.minPrice')}: {formatPrice(filters.priceRange?.min || 0, locale)}
                </Typography>
                <Typography variant="caption" color="text.secondary">
                  {t('filters.maxPrice')}: {formatPrice(filters.priceRange?.max || 500000000, locale)}
                </Typography>
              </Box>
            </Box>
          </AccordionDetails>
        </Accordion>
      </CardContent>
    </Card>
  );
};

export default FilterControls;
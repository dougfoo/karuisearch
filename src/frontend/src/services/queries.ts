/**
 * React Query hooks for data fetching
 * Provides caching, background updates, and error handling
 * Integrates with mock API service
 */

import { useQuery, useMutation, useQueryClient } from '@tanstack/react-query';
import { Property, WeeklyReport, PropertyFilters } from '@types/property';
import { mockApi } from './mockApi';
import { logger } from '@utils/logger';

// Query Keys
export const queryKeys = {
  properties: ['properties'] as const,
  property: (id: string) => ['property', id] as const,
  weeklyReport: (weekOffset: number) => ['weeklyReport', weekOffset] as const,
  favorites: ['favorites'] as const,
  search: (query: string) => ['search', query] as const,
  priceTrends: ['priceTrends'] as const,
} as const;

// Default query options
const defaultQueryOptions = {
  staleTime: 5 * 60 * 1000, // 5 minutes
  gcTime: 10 * 60 * 1000, // 10 minutes (formerly cacheTime)
  retry: 2,
  retryDelay: (attemptIndex: number) => Math.min(1000 * 2 ** attemptIndex, 30000),
};

// Properties Query Hook
export const useProperties = (filters?: PropertyFilters) => {
  return useQuery({
    queryKey: [...queryKeys.properties, filters],
    queryFn: () => mockApi.getProperties(filters),
    ...defaultQueryOptions,
    onSuccess: (data) => {
      logger.debug('Properties query successful', {
        component: 'queries',
        action: 'properties_success',
        metadata: { count: data.length, filters }
      });
    },
    onError: (error) => {
      logger.error('Properties query failed', {
        component: 'queries',
        action: 'properties_error',
        error: error.message,
        metadata: { filters }
      });
    },
  });
};

// Single Property Query Hook
export const useProperty = (id: string) => {
  return useQuery({
    queryKey: queryKeys.property(id),
    queryFn: () => mockApi.getProperty(id),
    ...defaultQueryOptions,
    enabled: !!id,
    onSuccess: (data) => {
      logger.debug('Property query successful', {
        component: 'queries',
        action: 'property_success',
        metadata: { propertyId: id, found: !!data }
      });
    },
    onError: (error) => {
      logger.error('Property query failed', {
        component: 'queries',
        action: 'property_error',
        error: error.message,
        metadata: { propertyId: id }
      });
    },
  });
};

// Weekly Report Query Hook
export const useWeeklyReport = (weekOffset: number = 0) => {
  return useQuery({
    queryKey: queryKeys.weeklyReport(weekOffset),
    queryFn: () => mockApi.getWeeklyReport(weekOffset),
    ...defaultQueryOptions,
    onSuccess: (data) => {
      logger.debug('Weekly report query successful', {
        component: 'queries',
        action: 'weekly_report_success',
        metadata: { 
          weekOffset, 
          newListings: data.newListings.length,
          totalListings: data.summary.totalListings 
        }
      });
    },
    onError: (error) => {
      logger.error('Weekly report query failed', {
        component: 'queries',
        action: 'weekly_report_error',
        error: error.message,
        metadata: { weekOffset }
      });
    },
  });
};

// Favorites Query Hook
export const useFavorites = () => {
  return useQuery({
    queryKey: queryKeys.favorites,
    queryFn: () => mockApi.getFavorites(),
    ...defaultQueryOptions,
    onSuccess: (data) => {
      logger.debug('Favorites query successful', {
        component: 'queries',
        action: 'favorites_success',
        metadata: { count: data.length }
      });
    },
    onError: (error) => {
      logger.error('Favorites query failed', {
        component: 'queries',
        action: 'favorites_error',
        error: error.message
      });
    },
  });
};

// Search Query Hook (with debouncing)
export const useSearch = (query: string, enabled: boolean = true) => {
  return useQuery({
    queryKey: queryKeys.search(query),
    queryFn: () => mockApi.searchProperties(query),
    ...defaultQueryOptions,
    enabled: enabled && query.length >= 2,
    staleTime: 30 * 1000, // 30 seconds for search results
    onSuccess: (data) => {
      logger.debug('Search query successful', {
        component: 'queries',
        action: 'search_success',
        metadata: { query: query.length > 0 ? '[search_performed]' : '[empty]', results: data.length }
      });
    },
    onError: (error) => {
      logger.error('Search query failed', {
        component: 'queries',
        action: 'search_error',
        error: error.message,
        metadata: { query: query.length > 0 ? '[search_performed]' : '[empty]' }
      });
    },
  });
};

// Price Trends Query Hook
export const usePriceTrends = () => {
  return useQuery({
    queryKey: queryKeys.priceTrends,
    queryFn: () => mockApi.getPriceTrends(),
    ...defaultQueryOptions,
    staleTime: 30 * 60 * 1000, // 30 minutes for trends data
    onSuccess: (data) => {
      logger.debug('Price trends query successful', {
        component: 'queries',
        action: 'price_trends_success',
        metadata: { 
          areas: Object.keys(data.averagePriceByArea).length,
          types: Object.keys(data.priceChangesByType).length,
          months: data.monthlyTrends.length
        }
      });
    },
    onError: (error) => {
      logger.error('Price trends query failed', {
        component: 'queries',
        action: 'price_trends_error',
        error: error.message
      });
    },
  });
};

// Toggle Favorite Mutation Hook
export const useToggleFavorite = () => {
  const queryClient = useQueryClient();

  return useMutation({
    mutationFn: (propertyId: string) => mockApi.toggleFavorite(propertyId),
    onSuccess: (isFavorited, propertyId) => {
      // Invalidate and refetch favorites
      queryClient.invalidateQueries({ queryKey: queryKeys.favorites });
      
      // Update properties cache if it exists
      queryClient.setQueriesData(
        { queryKey: queryKeys.properties },
        (oldData: Property[] | undefined) => {
          if (!oldData) return oldData;
          return oldData.map(property => 
            property.id === propertyId 
              ? { ...property, isFavorite: isFavorited }
              : property
          );
        }
      );

      logger.info('Favorite toggled successfully', {
        component: 'queries',
        action: 'toggle_favorite_success',
        metadata: { propertyId, isFavorited }
      });
    },
    onError: (error, propertyId) => {
      logger.error('Toggle favorite failed', {
        component: 'queries',
        action: 'toggle_favorite_error',
        error: error.message,
        metadata: { propertyId }
      });
    },
  });
};

// Prefetch utilities
export const usePrefetchProperty = () => {
  const queryClient = useQueryClient();

  return (propertyId: string) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.property(propertyId),
      queryFn: () => mockApi.getProperty(propertyId),
      staleTime: 5 * 60 * 1000,
    });

    logger.debug('Property prefetched', {
      component: 'queries',
      action: 'prefetch_property',
      metadata: { propertyId }
    });
  };
};

export const usePrefetchWeeklyReport = () => {
  const queryClient = useQueryClient();

  return (weekOffset: number) => {
    queryClient.prefetchQuery({
      queryKey: queryKeys.weeklyReport(weekOffset),
      queryFn: () => mockApi.getWeeklyReport(weekOffset),
      staleTime: 5 * 60 * 1000,
    });

    logger.debug('Weekly report prefetched', {
      component: 'queries',
      action: 'prefetch_weekly_report',
      metadata: { weekOffset }
    });
  };
};

// Query invalidation utilities
export const useInvalidateQueries = () => {
  const queryClient = useQueryClient();

  return {
    invalidateProperties: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.properties });
      logger.debug('Properties queries invalidated', {
        component: 'queries',
        action: 'invalidate_properties'
      });
    },
    invalidateFavorites: () => {
      queryClient.invalidateQueries({ queryKey: queryKeys.favorites });
      logger.debug('Favorites queries invalidated', {
        component: 'queries',
        action: 'invalidate_favorites'
      });
    },
    invalidateAll: () => {
      queryClient.invalidateQueries();
      logger.debug('All queries invalidated', {
        component: 'queries',
        action: 'invalidate_all'
      });
    },
  };
};
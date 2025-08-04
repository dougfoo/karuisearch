/**
 * React Query hooks for data fetching
 * Provides caching, background updates, and error handling
 * Integrates with mock API service
 */

import React from 'react';
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
  const query = useQuery({
    queryKey: [...queryKeys.properties, filters],
    queryFn: () => mockApi.getProperties(filters),
    ...defaultQueryOptions,
  });

  React.useEffect(() => {
    if (query.isSuccess && query.data) {
      logger.debug('Properties query successful', {
        component: 'queries',
        action: 'properties_success',
        metadata: { count: query.data.length, filters }
      });
    }
  }, [query.isSuccess, query.data, filters]);

  React.useEffect(() => {
    if (query.isError && query.error) {
      logger.error('Properties query failed', {
        component: 'queries',
        action: 'properties_error',
        error: query.error.message,
        metadata: { filters }
      });
    }
  }, [query.isError, query.error, filters]);

  return query;
};

// Single Property Query Hook
export const useProperty = (id: string) => {
  const query = useQuery({
    queryKey: queryKeys.property(id),
    queryFn: () => mockApi.getProperty(id),
    ...defaultQueryOptions,
    enabled: !!id,
  });

  React.useEffect(() => {
    if (query.isSuccess && query.data) {
      logger.debug('Property query successful', {
        component: 'queries',
        action: 'property_success',
        metadata: { propertyId: id, found: !!query.data }
      });
    }
  }, [query.isSuccess, query.data, id]);

  React.useEffect(() => {
    if (query.isError && query.error) {
      logger.error('Property query failed', {
        component: 'queries',
        action: 'property_error',
        error: query.error.message,
        metadata: { propertyId: id }
      });
    }
  }, [query.isError, query.error, id]);

  return query;
};

// Weekly Report Query Hook
export const useWeeklyReport = (weekOffset: number = 0) => {
  const query = useQuery({
    queryKey: queryKeys.weeklyReport(weekOffset),
    queryFn: () => mockApi.getWeeklyReport(weekOffset),
    ...defaultQueryOptions,
  });

  React.useEffect(() => {
    if (query.isSuccess && query.data) {
      logger.debug('Weekly report query successful', {
        component: 'queries',
        action: 'weekly_report_success',
        metadata: { 
          weekOffset, 
          newListings: query.data.newListings.length,
          totalListings: query.data.summary.totalListings 
        }
      });
    }
  }, [query.isSuccess, query.data, weekOffset]);

  React.useEffect(() => {
    if (query.isError && query.error) {
      logger.error('Weekly report query failed', {
        component: 'queries',
        action: 'weekly_report_error',
        error: query.error.message,
        metadata: { weekOffset }
      });
    }
  }, [query.isError, query.error, weekOffset]);

  return query;
};

// Favorites Query Hook
export const useFavorites = () => {
  const query = useQuery({
    queryKey: queryKeys.favorites,
    queryFn: () => mockApi.getFavorites(),
    ...defaultQueryOptions,
  });

  React.useEffect(() => {
    if (query.isSuccess && query.data) {
      logger.debug('Favorites query successful', {
        component: 'queries',
        action: 'favorites_success',
        metadata: { count: query.data.length }
      });
    }
  }, [query.isSuccess, query.data]);

  React.useEffect(() => {
    if (query.isError && query.error) {
      logger.error('Favorites query failed', {
        component: 'queries',
        action: 'favorites_error',
        error: query.error.message
      });
    }
  }, [query.isError, query.error]);

  return query;
};

// Search Query Hook (with debouncing)
export const useSearch = (query: string, enabled: boolean = true) => {
  const queryResult = useQuery({
    queryKey: queryKeys.search(query),
    queryFn: () => mockApi.searchProperties(query),
    ...defaultQueryOptions,
    enabled: enabled && query.length >= 2,
    staleTime: 30 * 1000, // 30 seconds for search results
  });

  React.useEffect(() => {
    if (queryResult.isSuccess && queryResult.data) {
      logger.debug('Search query successful', {
        component: 'queries',
        action: 'search_success',
        metadata: { query: query.length > 0 ? '[search_performed]' : '[empty]', results: queryResult.data.length }
      });
    }
  }, [queryResult.isSuccess, queryResult.data, query]);

  React.useEffect(() => {
    if (queryResult.isError && queryResult.error) {
      logger.error('Search query failed', {
        component: 'queries',
        action: 'search_error',
        error: queryResult.error.message,
        metadata: { query: query.length > 0 ? '[search_performed]' : '[empty]' }
      });
    }
  }, [queryResult.isError, queryResult.error, query]);

  return queryResult;
};

// Price Trends Query Hook
export const usePriceTrends = () => {
  const query = useQuery({
    queryKey: queryKeys.priceTrends,
    queryFn: () => mockApi.getPriceTrends(),
    ...defaultQueryOptions,
    staleTime: 30 * 60 * 1000, // 30 minutes for trends data
  });

  React.useEffect(() => {
    if (query.isSuccess && query.data) {
      logger.debug('Price trends query successful', {
        component: 'queries',
        action: 'price_trends_success',
        metadata: { 
          areas: Object.keys(query.data.averagePriceByArea).length,
          types: Object.keys(query.data.priceChangesByType).length,
          months: query.data.monthlyTrends.length
        }
      });
    }
  }, [query.isSuccess, query.data]);

  React.useEffect(() => {
    if (query.isError && query.error) {
      logger.error('Price trends query failed', {
        component: 'queries',
        action: 'price_trends_error',
        error: query.error.message
      });
    }
  }, [query.isError, query.error]);

  return query;
};

// Toggle Favorite Mutation Hook
export const useToggleFavorite = () => {
  const queryClient = useQueryClient();

  const mutation = useMutation({
    mutationFn: (propertyId: string) => mockApi.toggleFavorite(propertyId),
  });

  React.useEffect(() => {
    if (mutation.isSuccess && mutation.data !== undefined && mutation.variables) {
      const propertyId = mutation.variables;
      const isFavorited = mutation.data;
      
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
    }
  }, [mutation.isSuccess, mutation.data, mutation.variables, queryClient]);

  React.useEffect(() => {
    if (mutation.isError && mutation.error && mutation.variables) {
      const propertyId = mutation.variables;
      logger.error('Toggle favorite failed', {
        component: 'queries',
        action: 'toggle_favorite_error',
        error: mutation.error.message,
        metadata: { propertyId }
      });
    }
  }, [mutation.isError, mutation.error, mutation.variables]);

  return mutation;
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
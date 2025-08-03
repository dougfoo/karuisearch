/**
 * Mock API Service
 * Simulates backend API calls for development and testing
 * Provides realistic data with loading delays and error simulation
 */

import { Property, WeeklyReport, PropertyFilters } from '@types/property';
import { logger } from '@utils/logger';
import mockProperties from '@data/mockProperties.json';

// Simulate network delay
const MOCK_DELAY = {
  fast: 200,
  normal: 800,
  slow: 2000,
};

// Error simulation (5% chance by default)
const ERROR_RATE = 0.05;

class MockApiService {
  private properties: Property[] = mockProperties;
  private favoriteIds: Set<string> = new Set();

  // Simulate network delay
  private async delay(type: keyof typeof MOCK_DELAY = 'normal'): Promise<void> {
    const delayTime = MOCK_DELAY[type];
    return new Promise(resolve => setTimeout(resolve, delayTime));
  }

  // Simulate random errors
  private shouldSimulateError(): boolean {
    return Math.random() < ERROR_RATE;
  }

  // Get all properties with optional filtering
  async getProperties(filters?: PropertyFilters): Promise<Property[]> {
    logger.info('API call: getProperties', {
      component: 'mockApi',
      action: 'get_properties',
      metadata: { filters }
    });

    await this.delay('normal');

    if (this.shouldSimulateError()) {
      throw new Error('Failed to fetch properties from server');
    }

    let filteredProperties = [...this.properties];

    if (filters) {
      // Apply search term filter
      if (filters.searchTerm) {
        const searchLower = filters.searchTerm.toLowerCase();
        filteredProperties = filteredProperties.filter(property =>
          property.title.toLowerCase().includes(searchLower) ||
          property.location.toLowerCase().includes(searchLower) ||
          property.description?.toLowerCase().includes(searchLower)
        );
      }

      // Apply property type filter
      if (filters.propertyTypes && filters.propertyTypes.length > 0) {
        filteredProperties = filteredProperties.filter(property =>
          property.property_type && filters.propertyTypes!.includes(property.property_type)
        );
      }

      // Apply location filter
      if (filters.locations && filters.locations.length > 0) {
        filteredProperties = filteredProperties.filter(property =>
          filters.locations!.some(location => property.location.includes(location))
        );
      }

      // Apply price range filter
      if (filters.priceRange) {
        filteredProperties = filteredProperties.filter(property => {
          const price = this.parsePrice(property.price);
          return price >= filters.priceRange!.min && price <= filters.priceRange!.max;
        });
      }

      // Apply sorting
      if (filters.sortBy) {
        filteredProperties.sort((a, b) => {
          switch (filters.sortBy) {
            case 'price_asc':
              return this.parsePrice(a.price) - this.parsePrice(b.price);
            case 'price_desc':
              return this.parsePrice(b.price) - this.parsePrice(a.price);
            case 'date_asc':
              return new Date(a.date_first_seen).getTime() - new Date(b.date_first_seen).getTime();
            case 'date_desc':
            default:
              return new Date(b.date_first_seen).getTime() - new Date(a.date_first_seen).getTime();
          }
        });
      }

      // Apply pagination
      if (filters.page && filters.pageSize) {
        const startIndex = (filters.page - 1) * filters.pageSize;
        const endIndex = startIndex + filters.pageSize;
        filteredProperties = filteredProperties.slice(startIndex, endIndex);
      }
    }

    logger.debug('Properties filtered', {
      component: 'mockApi',
      action: 'properties_filtered',
      metadata: {
        totalCount: this.properties.length,
        filteredCount: filteredProperties.length,
        appliedFilters: filters
      }
    });

    return filteredProperties;
  }

  // Get a single property by ID
  async getProperty(id: string): Promise<Property | null> {
    logger.info('API call: getProperty', {
      component: 'mockApi',
      action: 'get_property',
      metadata: { propertyId: id }
    });

    await this.delay('fast');

    if (this.shouldSimulateError()) {
      throw new Error('Failed to fetch property details');
    }

    const property = this.properties.find(p => p.id === id);
    return property || null;
  }

  // Get weekly report
  async getWeeklyReport(weekOffset: number = 0): Promise<WeeklyReport> {
    logger.info('API call: getWeeklyReport', {
      component: 'mockApi',
      action: 'get_weekly_report',
      metadata: { weekOffset }
    });

    await this.delay('normal');

    if (this.shouldSimulateError()) {
      throw new Error('Failed to fetch weekly report');
    }

    // Calculate week dates
    const now = new Date();
    const startOfWeek = new Date(now);
    startOfWeek.setDate(now.getDate() - now.getDay() - (weekOffset * 7));
    startOfWeek.setHours(0, 0, 0, 0);
    
    const endOfWeek = new Date(startOfWeek);
    endOfWeek.setDate(startOfWeek.getDate() + 6);
    endOfWeek.setHours(23, 59, 59, 999);

    // Filter properties for this week
    const weekProperties = this.properties.filter(property => {
      const propertyDate = new Date(property.date_first_seen);
      return propertyDate >= startOfWeek && propertyDate <= endOfWeek;
    });

    // Create summary statistics
    const totalListings = weekProperties.length;
    const averagePrice = totalListings > 0 
      ? weekProperties.reduce((sum, p) => sum + this.parsePrice(p.price), 0) / totalListings
      : 0;

    const propertyTypes = weekProperties.reduce((acc, property) => {
      if (property.property_type) {
        acc[property.property_type] = (acc[property.property_type] || 0) + 1;
      }
      return acc;
    }, {} as Record<string, number>);

    const priceRanges = weekProperties.reduce((acc, property) => {
      const price = this.parsePrice(property.price);
      if (price < 30000000) acc['under_30m']++;
      else if (price < 50000000) acc['30_50m']++;
      else if (price < 100000000) acc['50_100m']++;
      else if (price < 200000000) acc['100_200m']++;
      else acc['over_200m']++;
      return acc;
    }, {
      under_30m: 0,
      '30_50m': 0,
      '50_100m': 0,
      '100_200m': 0,
      over_200m: 0,
    });

    return {
      weekStartDate: startOfWeek.toISOString(),
      weekEndDate: endOfWeek.toISOString(),
      newListings: weekProperties,
      summary: {
        totalListings,
        averagePrice,
        propertyTypes,
        priceRanges,
      },
    };
  }

  // Toggle favorite status
  async toggleFavorite(propertyId: string): Promise<boolean> {
    logger.info('API call: toggleFavorite', {
      component: 'mockApi',
      action: 'toggle_favorite',
      metadata: { propertyId }
    });

    await this.delay('fast');

    if (this.shouldSimulateError()) {
      throw new Error('Failed to update favorite status');
    }

    if (this.favoriteIds.has(propertyId)) {
      this.favoriteIds.delete(propertyId);
      return false;
    } else {
      this.favoriteIds.add(propertyId);
      return true;
    }
  }

  // Get favorite properties
  async getFavorites(): Promise<Property[]> {
    logger.info('API call: getFavorites', {
      component: 'mockApi',
      action: 'get_favorites'
    });

    await this.delay('fast');

    if (this.shouldSimulateError()) {
      throw new Error('Failed to fetch favorites');
    }

    return this.properties.filter(property => this.favoriteIds.has(property.id));
  }

  // Search properties with autocomplete
  async searchProperties(query: string): Promise<Property[]> {
    logger.info('API call: searchProperties', {
      component: 'mockApi',
      action: 'search_properties',
      metadata: { queryLength: query.length }
    });

    await this.delay('fast');

    if (this.shouldSimulateError()) {
      throw new Error('Search request failed');
    }

    if (!query || query.length < 2) {
      return [];
    }

    const searchLower = query.toLowerCase();
    const results = this.properties.filter(property =>
      property.title.toLowerCase().includes(searchLower) ||
      property.location.toLowerCase().includes(searchLower) ||
      property.description?.toLowerCase().includes(searchLower)
    );

    // Limit to 10 results for autocomplete
    return results.slice(0, 10);
  }

  // Get price trends
  async getPriceTrends(): Promise<{
    averagePriceByArea: Record<string, number>;
    priceChangesByType: Record<string, number>;
    monthlyTrends: Array<{ month: string; averagePrice: number; listingCount: number }>;
  }> {
    logger.info('API call: getPriceTrends', {
      component: 'mockApi',
      action: 'get_price_trends'
    });

    await this.delay('slow');

    if (this.shouldSimulateError()) {
      throw new Error('Failed to fetch price trends');
    }

    // Mock data for trends
    return {
      averagePriceByArea: {
        '旧軽井沢': 85000000,
        '新軽井沢': 72000000,
        '中軽井沢': 68000000,
        '南軽井沢': 62000000,
        '追分': 58000000,
        '長倉': 55000000,
        '発地': 48000000,
      },
      priceChangesByType: {
        '一戸建て': 2.3,
        '別荘': 1.8,
        'マンション': -0.5,
        '土地': 3.1,
      },
      monthlyTrends: [
        { month: '2024-01', averagePrice: 65000000, listingCount: 45 },
        { month: '2024-02', averagePrice: 67000000, listingCount: 52 },
        { month: '2024-03', averagePrice: 69000000, listingCount: 48 },
        { month: '2024-04', averagePrice: 71000000, listingCount: 58 },
        { month: '2024-05', averagePrice: 68000000, listingCount: 43 },
        { month: '2024-06', averagePrice: 72000000, listingCount: 61 },
      ],
    };
  }

  // Helper method to parse price from string
  private parsePrice(priceString: string): number {
    if (!priceString) return 0;
    
    // Handle Japanese format (万円, 億円)
    if (priceString.includes('万円')) {
      const match = priceString.match(/¥?([0-9,]+(?:\.[0-9]+)?)万円/);
      if (match) {
        return parseFloat(match[1].replace(/,/g, '')) * 10000;
      }
    }
    
    if (priceString.includes('億円')) {
      const match = priceString.match(/¥?([0-9,]+(?:\.[0-9]+)?)億円/);
      if (match) {
        return parseFloat(match[1].replace(/,/g, '')) * 100000000;
      }
    }
    
    // Handle regular number format
    const numbers = priceString.replace(/[^0-9]/g, '');
    return parseInt(numbers, 10) || 0;
  }
}

// Export singleton instance
export const mockApi = new MockApiService();
export default mockApi;
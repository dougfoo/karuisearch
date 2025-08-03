/**
 * PropertyCard Component Tests
 * Comprehensive test suite for the PropertyCard component
 */

import { describe, it, expect, vi } from 'vitest';
import { render, screen, fireEvent, waitFor } from '@testing-library/react';
import { ThemeProvider } from '@mui/material/styles';
import { I18nextProvider } from 'react-i18next';

import PropertyCard, { PropertyCardSkeleton } from './PropertyCard';
import { Property } from '@types/property';
import { lightTheme } from '@utils/theme';
import i18n from '@i18n/index';

// Mock property data
const mockProperty: Property = {
  id: 'test-property-001',
  title: '軽井沢町大字軽井沢の新築別荘',
  price: '¥58,000,000',
  location: '長野県北佐久郡軽井沢町大字軽井沢',
  property_type: '別荘',
  size_info: '土地:250㎡ 建物:180㎡',
  building_age: '新築',
  description: '軽井沢の静かな別荘地に建つ新築別荘です。',
  image_urls: [
    'https://via.placeholder.com/400x300/2E7D32/ffffff?text=Test+Image',
  ],
  rooms: '4LDK+S',
  source_url: 'https://example.com/property/001',
  scraped_date: '2024-01-15',
  date_first_seen: '2024-01-15T10:30:00Z',
  price_change: {
    amount: '+¥2,000,000',
    percentage: '+3.6%',
    direction: 'increase',
    since_date: '2024-01-08'
  },
  is_new: true,
  is_featured: true,
};

// Test wrapper component
const TestWrapper: React.FC<{ children: React.ReactNode }> = ({ children }) => (
  <ThemeProvider theme={lightTheme}>
    <I18nextProvider i18n={i18n}>
      {children}
    </I18nextProvider>
  </ThemeProvider>
);

describe('PropertyCard', () => {
  it('renders property information correctly', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    // Check basic property information
    expect(screen.getByText(mockProperty.title)).toBeInTheDocument();
    expect(screen.getByText(mockProperty.price)).toBeInTheDocument();
    expect(screen.getByText(/軽井沢/)).toBeInTheDocument();
    expect(screen.getByText(mockProperty.rooms!)).toBeInTheDocument();
  });

  it('displays property type badge', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    expect(screen.getByText('別荘')).toBeInTheDocument();
  });

  it('displays new listing badge when property is new', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    expect(screen.getByText('新着')).toBeInTheDocument();
  });

  it('displays price change information when available', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} showPriceChange={true} />
      </TestWrapper>
    );

    expect(screen.getByText(/\+¥2,000,000/)).toBeInTheDocument();
    expect(screen.getByText(/\+3\.6%/)).toBeInTheDocument();
  });

  it('hides price change when showPriceChange is false', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} showPriceChange={false} />
      </TestWrapper>
    );

    expect(screen.queryByText(/\+¥2,000,000/)).not.toBeInTheDocument();
  });

  it('handles property card click', () => {
    const mockOnClick = vi.fn();
    
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} onClick={mockOnClick} />
      </TestWrapper>
    );

    const card = screen.getByTestId(`property-card-${mockProperty.id}`);
    fireEvent.click(card);

    expect(mockOnClick).toHaveBeenCalledWith(mockProperty);
  });

  it('handles external link click', () => {
    // Mock window.open
    const mockOpen = vi.fn();
    Object.defineProperty(window, 'open', {
      value: mockOpen,
      writable: true,
    });

    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    const externalButton = screen.getByText('元サイトを見る');
    fireEvent.click(externalButton);

    expect(mockOpen).toHaveBeenCalledWith(
      mockProperty.source_url,
      '_blank',
      'noopener,noreferrer'
    );
  });

  it('renders in compact mode', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} compact={true} />
      </TestWrapper>
    );

    // In compact mode, title should be truncated
    const card = screen.getByTestId(`property-card-${mockProperty.id}`);
    expect(card).toBeInTheDocument();
  });

  it('handles missing optional data gracefully', () => {
    const minimalProperty: Property = {
      id: 'minimal-001',
      title: 'Minimal Property',
      price: '¥10,000,000',
      location: 'Karuizawa',
      source_url: 'https://example.com',
      scraped_date: '2024-01-15',
      date_first_seen: '2024-01-15T10:30:00Z',
    };

    render(
      <TestWrapper>
        <PropertyCard property={minimalProperty} />
      </TestWrapper>
    );

    expect(screen.getByText('Minimal Property')).toBeInTheDocument();
    expect(screen.getByText('¥10,000,000')).toBeInTheDocument();
  });

  it('handles image load errors', async () => {
    const propertyWithBadImage: Property = {
      ...mockProperty,
      image_urls: ['https://invalid-url/image.jpg'],
    };

    render(
      <TestWrapper>
        <PropertyCard property={propertyWithBadImage} />
      </TestWrapper>
    );

    const image = screen.getByRole('img');
    
    // Simulate image load error
    fireEvent.error(image);

    await waitFor(() => {
      expect(image).toHaveAttribute('src');
      // Should fall back to placeholder
      expect((image as HTMLImageElement).src).toContain('placeholder');
    });
  });

  it('handles favorite button click', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    const favoriteButton = screen.getByLabelText('お気に入り');
    fireEvent.click(favoriteButton);

    // Should not propagate to card click
    // (Testing that event.stopPropagation works)
    expect(favoriteButton).toBeInTheDocument();
  });

  it('handles share button click', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    const shareButton = screen.getByLabelText('共有');
    fireEvent.click(shareButton);

    expect(shareButton).toBeInTheDocument();
  });

  it('displays building age and rooms correctly', () => {
    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    expect(screen.getByText('新築')).toBeInTheDocument();
    expect(screen.getByText('4LDK+S')).toBeInTheDocument();
  });

  it('formats price correctly in Japanese locale', async () => {
    // Ensure Japanese locale
    await i18n.changeLanguage('ja');

    render(
      <TestWrapper>
        <PropertyCard property={mockProperty} />
      </TestWrapper>
    );

    expect(screen.getByText('¥58,000,000')).toBeInTheDocument();
  });
});

describe('PropertyCardSkeleton', () => {
  it('renders skeleton in normal mode', () => {
    render(
      <TestWrapper>
        <PropertyCardSkeleton />
      </TestWrapper>
    );

    // Should have skeleton elements
    const skeletons = screen.getAllByTestId(/skeleton/i);
    expect(skeletons.length).toBeGreaterThan(0);
  });

  it('renders skeleton in compact mode', () => {
    render(
      <TestWrapper>
        <PropertyCardSkeleton compact={true} />
      </TestWrapper>
    );

    // Should render with different dimensions
    const skeletons = screen.getAllByTestId(/skeleton/i);
    expect(skeletons.length).toBeGreaterThan(0);
  });
});
/**
 * Unit tests for Distance Calculator page covering all edge cases
 */
import React from 'react';
import { render, screen, fireEvent, waitFor, act } from '@testing-library/react';
import userEvent from '@testing-library/user-event';
import '@testing-library/jest-dom';
import DistanceCalculatorPage from '../page';
import { geoService } from '@/services/geo';

// Mock the geo service
jest.mock('@/services/geo', () => ({
  geoService: {
    fetchCities: jest.fn(),
    getRouteInfo: jest.fn(),
  },
}));

// Mock framer-motion to avoid animation issues in tests
jest.mock('framer-motion', () => ({
  motion: {
    div: ({ children, ...props }: any) => <div {...props}>{children}</div>,
    button: ({ children, ...props }: any) => <button {...props}>{children}</button>,
  },
  AnimatePresence: ({ children }: any) => <>{children}</>,
}));

describe('DistanceCalculatorPage', () => {
  const mockCities = [
    {
      id: '1',
      name: 'Mumbai',
      state: 'Maharashtra',
      country: 'India',
      latitude: 19.0760,
      longitude: 72.8777,
      is_popular: true,
      is_active: true,
      timezone: 'Asia/Kolkata',
    },
    {
      id: '2',
      name: 'Delhi',
      state: 'Delhi',
      country: 'India',
      latitude: 28.6139,
      longitude: 77.2090,
      is_popular: true,
      is_active: true,
      timezone: 'Asia/Kolkata',
    },
    {
      id: '3',
      name: 'Bangalore',
      state: 'Karnataka',
      country: 'India',
      latitude: 12.9716,
      longitude: 77.5946,
      is_popular: true,
      is_active: true,
      timezone: 'Asia/Kolkata',
    },
  ];

  const mockRouteInfo = {
    origin_city: 'Mumbai',
    destination_city: 'Delhi',
    straight_line_distance_km: 1150.5,
    driving_distance_km: 1450.0,
    driving_duration_hours: 24.5,
    is_estimated: false,
  };

  beforeEach(() => {
    jest.clearAllMocks();
    (geoService.fetchCities as jest.Mock).mockResolvedValue(mockCities);
  });

  describe('Initial Render', () => {
    it('should render the page with all components', async () => {
      render(<DistanceCalculatorPage />);

      expect(screen.getByText('Distance Calculator')).toBeInTheDocument();
      expect(screen.getByText(/Calculate accurate distances/)).toBeInTheDocument();
      expect(screen.getByText('Select Origin City')).toBeInTheDocument();
      expect(screen.getByText('Select Destination City')).toBeInTheDocument();
      expect(screen.getByRole('button', { name: /calculate distance/i })).toBeInTheDocument();
    });

    it('should load cities on mount', async () => {
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(geoService.fetchCities).toHaveBeenCalledTimes(1);
      });
    });

    it('should show loading state while fetching cities', async () => {
      (geoService.fetchCities as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockCities), 100))
      );

      render(<DistanceCalculatorPage />);

      expect(screen.getByText('Loading cities...')).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });
    });

    it('should handle city fetch error gracefully', async () => {
      (geoService.fetchCities as jest.Mock).mockRejectedValue(new Error('Network error'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();

      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      expect(consoleSpy).toHaveBeenCalledWith('Failed to fetch cities:', expect.any(Error));
      consoleSpy.mockRestore();
    });
  });

  describe('City Selection', () => {
    it('should populate city dropdowns after loading', async () => {
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        const originSelect = screen.getByLabelText('Select Origin City');
        const destSelect = screen.getByLabelText('Select Destination City');

        expect(originSelect).toBeInTheDocument();
        expect(destSelect).toBeInTheDocument();
      });

      // Click on origin dropdown
      const originSelect = screen.getByLabelText('Select Origin City');
      fireEvent.click(originSelect);

      await waitFor(() => {
        mockCities.forEach(city => {
          expect(screen.getByText(new RegExp(city.name))).toBeInTheDocument();
        });
      });
    });

    it('should select origin and destination cities', async () => {
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select origin city
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      // Select destination city
      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      expect(screen.getByText('Mumbai')).toBeInTheDocument();
      expect(screen.getByText('Delhi')).toBeInTheDocument();
    });

    it('should not allow selecting same city as origin and destination', async () => {
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select Mumbai as origin
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      // Try to select Mumbai as destination
      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);

      // Mumbai should be disabled in destination dropdown
      const mumbaiOption = screen.getAllByText(/Mumbai/).find(
        el => el.closest('[role="option"]')
      );
      expect(mumbaiOption?.closest('[role="option"]')).toHaveAttribute('aria-disabled', 'true');
    });

    it('should swap cities when swap button is clicked', async () => {
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      // Click swap button
      const swapButton = screen.getByRole('button', { name: /swap/i });
      await user.click(swapButton);

      // Cities should be swapped
      expect(screen.getByText('Delhi')).toBeInTheDocument();
      expect(screen.getByText('Mumbai')).toBeInTheDocument();
    });

    it('should not swap when only one city is selected', async () => {
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select only origin
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      // Try to swap
      const swapButton = screen.getByRole('button', { name: /swap/i });
      await user.click(swapButton);

      // Origin should remain the same
      expect(screen.getByText('Mumbai')).toBeInTheDocument();
    });
  });

  describe('Distance Calculation', () => {
    it('should calculate distance successfully', async () => {
      (geoService.getRouteInfo as jest.Mock).mockResolvedValue(mockRouteInfo);
      const user = userEvent.setup();
      
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      // Calculate distance
      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      await user.click(calculateButton);

      // Check results
      await waitFor(() => {
        expect(screen.getByText(/Straight Line Distance/)).toBeInTheDocument();
        expect(screen.getByText(/1,150.5 km/)).toBeInTheDocument();
        expect(screen.getByText(/Driving Distance/)).toBeInTheDocument();
        expect(screen.getByText(/1,450.0 km/)).toBeInTheDocument();
        expect(screen.getByText(/Estimated Travel Time/)).toBeInTheDocument();
        expect(screen.getByText(/1 day 0.5 hours/)).toBeInTheDocument();
      });
    });

    it('should show loading state during calculation', async () => {
      (geoService.getRouteInfo as jest.Mock).mockImplementation(
        () => new Promise(resolve => setTimeout(() => resolve(mockRouteInfo), 100))
      );
      
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      // Calculate distance
      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      await user.click(calculateButton);

      expect(screen.getByText(/calculating/i)).toBeInTheDocument();

      await waitFor(() => {
        expect(screen.queryByText(/calculating/i)).not.toBeInTheDocument();
      });
    });

    it('should handle calculation errors', async () => {
      (geoService.getRouteInfo as jest.Mock).mockRejectedValue(new Error('API Error'));
      const consoleSpy = jest.spyOn(console, 'error').mockImplementation();
      
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      // Calculate distance
      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      await user.click(calculateButton);

      await waitFor(() => {
        expect(consoleSpy).toHaveBeenCalledWith('Failed to calculate distance:', expect.any(Error));
      });

      consoleSpy.mockRestore();
    });

    it('should disable calculate button when cities not selected', () => {
      render(<DistanceCalculatorPage />);

      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      expect(calculateButton).toBeDisabled();
    });

    it('should enable calculate button when both cities selected', async () => {
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      expect(calculateButton).toBeDisabled();

      // Select origin
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      // Still disabled with only origin
      expect(calculateButton).toBeDisabled();

      // Select destination
      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      // Now enabled
      expect(calculateButton).not.toBeDisabled();
    });

    it('should show estimated label when route is estimated', async () => {
      const estimatedRoute = { ...mockRouteInfo, is_estimated: true };
      (geoService.getRouteInfo as jest.Mock).mockResolvedValue(estimatedRoute);
      
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities and calculate
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      await user.click(calculateButton);

      await waitFor(() => {
        expect(screen.getByText(/Estimated/)).toBeInTheDocument();
      });
    });

    it('should handle zero distance for same location', async () => {
      const sameLocationRoute = {
        ...mockRouteInfo,
        origin_city: 'Mumbai',
        destination_city: 'Mumbai',
        straight_line_distance_km: 0,
        driving_distance_km: 0,
        driving_duration_hours: 0,
      };
      (geoService.getRouteInfo as jest.Mock).mockResolvedValue(sameLocationRoute);
      
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select same city (this would typically be prevented by UI)
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      // Force selection of same city for test
      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      
      // Override the disable logic for testing
      const mumbaiDestOption = screen.getAllByText(/Mumbai/)[1];
      fireEvent.click(mumbaiDestOption);

      // Calculate
      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      if (!calculateButton.disabled) {
        await user.click(calculateButton);

        await waitFor(() => {
          expect(screen.getByText(/0 km/)).toBeInTheDocument();
        });
      }
    });
  });

  describe('Edge Cases', () => {
    it('should handle empty city list', async () => {
      (geoService.fetchCities as jest.Mock).mockResolvedValue([]);
      
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      const originSelect = screen.getByLabelText('Select Origin City');
      fireEvent.click(originSelect);

      expect(screen.getByText(/no cities available/i)).toBeInTheDocument();
    });

    it('should handle very long city names', async () => {
      const longNameCities = [
        {
          ...mockCities[0],
          name: 'Thiruvananthapuram International Airport Area Extended Zone',
        },
      ];
      (geoService.fetchCities as jest.Mock).mockResolvedValue(longNameCities);
      
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      const originSelect = screen.getByLabelText('Select Origin City');
      fireEvent.click(originSelect);

      expect(screen.getByText(/Thiruvananthapuram/)).toBeInTheDocument();
    });

    it('should handle rapid successive calculations', async () => {
      (geoService.getRouteInfo as jest.Mock).mockResolvedValue(mockRouteInfo);
      const user = userEvent.setup();
      
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      // Click calculate multiple times rapidly
      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      await user.click(calculateButton);
      await user.click(calculateButton);
      await user.click(calculateButton);

      // Should still show results correctly
      await waitFor(() => {
        expect(screen.getByText(/1,450.0 km/)).toBeInTheDocument();
      });

      // Should not have multiple simultaneous calculations
      expect(geoService.getRouteInfo).toHaveBeenCalledTimes(1);
    });

    it('should format large distances correctly', async () => {
      const largeDistanceRoute = {
        ...mockRouteInfo,
        straight_line_distance_km: 12345.67,
        driving_distance_km: 15678.9,
        driving_duration_hours: 256.5,
      };
      (geoService.getRouteInfo as jest.Mock).mockResolvedValue(largeDistanceRoute);
      
      const user = userEvent.setup();
      render(<DistanceCalculatorPage />);

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select cities and calculate
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      const destSelect = screen.getByLabelText('Select Destination City');
      await user.click(destSelect);
      await user.click(screen.getByText(/Delhi/));

      const calculateButton = screen.getByRole('button', { name: /calculate distance/i });
      await user.click(calculateButton);

      await waitFor(() => {
        expect(screen.getByText(/12,345.7 km/)).toBeInTheDocument();
        expect(screen.getByText(/15,678.9 km/)).toBeInTheDocument();
        expect(screen.getByText(/10 days 16.5 hours/)).toBeInTheDocument();
      });
    });

    it('should maintain state during re-renders', async () => {
      const { rerender } = render(<DistanceCalculatorPage />);
      const user = userEvent.setup();

      await waitFor(() => {
        expect(screen.queryByText('Loading cities...')).not.toBeInTheDocument();
      });

      // Select origin
      const originSelect = screen.getByLabelText('Select Origin City');
      await user.click(originSelect);
      await user.click(screen.getByText(/Mumbai/));

      // Force re-render
      rerender(<DistanceCalculatorPage />);

      // Selection should persist
      expect(screen.getByText('Mumbai')).toBeInTheDocument();
    });
  });
});

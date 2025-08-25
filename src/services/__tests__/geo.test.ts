/**
 * Unit tests for geo service covering all edge cases
 */
import { geoService } from '../geo';
import { apiClient } from '@/lib/api/client';
import { City, RouteInfo, FareCalculationRequest } from '@/types';

// Mock the API client
jest.mock('@/lib/api/client', () => ({
  apiClient: {
    get: jest.fn(),
    post: jest.fn(),
  },
}));

describe('GeoService', () => {
  const mockApiClient = apiClient as jest.Mocked<typeof apiClient>;

  beforeEach(() => {
    // Clear all mocks before each test
    jest.clearAllMocks();
    // Reset internal state
    (geoService as any).citiesCache = null;
    (geoService as any).cacheTimestamp = 0;
  });

  const mockCities: City[] = [
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
      name: 'Shimla',
      state: 'Himachal Pradesh',
      country: 'India',
      latitude: 31.1048,
      longitude: 77.1734,
      is_popular: false,
      is_active: true,
      timezone: 'Asia/Kolkata',
    },
  ];

  describe('fetchCities', () => {
    it('should fetch cities from API successfully', async () => {
      mockApiClient.get.mockResolvedValueOnce({ cities: mockCities });

      const cities = await geoService.fetchCities();

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/cities/', { params: {} });
      expect(cities).toEqual(mockCities);
    });

    it('should fetch only popular cities when requested', async () => {
      const popularCities = mockCities.filter(city => city.is_popular);
      mockApiClient.get.mockResolvedValueOnce({ cities: popularCities });

      const cities = await geoService.fetchCities(true);

      expect(mockApiClient.get).toHaveBeenCalledWith('/api/v1/cities/', { 
        params: { popular_only: true } 
      });
      expect(cities).toEqual(popularCities);
    });

    it('should return cached cities within cache duration', async () => {
      mockApiClient.get.mockResolvedValueOnce({ cities: mockCities });

      // First call - should hit API
      const cities1 = await geoService.fetchCities();
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);

      // Second call within cache duration - should use cache
      const cities2 = await geoService.fetchCities();
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      expect(cities2).toEqual(cities1);
    });

    it('should refetch cities after cache expires', async () => {
      mockApiClient.get.mockResolvedValueOnce({ cities: mockCities });

      // First call
      await geoService.fetchCities();
      
      // Manually expire cache
      (geoService as any).cacheTimestamp = Date.now() - 6 * 60 * 1000; // 6 minutes ago

      mockApiClient.get.mockResolvedValueOnce({ cities: mockCities });
      
      // Second call after cache expiry
      await geoService.fetchCities();
      
      expect(mockApiClient.get).toHaveBeenCalledTimes(2);
    });

    it('should filter cached popular cities without API call', async () => {
      mockApiClient.get.mockResolvedValueOnce({ cities: mockCities });

      // First call - fetch all cities
      await geoService.fetchCities();

      // Second call for popular cities - should use cache
      const popularCities = await geoService.fetchCities(true);
      
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      expect(popularCities).toEqual(mockCities.filter(city => city.is_popular));
    });

    it('should handle API errors and fallback to hardcoded cities', async () => {
      mockApiClient.get.mockRejectedValueOnce(new Error('Network error'));

      const cities = await geoService.fetchCities();

      expect(cities.length).toBeGreaterThan(0);
      expect(cities.some(city => city.name === 'Mumbai')).toBe(true);
    });

    it('should handle missing cities property in API response', async () => {
      mockApiClient.get.mockResolvedValueOnce({ data: [] }); // Wrong response format

      const cities = await geoService.fetchCities();

      // Should fallback to hardcoded cities
      expect(cities.length).toBeGreaterThan(0);
    });

    it('should handle empty cities array from API', async () => {
      mockApiClient.get.mockResolvedValueOnce({ cities: [] });

      const cities = await geoService.fetchCities();

      expect(cities).toEqual([]);
    });

    it('should handle concurrent fetch requests', async () => {
      mockApiClient.get.mockResolvedValueOnce({ cities: mockCities });

      // Make multiple concurrent requests
      const promises = Array(5).fill(null).map(() => geoService.fetchCities());
      const results = await Promise.all(promises);

      // API should only be called once due to caching
      expect(mockApiClient.get).toHaveBeenCalledTimes(1);
      
      // All results should be the same
      results.forEach(result => {
        expect(result).toEqual(mockCities);
      });
    });
  });

  describe('getRouteInfo', () => {
    const mockRouteInfo: RouteInfo = {
      origin_city: 'Mumbai',
      destination_city: 'Delhi',
      straight_line_distance_km: 1150.5,
      driving_distance_km: 1450.0,
      driving_duration_hours: 24.5,
      is_estimated: false,
    };

    it('should get route info successfully', async () => {
      mockApiClient.post.mockResolvedValueOnce(mockRouteInfo);

      const result = await geoService.getRouteInfo('Mumbai', 'Delhi');

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/cities/route-info', {
        origin_city: 'Mumbai',
        destination_city: 'Delhi',
      });
      expect(result).toEqual(mockRouteInfo);
    });

    it('should handle same origin and destination', async () => {
      const sameLocationRoute: RouteInfo = {
        origin_city: 'Mumbai',
        destination_city: 'Mumbai',
        straight_line_distance_km: 0,
        driving_distance_km: 0,
        driving_duration_hours: 0,
        is_estimated: false,
      };

      mockApiClient.post.mockResolvedValueOnce(sameLocationRoute);

      const result = await geoService.getRouteInfo('Mumbai', 'Mumbai');

      expect(result.driving_distance_km).toBe(0);
      expect(result.driving_duration_hours).toBe(0);
    });

    it('should handle API errors', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('API Error'));

      await expect(geoService.getRouteInfo('Mumbai', 'Delhi')).rejects.toThrow('API Error');
    });

    it('should handle empty city names', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('City not found'));

      await expect(geoService.getRouteInfo('', '')).rejects.toThrow();
    });

    it('should handle special characters in city names', async () => {
      mockApiClient.post.mockResolvedValueOnce(mockRouteInfo);

      await geoService.getRouteInfo('São Paulo', 'New York');

      expect(mockApiClient.post).toHaveBeenCalledWith('/api/v1/cities/route-info', {
        origin_city: 'São Paulo',
        destination_city: 'New York',
      });
    });

    it('should handle network timeout', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Request timeout'));

      await expect(geoService.getRouteInfo('Mumbai', 'Delhi')).rejects.toThrow('Request timeout');
    });
  });

  describe('calculateFare', () => {
    const mockFareRequest: FareCalculationRequest = {
      pickup_location: { lat: 19.0760, lng: 72.8777 },
      drop_location: { lat: 28.6139, lng: 77.2090 },
      cab_type: 'sedan',
      trip_type: 'one-way',
      pickup_city: 'Mumbai',
      drop_city: 'Delhi',
    };

    const mockFareResponse = {
      base_fare: 1000,
      distance_fare: 5000,
      time_fare: 500,
      surge_multiplier: 1.0,
      total_fare: 6500,
      currency: 'INR',
      breakdown: {
        base: 1000,
        distance: 5000,
        time: 500,
      },
    };

    it('should calculate fare successfully', async () => {
      mockApiClient.post.mockResolvedValueOnce(mockFareResponse);

      const result = await geoService.calculateFare(mockFareRequest);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/bookings/calculate-fare',
        mockFareRequest
      );
      expect(result).toEqual(mockFareResponse);
    });

    it('should handle fare calculation without city names', async () => {
      const requestWithoutCities = {
        ...mockFareRequest,
        pickup_city: undefined,
        drop_city: undefined,
      };

      mockApiClient.post.mockResolvedValueOnce(mockFareResponse);

      await geoService.calculateFare(requestWithoutCities);

      expect(mockApiClient.post).toHaveBeenCalledWith(
        '/api/v1/bookings/calculate-fare',
        requestWithoutCities
      );
    });

    it('should handle invalid cab type', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Invalid cab type'));

      const invalidRequest = { ...mockFareRequest, cab_type: 'invalid' };

      await expect(geoService.calculateFare(invalidRequest)).rejects.toThrow('Invalid cab type');
    });

    it('should handle fare calculation errors', async () => {
      mockApiClient.post.mockRejectedValueOnce(new Error('Service unavailable'));

      await expect(geoService.calculateFare(mockFareRequest)).rejects.toThrow('Service unavailable');
    });
  });

  describe('getHardcodedCities', () => {
    it('should return hardcoded cities', () => {
      const cities = (geoService as any).getHardcodedCities();

      expect(Array.isArray(cities)).toBe(true);
      expect(cities.length).toBeGreaterThan(0);
      expect(cities.every((city: City) => city.name && city.latitude && city.longitude)).toBe(true);
    });

    it('should filter popular cities from hardcoded list', () => {
      const popularCities = (geoService as any).getHardcodedCities(true);

      expect(popularCities.every((city: City) => city.is_popular)).toBe(true);
      expect(popularCities.length).toBeLessThan((geoService as any).getHardcodedCities().length);
    });
  });

  describe('Edge cases', () => {
    it('should handle very large city lists', async () => {
      const largeCityList = Array(1000).fill(null).map((_, i) => ({
        id: `${i}`,
        name: `City${i}`,
        state: `State${i}`,
        country: 'India',
        latitude: 20 + i * 0.01,
        longitude: 70 + i * 0.01,
        is_popular: i < 10,
        is_active: true,
        timezone: 'Asia/Kolkata',
      }));

      mockApiClient.get.mockResolvedValueOnce({ cities: largeCityList });

      const cities = await geoService.fetchCities();

      expect(cities.length).toBe(1000);
    });

    it('should handle unicode city names correctly', async () => {
      const unicodeCities: City[] = [
        {
          id: '1',
          name: 'São Paulo',
          state: 'SP',
          country: 'Brazil',
          latitude: -23.5505,
          longitude: -46.6333,
          is_popular: true,
          is_active: true,
          timezone: 'America/Sao_Paulo',
        },
        {
          id: '2',
          name: '北京',
          state: 'Beijing',
          country: 'China',
          latitude: 39.9042,
          longitude: 116.4074,
          is_popular: true,
          is_active: true,
          timezone: 'Asia/Shanghai',
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ cities: unicodeCities });

      const cities = await geoService.fetchCities();

      expect(cities[0].name).toBe('São Paulo');
      expect(cities[1].name).toBe('北京');
    });

    it('should handle malformed API responses gracefully', async () => {
      // Return null instead of object
      mockApiClient.get.mockResolvedValueOnce(null);

      const cities = await geoService.fetchCities();

      // Should fallback to hardcoded cities
      expect(cities.length).toBeGreaterThan(0);
    });

    it('should handle partial city data', async () => {
      const partialCities = [
        {
          id: '1',
          name: 'Mumbai',
          // Missing other required fields
        },
      ];

      mockApiClient.get.mockResolvedValueOnce({ cities: partialCities });

      const cities = await geoService.fetchCities();

      // Should still return the data, application should handle validation
      expect(cities).toEqual(partialCities);
    });

    it('should maintain data integrity during concurrent operations', async () => {
      const cities1 = mockCities.slice(0, 2);
      const cities2 = mockCities.slice(1, 3);

      mockApiClient.get
        .mockResolvedValueOnce({ cities: cities1 })
        .mockResolvedValueOnce({ cities: cities2 });

      // First request
      const result1 = await geoService.fetchCities();
      
      // Expire cache
      (geoService as any).cacheTimestamp = 0;
      
      // Second request
      const result2 = await geoService.fetchCities();

      expect(result1).toEqual(cities1);
      expect(result2).toEqual(cities2);
    });
  });
});
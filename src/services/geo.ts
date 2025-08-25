/**
 * Geographic services for the frontend to fetch cities and calculate distances.
 */
import { apiClient } from '@/lib/api/client';

export interface City {
  id: string;
  name: string;
  state: string;
  country: string;
  latitude: number;
  longitude: number;
  is_popular: boolean;
}

export interface RouteInfo {
  origin: City;
  destination: City;
  straight_line_distance_km: number;
  driving_distance_km: number;
  estimated_time_hours: number;
  estimated_time_formatted: string;
}

export interface FareCalculationRequest {
  pickup_location: {
    lat: number;
    lng: number;
  };
  drop_location: {
    lat: number;
    lng: number;
  };
  cab_type: string;
  trip_type: string;
  pickup_city?: string;
  drop_city?: string;
}

class GeoService {
  private static instance: GeoService;
  private citiesCache: City[] | null = null;
  private cacheTimestamp: number = 0;
  private readonly CACHE_DURATION = 5 * 60 * 1000; // 5 minutes

  private constructor() {}

  static getInstance(): GeoService {
    if (!GeoService.instance) {
      GeoService.instance = new GeoService();
    }
    return GeoService.instance;
  }

  async fetchCities(popularOnly: boolean = false): Promise<City[]> {
    try {
      // Check cache
      if (this.citiesCache && Date.now() - this.cacheTimestamp < this.CACHE_DURATION) {
        const cities = this.citiesCache;
        return popularOnly ? cities.filter(city => city.is_popular) : cities;
      }

      // Fetch from API
      const params = popularOnly ? { popular_only: true } : {};
      const response = await apiClient.get('/api/v1/cities/', { params });
      
      if (response.cities) {
        this.citiesCache = response.cities;
        this.cacheTimestamp = Date.now();
        return response.cities;
      }
      
      // Fallback to hardcoded cities if API fails
      return this.getHardcodedCities(popularOnly);
    } catch (error) {
      console.error('Failed to fetch cities:', error);
      // Fallback to hardcoded cities
      return this.getHardcodedCities(popularOnly);
    }
  }

  async getRouteInfo(originCity: string, destinationCity: string): Promise<RouteInfo> {
    try {
      const response = await apiClient.post('/api/v1/cities/route-info', {
        origin_city: originCity,
        destination_city: destinationCity,
      });
      
      return response;
    } catch (error) {
      console.error('Failed to get route info:', error);
      throw error;
    }
  }

  async calculateFare(request: FareCalculationRequest) {
    try {
      const response = await apiClient.post('/api/v1/bookings/calculate-fare', request);
      return response;
    } catch (error) {
      console.error('Failed to calculate fare:', error);
      throw error;
    }
  }

  private getHardcodedCities(popularOnly: boolean = false): City[] {
    const cities: City[] = [
      { id: '1', name: 'Mumbai', state: 'Maharashtra', country: 'India', latitude: 19.0760, longitude: 72.8777, is_popular: true },
      { id: '2', name: 'Delhi', state: 'Delhi', country: 'India', latitude: 28.6139, longitude: 77.2090, is_popular: true },
      { id: '3', name: 'Bangalore', state: 'Karnataka', country: 'India', latitude: 12.9716, longitude: 77.5946, is_popular: true },
      { id: '4', name: 'Hyderabad', state: 'Telangana', country: 'India', latitude: 17.3850, longitude: 78.4867, is_popular: true },
      { id: '5', name: 'Chennai', state: 'Tamil Nadu', country: 'India', latitude: 13.0827, longitude: 80.2707, is_popular: true },
      { id: '6', name: 'Kolkata', state: 'West Bengal', country: 'India', latitude: 22.5726, longitude: 88.3639, is_popular: true },
      { id: '7', name: 'Pune', state: 'Maharashtra', country: 'India', latitude: 18.5204, longitude: 73.8567, is_popular: true },
      { id: '8', name: 'Ahmedabad', state: 'Gujarat', country: 'India', latitude: 23.0225, longitude: 72.5714, is_popular: true },
      { id: '9', name: 'Jaipur', state: 'Rajasthan', country: 'India', latitude: 26.9124, longitude: 75.7873, is_popular: true },
      { id: '10', name: 'Lucknow', state: 'Uttar Pradesh', country: 'India', latitude: 26.8467, longitude: 80.9462, is_popular: false },
      { id: '11', name: 'Surat', state: 'Gujarat', country: 'India', latitude: 21.1702, longitude: 72.8311, is_popular: false },
      { id: '12', name: 'Nagpur', state: 'Maharashtra', country: 'India', latitude: 21.1458, longitude: 79.0882, is_popular: false },
      { id: '13', name: 'Indore', state: 'Madhya Pradesh', country: 'India', latitude: 22.7196, longitude: 75.8577, is_popular: false },
      { id: '14', name: 'Bhopal', state: 'Madhya Pradesh', country: 'India', latitude: 23.2599, longitude: 77.4126, is_popular: false },
      { id: '15', name: 'Patna', state: 'Bihar', country: 'India', latitude: 25.5941, longitude: 85.1376, is_popular: false },
      { id: '16', name: 'Vadodara', state: 'Gujarat', country: 'India', latitude: 22.3072, longitude: 73.1812, is_popular: false },
      { id: '17', name: 'Ludhiana', state: 'Punjab', country: 'India', latitude: 30.9010, longitude: 75.8573, is_popular: false },
      { id: '18', name: 'Agra', state: 'Uttar Pradesh', country: 'India', latitude: 27.1767, longitude: 78.0081, is_popular: false },
      { id: '19', name: 'Nashik', state: 'Maharashtra', country: 'India', latitude: 19.9975, longitude: 73.7898, is_popular: false },
      { id: '20', name: 'Varanasi', state: 'Uttar Pradesh', country: 'India', latitude: 25.3176, longitude: 82.9739, is_popular: false },
    ];

    return popularOnly ? cities.filter(city => city.is_popular) : cities;
  }
}

export const geoService = GeoService.getInstance();

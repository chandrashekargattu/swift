import { CabType } from '@/types';

export const cabTypes: CabType[] = [
  {
    id: 'sedan',
    name: 'Sedan',
    description: 'Comfortable sedan for up to 4 passengers',
    capacity: 4,
    pricePerKm: 12,
    basePrice: 300,
    image: 'https://images.unsplash.com/photo-1550355291-bbee04a92027?w=800&q=80',
    features: ['AC', 'Music System', 'Comfortable Seats', 'GPS Navigation']
  },
  {
    id: 'suv',
    name: 'SUV',
    description: 'Spacious SUV for up to 6 passengers',
    capacity: 6,
    pricePerKm: 16,
    basePrice: 500,
    image: 'https://images.unsplash.com/photo-1519641471654-76ce0107ad1b?w=800&q=80',
    features: ['AC', 'Music System', 'Extra Luggage Space', 'GPS Navigation', 'Comfortable Seats']
  },
  {
    id: 'luxury',
    name: 'Luxury',
    description: 'Premium luxury sedan for special occasions',
    capacity: 4,
    pricePerKm: 25,
    basePrice: 800,
    image: 'https://images.unsplash.com/photo-1563720360172-67b8f3dce741?w=800&q=80',
    features: ['Premium AC', 'Premium Sound System', 'Leather Seats', 'GPS Navigation', 'Complimentary Water', 'WiFi']
  },
  {
    id: 'traveller',
    name: 'Tempo Traveller',
    description: 'Large vehicle for group travel up to 12 passengers',
    capacity: 12,
    pricePerKm: 22,
    basePrice: 1000,
    image: 'https://images.unsplash.com/photo-1544620347-c4fd4a3d5957?w=800&q=80',
    features: ['AC', 'Music System', 'Spacious', 'GPS Navigation', 'Comfortable Seats', 'Large Luggage Space']
  }
];

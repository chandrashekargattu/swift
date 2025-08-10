export interface Location {
  id: string;
  name: string;
  state: string;
  lat: number;
  lng: number;
  popular?: boolean;
}

export interface CabType {
  id: string;
  name: string;
  description: string;
  capacity: number;
  pricePerKm: number;
  basePrice: number;
  image: string;
  features: string[];
}

export interface BookingDetails {
  from: Location | null;
  to: Location | null;
  pickupDate: Date;
  pickupTime: string;
  returnDate?: Date;
  cabType: CabType | null;
  tripType: 'one-way' | 'round-trip';
  passengers: number;
  distance?: number;
  estimatedPrice?: number;
}

export interface PriceBreakdown {
  baseFare: number;
  distanceCharge: number;
  taxes: number;
  total: number;
  discount?: number;
}

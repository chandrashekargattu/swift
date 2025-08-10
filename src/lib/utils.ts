import { type ClassValue, clsx } from 'clsx';
import { twMerge } from 'tailwind-merge';

export function cn(...inputs: ClassValue[]) {
  return twMerge(clsx(inputs));
}

export function calculateDistance(lat1: number, lon1: number, lat2: number, lon2: number): number {
  const R = 6371; // Earth's radius in kilometers
  const dLat = (lat2 - lat1) * Math.PI / 180;
  const dLon = (lon2 - lon1) * Math.PI / 180;
  const a = 
    Math.sin(dLat/2) * Math.sin(dLat/2) +
    Math.cos(lat1 * Math.PI / 180) * Math.cos(lat2 * Math.PI / 180) *
    Math.sin(dLon/2) * Math.sin(dLon/2);
  const c = 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1-a));
  return R * c;
}

export function calculatePrice(distance: number, pricePerKm: number, basePrice: number): number {
  const distanceCharge = distance * pricePerKm;
  const subtotal = basePrice + distanceCharge;
  const taxes = subtotal * 0.18; // 18% GST
  return Math.round(subtotal + taxes);
}

export function formatPrice(price: number): string {
  return new Intl.NumberFormat('en-IN', {
    style: 'currency',
    currency: 'INR',
    minimumFractionDigits: 0,
    maximumFractionDigits: 0,
  }).format(price);
}

export function formatDistance(distance: number): string {
  return `${Math.round(distance)} km`;
}

export function formatDuration(distance: number): string {
  // Assuming average speed of 60 km/h for estimation
  const hours = distance / 60;
  const fullHours = Math.floor(hours);
  const minutes = Math.round((hours - fullHours) * 60);
  
  if (fullHours === 0) {
    return `${minutes} mins`;
  } else if (minutes === 0) {
    return `${fullHours} hr${fullHours > 1 ? 's' : ''}`;
  } else {
    return `${fullHours} hr${fullHours > 1 ? 's' : ''} ${minutes} mins`;
  }
}

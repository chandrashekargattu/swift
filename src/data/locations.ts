import { Location } from '@/types';

export const popularLocations: Location[] = [
  // Major Cities - North
  { id: 'del', name: 'New Delhi', state: 'Delhi', lat: 28.6139, lng: 77.2090, popular: true },
  { id: 'mum', name: 'Mumbai', state: 'Maharashtra', lat: 19.0760, lng: 72.8777, popular: true },
  { id: 'blr', name: 'Bangalore', state: 'Karnataka', lat: 12.9716, lng: 77.5946, popular: true },
  { id: 'kol', name: 'Kolkata', state: 'West Bengal', lat: 22.5726, lng: 88.3639, popular: true },
  { id: 'che', name: 'Chennai', state: 'Tamil Nadu', lat: 13.0827, lng: 80.2707, popular: true },
  { id: 'hyd', name: 'Hyderabad', state: 'Telangana', lat: 17.3850, lng: 78.4867, popular: true },
  { id: 'pun', name: 'Pune', state: 'Maharashtra', lat: 18.5204, lng: 73.8567, popular: true },
  { id: 'ahm', name: 'Ahmedabad', state: 'Gujarat', lat: 23.0225, lng: 72.5714, popular: true },
  
  // North India
  { id: 'jpr', name: 'Jaipur', state: 'Rajasthan', lat: 26.9124, lng: 75.7873 },
  { id: 'lko', name: 'Lucknow', state: 'Uttar Pradesh', lat: 26.8467, lng: 80.9462 },
  { id: 'agr', name: 'Agra', state: 'Uttar Pradesh', lat: 27.1767, lng: 78.0081 },
  { id: 'chd', name: 'Chandigarh', state: 'Chandigarh', lat: 30.7333, lng: 76.7794 },
  { id: 'ddn', name: 'Dehradun', state: 'Uttarakhand', lat: 30.3165, lng: 78.0322 },
  { id: 'sml', name: 'Shimla', state: 'Himachal Pradesh', lat: 31.1048, lng: 77.1734 },
  { id: 'amr', name: 'Amritsar', state: 'Punjab', lat: 31.6340, lng: 74.8723 },
  
  // South India
  { id: 'cbe', name: 'Coimbatore', state: 'Tamil Nadu', lat: 11.0168, lng: 76.9558 },
  { id: 'koc', name: 'Kochi', state: 'Kerala', lat: 9.9312, lng: 76.2673 },
  { id: 'tvm', name: 'Thiruvananthapuram', state: 'Kerala', lat: 8.5241, lng: 76.9366 },
  { id: 'mys', name: 'Mysore', state: 'Karnataka', lat: 12.2958, lng: 76.6394 },
  { id: 'viz', name: 'Visakhapatnam', state: 'Andhra Pradesh', lat: 17.6868, lng: 83.2185 },
  { id: 'mdu', name: 'Madurai', state: 'Tamil Nadu', lat: 9.9252, lng: 78.1198 },
  
  // West India
  { id: 'srt', name: 'Surat', state: 'Gujarat', lat: 21.1702, lng: 72.8311 },
  { id: 'vdz', name: 'Vadodara', state: 'Gujarat', lat: 22.3072, lng: 73.1812 },
  { id: 'nsk', name: 'Nashik', state: 'Maharashtra', lat: 19.9975, lng: 73.7898 },
  { id: 'ngp', name: 'Nagpur', state: 'Maharashtra', lat: 21.1458, lng: 79.0882 },
  { id: 'ind', name: 'Indore', state: 'Madhya Pradesh', lat: 22.7196, lng: 75.8577 },
  { id: 'bpl', name: 'Bhopal', state: 'Madhya Pradesh', lat: 23.2599, lng: 77.4126 },
  
  // East India
  { id: 'pat', name: 'Patna', state: 'Bihar', lat: 25.5941, lng: 85.1376 },
  { id: 'bhu', name: 'Bhubaneswar', state: 'Odisha', lat: 20.2961, lng: 85.8245 },
  { id: 'gwh', name: 'Guwahati', state: 'Assam', lat: 26.1445, lng: 91.7362 },
  { id: 'ran', name: 'Ranchi', state: 'Jharkhand', lat: 23.3441, lng: 85.3096 },
];

export const getLocationsByState = (state: string): Location[] => {
  return popularLocations.filter(loc => loc.state === state);
};

export const searchLocations = (query: string): Location[] => {
  const lowerQuery = query.toLowerCase();
  return popularLocations.filter(loc => 
    loc.name.toLowerCase().includes(lowerQuery) || 
    loc.state.toLowerCase().includes(lowerQuery)
  );
};

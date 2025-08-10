'use client';

import { useState, useEffect } from 'react';
import { useAuth } from '@/contexts/AuthContext';
import { apiClient } from '@/lib/api/client';

export default function DebugBookingPage() {
  const { user } = useAuth();
  const [token, setToken] = useState<string | null>(null);
  const [testResult, setTestResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get token from localStorage
    const accessToken = localStorage.getItem('access_token');
    setToken(accessToken);
  }, []);

  const testBookingAPI = async () => {
    setLoading(true);
    setTestResult('');

    try {
      const testBookingData = {
        pickup_location: {
          name: "Mumbai Airport",
          address: "Mumbai Airport, Maharashtra",
          city: "Mumbai",
          state: "Maharashtra",
          lat: 19.0896,
          lng: 72.8656
        },
        drop_location: {
          name: "Pune Railway Station",
          address: "Pune Railway Station, Maharashtra",
          city: "Pune",
          state: "Maharashtra",
          lat: 18.5196,
          lng: 73.8553
        },
        pickup_datetime: new Date(Date.now() + 24 * 60 * 60 * 1000).toISOString(), // Tomorrow
        trip_type: "one-way",
        cab_type: "sedan",
        passengers: 2,
        payment_method: "cash",
        special_requests: ""
      };

      console.log('Sending booking data:', testBookingData);
      
      const response = await apiClient.post('/api/v1/bookings/', testBookingData);
      setTestResult(`Success! Booking created: ${JSON.stringify(response, null, 2)}`);
    } catch (error: any) {
      console.error('Booking test failed:', error);
      setTestResult(`Error: ${error.message}\n\nDetails: ${JSON.stringify(error.data || error, null, 2)}`);
    } finally {
      setLoading(false);
    }
  };

  const refreshPage = () => {
    window.location.reload();
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-4xl mx-auto space-y-6">
        <h1 className="text-3xl font-bold">Debug Booking API</h1>
        
        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-semibold">Authentication Status</h2>
          
          <div className="space-y-2">
            <div className="flex items-center gap-2">
              <span className="font-medium">User:</span>
              <span className={user ? 'text-green-600' : 'text-red-600'}>
                {user ? `${user.email} (${user.full_name})` : 'Not logged in'}
              </span>
            </div>
            
            <div className="flex items-center gap-2">
              <span className="font-medium">Access Token:</span>
              <span className={token ? 'text-green-600' : 'text-red-600'}>
                {token ? `${token.substring(0, 20)}...` : 'No token found'}
              </span>
            </div>
          </div>

          <button
            onClick={refreshPage}
            className="px-4 py-2 bg-gray-600 text-white rounded hover:bg-gray-700"
          >
            Refresh Page
          </button>
        </div>

        <div className="bg-white rounded-lg shadow p-6 space-y-4">
          <h2 className="text-xl font-semibold">Test Booking API</h2>
          
          <button
            onClick={testBookingAPI}
            disabled={loading || !user}
            className="px-6 py-3 bg-blue-600 text-white rounded hover:bg-blue-700 disabled:opacity-50 disabled:cursor-not-allowed"
          >
            {loading ? 'Testing...' : 'Test Booking API'}
          </button>
          
          {!user && (
            <p className="text-red-600">You must be logged in to test the booking API</p>
          )}
          
          {testResult && (
            <div className="mt-4">
              <h3 className="font-semibold mb-2">Result:</h3>
              <pre className="p-4 bg-gray-100 rounded overflow-x-auto whitespace-pre-wrap">
                {testResult}
              </pre>
            </div>
          )}
        </div>

        <div className="bg-white rounded-lg shadow p-6">
          <h2 className="text-xl font-semibold mb-4">Debug Information</h2>
          
          <div className="space-y-2 text-sm">
            <p><strong>API URL:</strong> {process.env.NEXT_PUBLIC_API_URL || 'Not set'}</p>
            <p><strong>Browser:</strong> {typeof window !== 'undefined' ? navigator.userAgent : 'N/A'}</p>
            <p><strong>Local Storage Keys:</strong></p>
            <ul className="ml-4 list-disc">
              {typeof window !== 'undefined' && Object.keys(localStorage).map(key => (
                <li key={key}>{key}</li>
              ))}
            </ul>
          </div>
        </div>
      </div>
    </div>
  );
}

'use client';

import { useEffect, useState } from 'react';

export default function ApiTestPage() {
  const [apiUrl, setApiUrl] = useState<string>('');
  const [testResult, setTestResult] = useState<string>('');
  const [loading, setLoading] = useState(false);

  useEffect(() => {
    // Get the API URL from environment
    const url = process.env.NEXT_PUBLIC_API_URL || 'http://localhost:8000';
    setApiUrl(url);
  }, []);

  const testConnection = async () => {
    setLoading(true);
    setTestResult('');
    
    try {
      console.log('Testing API connection to:', apiUrl);
      
      // Test 1: Direct fetch to backend docs
      const response = await fetch(`${apiUrl}/docs`, {
        method: 'GET',
        mode: 'no-cors' // Try without CORS first
      });
      
      console.log('Response:', response);
      setTestResult(`Direct fetch result: ${response.type} (${response.status || 'opaque'})`);
      
      // Test 2: Try with CORS
      try {
        const corsResponse = await fetch(`${apiUrl}/api/v1/auth/login`, {
          method: 'POST',
          headers: {
            'Content-Type': 'application/json',
          },
          body: JSON.stringify({
            email: 'test@example.com',
            password: 'wrong'
          })
        });
        
        const data = await corsResponse.text();
        setTestResult(prev => prev + `\nCORS fetch: ${corsResponse.status} - ${data.substring(0, 100)}...`);
      } catch (corsError: any) {
        setTestResult(prev => prev + `\nCORS Error: ${corsError.message}`);
      }
      
    } catch (error: any) {
      console.error('Test error:', error);
      setTestResult(`Error: ${error.message}`);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="min-h-screen p-8 bg-gray-50">
      <div className="max-w-2xl mx-auto bg-white rounded-lg shadow p-6">
        <h1 className="text-2xl font-bold mb-6">API Connection Test</h1>
        
        <div className="space-y-4">
          <div>
            <label className="block text-sm font-medium text-gray-700">API URL:</label>
            <input
              type="text"
              value={apiUrl}
              onChange={(e) => setApiUrl(e.target.value)}
              className="mt-1 block w-full rounded-md border-gray-300 shadow-sm focus:border-blue-500 focus:ring-blue-500 sm:text-sm p-2 border"
            />
          </div>
          
          <div>
            <label className="block text-sm font-medium text-gray-700 mb-2">Environment Variable:</label>
            <code className="block p-3 bg-gray-100 rounded">
              NEXT_PUBLIC_API_URL = {process.env.NEXT_PUBLIC_API_URL || 'undefined'}
            </code>
          </div>
          
          <button
            onClick={testConnection}
            disabled={loading}
            className="w-full bg-blue-600 text-white rounded-md px-4 py-2 hover:bg-blue-700 disabled:opacity-50"
          >
            {loading ? 'Testing...' : 'Test Connection'}
          </button>
          
          {testResult && (
            <div>
              <label className="block text-sm font-medium text-gray-700 mb-2">Result:</label>
              <pre className="p-3 bg-gray-100 rounded whitespace-pre-wrap">{testResult}</pre>
            </div>
          )}
          
          <div className="mt-6 p-4 bg-yellow-50 rounded">
            <p className="text-sm text-gray-700">
              <strong>Debug Info:</strong><br/>
              - Open browser console for detailed logs<br/>
              - Backend should be running on {apiUrl}<br/>
              - Check Network tab for request details
            </p>
          </div>
        </div>
      </div>
    </div>
  );
}

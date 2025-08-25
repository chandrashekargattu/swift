'use client';

import React, { useState, useCallback } from 'react';
import { useDropzone } from 'react-dropzone';
import { Upload, Download, FileText, AlertCircle, CheckCircle, XCircle } from 'lucide-react';
import { apiClient } from '@/lib/api/client';
import { useAuth } from '@/contexts/AuthContext';
import { useRouter } from 'next/navigation';

interface UploadResult {
  total_rows: number;
  valid_rows: number;
  invalid_rows: number;
  errors: Array<{
    row: number;
    city: string;
    error: string;
  }>;
  message: string;
}

export default function CSVUploadPage() {
  const { user } = useAuth();
  const router = useRouter();
  const [file, setFile] = useState<File | null>(null);
  const [uploading, setUploading] = useState(false);
  const [result, setResult] = useState<UploadResult | null>(null);
  const [uploadType, setUploadType] = useState<'kafka' | 'direct'>('direct');

  // Redirect if not admin
  React.useEffect(() => {
    if (user && user.role !== 'admin') {
      router.push('/');
    }
  }, [user, router]);

  const onDrop = useCallback((acceptedFiles: File[]) => {
    if (acceptedFiles.length > 0) {
      setFile(acceptedFiles[0]);
      setResult(null);
    }
  }, []);

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: {
      'text/csv': ['.csv']
    },
    maxFiles: 1
  });

  const handleUpload = async () => {
    if (!file) return;

    setUploading(true);
    setResult(null);

    const formData = new FormData();
    formData.append('file', file);

    try {
      const endpoint = uploadType === 'kafka' 
        ? '/api/v1/csv-upload/upload'
        : '/api/v1/csv-upload/upload-direct';

      const response = await apiClient.post(endpoint, formData, {
        headers: {
          'Content-Type': 'multipart/form-data'
        }
      });

      setResult(response);
    } catch (error: any) {
      setResult({
        total_rows: 0,
        valid_rows: 0,
        invalid_rows: 0,
        errors: [],
        message: error.response?.data?.detail || 'Upload failed'
      });
    } finally {
      setUploading(false);
    }
  };

  const downloadTemplate = async () => {
    try {
      const response = await apiClient.get('/api/v1/csv-upload/template');
      const blob = new Blob([response.content], { type: 'text/csv' });
      const url = window.URL.createObjectURL(blob);
      const a = document.createElement('a');
      a.href = url;
      a.download = response.filename;
      a.click();
      window.URL.revokeObjectURL(url);
    } catch (error) {
      console.error('Failed to download template:', error);
    }
  };

  const downloadSample = () => {
    const sampleData = `city_name,state,latitude,longitude,pincode,district,is_metro,is_capital,population,area_sq_km,alternate_names
Mumbai,Maharashtra,19.0760,72.8777,400001,Mumbai,true,false,20411000,603.4,"Bombay"
Delhi,Delhi,28.6139,77.2090,110001,New Delhi,true,true,32941000,1484,"New Delhi,NCR"
Bengaluru,Karnataka,12.9716,77.5946,560001,Bengaluru Urban,true,true,13193000,741,"Bangalore,Silicon Valley of India"`;
    
    const blob = new Blob([sampleData], { type: 'text/csv' });
    const url = window.URL.createObjectURL(blob);
    const a = document.createElement('a');
    a.href = url;
    a.download = 'sample_cities.csv';
    a.click();
    window.URL.revokeObjectURL(url);
  };

  if (!user || user.role !== 'admin') {
    return (
      <div className="min-h-screen flex items-center justify-center">
        <div className="text-center">
          <AlertCircle className="w-12 h-12 text-red-500 mx-auto mb-4" />
          <h2 className="text-xl font-semibold">Admin Access Required</h2>
          <p className="text-gray-600 mt-2">You need admin privileges to access this page.</p>
        </div>
      </div>
    );
  }

  return (
    <div className="min-h-screen bg-gray-50 py-12 px-4 sm:px-6 lg:px-8">
      <div className="max-w-4xl mx-auto">
        <div className="bg-white rounded-lg shadow-xl p-8">
          <h1 className="text-3xl font-bold text-gray-900 mb-8">City Data CSV Upload</h1>

          {/* Format Requirements */}
          <div className="bg-blue-50 rounded-lg p-6 mb-8">
            <h3 className="text-lg font-semibold text-blue-900 mb-4">CSV Format Requirements</h3>
            <div className="grid grid-cols-2 md:grid-cols-3 gap-3">
              <div className="flex items-center">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                <span className="text-sm">city_name (required)</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                <span className="text-sm">state (required)</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                <span className="text-sm">latitude (required)</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-red-500 rounded-full mr-2"></span>
                <span className="text-sm">longitude (required)</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">pincode</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">district</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">is_metro</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">is_capital</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">population</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">area_sq_km</span>
              </div>
              <div className="flex items-center">
                <span className="w-2 h-2 bg-blue-500 rounded-full mr-2"></span>
                <span className="text-sm">alternate_names</span>
              </div>
            </div>
            <div className="mt-4 flex gap-4">
              <button
                onClick={downloadTemplate}
                className="flex items-center gap-2 px-4 py-2 bg-white text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50"
              >
                <Download className="w-4 h-4" />
                Download Template
              </button>
              <button
                onClick={downloadSample}
                className="flex items-center gap-2 px-4 py-2 bg-white text-blue-600 border border-blue-300 rounded-lg hover:bg-blue-50"
              >
                <FileText className="w-4 h-4" />
                Sample Data
              </button>
            </div>
          </div>

          {/* Upload Area */}
          <div
            {...getRootProps()}
            className={`border-3 border-dashed rounded-lg p-8 text-center cursor-pointer transition-colors ${
              isDragActive
                ? 'border-purple-500 bg-purple-50'
                : 'border-gray-300 hover:border-purple-400 hover:bg-gray-50'
            }`}
          >
            <input {...getInputProps()} />
            <Upload className="w-12 h-12 mx-auto mb-4 text-gray-400" />
            {file ? (
              <div>
                <p className="text-lg font-medium">{file.name}</p>
                <p className="text-sm text-gray-500">{(file.size / 1024).toFixed(2)} KB</p>
              </div>
            ) : (
              <div>
                <p className="text-lg font-medium">Drag & drop your CSV file here</p>
                <p className="text-sm text-gray-500 mt-2">or click to browse</p>
              </div>
            )}
          </div>

          {/* Upload Options */}
          {file && (
            <div className="mt-6">
              <div className="flex items-center justify-center gap-4 mb-4">
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="direct"
                    checked={uploadType === 'direct'}
                    onChange={(e) => setUploadType(e.target.value as 'direct')}
                    className="mr-2"
                  />
                  <span className="text-sm">Direct Import (Recommended)</span>
                </label>
                <label className="flex items-center">
                  <input
                    type="radio"
                    value="kafka"
                    checked={uploadType === 'kafka'}
                    onChange={(e) => setUploadType(e.target.value as 'kafka')}
                    className="mr-2"
                  />
                  <span className="text-sm">Via Kafka (Event Streaming)</span>
                </label>
              </div>
              <button
                onClick={handleUpload}
                disabled={uploading}
                className={`w-full py-3 px-4 rounded-lg font-medium transition-colors ${
                  uploading
                    ? 'bg-gray-300 cursor-not-allowed'
                    : 'bg-purple-600 hover:bg-purple-700 text-white'
                }`}
              >
                {uploading ? 'Uploading...' : `Upload ${uploadType === 'kafka' ? 'to Kafka' : 'Directly'}`}
              </button>
            </div>
          )}

          {/* Results */}
          {result && (
            <div className={`mt-8 p-6 rounded-lg ${
              result.invalid_rows > 0 
                ? 'bg-yellow-50 border border-yellow-200' 
                : 'bg-green-50 border border-green-200'
            }`}>
              <div className="flex items-start gap-4">
                {result.invalid_rows > 0 ? (
                  <AlertCircle className="w-6 h-6 text-yellow-600 flex-shrink-0" />
                ) : (
                  <CheckCircle className="w-6 h-6 text-green-600 flex-shrink-0" />
                )}
                <div className="flex-1">
                  <h3 className="font-semibold text-lg">{result.message}</h3>
                  <div className="grid grid-cols-3 gap-4 mt-4">
                    <div className="text-center">
                      <div className="text-2xl font-bold">{result.total_rows}</div>
                      <div className="text-sm text-gray-600">Total Rows</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-green-600">{result.valid_rows}</div>
                      <div className="text-sm text-gray-600">Valid Rows</div>
                    </div>
                    <div className="text-center">
                      <div className="text-2xl font-bold text-red-600">{result.invalid_rows}</div>
                      <div className="text-sm text-gray-600">Invalid Rows</div>
                    </div>
                  </div>
                  
                  {result.errors.length > 0 && (
                    <div className="mt-4">
                      <h4 className="font-medium mb-2">Errors:</h4>
                      <div className="space-y-2 max-h-48 overflow-y-auto">
                        {result.errors.map((error, index) => (
                          <div key={index} className="bg-white p-3 rounded border border-red-200 text-sm">
                            <span className="font-medium">Row {error.row}</span>
                            <span className="text-gray-600"> ({error.city}):</span>
                            <span className="text-red-600 ml-2">{error.error}</span>
                          </div>
                        ))}
                      </div>
                    </div>
                  )}
                </div>
              </div>
            </div>
          )}
        </div>
      </div>
    </div>
  );
}

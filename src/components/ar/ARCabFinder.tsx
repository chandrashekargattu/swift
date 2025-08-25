'use client';

import React, { useState, useEffect, useRef } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { 
  Camera, 
  Navigation, 
  Car, 
  User, 
  X, 
  Maximize,
  Info,
  Phone,
  MessageCircle,
  MapPin,
  Compass
} from 'lucide-react';

interface ARCabFinderProps {
  bookingId: string;
  cabDetails: {
    plateNumber: string;
    model: string;
    color: string;
    driverName: string;
    driverPhone: string;
    location: {
      lat: number;
      lng: number;
    };
    distance: number;
    eta: number;
  };
  userLocation: {
    lat: number;
    lng: number;
  };
  onClose: () => void;
}

export default function ARCabFinder({ 
  bookingId, 
  cabDetails, 
  userLocation,
  onClose 
}: ARCabFinderProps) {
  const [isARActive, setIsARActive] = useState(false);
  const [cameraStream, setCameraStream] = useState<MediaStream | null>(null);
  const [heading, setHeading] = useState(0);
  const [distance, setDistance] = useState(cabDetails.distance);
  const [arError, setArError] = useState<string | null>(null);
  const videoRef = useRef<HTMLVideoElement>(null);
  const canvasRef = useRef<HTMLCanvasElement>(null);

  useEffect(() => {
    if (isARActive) {
      startAR();
    } else {
      stopAR();
    }

    return () => stopAR();
  }, [isARActive]);

  useEffect(() => {
    // Update distance in real-time
    const interval = setInterval(() => {
      // In real app, this would fetch real-time location
      setDistance(prev => Math.max(0, prev - 0.5));
    }, 1000);

    return () => clearInterval(interval);
  }, []);

  const startAR = async () => {
    try {
      // Request camera permission
      const stream = await navigator.mediaDevices.getUserMedia({
        video: { 
          facingMode: 'environment',
          width: { ideal: 1920 },
          height: { ideal: 1080 }
        }
      });

      setCameraStream(stream);
      if (videoRef.current) {
        videoRef.current.srcObject = stream;
      }

      // Start device orientation tracking
      if (window.DeviceOrientationEvent) {
        window.addEventListener('deviceorientation', handleOrientation);
      }

      // Start AR rendering
      renderAR();
    } catch (error) {
      console.error('AR Error:', error);
      setArError('Unable to access camera. Please check permissions.');
    }
  };

  const stopAR = () => {
    if (cameraStream) {
      cameraStream.getTracks().forEach(track => track.stop());
      setCameraStream(null);
    }
    window.removeEventListener('deviceorientation', handleOrientation);
  };

  const handleOrientation = (event: DeviceOrientationEvent) => {
    if (event.alpha !== null) {
      setHeading(event.alpha);
    }
  };

  const calculateBearing = () => {
    // Calculate bearing from user to cab
    const lat1 = userLocation.lat * Math.PI / 180;
    const lat2 = cabDetails.location.lat * Math.PI / 180;
    const deltaLng = (cabDetails.location.lng - userLocation.lng) * Math.PI / 180;

    const x = Math.sin(deltaLng) * Math.cos(lat2);
    const y = Math.cos(lat1) * Math.sin(lat2) - 
              Math.sin(lat1) * Math.cos(lat2) * Math.cos(deltaLng);

    const bearing = Math.atan2(x, y) * 180 / Math.PI;
    return (bearing + 360) % 360;
  };

  const renderAR = () => {
    if (!canvasRef.current || !videoRef.current) return;

    const canvas = canvasRef.current;
    const ctx = canvas.getContext('2d');
    const video = videoRef.current;

    const draw = () => {
      if (!ctx) return;

      // Set canvas size
      canvas.width = video.videoWidth;
      canvas.height = video.videoHeight;

      // Draw video frame
      ctx.drawImage(video, 0, 0, canvas.width, canvas.height);

      // Calculate position for AR overlay
      const bearing = calculateBearing();
      const relativeBearing = (bearing - heading + 360) % 360;
      
      // Check if cab is in view (within 30 degrees)
      if (relativeBearing > 330 || relativeBearing < 30) {
        // Draw AR marker
        const centerX = canvas.width / 2 + (relativeBearing - 360) * 20;
        const centerY = canvas.height / 2;

        // Draw distance indicator
        ctx.fillStyle = 'rgba(59, 130, 246, 0.8)';
        ctx.beginPath();
        ctx.arc(centerX, centerY, 80, 0, 2 * Math.PI);
        ctx.fill();

        // Draw car icon
        ctx.fillStyle = 'white';
        ctx.font = '48px Arial';
        ctx.textAlign = 'center';
        ctx.fillText('🚗', centerX, centerY + 15);

        // Draw distance
        ctx.fillStyle = 'white';
        ctx.font = 'bold 20px Arial';
        ctx.fillText(`${distance.toFixed(0)}m`, centerX, centerY + 50);

        // Draw plate number
        ctx.fillStyle = 'rgba(0, 0, 0, 0.7)';
        ctx.fillRect(centerX - 60, centerY - 100, 120, 30);
        ctx.fillStyle = 'white';
        ctx.font = '16px Arial';
        ctx.fillText(cabDetails.plateNumber, centerX, centerY - 80);

        // Draw arrow pointing down
        ctx.beginPath();
        ctx.moveTo(centerX, centerY + 80);
        ctx.lineTo(centerX - 20, centerY + 100);
        ctx.lineTo(centerX + 20, centerY + 100);
        ctx.closePath();
        ctx.fill();
      } else {
        // Draw direction indicator
        const edgeX = relativeBearing > 180 ? 50 : canvas.width - 50;
        ctx.fillStyle = 'rgba(59, 130, 246, 0.8)';
        ctx.beginPath();
        if (relativeBearing > 180) {
          // Arrow pointing left
          ctx.moveTo(edgeX, canvas.height / 2);
          ctx.lineTo(edgeX + 30, canvas.height / 2 - 20);
          ctx.lineTo(edgeX + 30, canvas.height / 2 + 20);
        } else {
          // Arrow pointing right
          ctx.moveTo(edgeX, canvas.height / 2);
          ctx.lineTo(edgeX - 30, canvas.height / 2 - 20);
          ctx.lineTo(edgeX - 30, canvas.height / 2 + 20);
        }
        ctx.closePath();
        ctx.fill();
      }

      requestAnimationFrame(draw);
    };

    video.addEventListener('loadedmetadata', draw);
  };

  return (
    <AnimatePresence>
      <motion.div
        initial={{ opacity: 0 }}
        animate={{ opacity: 1 }}
        exit={{ opacity: 0 }}
        className="fixed inset-0 z-50 bg-black"
      >
        {!isARActive ? (
          // AR Preview Screen
          <div className="relative h-full flex flex-col">
            <div className="absolute inset-0 bg-gradient-to-br from-blue-900 via-purple-900 to-black opacity-90" />
            
            <div className="relative z-10 flex-1 flex flex-col p-6">
              {/* Header */}
              <div className="flex justify-between items-center mb-8">
                <h2 className="text-2xl font-bold text-white">Find Your Cab</h2>
                <button
                  onClick={onClose}
                  className="p-2 bg-white/20 rounded-full hover:bg-white/30 transition-colors"
                >
                  <X className="w-6 h-6 text-white" />
                </button>
              </div>

              {/* Cab Details */}
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8">
                <div className="flex items-center justify-between mb-4">
                  <div>
                    <p className="text-white/60 text-sm">Your Cab</p>
                    <p className="text-2xl font-bold text-white">{cabDetails.plateNumber}</p>
                  </div>
                  <div className="w-16 h-16 bg-white/20 rounded-full flex items-center justify-center">
                    <Car className="w-8 h-8 text-white" />
                  </div>
                </div>
                
                <div className="grid grid-cols-2 gap-4 mb-4">
                  <div>
                    <p className="text-white/60 text-sm">Model</p>
                    <p className="text-white font-medium">{cabDetails.model}</p>
                  </div>
                  <div>
                    <p className="text-white/60 text-sm">Color</p>
                    <p className="text-white font-medium">{cabDetails.color}</p>
                  </div>
                </div>

                <div className="border-t border-white/20 pt-4">
                  <div className="flex items-center justify-between">
                    <div className="flex items-center gap-3">
                      <div className="w-10 h-10 bg-white/20 rounded-full flex items-center justify-center">
                        <User className="w-5 h-5 text-white" />
                      </div>
                      <div>
                        <p className="text-white font-medium">{cabDetails.driverName}</p>
                        <p className="text-white/60 text-sm">Driver</p>
                      </div>
                    </div>
                    <div className="flex gap-2">
                      <button className="p-2 bg-green-500 rounded-full hover:bg-green-600 transition-colors">
                        <Phone className="w-5 h-5 text-white" />
                      </button>
                      <button className="p-2 bg-blue-500 rounded-full hover:bg-blue-600 transition-colors">
                        <MessageCircle className="w-5 h-5 text-white" />
                      </button>
                    </div>
                  </div>
                </div>
              </div>

              {/* Distance Info */}
              <div className="bg-white/10 backdrop-blur-md rounded-2xl p-6 mb-8">
                <div className="flex items-center justify-between">
                  <div className="flex items-center gap-3">
                    <Navigation className="w-6 h-6 text-blue-400" />
                    <div>
                      <p className="text-white font-medium">{distance}m away</p>
                      <p className="text-white/60 text-sm">ETA: {cabDetails.eta} mins</p>
                    </div>
                  </div>
                  <div className="w-20 h-20">
                    <svg className="w-full h-full" viewBox="0 0 100 100">
                      <circle
                        cx="50"
                        cy="50"
                        r="45"
                        fill="none"
                        stroke="rgba(255,255,255,0.2)"
                        strokeWidth="8"
                      />
                      <circle
                        cx="50"
                        cy="50"
                        r="45"
                        fill="none"
                        stroke="url(#gradient)"
                        strokeWidth="8"
                        strokeDasharray={`${(1 - distance / 1000) * 283} 283`}
                        transform="rotate(-90 50 50)"
                      />
                      <defs>
                        <linearGradient id="gradient">
                          <stop offset="0%" stopColor="#3B82F6" />
                          <stop offset="100%" stopColor="#8B5CF6" />
                        </linearGradient>
                      </defs>
                    </svg>
                  </div>
                </div>
              </div>

              {/* AR Instructions */}
              <div className="bg-gradient-to-r from-blue-500/20 to-purple-500/20 rounded-2xl p-6 mb-8">
                <h3 className="text-white font-semibold mb-3 flex items-center gap-2">
                  <Info className="w-5 h-5" />
                  How AR Finder Works
                </h3>
                <ol className="text-white/80 text-sm space-y-2">
                  <li>1. Point your phone camera towards the street</li>
                  <li>2. Follow the on-screen indicators to locate your cab</li>
                  <li>3. Look for the blue marker showing your cab\'s position</li>
                  <li>4. The marker will show distance and plate number</li>
                </ol>
              </div>

              {/* Start AR Button */}
              <motion.button
                whileHover={{ scale: 1.05 }}
                whileTap={{ scale: 0.95 }}
                onClick={() => setIsARActive(true)}
                className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white font-bold py-4 rounded-2xl flex items-center justify-center gap-3 hover:shadow-2xl transition-all"
              >
                <Camera className="w-6 h-6" />
                Start AR Cab Finder
              </motion.button>
            </div>
          </div>
        ) : (
          // AR Camera View
          <div className="relative h-full">
            <video
              ref={videoRef}
              autoPlay
              playsInline
              className="absolute inset-0 w-full h-full object-cover"
            />
            <canvas
              ref={canvasRef}
              className="absolute inset-0 w-full h-full"
            />
            
            {/* AR Overlay UI */}
            <div className="absolute inset-0 pointer-events-none">
              {/* Top Bar */}
              <div className="bg-gradient-to-b from-black/50 to-transparent p-4">
                <div className="flex justify-between items-center">
                  <div className="bg-black/50 backdrop-blur-md rounded-full px-4 py-2">
                    <p className="text-white font-medium">{cabDetails.plateNumber}</p>
                  </div>
                  <div className="bg-black/50 backdrop-blur-md rounded-full px-4 py-2 flex items-center gap-2">
                    <MapPin className="w-4 h-4 text-white" />
                    <p className="text-white font-medium">{distance}m</p>
                  </div>
                </div>
              </div>

              {/* Compass */}
              <div className="absolute top-1/2 left-4 -translate-y-1/2">
                <div className="relative w-16 h-16">
                  <Compass className="w-full h-full text-white/50" />
                  <div 
                    className="absolute inset-2 flex items-center justify-center"
                    style={{ transform: `rotate(${-heading}deg)` }}
                  >
                    <div className="w-1 h-6 bg-red-500" />
                  </div>
                </div>
              </div>
            </div>

            {/* Close Button */}
            <button
              onClick={() => setIsARActive(false)}
              className="absolute top-4 right-4 p-3 bg-black/50 backdrop-blur-md rounded-full hover:bg-black/70 transition-colors pointer-events-auto"
            >
              <X className="w-6 h-6 text-white" />
            </button>

            {/* Error Message */}
            {arError && (
              <div className="absolute bottom-20 left-4 right-4 bg-red-500 text-white p-4 rounded-lg">
                {arError}
              </div>
            )}
          </div>
        )}
      </motion.div>
    </AnimatePresence>
  );
}

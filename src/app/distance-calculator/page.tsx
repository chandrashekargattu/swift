"use client";

import { useState, useEffect } from "react";
import { motion } from "framer-motion";
import { MapPin, Calculator, Car, Clock } from "lucide-react";
import { geoService, City } from "@/services/geo";

export default function DistanceCalculator() {
  const [cities, setCities] = useState<City[]>([]);
  const [originCity, setOriginCity] = useState<string>("");
  const [destinationCity, setDestinationCity] = useState<string>("");
  const [routeInfo, setRouteInfo] = useState<any>(null);
  const [loading, setLoading] = useState(false);
  const [error, setError] = useState<string>("");

  useEffect(() => {
    // Fetch cities on mount
    geoService.fetchCities().then(setCities).catch(console.error);
  }, []);

  const calculateRoute = async () => {
    if (!originCity || !destinationCity) {
      setError("Please select both origin and destination cities");
      return;
    }

    if (originCity === destinationCity) {
      setError("Origin and destination cannot be the same");
      return;
    }

    setLoading(true);
    setError("");
    setRouteInfo(null);

    try {
      const info = await geoService.getRouteInfo(originCity, destinationCity);
      setRouteInfo(info);
    } catch (err: any) {
      setError(err.message || "Failed to calculate route");
    } finally {
      setLoading(false);
    }
  };

  return (
    <main className="min-h-screen pt-20">
      <section className="py-16 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Dynamic Distance Calculator
            </h1>
            <p className="text-lg text-gray-600">
              Calculate accurate driving distances between cities using our advanced routing algorithm
            </p>
          </motion.div>

          <div className="max-w-2xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              animate={{ opacity: 1, y: 0 }}
              transition={{ duration: 0.5, delay: 0.1 }}
              className="bg-white rounded-xl shadow-lg p-8"
            >
              <div className="grid md:grid-cols-2 gap-6 mb-6">
                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MapPin className="w-4 h-4 inline mr-1" />
                    Origin City
                  </label>
                  <select
                    value={originCity}
                    onChange={(e) => setOriginCity(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select origin city</option>
                    {cities.map((city) => (
                      <option key={city.id} value={city.name}>
                        {city.name}, {city.state}
                      </option>
                    ))}
                  </select>
                </div>

                <div>
                  <label className="block text-sm font-medium text-gray-700 mb-2">
                    <MapPin className="w-4 h-4 inline mr-1" />
                    Destination City
                  </label>
                  <select
                    value={destinationCity}
                    onChange={(e) => setDestinationCity(e.target.value)}
                    className="w-full px-4 py-3 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                  >
                    <option value="">Select destination city</option>
                    {cities.map((city) => (
                      <option key={city.id} value={city.name}>
                        {city.name}, {city.state}
                      </option>
                    ))}
                  </select>
                </div>
              </div>

              {error && (
                <div className="mb-4 p-3 bg-red-50 text-red-600 rounded-lg">
                  {error}
                </div>
              )}

              <button
                onClick={calculateRoute}
                disabled={loading}
                className="w-full bg-blue-600 text-white py-3 rounded-lg hover:bg-blue-700 transition-colors disabled:bg-gray-400 flex items-center justify-center gap-2"
              >
                {loading ? (
                  <>
                    <div className="animate-spin h-5 w-5 border-2 border-white border-t-transparent rounded-full"></div>
                    Calculating...
                  </>
                ) : (
                  <>
                    <Calculator className="w-5 h-5" />
                    Calculate Distance
                  </>
                )}
              </button>

              {routeInfo && (
                <motion.div
                  initial={{ opacity: 0, y: 20 }}
                  animate={{ opacity: 1, y: 0 }}
                  className="mt-8 space-y-6"
                >
                  <div className="text-center">
                    <h3 className="text-xl font-semibold mb-2">Route Information</h3>
                    <p className="text-gray-600">
                      {routeInfo.origin.name} → {routeInfo.destination.name}
                    </p>
                  </div>

                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-blue-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Car className="w-5 h-5 text-blue-600" />
                        <span className="font-medium">Driving Distance</span>
                      </div>
                      <p className="text-2xl font-bold text-blue-600">
                        {routeInfo.driving_distance_km} km
                      </p>
                    </div>

                    <div className="bg-green-50 rounded-lg p-4">
                      <div className="flex items-center gap-2 mb-2">
                        <Clock className="w-5 h-5 text-green-600" />
                        <span className="font-medium">Estimated Time</span>
                      </div>
                      <p className="text-2xl font-bold text-green-600">
                        {routeInfo.estimated_time_formatted}
                      </p>
                    </div>
                  </div>

                  <div className="border-t pt-4">
                    <div className="space-y-2 text-sm">
                      <div className="flex justify-between">
                        <span className="text-gray-600">Straight Line Distance:</span>
                        <span className="font-medium">
                          {routeInfo.straight_line_distance_km} km
                        </span>
                      </div>
                      <div className="flex justify-between">
                        <span className="text-gray-600">Route Efficiency:</span>
                        <span className="font-medium">
                          {((routeInfo.straight_line_distance_km / routeInfo.driving_distance_km) * 100).toFixed(1)}%
                        </span>
                      </div>
                    </div>
                  </div>

                  <div className="bg-amber-50 border border-amber-200 rounded-lg p-4">
                    <p className="text-sm text-amber-800">
                      <strong>Note:</strong> The driving distance is calculated using actual road routes 
                      and takes into account highways, roads, and typical driving conditions. 
                      This provides more accurate fare calculations than straight-line distance.
                    </p>
                  </div>
                </motion.div>
              )}
            </motion.div>
          </div>
        </div>
      </section>
    </main>
  );
}

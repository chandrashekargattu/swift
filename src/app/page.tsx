'use client';

import { Shield, Clock, CreditCard, HeadphonesIcon, MapPin, Star, Users, Car, Phone, ChevronRight, CheckCircle } from 'lucide-react';
import { motion } from 'framer-motion';
import Link from 'next/link';
import { popularLocations } from '@/data/locations';
import { cabTypes as cabs } from '@/data/cabs';
import BookingForm from '@/components/booking/BookingForm';

export default function Home() {
  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-blue-50 via-white to-purple-50">
        <div className="container mx-auto px-4">
          <div className="max-w-7xl mx-auto">
            <div className="grid lg:grid-cols-2 gap-12 items-center">
              {/* Left Content */}
              <motion.div 
                initial={{ opacity: 0, x: -50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6 }}
              >
                <h1 className="text-4xl md:text-5xl lg:text-6xl font-bold mb-6">
                  Travel Comfortably Across{' '}
                  <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">
                    India
                  </span>
                </h1>
                <p className="text-lg md:text-xl text-gray-600 mb-8">
                  Book reliable interstate cabs for comfortable long-distance travel. 
                  Professional drivers, transparent pricing, and 24/7 support.
                </p>
                
                {/* Trust Badge */}
                <div className="flex items-center space-x-4 mb-8">
                  <div className="flex items-center">
                    <Star className="w-5 h-5 text-yellow-400 fill-current" />
                    <span className="ml-1 font-semibold">4.3</span>
                    <span className="ml-2 text-sm text-gray-600">Average Rating</span>
                  </div>
                  <div className="text-gray-400">•</div>
                  <div className="text-sm text-gray-600">
                    {(() => {
                      const startDate = new Date('2025-08-10');
                      const currentDate = new Date();
                      const monthsInOperation = Math.max(0, Math.floor((currentDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 30)));
                      const baseCustomers = 50;
                      const customerGrowthRate = 35;
                      const totalCustomers = Math.max(0, baseCustomers + (monthsInOperation * customerGrowthRate));
                      return totalCustomers > 0 ? `${totalCustomers}+ Happy Customers` : 'Launching Soon';
                    })()}
                  </div>
                </div>
                
                <div className="flex flex-col sm:flex-row gap-4 mb-12">
                  <Link href="/fleet" className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-4 rounded-lg hover:shadow-lg transition-all flex items-center justify-center space-x-2 group">
                    <span>Book Your Ride</span>
                    <ChevronRight className="w-5 h-5 transform group-hover:translate-x-1 transition-transform" />
                  </Link>
                  <button className="border-2 border-gray-300 text-gray-700 px-8 py-4 rounded-lg hover:border-blue-500 hover:text-blue-600 transition-all flex items-center justify-center space-x-2">
                    <Phone className="w-5 h-5" />
                    <span>+91 8143243584</span>
                  </button>
                </div>

                {/* Features Grid */}
                <div className="grid grid-cols-2 gap-4">
                  {[
                    { icon: Shield, text: 'Safe & Secure' },
                    { icon: Clock, text: '24/7 Available' },
                    { icon: CreditCard, text: 'Transparent Pricing' },
                    { icon: HeadphonesIcon, text: 'Customer Support' }
                  ].map((feature, index) => (
                    <motion.div 
                      key={index}
                      initial={{ opacity: 0, y: 20 }}
                      animate={{ opacity: 1, y: 0 }}
                      transition={{ delay: index * 0.1 + 0.3 }}
                      className="flex items-center space-x-3 bg-white p-3 rounded-lg shadow-sm"
                    >
                      <feature.icon className="w-5 h-5 text-blue-600" />
                      <span className="text-sm font-medium">{feature.text}</span>
                    </motion.div>
                  ))}
                </div>
              </motion.div>

              {/* Right Content - Booking Form */}
              <motion.div 
                initial={{ opacity: 0, x: 50 }}
                animate={{ opacity: 1, x: 0 }}
                transition={{ duration: 0.6, delay: 0.2 }}
                className="lg:pl-12"
              >
                <div className="bg-white rounded-2xl shadow-xl p-6 md:p-8">
                  <h2 className="text-2xl font-bold mb-6">Quick Booking</h2>
                  <BookingForm />
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Why Choose Us Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Why Choose RideSwift?</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Experience the best interstate travel service with our commitment to safety, comfort, and reliability.
            </p>
          </div>

          <div className="grid md:grid-cols-3 gap-8">
            {[
              {
                title: 'Professional Drivers',
                description: 'Experienced and verified drivers for your safe journey',
                icon: Users,
                color: 'blue'
              },
              {
                title: 'Best Prices',
                description: 'Transparent pricing with no hidden charges',
                icon: CreditCard,
                color: 'purple'
              },
              {
                title: '24/7 Support',
                description: 'Round the clock customer support for your assistance',
                icon: HeadphonesIcon,
                color: 'green'
              }
            ].map((feature, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className={`inline-flex items-center justify-center w-16 h-16 rounded-full bg-${feature.color}-100 mb-4`}>
                  <feature.icon className={`w-8 h-8 text-${feature.color}-600`} />
                </div>
                <h3 className="text-xl font-semibold mb-2">{feature.title}</h3>
                <p className="text-gray-600">{feature.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Popular Routes Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Popular Interstate Routes</h2>
            <p className="text-gray-600">Most frequently booked routes by our customers</p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-6">
            {[
              { from: 'Hyderabad', to: 'Bangalore', distance: '570 km', duration: '8 hours' },
              { from: 'Hyderabad', to: 'Chennai', distance: '520 km', duration: '8 hours' },
              { from: 'Hyderabad', to: 'Mumbai', distance: '710 km', duration: '10 hours' },
              { from: 'Delhi', to: 'Jaipur', distance: '280 km', duration: '5 hours' },
              { from: 'Bangalore', to: 'Chennai', distance: '350 km', duration: '6 hours' },
              { from: 'Mumbai', to: 'Pune', distance: '150 km', duration: '3 hours' }
            ].map((route, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl p-6 shadow-sm hover:shadow-lg transition-all cursor-pointer"
              >
                <div className="flex items-center justify-between mb-4">
                  <div className="flex items-center space-x-3">
                    <MapPin className="w-5 h-5 text-blue-600" />
                    <span className="font-semibold">{route.from}</span>
                  </div>
                  <div className="flex-1 mx-4 border-t-2 border-dashed"></div>
                  <div className="flex items-center space-x-3">
                    <span className="font-semibold">{route.to}</span>
                    <MapPin className="w-5 h-5 text-purple-600" />
                  </div>
                </div>
                <div className="flex justify-between text-sm text-gray-600">
                  <span>{route.distance}</span>
                  <span>{route.duration}</span>
                </div>
              </motion.div>
            ))}
          </div>
          
          <div className="text-center mt-8">
            <Link href="/pricing" className="inline-flex items-center space-x-2 text-blue-600 hover:text-blue-700 transition-colors">
              <span>View all routes and pricing</span>
              <ChevronRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Our Fleet Preview */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Our Fleet</h2>
            <p className="text-gray-600">Choose from our wide range of comfortable vehicles</p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6">
            {cabs.slice(0, 4).map((cab, index) => {
              const icons: Record<string, string> = {
                sedan: '🚗',
                suv: '🚙',
                luxury: '🚘',
                traveller: '🚐'
              };
              
              return (
                <motion.div
                  key={cab.id}
                  initial={{ opacity: 0, y: 20 }}
                  whileInView={{ opacity: 1, y: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className="bg-white rounded-xl shadow-sm hover:shadow-lg transition-all"
                >
                  <div className="p-6">
                    <div className="text-4xl mb-4">{icons[cab.id] || '🚗'}</div>
                    <h3 className="text-lg font-semibold mb-2">{cab.name}</h3>
                    <p className="text-gray-600 text-sm mb-4">{cab.description}</p>
                    <div className="flex items-center justify-between">
                      <span className="text-2xl font-bold text-blue-600">₹{cab.pricePerKm}/km</span>
                      <span className="text-sm text-gray-500">{cab.capacity} Seater</span>
                    </div>
                  </div>
                </motion.div>
              );
            })}
          </div>

          <div className="text-center mt-8">
            <Link href="/fleet" className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg hover:shadow-lg transition-all inline-flex items-center space-x-2">
              <span>View All Vehicles</span>
              <ChevronRight className="w-5 h-5" />
            </Link>
          </div>
        </div>
      </section>

      {/* Testimonials */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">What Our Customers Say</h2>
            <p className="text-gray-600">Real experiences from our valued customers</p>
          </div>

          <div className="grid md:grid-cols-3 gap-8 max-w-5xl mx-auto">
            {[
              {
                name: 'Rahul Sharma',
                rating: 4,
                comment: 'Good service overall. The driver was professional and the journey was comfortable. Would use again.',
                route: 'Hyderabad to Bangalore',
                date: '2 weeks ago'
              },
              {
                name: 'Priya Patel',
                rating: 5,
                comment: 'Excellent experience! Driver arrived on time and the car was spotlessly clean. Best rates I found.',
                route: 'Delhi to Jaipur',
                date: '1 month ago'
              },
              {
                name: 'Amit Kumar',
                rating: 4,
                comment: 'Reliable service with transparent pricing. The booking process was simple and hassle-free.',
                route: 'Hyderabad to Chennai',
                date: '3 weeks ago'
              }
            ].map((testimonial, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl p-6 shadow-sm"
              >
                <div className="flex items-center mb-4">
                  {[...Array(5)].map((_, i) => (
                    <Star 
                      key={i} 
                      className={`w-5 h-5 ${i < testimonial.rating ? 'text-yellow-400 fill-current' : 'text-gray-300'}`} 
                    />
                  ))}
                  <span className="ml-2 text-sm text-gray-600">{testimonial.rating}.0</span>
                </div>
                <p className="text-gray-700 mb-4">&ldquo;{testimonial.comment}&rdquo;</p>
                <div>
                  <p className="font-semibold">{testimonial.name}</p>
                  <p className="text-sm text-gray-600">{testimonial.route}</p>
                  <p className="text-xs text-gray-400 mt-1">{testimonial.date}</p>
                </div>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Ready for Your Next Journey?</h2>
          <p className="text-xl mb-8 opacity-90">Book your interstate cab in just a few clicks</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <Link href="/fleet" className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:shadow-lg transition-all inline-flex items-center space-x-2">
              <span>Book Now</span>
              <ChevronRight className="w-5 h-5" />
            </Link>
            <Link href="/contact" className="border-2 border-white text-white px-8 py-3 rounded-lg hover:bg-white hover:text-blue-600 transition-all">
              Contact Us
            </Link>
          </div>
        </div>
      </section>
    </main>
  );
}
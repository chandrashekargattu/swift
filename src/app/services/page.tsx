'use client';

import { motion } from 'framer-motion';
import { Shield, Clock, MapPin, Users, Car, CreditCard, HeadphonesIcon, Wifi, Music, Coffee } from 'lucide-react';

export default function Services() {
  const services = [
    {
      icon: Car,
      title: 'Interstate Cab Service',
      description: 'Comfortable long-distance travel between cities with professional drivers',
      features: ['AC vehicles', 'GPS tracked', 'Experienced drivers', 'Multiple stops allowed']
    },
    {
      icon: Clock,
      title: '24/7 Availability',
      description: 'Book your ride anytime, anywhere. We\'re always ready to serve you',
      features: ['Round the clock service', 'Emergency bookings', 'Instant confirmation', 'No surge pricing']
    },
    {
      icon: Shield,
      title: 'Safe & Secure Travel',
      description: 'Your safety is our priority with verified drivers and sanitized vehicles',
      features: ['Verified drivers', 'Sanitized vehicles', 'Real-time tracking', 'Emergency support']
    },
    {
      icon: Users,
      title: 'Corporate Services',
      description: 'Special packages for business travelers and corporate accounts',
      features: ['Monthly billing', 'Dedicated support', 'Priority bookings', 'Custom reports']
    },
    {
      icon: MapPin,
      title: 'Airport Transfers',
      description: 'Hassle-free pickup and drop services to all major airports',
      features: ['On-time guarantee', 'Flight tracking', 'Meet & greet', 'Free waiting time']
    },
    {
      icon: CreditCard,
      title: 'Flexible Payment',
      description: 'Multiple payment options for your convenience',
      features: ['Cash payment', 'UPI/Cards', 'Corporate billing', 'No hidden charges']
    }
  ];

  const amenities = [
    { icon: Wifi, name: 'Free WiFi', description: 'Stay connected throughout your journey' },
    { icon: Music, name: 'Music System', description: 'Enjoy your favorite music on the go' },
    { icon: Coffee, name: 'Refreshments', description: 'Complimentary water bottles' },
    { icon: HeadphonesIcon, name: '24/7 Support', description: 'Always here to help you' }
  ];

  return (
    <main className="min-h-screen">
      {/* Hero Section */}
      <section className="pt-24 pb-16 bg-gradient-to-br from-blue-50 to-purple-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="text-center max-w-3xl mx-auto"
          >
            <h1 className="text-4xl md:text-5xl font-bold mb-6">
              Our <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Services</span>
            </h1>
            <p className="text-lg text-gray-600">
              We offer comprehensive interstate cab services designed to make your journey comfortable, safe, and memorable.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Services Grid */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-3 gap-8">
            {services.map((service, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl shadow-lg p-6 hover:shadow-xl transition-all"
              >
                <div className="w-14 h-14 bg-gradient-to-br from-blue-500 to-purple-600 rounded-xl flex items-center justify-center mb-4">
                  <service.icon className="w-7 h-7 text-white" />
                </div>
                <h3 className="text-xl font-semibold mb-3">{service.title}</h3>
                <p className="text-gray-600 mb-4">{service.description}</p>
                <ul className="space-y-2">
                  {service.features.map((feature, idx) => (
                    <li key={idx} className="flex items-start space-x-2">
                      <svg className="w-5 h-5 text-green-500 mt-0.5" fill="none" stroke="currentColor" viewBox="0 0 24 24">
                        <path strokeLinecap="round" strokeLinejoin="round" strokeWidth={2} d="M5 13l4 4L19 7" />
                      </svg>
                      <span className="text-sm text-gray-700">{feature}</span>
                    </li>
                  ))}
                </ul>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Process Section */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">How It Works</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              Booking your interstate cab is simple and takes just a few minutes
            </p>
          </div>

          <div className="grid md:grid-cols-4 gap-8 max-w-5xl mx-auto">
            {[
              { step: '1', title: 'Choose Route', description: 'Select your pickup and drop locations' },
              { step: '2', title: 'Select Vehicle', description: 'Choose from our range of vehicles' },
              { step: '3', title: 'Book & Pay', description: 'Confirm booking with flexible payment' },
              { step: '4', title: 'Travel Comfortably', description: 'Enjoy your journey with us' }
            ].map((item, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <div className="w-16 h-16 bg-gradient-to-br from-blue-500 to-purple-600 rounded-full flex items-center justify-center text-white text-2xl font-bold mx-auto mb-4">
                  {item.step}
                </div>
                <h3 className="text-lg font-semibold mb-2">{item.title}</h3>
                <p className="text-gray-600 text-sm">{item.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Amenities Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Travel Amenities</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              We ensure your journey is comfortable with these complimentary amenities
            </p>
          </div>

          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-5xl mx-auto">
            {amenities.map((amenity, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.9 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-6 rounded-xl bg-gray-50 hover:bg-gray-100 transition-colors"
              >
                <amenity.icon className="w-12 h-12 text-blue-600 mx-auto mb-3" />
                <h3 className="font-semibold mb-2">{amenity.name}</h3>
                <p className="text-sm text-gray-600">{amenity.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Experience Premium Travel Services</h2>
          <p className="text-xl mb-8 opacity-90">Book your next interstate journey with us</p>
          <div className="flex flex-col sm:flex-row gap-4 justify-center">
            <a href="/fleet" className="bg-white text-blue-600 px-8 py-3 rounded-lg hover:shadow-lg transition-all inline-block">
              Book Your Ride
            </a>
            <a href="/contact" className="border-2 border-white text-white px-8 py-3 rounded-lg hover:bg-white hover:text-blue-600 transition-all inline-block">
              Get in Touch
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}

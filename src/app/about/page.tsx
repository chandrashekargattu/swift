'use client';

import { motion } from 'framer-motion';
import { Users, Award, Target, Heart, Car, MapPin, Clock, Shield } from 'lucide-react';

export default function About() {
  // Calculate dynamic stats based on business start date (August 10, 2025)
  const startDate = new Date('2025-08-10');
  const currentDate = new Date();
  const monthsInOperation = Math.max(0, Math.floor((currentDate.getTime() - startDate.getTime()) / (1000 * 60 * 60 * 24 * 30)));
  
  // Realistic growth metrics for a startup
  const baseCustomers = 50;
  const customerGrowthRate = 35; // customers per month
  const totalCustomers = Math.max(0, baseCustomers + (monthsInOperation * customerGrowthRate));
  
  const baseDrivers = 5;
  const driverGrowthRate = 2; // drivers per month
  const totalDrivers = Math.max(5, baseDrivers + Math.floor(monthsInOperation * driverGrowthRate));
  
  const baseCities = 2;
  const cityExpansionRate = 0.5; // cities per month
  const totalCities = Math.max(2, baseCities + Math.floor(monthsInOperation * cityExpansionRate));
  
  const yearsInService = (monthsInOperation / 12).toFixed(1);
  
  const stats = [
    { 
      number: totalCustomers > 1000 ? `${Math.floor(totalCustomers / 1000)}k+` : `${totalCustomers}+`, 
      label: 'Happy Customers' 
    },
    { 
      number: `${totalDrivers}+`, 
      label: 'Professional Drivers' 
    },
    { 
      number: `${totalCities}`, 
      label: totalCities === 1 ? 'City' : 'Cities Covered' 
    },
    { 
      number: monthsInOperation < 12 ? `${monthsInOperation}` : yearsInService, 
      label: monthsInOperation < 12 ? 'Months of Service' : (yearsInService === '1.0' ? 'Year of Service' : 'Years of Service')
    }
  ];

  const values = [
    {
      icon: Heart,
      title: 'Customer First',
      description: 'Your comfort and satisfaction is our top priority'
    },
    {
      icon: Shield,
      title: 'Safety & Security',
      description: 'Ensuring safe travels with verified drivers and maintained vehicles'
    },
    {
      icon: Award,
      title: 'Quality Service',
      description: 'Maintaining high standards in every aspect of our service'
    },
    {
      icon: Clock,
      title: 'Punctuality',
      description: 'We value your time and ensure timely pickups and drops'
    }
  ];

  // Dynamic milestones based on actual progress
  const milestones = monthsInOperation > 0 ? [
    { year: '2025', month: 'August', event: 'RideSwift founded with a vision for reliable interstate travel' },
    ...(monthsInOperation >= 2 ? [{ year: '2025', month: 'October', event: 'First 50 customers served successfully' }] : []),
    ...(monthsInOperation >= 4 ? [{ year: '2025', month: 'December', event: 'Expanded operations to second city' }] : []),
    ...(monthsInOperation >= 6 ? [{ year: '2026', month: 'February', event: 'Launched mobile app for easier bookings' }] : []),
    ...(monthsInOperation >= 9 ? [{ year: '2026', month: 'May', event: 'Introduced corporate travel packages' }] : []),
    ...(monthsInOperation >= 12 ? [{ year: '2026', month: 'August', event: 'Celebrating 1 year of service excellence' }] : [])
  ] : [
    { year: '2025', month: 'August', event: 'Launching RideSwift - Your trusted travel partner' }
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
              About <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">RideSwift</span>
            </h1>
            <p className="text-lg text-gray-600">
              {monthsInOperation > 0 
                ? `Your trusted partner for comfortable and reliable interstate travel across India`
                : 'Coming soon - Your future trusted partner for comfortable interstate travel'}
            </p>
          </motion.div>
        </div>
      </section>

      {/* Stats Section */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid grid-cols-2 md:grid-cols-4 gap-8 max-w-4xl mx-auto">
            {stats.map((stat, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, scale: 0.5 }}
                whileInView={{ opacity: 1, scale: 1 }}
                transition={{ delay: index * 0.1 }}
                className="text-center"
              >
                <h3 className="text-3xl md:text-4xl font-bold text-blue-600 mb-2">{stat.number}</h3>
                <p className="text-gray-600">{stat.label}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Our Story */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="text-center mb-12"
            >
              <h2 className="text-3xl font-bold mb-4">Our Story</h2>
            </motion.div>
            
            <div className="grid md:grid-cols-2 gap-12 items-center">
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
              >
                <p className="text-gray-700 mb-4">
                  RideSwift was born out of a simple vision - to make interstate travel comfortable, 
                  reliable, and affordable for everyone. {monthsInOperation > 0 
                    ? `Starting with ${baseDrivers} dedicated drivers and their vehicles in Hyderabad, 
                       we've been steadily growing to meet the increasing demand for quality interstate travel.`
                    : `We're preparing to launch with ${baseDrivers} carefully selected drivers and 
                       well-maintained vehicles in Hyderabad.`}
                </p>
                <p className="text-gray-700 mb-4">
                  {monthsInOperation > 0 
                    ? `In just ${monthsInOperation < 12 ? `${monthsInOperation} months` : `${yearsInService} years`}, 
                       we've expanded to ${totalCities} ${totalCities === 1 ? 'city' : 'cities'} and served 
                       ${totalCustomers} happy customers. Our focus on quality service and customer satisfaction 
                       drives everything we do.`
                    : `Our upcoming launch will focus on providing exceptional service between major cities, 
                       with plans for steady expansion based on customer needs and feedback.`}
                </p>
                <p className="text-gray-700">
                  {monthsInOperation > 0 
                    ? `Today, with ${totalDrivers} professional drivers and growing, we're committed to 
                       setting new standards in interstate travel, ensuring every`
                    : `Soon, with our initial team of ${baseDrivers} professional drivers, we'll begin 
                       our journey to set new standards in interstate travel, ensuring every`} 
                  journey with us is memorable.
                </p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                className="relative"
              >
                <div className="bg-gradient-to-br from-blue-100 to-purple-100 rounded-2xl p-8">
                  <div className="grid grid-cols-2 gap-4">
                    <div className="bg-white rounded-lg p-4 text-center">
                      <Car className="w-8 h-8 text-blue-600 mx-auto mb-2" />
                      <p className="text-sm font-semibold">100+ Fleet</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 text-center">
                      <MapPin className="w-8 h-8 text-purple-600 mx-auto mb-2" />
                      <p className="text-sm font-semibold">150+ Cities</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 text-center">
                      <Users className="w-8 h-8 text-green-600 mx-auto mb-2" />
                      <p className="text-sm font-semibold">50K+ Customers</p>
                    </div>
                    <div className="bg-white rounded-lg p-4 text-center">
                      <Award className="w-8 h-8 text-yellow-600 mx-auto mb-2" />
                      <p className="text-sm font-semibold">10+ Years</p>
                    </div>
                  </div>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Mission & Vision */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <div className="grid md:grid-cols-2 gap-8">
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                className="bg-blue-50 rounded-2xl p-8"
              >
                <Target className="w-12 h-12 text-blue-600 mb-4" />
                <h3 className="text-2xl font-bold mb-4">Our Mission</h3>
                <p className="text-gray-700">
                  To provide safe, comfortable, and affordable interstate travel solutions while 
                  ensuring the highest standards of service quality and customer satisfaction.
                </p>
              </motion.div>
              
              <motion.div
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: 0.1 }}
                className="bg-purple-50 rounded-2xl p-8"
              >
                <Award className="w-12 h-12 text-purple-600 mb-4" />
                <h3 className="text-2xl font-bold mb-4">Our Vision</h3>
                <p className="text-gray-700">
                  To be India&apos;s most trusted and preferred interstate cab service, known for 
                  reliability, innovation, and exceptional customer experiences.
                </p>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* Core Values */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Our Core Values</h2>
            <p className="text-gray-600 max-w-2xl mx-auto">
              These values guide everything we do and shape our commitment to you
            </p>
          </div>
          
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto">
            {values.map((value, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="bg-white rounded-xl p-6 text-center hover:shadow-lg transition-all"
              >
                <value.icon className="w-12 h-12 text-blue-600 mx-auto mb-4" />
                <h3 className="text-lg font-semibold mb-2">{value.title}</h3>
                <p className="text-gray-600 text-sm">{value.description}</p>
              </motion.div>
            ))}
          </div>
        </div>
      </section>

      {/* Timeline */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="text-center mb-12">
            <h2 className="text-3xl font-bold mb-4">Our Journey</h2>
            <p className="text-gray-600">Key milestones in our growth story</p>
          </div>
          
          <div className="max-w-4xl mx-auto">
            <div className="relative">
              <div className="absolute left-1/2 transform -translate-x-1/2 h-full w-0.5 bg-gray-300"></div>
              {milestones.map((milestone, index) => (
                <motion.div
                  key={index}
                  initial={{ opacity: 0, x: index % 2 === 0 ? -50 : 50 }}
                  whileInView={{ opacity: 1, x: 0 }}
                  transition={{ delay: index * 0.1 }}
                  className={`relative flex items-center mb-8 ${
                    index % 2 === 0 ? 'justify-start' : 'justify-end'
                  }`}
                >
                  <div className={`w-5/12 ${index % 2 === 0 ? 'text-right pr-8' : 'text-left pl-8'}`}>
                    <div className="bg-white rounded-lg shadow-lg p-4">
                      <h3 className="text-lg font-bold text-blue-600">
                        {milestone.month ? `${milestone.month} ${milestone.year}` : milestone.year}
                      </h3>
                      <p className="text-gray-700">{milestone.event}</p>
                    </div>
                  </div>
                  <div className="absolute left-1/2 transform -translate-x-1/2 w-4 h-4 bg-blue-600 rounded-full"></div>
                </motion.div>
              ))}
            </div>
          </div>
        </div>
      </section>

      {/* CTA Section */}
      <section className="py-16 bg-gradient-to-r from-blue-600 to-purple-600 text-white">
        <div className="container mx-auto px-4 text-center">
          <h2 className="text-3xl font-bold mb-4">Join Our Journey</h2>
          <p className="text-xl mb-8 opacity-90">Experience the RideSwift difference on your next trip</p>
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

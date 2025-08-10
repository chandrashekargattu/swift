'use client';

import { motion } from 'framer-motion';
import { useState } from 'react';
import { Phone, Mail, MapPin, Clock, Send } from 'lucide-react';

export default function Contact() {
  const [formData, setFormData] = useState({
    name: '',
    email: '',
    phone: '',
    subject: '',
    message: ''
  });

  const handleSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    // Handle form submission
    alert('Thank you for contacting us! We will get back to you soon.');
    setFormData({
      name: '',
      email: '',
      phone: '',
      subject: '',
      message: ''
    });
  };

  const handleChange = (e: React.ChangeEvent<HTMLInputElement | HTMLTextAreaElement | HTMLSelectElement>) => {
    setFormData({
      ...formData,
      [e.target.name]: e.target.value
    });
  };

  const contactInfo = [
    {
      icon: Phone,
      title: 'Phone',
      details: ['+91 8143243584', '1800-123-4567'],
      color: 'blue'
    },
    {
      icon: Mail,
      title: 'Email',
      details: ['info@rideswift.com', 'support@rideswift.com'],
      color: 'purple'
    },
    {
      icon: MapPin,
      title: 'Address',
      details: ['Hyderabad, Telangana', 'India'],
      color: 'green'
    },
    {
      icon: Clock,
      title: 'Working Hours',
      details: ['24/7 Available', 'Round the clock support'],
      color: 'orange'
    }
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
              Contact <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Us</span>
            </h1>
            <p className="text-lg text-gray-600">
              We&apos;re here to help! Reach out to us for any queries, feedback, or assistance.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Contact Info Cards */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="grid md:grid-cols-2 lg:grid-cols-4 gap-6 max-w-6xl mx-auto mb-16">
            {contactInfo.map((info, index) => (
              <motion.div
                key={index}
                initial={{ opacity: 0, y: 20 }}
                whileInView={{ opacity: 1, y: 0 }}
                transition={{ delay: index * 0.1 }}
                className="text-center p-6 bg-gray-50 rounded-xl hover:shadow-lg transition-all"
              >
                <div className={`inline-flex items-center justify-center w-14 h-14 rounded-full bg-${info.color}-100 mb-4`}>
                  <info.icon className={`w-7 h-7 text-${info.color}-600`} />
                </div>
                <h3 className="text-lg font-semibold mb-3">{info.title}</h3>
                {info.details.map((detail, idx) => (
                  <p key={idx} className="text-gray-600 text-sm">
                    {info.title === 'Phone' ? (
                      <a href={`tel:${detail.replace(/\s/g, '')}`} className="hover:text-blue-600 transition-colors">
                        {detail}
                      </a>
                    ) : info.title === 'Email' ? (
                      <a href={`mailto:${detail}`} className="hover:text-blue-600 transition-colors">
                        {detail}
                      </a>
                    ) : (
                      detail
                    )}
                  </p>
                ))}
              </motion.div>
            ))}
          </div>

          {/* Contact Form */}
          <div className="max-w-5xl mx-auto">
            <div className="grid md:grid-cols-2 gap-12">
              {/* Form */}
              <motion.div
                initial={{ opacity: 0, x: -20 }}
                whileInView={{ opacity: 1, x: 0 }}
              >
                <h2 className="text-2xl font-bold mb-6">Send us a Message</h2>
                <form onSubmit={handleSubmit} className="space-y-4">
                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Your Name *
                      </label>
                      <input
                        type="text"
                        name="name"
                        value={formData.name}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="John Doe"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Email Address *
                      </label>
                      <input
                        type="email"
                        name="email"
                        value={formData.email}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="john@example.com"
                      />
                    </div>
                  </div>

                  <div className="grid md:grid-cols-2 gap-4">
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Phone Number
                      </label>
                      <input
                        type="tel"
                        name="phone"
                        value={formData.phone}
                        onChange={handleChange}
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                        placeholder="+91 98765 43210"
                      />
                    </div>
                    <div>
                      <label className="block text-sm font-medium text-gray-700 mb-1">
                        Subject *
                      </label>
                      <select
                        name="subject"
                        value={formData.subject}
                        onChange={handleChange}
                        required
                        className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      >
                        <option value="">Select a subject</option>
                        <option value="booking">Booking Inquiry</option>
                        <option value="support">Customer Support</option>
                        <option value="corporate">Corporate Services</option>
                        <option value="feedback">Feedback</option>
                        <option value="other">Other</option>
                      </select>
                    </div>
                  </div>

                  <div>
                    <label className="block text-sm font-medium text-gray-700 mb-1">
                      Message *
                    </label>
                    <textarea
                      name="message"
                      value={formData.message}
                      onChange={handleChange}
                      required
                      rows={5}
                      className="w-full px-4 py-2 border border-gray-300 rounded-lg focus:ring-2 focus:ring-blue-500 focus:border-transparent"
                      placeholder="Tell us how we can help you..."
                    />
                  </div>

                  <button
                    type="submit"
                    className="w-full bg-gradient-to-r from-blue-500 to-purple-600 text-white py-3 rounded-lg hover:shadow-lg transition-all flex items-center justify-center space-x-2"
                  >
                    <Send className="w-5 h-5" />
                    <span>Send Message</span>
                  </button>
                </form>
              </motion.div>

              {/* Map/Additional Info */}
              <motion.div
                initial={{ opacity: 0, x: 20 }}
                whileInView={{ opacity: 1, x: 0 }}
                className="space-y-8"
              >
                <div>
                  <h3 className="text-2xl font-bold mb-6">Get in Touch</h3>
                  <p className="text-gray-600 mb-6">
                    Have questions about our services? Need help with your booking? 
                    Our customer support team is available 24/7 to assist you.
                  </p>
                </div>

                <div className="bg-gray-50 rounded-xl p-6">
                  <h4 className="font-semibold mb-4">Quick Support</h4>
                  <div className="space-y-4">
                    <div>
                      <p className="text-sm text-gray-600 mb-1">For immediate assistance:</p>
                      <a href="tel:+918143243584" className="text-lg font-semibold text-blue-600 hover:text-blue-700">
                        +91 8143243584
                      </a>
                    </div>
                    <div>
                      <p className="text-sm text-gray-600 mb-1">WhatsApp Support:</p>
                      <a href="https://wa.me/918143243584" className="text-lg font-semibold text-green-600 hover:text-green-700">
                        +91 8143243584
                      </a>
                    </div>
                  </div>
                </div>

                <div className="bg-blue-50 rounded-xl p-6">
                  <h4 className="font-semibold mb-4">Office Hours</h4>
                  <p className="text-gray-700">
                    While our cab services are available 24/7, our office operates:
                  </p>
                  <ul className="mt-3 space-y-1 text-sm text-gray-600">
                    <li>Monday - Saturday: 9:00 AM - 8:00 PM</li>
                    <li>Sunday: 10:00 AM - 6:00 PM</li>
                    <li>Public Holidays: Limited Support</li>
                  </ul>
                </div>
              </motion.div>
            </div>
          </div>
        </div>
      </section>

      {/* FAQ Preview */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center max-w-3xl mx-auto">
            <h2 className="text-3xl font-bold mb-4">Need Quick Answers?</h2>
            <p className="text-gray-600 mb-8">
              Check out our frequently asked questions for instant help
            </p>
            <a href="/help" className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-8 py-3 rounded-lg hover:shadow-lg transition-all inline-block">
              Visit Help Center
            </a>
          </div>
        </div>
      </section>
    </main>
  );
}

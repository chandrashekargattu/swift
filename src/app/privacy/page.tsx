'use client';

import { motion } from 'framer-motion';
import { Phone, MapPin } from 'lucide-react';

export default function Privacy() {
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
              Privacy <span className="text-transparent bg-clip-text bg-gradient-to-r from-blue-600 to-purple-600">Policy</span>
            </h1>
            <p className="text-lg text-gray-600">
              Your privacy is important to us. Learn how we collect, use, and protect your information.
            </p>
          </motion.div>
        </div>
      </section>

      {/* Privacy Policy Content */}
      <section className="py-16 bg-white">
        <div className="container mx-auto px-4">
          <div className="max-w-4xl mx-auto">
            <motion.div
              initial={{ opacity: 0, y: 20 }}
              whileInView={{ opacity: 1, y: 0 }}
              className="bg-white rounded-2xl shadow-lg p-8 space-y-6"
            >
              <div className="text-sm text-gray-600 mb-4">
                <p>Effective Date: {new Date().toLocaleDateString()}</p>
                <p className="mt-2">At RideSwift, we take your privacy seriously. This Privacy Policy explains how we collect, use, disclose, and safeguard your information when you use our interstate cab booking service.</p>
              </div>

              <div className="space-y-8">
                <div>
                  <h3 className="text-xl font-semibold mb-3">1. Information We Collect</h3>
                  <div className="space-y-2 text-gray-700">
                    <h4 className="font-semibold">Personal Information:</h4>
                    <ul className="list-disc pl-6 space-y-1">
                      <li>Name, email address, and phone number</li>
                      <li>Pickup and drop-off locations</li>
                      <li>Payment information (processed securely through payment gateways)</li>
                      <li>Government-issued ID for verification (when required)</li>
                    </ul>
                    
                    <h4 className="font-semibold mt-3">Usage Information:</h4>
                    <ul className="list-disc pl-6 space-y-1">
                      <li>Trip history and preferences</li>
                      <li>Device information and IP address</li>
                      <li>Location data (only during active bookings)</li>
                    </ul>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">2. How We Use Your Information</h3>
                  <ul className="list-disc pl-6 space-y-2 text-gray-700">
                    <li>To provide and improve our cab booking services</li>
                    <li>To process bookings and payments</li>
                    <li>To communicate booking confirmations and updates</li>
                    <li>To ensure safety and security for all users</li>
                    <li>To provide customer support</li>
                    <li>To send promotional offers (with your consent)</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">3. Information Sharing</h3>
                  <p className="text-gray-700 mb-2">We share your information only in the following circumstances:</p>
                  <ul className="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>With Drivers:</strong> Name, phone number, and trip details for service delivery</li>
                    <li><strong>With Payment Processors:</strong> For secure transaction processing</li>
                    <li><strong>For Legal Compliance:</strong> When required by law or to protect our rights</li>
                    <li><strong>With Your Consent:</strong> For any other purposes with your explicit permission</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">4. Data Security</h3>
                  <div className="space-y-2 text-gray-700">
                    <p>We implement industry-standard security measures including:</p>
                    <ul className="list-disc pl-6 space-y-1">
                      <li>256-bit SSL encryption for all data transmissions</li>
                      <li>Secure servers with regular security audits</li>
                      <li>Limited access to personal information by employees</li>
                      <li>Regular security training for our staff</li>
                      <li>PCI DSS compliance for payment processing</li>
                    </ul>
                  </div>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">5. Your Rights</h3>
                  <ul className="list-disc pl-6 space-y-2 text-gray-700">
                    <li><strong>Access:</strong> Request a copy of your personal data</li>
                    <li><strong>Correction:</strong> Update or correct your information</li>
                    <li><strong>Deletion:</strong> Request deletion of your account and data</li>
                    <li><strong>Opt-out:</strong> Unsubscribe from marketing communications</li>
                    <li><strong>Data Portability:</strong> Receive your data in a portable format</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">6. Location Data</h3>
                  <p className="text-gray-700">We collect location data only when you have given us permission and only during active bookings to:</p>
                  <ul className="list-disc pl-6 space-y-1 text-gray-700 mt-2">
                    <li>Show available cabs near you</li>
                    <li>Calculate accurate fare estimates</li>
                    <li>Track your trip for safety</li>
                    <li>Improve our route optimization</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">7. Cookies and Tracking</h3>
                  <p className="text-gray-700">We use cookies and similar technologies to:</p>
                  <ul className="list-disc pl-6 space-y-1 text-gray-700 mt-2">
                    <li>Remember your preferences</li>
                    <li>Understand how you use our service</li>
                    <li>Improve user experience</li>
                    <li>Provide personalized content</li>
                  </ul>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">8. Children&apos;s Privacy</h3>
                  <p className="text-gray-700">Our services are not intended for children under 18. We do not knowingly collect information from children. If you believe we have collected information from a child, please contact us immediately.</p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">9. Data Retention</h3>
                  <p className="text-gray-700">We retain your information for as long as necessary to provide our services and comply with legal obligations. Trip history is retained for 3 years for your convenience and regulatory compliance.</p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">10. Updates to This Policy</h3>
                  <p className="text-gray-700">We may update this Privacy Policy periodically. We will notify you of significant changes via email or through our app. Continued use of our services after changes constitutes acceptance.</p>
                </div>

                <div>
                  <h3 className="text-xl font-semibold mb-3">11. Contact Us</h3>
                  <div className="bg-blue-50 p-4 rounded-lg">
                    <p className="text-gray-700 mb-2">For any privacy-related questions or concerns:</p>
                    <div className="space-y-2">
                      <p className="flex items-center space-x-2">
                        <Phone className="w-4 h-4 text-blue-600" />
                        <span>+91 8143243584</span>
                      </p>
                      <p className="flex items-center space-x-2">
                        <MapPin className="w-4 h-4 text-blue-600" />
                        <span>Hyderabad, Telangana</span>
                      </p>
                      <p className="text-gray-600">Email: privacy@rideswift.com</p>
                    </div>
                  </div>
                </div>
              </div>
            </motion.div>
          </div>
        </div>
      </section>

      {/* Additional Links */}
      <section className="py-16 bg-gray-50">
        <div className="container mx-auto px-4">
          <div className="text-center">
            <h2 className="text-2xl font-bold mb-8">Related Information</h2>
            <div className="flex flex-col sm:flex-row gap-4 justify-center">
              <a href="/help" className="bg-white text-gray-700 px-6 py-3 rounded-lg shadow hover:shadow-lg transition-all inline-block">
                Help Center
              </a>
              <a href="/contact" className="bg-gradient-to-r from-blue-500 to-purple-600 text-white px-6 py-3 rounded-lg hover:shadow-lg transition-all inline-block">
                Contact Support
              </a>
            </div>
          </div>
        </div>
      </section>
    </main>
  );
}

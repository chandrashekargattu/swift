"use client";

import { useState } from "react";
import { motion } from "framer-motion";
import { Instagram, Facebook, Twitter, Linkedin, Share2 } from "lucide-react";
import InstagramFeed from "@/components/social/InstagramFeed";
import SocialShare from "@/components/social/SocialShare";

export default function SocialPage() {
  const [activeTab, setActiveTab] = useState("instagram");

  return (
    <main className="min-h-screen pt-20">
      <section className="py-16 bg-gradient-to-br from-purple-50 to-pink-50">
        <div className="container mx-auto px-4">
          <motion.div
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            transition={{ duration: 0.5 }}
            className="text-center max-w-3xl mx-auto mb-12"
          >
            <h1 className="text-4xl font-bold text-gray-900 mb-4">
              Connect With RideSwift
            </h1>
            <p className="text-lg text-gray-600">
              Follow us on social media for updates, travel tips, and exclusive offers
            </p>
          </motion.div>

          {/* Social Media Links */}
          <div className="flex justify-center gap-4 mb-12">
            <a
              href="https://instagram.com/rideswift"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 bg-gradient-to-br from-purple-500 to-pink-500 text-white rounded-full hover:opacity-90 transition-opacity"
            >
              <Instagram className="w-6 h-6" />
            </a>
            <a
              href="https://facebook.com/rideswift"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 bg-blue-600 text-white rounded-full hover:opacity-90 transition-opacity"
            >
              <Facebook className="w-6 h-6" />
            </a>
            <a
              href="https://twitter.com/rideswift"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 bg-black text-white rounded-full hover:opacity-90 transition-opacity"
            >
              <Twitter className="w-6 h-6" />
            </a>
            <a
              href="https://linkedin.com/company/rideswift"
              target="_blank"
              rel="noopener noreferrer"
              className="p-3 bg-blue-700 text-white rounded-full hover:opacity-90 transition-opacity"
            >
              <Linkedin className="w-6 h-6" />
            </a>
          </div>

          {/* Tab Navigation */}
          <div className="flex justify-center mb-8">
            <div className="bg-white rounded-lg shadow-sm p-1 inline-flex">
              <button
                onClick={() => setActiveTab("instagram")}
                className={`px-6 py-2 rounded-md transition-colors ${
                  activeTab === "instagram"
                    ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Instagram Feed
              </button>
              <button
                onClick={() => setActiveTab("share")}
                className={`px-6 py-2 rounded-md transition-colors ${
                  activeTab === "share"
                    ? "bg-gradient-to-r from-purple-500 to-pink-500 text-white"
                    : "text-gray-600 hover:text-gray-900"
                }`}
              >
                Share & Earn
              </button>
            </div>
          </div>
        </div>
      </section>

      <section className="py-16">
        <div className="container mx-auto px-4">
          {activeTab === "instagram" ? (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
            >
              <InstagramFeed username="rideswift" limit={12} />
            </motion.div>
          ) : (
            <motion.div
              initial={{ opacity: 0 }}
              animate={{ opacity: 1 }}
              transition={{ duration: 0.3 }}
              className="max-w-4xl mx-auto"
            >
              <div className="bg-white rounded-xl shadow-lg p-8 mb-8">
                <h2 className="text-2xl font-bold text-gray-900 mb-4">
                  Share Your Journey
                </h2>
                <p className="text-gray-600 mb-6">
                  Share your RideSwift experience with friends and earn rewards!
                </p>
                
                <div className="grid md:grid-cols-2 gap-6">
                  <div className="bg-blue-50 rounded-lg p-6">
                    <h3 className="font-semibold text-lg mb-2">
                      Refer a Friend
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Get ₹200 off when your friend takes their first ride
                    </p>
                    <SocialShare
                      title="Join me on RideSwift and get 20% off your first ride!"
                      description="Use my referral code for exclusive discounts"
                    />
                  </div>
                  
                  <div className="bg-green-50 rounded-lg p-6">
                    <h3 className="font-semibold text-lg mb-2">
                      Share Your Rides
                    </h3>
                    <p className="text-gray-600 mb-4">
                      Share your travel stories and inspire others
                    </p>
                    <SocialShare
                      title="Just booked my ride with RideSwift!"
                      description="Comfortable interstate travel made easy"
                    />
                  </div>
                </div>
              </div>

              <div className="bg-gradient-to-r from-purple-600 to-pink-600 rounded-xl p-8 text-white">
                <h2 className="text-2xl font-bold mb-4">
                  Become a Social Ambassador
                </h2>
                <p className="mb-6">
                  Join our influencer program and earn exclusive benefits:
                </p>
                <ul className="space-y-2 mb-6">
                  <li className="flex items-start gap-2">
                    <span className="text-2xl">✓</span>
                    <span>Free rides every month</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-2xl">✓</span>
                    <span>Exclusive discount codes for followers</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-2xl">✓</span>
                    <span>Early access to new features</span>
                  </li>
                  <li className="flex items-start gap-2">
                    <span className="text-2xl">✓</span>
                    <span>Monthly cash rewards</span>
                  </li>
                </ul>
                <button className="bg-white text-purple-600 px-6 py-3 rounded-lg font-semibold hover:bg-gray-100 transition-colors">
                  Apply Now
                </button>
              </div>
            </motion.div>
          )}
        </div>
      </section>
    </main>
  );
}

'use client';

import Link from 'next/link';
import { Car, Phone, MapPin } from 'lucide-react';

export default function Footer() {
  return (
    <footer className="bg-gray-900 text-white py-12">
      <div className="container mx-auto px-4">
        <div className="grid md:grid-cols-4 gap-8">
          <div>
            <div className="flex items-center space-x-2 mb-4">
              <div className="bg-white p-2 rounded-lg">
                <Car className="w-6 h-6 text-blue-600" />
              </div>
              <span className="text-xl font-bold">RideSwift</span>
            </div>
            <p className="text-gray-400">Your trusted partner for comfortable interstate travel</p>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Quick Links</h4>
            <ul className="space-y-2 text-gray-400">
              <li><Link href="/about" className="hover:text-white transition-colors">About Us</Link></li>
              <li><Link href="/services" className="hover:text-white transition-colors">Services</Link></li>
              <li><Link href="/pricing" className="hover:text-white transition-colors">Pricing</Link></li>
              <li><Link href="/contact" className="hover:text-white transition-colors">Contact</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Support</h4>
            <ul className="space-y-2 text-gray-400">
              <li><Link href="/help" className="hover:text-white transition-colors">Help Center</Link></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); alert('Safety information page coming soon!'); }} className="hover:text-white transition-colors cursor-pointer">Safety</a></li>
              <li><a href="#" onClick={(e) => { e.preventDefault(); alert('Terms & Conditions page coming soon!'); }} className="hover:text-white transition-colors cursor-pointer">Terms & Conditions</a></li>
              <li><Link href="/privacy" className="hover:text-white transition-colors">Privacy Policy</Link></li>
            </ul>
          </div>
          
          <div>
            <h4 className="font-semibold mb-4">Contact Us</h4>
            <ul className="space-y-2 text-gray-400">
              <li>📞 +91 8143243584</li>
              <li>📧 info@rideswift.com</li>
              <li>📍 Hyderabad, Telangana</li>
            </ul>
          </div>
        </div>
        
        <div className="border-t border-gray-800 mt-8 pt-8 text-center text-gray-400">
          <p>&copy; 2024 RideSwift. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

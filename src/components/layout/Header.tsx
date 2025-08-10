'use client';

import React from 'react';
import { motion } from 'framer-motion';
import { Car, Menu, X, Phone, User, LogOut, ChevronDown } from 'lucide-react';
import Link from 'next/link';
import { usePathname } from 'next/navigation';
import { useAuth } from '@/contexts/AuthContext';

export default function Header() {
  const [isMenuOpen, setIsMenuOpen] = React.useState(false);
  const [isUserMenuOpen, setIsUserMenuOpen] = React.useState(false);
  const pathname = usePathname();
  const { user, signOut, isLoading } = useAuth();
  const userMenuRef = React.useRef<HTMLDivElement>(null);

  const isActive = (path: string) => pathname === path;
  
  const handleSignOut = () => {
    signOut();
    setIsUserMenuOpen(false);
    setIsMenuOpen(false);
  };
  
  // Close user menu when clicking outside
  React.useEffect(() => {
    const handleClickOutside = (event: MouseEvent) => {
      if (userMenuRef.current && !userMenuRef.current.contains(event.target as Node)) {
        setIsUserMenuOpen(false);
      }
    };

    document.addEventListener('mousedown', handleClickOutside);
    return () => document.removeEventListener('mousedown', handleClickOutside);
  }, []);

  return (
    <header className="fixed top-0 left-0 right-0 z-50 bg-white/80 backdrop-blur-md shadow-sm">
      <div className="container mx-auto px-4">
        <div className="flex items-center justify-between h-16">
          {/* Logo */}
          <motion.div 
            initial={{ opacity: 0, x: -20 }}
            animate={{ opacity: 1, x: 0 }}
          >
            <Link href="/" className="flex items-center space-x-2">
              <div className="bg-gradient-to-br from-blue-500 to-purple-600 p-2 rounded-xl">
                <Car className="w-6 h-6 text-white" />
              </div>
              <span className="text-xl font-bold gradient-text">RideSwift</span>
            </Link>
          </motion.div>

          {/* Desktop Navigation */}
          <nav className="hidden md:flex items-center space-x-8">
            <Link href="/" className={`transition-colors ${isActive('/') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Home
            </Link>
            <Link href="/services" className={`transition-colors ${isActive('/services') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Services
            </Link>
            <Link href="/fleet" className={`transition-colors ${isActive('/fleet') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Our Fleet
            </Link>
            <Link href="/carpool" className={`transition-colors ${isActive('/carpool') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Carpool
            </Link>
            <Link href="/pricing" className={`transition-colors ${isActive('/pricing') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Pricing
            </Link>
            <Link href="/about" className={`transition-colors ${isActive('/about') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              About
            </Link>
            <Link href="/contact" className={`transition-colors ${isActive('/contact') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Contact
            </Link>
            <Link href="/privacy" className={`transition-colors ${isActive('/privacy') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
              Privacy
            </Link>
          </nav>

          {/* CTA Buttons */}
          <div className="hidden md:flex items-center space-x-4">
            <a href="tel:+918143243584" className="flex items-center space-x-2 text-gray-700 hover:text-blue-600 transition-colors">
              <Phone className="w-4 h-4" />
              <span>+91 8143243584</span>
            </a>
            {isLoading ? (
              <div className="animate-pulse bg-gray-200 h-10 w-24 rounded-lg"></div>
            ) : user ? (
              <div className="relative" ref={userMenuRef}>
                <button
                  onClick={() => setIsUserMenuOpen(!isUserMenuOpen)}
                  className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all"
                >
                  <User className="w-4 h-4" />
                  <span>{user.full_name.split(' ')[0]}</span>
                  <ChevronDown className={`w-4 h-4 transition-transform ${isUserMenuOpen ? 'rotate-180' : ''}`} />
                </button>
                
                {isUserMenuOpen && (
                  <motion.div
                    initial={{ opacity: 0, y: -10 }}
                    animate={{ opacity: 1, y: 0 }}
                    className="absolute right-0 mt-2 w-56 bg-white rounded-lg shadow-xl py-2 z-50"
                  >
                    <div className="px-4 py-2 border-b">
                      <p className="text-sm font-semibold text-gray-800">{user.full_name}</p>
                      <p className="text-xs text-gray-600">{user.email}</p>
                    </div>
                    <Link
                      href="/profile"
                      onClick={() => setIsUserMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      My Profile
                    </Link>
                    <Link
                      href="/bookings"
                      onClick={() => setIsUserMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100"
                    >
                      My Bookings
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="block w-full text-left px-4 py-2 text-sm text-red-600 hover:bg-red-50"
                    >
                      <span className="flex items-center space-x-2">
                        <LogOut className="w-4 h-4" />
                        <span>Sign Out</span>
                      </span>
                    </button>
                  </motion.div>
                )}
              </div>
            ) : (
              <Link href="/signin" className="flex items-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg hover:shadow-lg transition-all">
                <User className="w-4 h-4" />
                <span>Sign In</span>
              </Link>
            )}
          </div>

          {/* Mobile Menu Button */}
          <button 
            className="md:hidden"
            onClick={() => setIsMenuOpen(!isMenuOpen)}
          >
            {isMenuOpen ? <X className="w-6 h-6" /> : <Menu className="w-6 h-6" />}
          </button>
        </div>

        {/* Mobile Menu */}
        {isMenuOpen && (
          <motion.div 
            initial={{ opacity: 0, y: -20 }}
            animate={{ opacity: 1, y: 0 }}
            className="md:hidden py-4 border-t"
          >
            <nav className="flex flex-col space-y-4">
              <Link href="/" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Home
              </Link>
              <Link href="/services" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/services') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Services
              </Link>
              <Link href="/fleet" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/fleet') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Our Fleet
              </Link>
              <Link href="/carpool" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/carpool') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Carpool
              </Link>
              <Link href="/pricing" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/pricing') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Pricing
              </Link>
              <Link href="/about" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/about') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                About
              </Link>
              <Link href="/contact" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/contact') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Contact
              </Link>
              <Link href="/privacy" onClick={() => setIsMenuOpen(false)} className={`transition-colors ${isActive('/privacy') ? 'text-blue-600 font-semibold' : 'text-gray-700 hover:text-blue-600'}`}>
                Privacy
              </Link>
              <a href="tel:+918143243584" className="flex items-center space-x-2 text-gray-700">
                <Phone className="w-4 h-4" />
                <span>+91 8143243584</span>
              </a>
              {user ? (
                <>
                  <div className="border-t pt-4 mt-4">
                    <div className="px-4 py-2 bg-gray-50 rounded-lg mb-2">
                      <p className="text-sm font-semibold text-gray-800">{user.full_name}</p>
                      <p className="text-xs text-gray-600">{user.email}</p>
                    </div>
                    <Link
                      href="/profile"
                      onClick={() => setIsMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                    >
                      My Profile
                    </Link>
                    <Link
                      href="/bookings"
                      onClick={() => setIsMenuOpen(false)}
                      className="block px-4 py-2 text-sm text-gray-700 hover:bg-gray-100 rounded"
                    >
                      My Bookings
                    </Link>
                    <button
                      onClick={handleSignOut}
                      className="flex items-center space-x-2 w-full px-4 py-2 text-sm text-red-600 hover:bg-red-50 rounded"
                    >
                      <LogOut className="w-4 h-4" />
                      <span>Sign Out</span>
                    </button>
                  </div>
                </>
              ) : (
                <Link href="/signin" onClick={() => setIsMenuOpen(false)} className="flex items-center justify-center space-x-2 bg-gradient-to-r from-blue-500 to-purple-600 text-white px-4 py-2 rounded-lg">
                  <User className="w-4 h-4" />
                  <span>Sign In</span>
                </Link>
              )}
            </nav>
          </motion.div>
        )}
      </div>
    </header>
  );
}
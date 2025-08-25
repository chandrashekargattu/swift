'use client';

import { useEffect } from 'react';
import { useRouter } from 'next/navigation';

export default function ClearAuth() {
  const router = useRouter();

  useEffect(() => {
    // Clear all auth-related storage
    localStorage.clear();
    sessionStorage.clear();
    
    // Clear cookies
    document.cookie.split(";").forEach((c) => {
      document.cookie = c
        .replace(/^ +/, "")
        .replace(/=.*/, "=;expires=" + new Date().toUTCString() + ";path=/");
    });
    
    // Redirect to home after clearing
    setTimeout(() => {
      router.push('/');
    }, 1000);
  }, [router]);

  return (
    <div className="min-h-screen flex items-center justify-center">
      <div className="text-center">
        <h1 className="text-2xl font-bold mb-4">Clearing Authentication...</h1>
        <p className="text-gray-600">Redirecting to home page...</p>
      </div>
    </div>
  );
}

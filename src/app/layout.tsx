import type { Metadata } from "next";
import { Inter } from "next/font/google";
import "./globals.css";
import Header from "@/components/layout/Header";
import Footer from "@/components/layout/Footer";
import { AuthProvider } from "@/contexts/AuthContext";
import ErrorBoundary from "@/components/ErrorBoundary";
import ChatbotWrapper from "@/components/Chatbot/ChatbotWrapper";

const inter = Inter({
  subsets: ["latin"],
  variable: "--font-inter",
});

export const metadata: Metadata = {
  title: "RideSwift - Premium Interstate Cab Booking",
  description: "Book premium cabs for interstate and local travel with comfort and reliability",
  keywords: "cab booking, interstate travel, taxi service, ride booking",
};

export default function RootLayout({
  children,
}: Readonly<{
  children: React.ReactNode;
}>) {
  return (
    <html lang="en" className={inter.variable}>
      <body className="font-sans antialiased bg-gradient-to-br from-slate-50 to-slate-100 dark:from-slate-900 dark:to-slate-800">
        <ErrorBoundary>
          <AuthProvider>
            <Header />
            {children}
            <Footer />
            <ChatbotWrapper />
          </AuthProvider>
        </ErrorBoundary>
      </body>
    </html>
  );
}
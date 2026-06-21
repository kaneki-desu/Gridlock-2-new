import type { Metadata } from 'next';
import Header from '@/components/Header';
import Footer from '@/components/Footer';
import './globals.css';

export const metadata: Metadata = {
  title: 'TrafficTwin AI - Traffic Intelligence System',
  description: 'Adaptive traffic intelligence system for event-driven congestion management',
  icons: {
    icon: '/favicon.ico',
  },
};

export default function RootLayout({ children }: { children: React.ReactNode }) {
  return (
    <html lang="en">
      <body className="bg-gray-50">
        <Header />
        <main className="container py-8 min-h-screen">
          {children}
        </main>
        <Footer />
      </body>
    </html>
  );
}

import React from 'react';
import Link from 'next/link';
import { AlertTriangle, BarChart3 } from 'lucide-react';

export default function Header() {
  return (
    <header className="bg-gradient-to-r from-blue-600 to-blue-800 text-white shadow-lg">
      <div className="container py-6">
        <div className="flex items-center justify-between">
          <Link href="/" className="flex items-center gap-3">
            <div className="bg-white bg-opacity-20 p-2 rounded-lg">
              <AlertTriangle size={28} />
            </div>
            <div>
              <h1 className="text-3xl font-bold">TrafficTwin AI</h1>
              <p className="text-blue-100 text-sm">Adaptive Traffic Intelligence</p>
            </div>
          </Link>
          
          <nav className="flex items-center gap-6">
            <Link href="/" className="hover:text-blue-100 transition">
              Dashboard
            </Link>
            <Link href="/incidents" className="hover:text-blue-100 transition">
              Incidents
            </Link>
            <Link href="/analytics" className="hover:text-blue-100 transition">
              Analytics
            </Link>
          </nav>
        </div>
      </div>
    </header>
  );
}

import React from 'react';

export default function Footer() {
  return (
    <footer className="bg-gray-800 text-gray-400 py-8 mt-12">
      <div className="container">
        <div className="grid grid-cols-1 md:grid-cols-3 gap-8 mb-8">
          <div>
            <h3 className="text-white font-bold mb-2">TrafficTwin AI</h3>
            <p className="text-sm">Intelligent traffic management powered by machine learning</p>
          </div>
          <div>
            <h4 className="text-white font-bold mb-3">Links</h4>
            <ul className="space-y-2 text-sm">
              <li><a href="/api/docs" className="hover:text-white transition">API Docs</a></li>
              <li><a href="#" className="hover:text-white transition">Documentation</a></li>
            </ul>
          </div>
          <div>
            <h4 className="text-white font-bold mb-3">Contact</h4>
            <p className="text-sm">Support: support@traffictwin.ai</p>
          </div>
        </div>
        <div className="border-t border-gray-700 pt-4 text-center text-sm">
          <p>&copy; 2024 TrafficTwin AI. All rights reserved.</p>
        </div>
      </div>
    </footer>
  );
}

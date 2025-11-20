import React, { useState, useEffect } from 'react';
import axios from 'axios';
import Dashboard from './components/Dashboard';
import { Activity, ShieldCheck, AlertTriangle } from 'lucide-react';

function App() {
  return (
    <div className="min-h-screen p-8">
      <header className="mb-10 flex items-center justify-between">
        <div>
          <h1 className="text-4xl font-bold bg-clip-text text-transparent bg-gradient-to-r from-blue-400 to-indigo-500">
            Anomaly Detection
          </h1>
          <p className="text-text-secondary mt-2">Real-time Transaction Monitoring System</p>
        </div>
        <div className="flex gap-4">
          <div className="flex items-center gap-2 px-4 py-2 bg-bg-secondary rounded-lg border border-white/5">
            <div className="w-2 h-2 rounded-full bg-green-500 animate-pulse"></div>
            <span className="text-sm font-medium">System Active</span>
          </div>
        </div>
      </header>
      
      <main>
        <Dashboard />
      </main>
    </div>
  );
}

export default App;

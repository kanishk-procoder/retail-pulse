import React, { useState, useEffect } from 'react';
import Sidebar from './components/Sidebar';
import Header from './components/Header';
import Overview from './pages/Overview';
import Segmentation from './pages/Segmentation';
import Forecasting from './pages/Forecasting';
import ChurnRadar from './pages/ChurnRadar';
import InventoryCenter from './pages/InventoryCenter';
import Leaderboard from './pages/Leaderboard';

export default function App() {
  const [activeTab, setActiveTab] = useState('overview');
  const [overviewData, setOverviewData] = useState(null);
  const [isRefreshing, setIsRefreshing] = useState(false);
  const [loading, setLoading] = useState(true);

  const fetchOverview = () => {
    setIsRefreshing(true);
    fetch('/api/overview')
      .then((res) => {
        if (!res.ok) throw new Error('API server unreachable');
        return res.json();
      })
      .then((data) => {
        setOverviewData(data);
        setIsRefreshing(false);
        setLoading(false);
      })
      .catch((err) => {
        console.error('Failed to fetch overview data:', err);
        setIsRefreshing(false);
        setLoading(false);
      });
  };

  useEffect(() => {
    fetchOverview();
  }, []);

  return (
    <div className="flex min-h-screen bg-slate-950 text-slate-100">
      {/* Sidebar Navigation */}
      <Sidebar
        activeTab={activeTab}
        setActiveTab={setActiveTab}
        kpis={overviewData?.kpis}
      />

      {/* Main Content Area */}
      <div className="flex-1 flex flex-col min-w-0">
        <Header
          activeTab={activeTab}
          onRefresh={fetchOverview}
          isRefreshing={isRefreshing}
        />

        <main className="flex-1 p-8 max-w-7xl w-full mx-auto">
          {loading ? (
            <div className="h-96 flex flex-col items-center justify-center text-slate-400 gap-3">
              <div className="w-8 h-8 border-2 border-sky-500 border-t-transparent rounded-full animate-spin"></div>
              <span className="text-sm font-medium">Connecting to RetailPulse FastAPI Engine...</span>
            </div>
          ) : (
            <>
              {activeTab === 'overview' && <Overview overviewData={overviewData} />}
              {activeTab === 'segmentation' && <Segmentation />}
              {activeTab === 'forecasting' && <Forecasting />}
              {activeTab === 'churn' && <ChurnRadar />}
              {activeTab === 'inventory' && <InventoryCenter />}
              {activeTab === 'leaderboard' && <Leaderboard />}
            </>
          )}
        </main>
      </div>
    </div>
  );
}


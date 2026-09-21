import React from 'react';
import { Search, RefreshCw, Layers, ShieldCheck } from 'lucide-react';

export default function Header({ activeTab, onRefresh, isRefreshing }) {
  const titles = {
    overview: { title: 'Executive Overview', desc: 'Real-time financial telemetry, rolling revenue trajectory, and geographic demand.' },
    segmentation: { title: 'Customer Segmentation Hub', desc: '5 behavioral clusters identified via K-Means with interactive customer lookup.' },
    forecasting: { title: 'Predictive Demand Forecasting', desc: 'Deep learning 30-day forward projections with What-If scenario simulation.' },
    churn: { title: 'Customer Churn Radar', desc: 'Proactive retention radar powered by Random Forest and global SHAP attribution.' },
    inventory: { title: 'Prescriptive Inventory Command', desc: 'Automated safety stock, reorder point alerts, and EOQ policy engine for 4,305 SKUs.' },
    leaderboard: { title: 'AI Model Tournament & Benchmarks', desc: 'Head-to-head performance leaderboard across all 18 evaluated algorithms.' }
  };

  const info = titles[activeTab] || titles.overview;

  return (
    <header className="h-20 border-b border-slate-800 bg-slate-900/60 backdrop-blur-md px-8 flex items-center justify-between sticky top-0 z-20">
      <div>
        <h1 className="text-xl font-bold text-white tracking-tight flex items-center gap-2">
          {info.title}
          <span className="text-xs font-semibold px-2 py-0.5 rounded-full bg-slate-800 text-sky-400 border border-slate-700">
            Live Production
          </span>
        </h1>
        <p className="text-xs text-slate-400 mt-0.5">{info.desc}</p>
      </div>

      <div className="flex items-center gap-4">
        <button
          onClick={onRefresh}
          disabled={isRefreshing}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-300 text-xs font-medium border border-slate-700/80 transition-colors disabled:opacity-50"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${isRefreshing ? 'animate-spin text-sky-400' : ''}`} />
          <span>Sync Data</span>
        </button>

        <div className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-emerald-500/10 text-emerald-400 border border-emerald-500/20 text-xs font-semibold">
          <ShieldCheck className="w-3.5 h-3.5" />
          <span>Champion Models Active</span>
        </div>
      </div>
    </header>
  );
}


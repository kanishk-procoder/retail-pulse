import React from 'react';
import {
  LayoutDashboard,
  Users,
  TrendingUp,
  AlertTriangle,
  Package,
  Award,
  Activity,
  Zap
} from 'lucide-react';

export default function Sidebar({ activeTab, setActiveTab, kpis }) {
  const navItems = [
    { id: 'overview', label: 'Executive Overview', icon: LayoutDashboard },
    { id: 'segmentation', label: 'Customer Segmentation', icon: Users },
    { id: 'forecasting', label: 'Demand Forecasting', icon: TrendingUp },
    {
      id: 'churn',
      label: 'Churn Risk Radar',
      icon: AlertTriangle,
      badge: kpis?.high_risk_customers ? `${kpis.high_risk_customers.toLocaleString()}` : null,
      badgeColor: 'bg-rose-500/20 text-rose-400 border-rose-500/30'
    },
    {
      id: 'inventory',
      label: 'Inventory Command',
      icon: Package,
      badge: kpis?.critical_inventory_items ? `${kpis.critical_inventory_items.toLocaleString()}` : null,
      badgeColor: 'bg-amber-500/20 text-amber-400 border-amber-500/30'
    },
    { id: 'leaderboard', label: 'Model Tournament', icon: Award, highlight: true }
  ];

  return (
    <aside className="w-64 bg-slate-900/90 border-r border-slate-800 flex flex-col justify-between shrink-0 h-screen sticky top-0">
      <div>
        {/* Brand Header */}
        <div className="p-5 border-b border-slate-800/80 flex items-center gap-3">
          <div className="w-10 h-10 rounded-xl bg-gradient-to-tr from-sky-500 to-indigo-600 flex items-center justify-center shadow-lg shadow-sky-500/20">
            <Activity className="w-5 h-5 text-white animate-pulse" />
          </div>
          <div>
            <div className="flex items-center gap-1.5">
              <span className="font-extrabold text-lg tracking-tight text-white">RetailPulse</span>
              <span className="text-[10px] font-bold px-1.5 py-0.5 rounded bg-sky-500/20 text-sky-400 border border-sky-500/30">AI 2.0</span>
            </div>
            <p className="text-xs text-slate-400">Enterprise Analytics</p>
          </div>
        </div>

        {/* Navigation Items */}
        <nav className="p-3 space-y-1">
          <div className="px-3 py-2 text-[11px] font-semibold tracking-wider text-slate-500 uppercase">
            Intelligence Modules
          </div>
          {navItems.map((item) => {
            const Icon = item.icon;
            const isActive = activeTab === item.id;
            return (
              <button
                key={item.id}
                onClick={() => setActiveTab(item.id)}
                className={`w-full flex items-center justify-between px-3.5 py-2.5 rounded-lg text-sm font-medium transition-all duration-200 ${
                  isActive
                    ? 'bg-sky-500 text-white shadow-lg shadow-sky-500/25'
                    : 'text-slate-300 hover:text-white hover:bg-slate-800/60'
                }`}
              >
                <div className="flex items-center gap-3">
                  <Icon className={`w-4 h-4 ${isActive ? 'text-white' : 'text-slate-400'}`} />
                  <span>{item.label}</span>
                </div>
                {item.badge && (
                  <span className={`text-[11px] px-2 py-0.5 rounded-full border font-semibold ${item.badgeColor}`}>
                    {item.badge}
                  </span>
                )}
                {item.highlight && !isActive && (
                  <span className="w-2 h-2 rounded-full bg-indigo-400"></span>
                )}
              </button>
            );
          })}
        </nav>
      </div>

      {/* Footer System Status */}
      <div className="p-4 border-t border-slate-800/80 bg-slate-950/40">
        <div className="flex items-center gap-2.5">
          <span className="relative flex h-2.5 w-2.5">
            <span className="animate-ping absolute inline-flex h-full w-full rounded-full bg-emerald-400 opacity-75"></span>
            <span className="relative inline-flex rounded-full h-2.5 w-2.5 bg-emerald-500"></span>
          </span>
          <div className="text-xs">
            <p className="font-semibold text-slate-200">FastAPI REST Engine</p>
            <p className="text-[11px] text-slate-400">Port 8000 • In-Memory Cache</p>
          </div>
        </div>
        <div className="mt-3 pt-3 border-t border-slate-800/60 flex justify-between items-center text-[10px] text-slate-500">
          <span>Zidio Dev Reference</span>
          <span className="font-mono">v2.0-SaaS</span>
        </div>
      </div>
    </aside>
  );
}


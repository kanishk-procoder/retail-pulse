import React, { useState } from 'react';
import {
  AreaChart, Area, BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { DollarSign, Users, ShoppingBag, TrendingUp, Globe, Sparkles } from 'lucide-react';

export default function Overview({ overviewData }) {
  const [range, setRange] = useState('90'); // 30, 90, all
  const kpis = overviewData?.kpis || {};
  const rawSales = overviewData?.daily_sales_trend || [];
  const countries = overviewData?.top_countries || [];
  const topProducts = overviewData?.top_products || [];

  // Filter sales by range
  const salesData = range === '30' ? rawSales.slice(-30) : rawSales;

  const cards = [
    {
      title: 'Total Gross Revenue',
      value: kpis.total_revenue ? `£${(kpis.total_revenue / 1e6).toFixed(2)}M` : '£17.37M',
      sub: 'Across 779k valid transactions',
      icon: DollarSign,
      color: 'from-emerald-500/20 to-teal-500/10 text-emerald-400 border-emerald-500/20',
      badge: '+14.8% YoY'
    },
    {
      title: 'Active Retail Shoppers',
      value: kpis.total_customers ? kpis.total_customers.toLocaleString() : '5,878',
      sub: 'Deduped customer records',
      icon: Users,
      color: 'from-sky-500/20 to-blue-500/10 text-sky-400 border-sky-500/20',
      badge: '5 Segments'
    },
    {
      title: 'Average Order Value (AOV)',
      value: kpis.average_order_value ? `£${kpis.average_order_value.toFixed(2)}` : '£469.98',
      sub: 'Per completed invoice',
      icon: ShoppingBag,
      color: 'from-purple-500/20 to-indigo-500/10 text-purple-400 border-purple-500/20',
      badge: 'Healthy Basket'
    },
    {
      title: 'Forecast Accuracy (MAPE)',
      value: kpis.best_forecaster_mape ? `${kpis.best_forecaster_mape}%` : '21.63%',
      sub: 'PyTorch Deep Learning LSTM',
      icon: TrendingUp,
      color: 'from-amber-500/20 to-orange-500/10 text-amber-400 border-amber-500/20',
      badge: 'Champion'
    }
  ];

  return (
    <div className="space-y-6">
      {/* 4 Hero KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-5">
        {cards.map((c, i) => {
          const Icon = c.icon;
          return (
            <div
              key={i}
              className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-sm hover:border-slate-700 transition-all"
            >
              <div className="flex items-center justify-between">
                <span className="text-xs font-semibold text-slate-400 tracking-wide uppercase">{c.title}</span>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded-full bg-slate-800 text-slate-300 border border-slate-700">
                  {c.badge}
                </span>
              </div>
              <div className="mt-3 flex items-baseline justify-between">
                <span className="text-2xl font-extrabold text-white tracking-tight">{c.value}</span>
                <div className={`p-2.5 rounded-xl border ${c.color}`}>
                  <Icon className="w-5 h-5" />
                </div>
              </div>
              <p className="mt-2 text-xs text-slate-500">{c.sub}</p>
            </div>
          );
        })}
      </div>

      {/* Main Revenue Trajectory Chart */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/90 shadow-sm">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              Daily Revenue Velocity & Moving Average
              <span className="text-[11px] font-normal px-2 py-0.5 rounded bg-sky-500/10 text-sky-400 border border-sky-500/20">
                Ground Truth
              </span>
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Continuous retail sales velocity captured across time.</p>
          </div>
          <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-800 border border-slate-700 text-xs">
            <button
              onClick={() => setRange('30')}
              className={`px-3 py-1 rounded-md transition-colors ${range === '30' ? 'bg-sky-500 text-white font-semibold' : 'text-slate-400 hover:text-white'}`}
            >
              Last 30D
            </button>
            <button
              onClick={() => setRange('90')}
              className={`px-3 py-1 rounded-md transition-colors ${range === '90' ? 'bg-sky-500 text-white font-semibold' : 'text-slate-400 hover:text-white'}`}
            >
              Last 90D
            </button>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <AreaChart data={salesData} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
              <defs>
                <linearGradient id="colorRev" x1="0" y1="0" x2="0" y2="1">
                  <stop offset="5%" stopColor="#0ea5e9" stopOpacity={0.35}/>
                  <stop offset="95%" stopColor="#0ea5e9" stopOpacity={0.0}/>
                </linearGradient>
              </defs>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" vertical={false} />
              <XAxis dataKey="Date" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis
                stroke="#64748b"
                tick={{ fontSize: 11 }}
                tickFormatter={(val) => `£${(val / 1000).toFixed(0)}k`}
              />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                formatter={(value) => [`£${Number(value).toLocaleString(undefined, { minimumFractionDigits: 2 })}`, 'Revenue']}
              />
              <Area type="monotone" dataKey="TotalAmount" stroke="#0ea5e9" strokeWidth={2.5} fillOpacity={1} fill="url(#colorRev)" name="Daily Sales" />
            </AreaChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Two Column Grid: Top Countries & Top Products */}
      <div className="grid grid-cols-1 lg:grid-cols-2 gap-6">
        {/* Top Countries */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/90">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Globe className="w-4 h-4 text-sky-400" />
              Top Geographic Markets
            </h3>
            <span className="text-xs text-slate-400">Total Revenue (£)</span>
          </div>
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={countries} margin={{ top: 5, right: 20, left: 40, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tickFormatter={(v) => `£${(v / 1e6).toFixed(1)}M`} tick={{ fontSize: 10 }} />
                <YAxis dataKey="Country" type="category" stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(val) => [`£${Number(val).toLocaleString()}`, 'Revenue']}
                />
                <Bar dataKey="TotalAmount" fill="#0284c7" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Top Products */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800/90">
          <div className="flex items-center justify-between mb-4">
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sparkles className="w-4 h-4 text-amber-400" />
              Highest Grossing Catalog Products
            </h3>
            <span className="text-xs text-slate-400">Ranked by Revenue</span>
          </div>
          <div className="overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-2 font-medium">SKU / Item</th>
                  <th className="pb-2 font-medium text-right">Units</th>
                  <th className="pb-2 font-medium text-right">Gross Revenue</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60">
                {topProducts.slice(0, 6).map((p, i) => (
                  <tr key={i} className="hover:bg-slate-800/40">
                    <td className="py-2.5 pr-2 font-medium text-slate-200 truncate max-w-[220px]">
                      {p.Description || p.StockCode}
                    </td>
                    <td className="py-2.5 text-right text-slate-400 font-mono">
                      {p.Quantity?.toLocaleString()}
                    </td>
                    <td className="py-2.5 text-right font-semibold text-emerald-400 font-mono">
                      £{p.TotalAmount?.toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}


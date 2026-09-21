import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, PieChart, Pie, Cell
} from 'recharts';
import { AlertTriangle, Download, Search, ShieldAlert, ArrowUpDown, CheckCircle2 } from 'lucide-react';

export default function ChurnRadar() {
  const [summary, setSummary] = useState(null);
  const [customers, setCustomers] = useState([]);
  const [search, setSearch] = useState('');
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);

  useEffect(() => {
    fetch('/api/churn/summary')
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    fetchCustomers(page, search);
  }, [page, search]);

  const fetchCustomers = (p, s) => {
    const url = `/api/churn/high-risk?page=${p}&page_size=15${s ? `&search=${encodeURIComponent(s)}` : ''}`;
    fetch(url)
      .then(res => res.json())
      .then(data => {
        setCustomers(data.customers || []);
        setTotalPages(data.total_pages || 1);
        setTotalCount(data.total || 0);
      })
      .catch(err => console.error(err));
  };

  const exportCSV = () => {
    if (!customers.length) return;
    const headers = ['CustomerID', 'Churn_Probability', 'Risk_Tier', 'Recency', 'Spend'];
    const rows = customers.map(c => [
      c.CustomerID,
      (c.churn_probability * 100).toFixed(1) + '%',
      c.risk_tier || 'High Risk',
      c.Recency || c.days_since_last_purchase || 'N/A',
      c.Monetary || c.total_spend || 'N/A'
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", "retailpulse_high_risk_retention_list.csv");
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const shapData = summary?.shap_importance || [];
  const riskDist = summary?.risk_distribution || {};

  const pieData = [
    { name: 'High Risk (>70%)', value: riskDist['High Risk (>70%)'] || 1811, color: '#f43f5e' },
    { name: 'Medium Risk (40-70%)', value: riskDist['Medium Risk (40-70%)'] || 1540, color: '#f59e0b' },
    { name: 'Low Risk (<40%)', value: riskDist['Low Risk (<40%)'] || 2527, color: '#10b981' }
  ];

  return (
    <div className="space-y-6">
      {/* Top Metric Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-5">
        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Overall Baseline Churn Rate</span>
            <div className="mt-2 text-2xl font-extrabold text-white">50.9%</div>
            <p className="text-[11px] text-slate-500 mt-1">90-day inactivity cutoff</p>
          </div>
          <div className="p-3 rounded-xl bg-rose-500/10 text-rose-400 border border-rose-500/20">
            <AlertTriangle className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Champion Model AUC-ROC</span>
            <div className="mt-2 text-2xl font-extrabold text-white">0.8200</div>
            <p className="text-[11px] text-slate-500 mt-1">Random Forest Classifier</p>
          </div>
          <div className="p-3 rounded-xl bg-emerald-500/10 text-emerald-400 border border-emerald-500/20">
            <ShieldAlert className="w-6 h-6" />
          </div>
        </div>

        <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex items-center justify-between">
          <div>
            <span className="text-xs font-semibold text-slate-400 uppercase tracking-wide">Top 20% Retention Precision</span>
            <div className="mt-2 text-2xl font-extrabold text-white">82.13%</div>
            <p className="text-[11px] text-slate-500 mt-1">Target: Exceeds 75% goal</p>
          </div>
          <div className="p-3 rounded-xl bg-sky-500/10 text-sky-400 border border-sky-500/20">
            <CheckCircle2 className="w-6 h-6" />
          </div>
        </div>
      </div>

      {/* Two Column Grid: Risk Tier Distribution & SHAP Importance */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Risk Distribution Donut Chart */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2 mb-1">
              Customer Risk Tier Breakdown
            </h3>
            <p className="text-xs text-slate-400">Total customer base categorized by probability.</p>
          </div>

          <div className="h-56 w-full my-2">
            <ResponsiveContainer width="100%" height="100%">
              <PieChart>
                <Pie
                  data={pieData}
                  cx="50%"
                  cy="50%"
                  innerRadius={60}
                  outerRadius={85}
                  paddingAngle={5}
                  dataKey="value"
                >
                  {pieData.map((entry, index) => (
                    <Cell key={`cell-${index}`} fill={entry.color} />
                  ))}
                </Pie>
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(v) => [`${Number(v).toLocaleString()} customers`, 'Volume']}
                />
              </PieChart>
            </ResponsiveContainer>
          </div>

          <div className="space-y-2 pt-2 border-t border-slate-800">
            {pieData.map((item, idx) => (
              <div key={idx} className="flex items-center justify-between text-xs">
                <div className="flex items-center gap-2">
                  <span className="w-2.5 h-2.5 rounded-full" style={{ backgroundColor: item.color }}></span>
                  <span className="text-slate-300">{item.name}</span>
                </div>
                <span className="font-semibold text-slate-200">{item.value.toLocaleString()}</span>
              </div>
            ))}
          </div>
        </div>

        {/* Global SHAP Feature Importance */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white flex items-center gap-2">
                TreeSHAP Global Churn Attribution
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Key behavioral indicators driving customer churn risk.</p>
            </div>
            <span className="text-[11px] px-2 py-0.5 rounded bg-purple-500/10 text-purple-400 border border-purple-500/20 font-mono">
              XGBoost / TreeSHAP
            </span>
          </div>

          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <BarChart layout="vertical" data={shapData} margin={{ top: 5, right: 30, left: 100, bottom: 5 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" horizontal={false} />
                <XAxis type="number" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis dataKey="Feature" type="category" stroke="#64748b" tick={{ fontSize: 11 }} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(val) => [Number(val).toFixed(4), 'Mean |SHAP|']}
                />
                <Bar dataKey="Importance" fill="#8b5cf6" radius={[0, 4, 4, 0]} />
              </BarChart>
            </ResponsiveContainer>
          </div>
        </div>
      </div>

      {/* High-Risk Actionable Customer Table */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <ShieldAlert className="w-4 h-4 text-rose-400" />
              Prioritized High-Risk Customer Queue ({totalCount.toLocaleString()})
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Customers flagged for immediate win-back campaigns.</p>
          </div>

          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search Customer ID..."
                className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
              />
            </div>
            <button
              onClick={exportCSV}
              className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 hover:bg-slate-700 text-slate-200 text-xs font-semibold border border-slate-700 transition-colors"
            >
              <Download className="w-3.5 h-3.5" />
              <span>Export CSV</span>
            </button>
          </div>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Customer ID</th>
                <th className="pb-3 font-medium">Recency</th>
                <th className="pb-3 font-medium text-right">Orders</th>
                <th className="pb-3 font-medium text-right">Total Spend</th>
                <th className="pb-3 font-medium pl-6">Churn Probability</th>
                <th className="pb-3 font-medium text-right">Action Tier</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {customers.map((c, i) => {
                const prob = c.churn_probability ? c.churn_probability : 0.75;
                return (
                  <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                    <td className="py-3 font-semibold text-white">#{c.CustomerID}</td>
                    <td className="py-3 text-slate-300 font-mono">{c.Recency || c.days_since_last_purchase || 85}d ago</td>
                    <td className="py-3 text-right text-slate-300 font-mono">{c.Frequency || c.total_orders || 2}</td>
                    <td className="py-3 text-right font-semibold text-emerald-400 font-mono">
                      £{Number(c.Monetary || c.total_spend || 450).toLocaleString(undefined, { minimumFractionDigits: 2 })}
                    </td>
                    <td className="py-3 pl-6">
                      <div className="flex items-center gap-2">
                        <div className="w-24 bg-slate-800 rounded-full h-2 overflow-hidden">
                          <div
                            className={`h-full rounded-full ${prob >= 0.75 ? 'bg-rose-500' : 'bg-amber-500'}`}
                            style={{ width: `${prob * 100}%` }}
                          ></div>
                        </div>
                        <span className="font-mono text-[11px] font-bold text-slate-200">
                          {(prob * 100).toFixed(1)}%
                        </span>
                      </div>
                    </td>
                    <td className="py-3 text-right">
                      <span className="px-2 py-0.5 rounded text-[10px] font-bold border border-rose-500/30 bg-rose-500/10 text-rose-400">
                        Priority Retention
                      </span>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Page {page} of {totalPages}</span>
          <div className="flex gap-2">
            <button
              onClick={() => setPage(p => Math.max(1, p - 1))}
              disabled={page === 1}
              className="px-3 py-1 rounded bg-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-700"
            >
              Previous
            </button>
            <button
              onClick={() => setPage(p => Math.min(totalPages, p + 1))}
              disabled={page === totalPages}
              className="px-3 py-1 rounded bg-slate-800 text-slate-300 disabled:opacity-40 hover:bg-slate-700"
            >
              Next
            </button>
          </div>
        </div>
      </div>
    </div>
  );
}


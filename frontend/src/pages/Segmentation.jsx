import React, { useState, useEffect } from 'react';
import {
  ScatterChart, Scatter, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, ZAxis
} from 'recharts';
import { Users, Search, ShieldCheck, ArrowRight, UserCheck, AlertCircle } from 'lucide-react';

export default function Segmentation() {
  const [segments, setSegments] = useState([]);
  const [customersSample, setCustomersSample] = useState([]);
  const [searchId, setSearchId] = useState('18102');
  const [searchedCustomer, setSearchedCustomer] = useState(null);
  const [searchError, setSearchError] = useState('');
  const [isSearching, setIsSearching] = useState(false);

  useEffect(() => {
    fetch('/api/segmentation/summary')
      .then(res => res.json())
      .then(data => setSegments(data.segments || []))
      .catch(err => console.error(err));

    fetch('/api/segmentation/customers?limit=350')
      .then(res => res.json())
      .then(data => setCustomersSample(data.customers || []))
      .catch(err => console.error(err));

    // Initial customer lookup
    handleSearch('18102');
  }, []);

  const handleSearch = (idToSearch) => {
    const targetId = idToSearch || searchId;
    if (!targetId) return;
    setIsSearching(true);
    setSearchError('');
    fetch(`/api/segmentation/customer/${targetId}`)
      .then(res => {
        if (!res.ok) throw new Error('Customer not found in database');
        return res.json();
      })
      .then(data => {
        setSearchedCustomer(data);
        setIsSearching(false);
      })
      .catch(err => {
        setSearchError(err.message);
        setSearchedCustomer(null);
        setIsSearching(false);
      });
  };

  const getSegmentColor = (name) => {
    if (name?.includes('Champion')) return 'border-emerald-500/40 bg-emerald-500/10 text-emerald-400';
    if (name?.includes('Loyal')) return 'border-sky-500/40 bg-sky-500/10 text-sky-400';
    if (name?.includes('Promising')) return 'border-indigo-500/40 bg-indigo-500/10 text-indigo-400';
    if (name?.includes('At Risk')) return 'border-amber-500/40 bg-amber-500/10 text-amber-400';
    return 'border-rose-500/40 bg-rose-500/10 text-rose-400';
  };

  return (
    <div className="space-y-6">
      {/* 5 Segment Overview Cards */}
      <div className="grid grid-cols-1 md:grid-cols-5 gap-4">
        {segments.map((s, i) => (
          <div
            key={i}
            className="p-4 rounded-xl bg-slate-900/70 border border-slate-800 shadow-sm flex flex-col justify-between hover:border-slate-700 transition-all"
          >
            <div>
              <span className={`text-[10px] font-bold px-2 py-0.5 rounded-md border inline-block ${getSegmentColor(s.RFM_Segment)}`}>
                {s.RFM_Segment}
              </span>
              <div className="mt-3">
                <span className="text-xl font-extrabold text-white">
                  {s.Customer_Count ? s.Customer_Count.toLocaleString() : (s.Count || 0).toLocaleString()}
                </span>
                <span className="text-xs text-slate-500 ml-1.5">customers</span>
              </div>
            </div>
            <div className="mt-4 pt-3 border-t border-slate-800/80 text-[11px] text-slate-400 space-y-1">
              <div className="flex justify-between">
                <span>Avg Spend:</span>
                <span className="font-semibold text-slate-200">£{Number(s.Avg_Spend || s.Mon_Mean || 0).toLocaleString(undefined, { maximumFractionDigits: 0 })}</span>
              </div>
              <div className="flex justify-between">
                <span>Recency:</span>
                <span className="font-semibold text-slate-200">{Number(s.Avg_Recency_Days || s.Rec_Mean || 0).toFixed(0)} days</span>
              </div>
            </div>
          </div>
        ))}
      </div>

      {/* Main Row: 2D Spatial Scatter Plot + Customer Lookup Tool */}
      <div className="grid grid-cols-1 lg:grid-cols-3 gap-6">
        {/* Spatial RFM Scatter Plot */}
        <div className="lg:col-span-2 p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
          <div className="flex items-center justify-between mb-4">
            <div>
              <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
                <Users className="w-4 h-4 text-sky-400" />
                Customer RFM Spatial Separation (Recency vs Monetary)
              </h3>
              <p className="text-xs text-slate-400 mt-0.5">Sampled customer distribution showing distinct behavioral clusters.</p>
            </div>
          </div>

          <div className="h-80 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <ScatterChart margin={{ top: 10, right: 20, bottom: 20, left: 10 }}>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis
                  type="number"
                  dataKey="Recency"
                  name="Recency"
                  unit="d"
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  label={{ value: 'Recency (Days Inactive)', position: 'insideBottom', offset: -10, fill: '#64748b', fontSize: 11 }}
                />
                <YAxis
                  type="number"
                  dataKey="Monetary"
                  name="Monetary Spend"
                  unit="£"
                  stroke="#64748b"
                  tick={{ fontSize: 11 }}
                  tickFormatter={(v) => `£${(v / 1000).toFixed(0)}k`}
                />
                <ZAxis type="number" dataKey="Frequency" range={[20, 140]} name="Orders" />
                <Tooltip
                  cursor={{ strokeDasharray: '3 3' }}
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(value, name) => [name === 'Recency' ? `${value} days` : `£${Number(value).toLocaleString()}`, name]}
                />
                <Scatter name="Customers" data={customersSample} fill="#38bdf8" fillOpacity={0.7} />
              </ScatterChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Live Customer Profile Lookup Card */}
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col justify-between">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <UserCheck className="w-4 h-4 text-emerald-400" />
              Customer Profile Lookup
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Inspect any individual customer's RFM tier & playbook.</p>

            {/* Search Input */}
            <div className="mt-4 flex gap-2">
              <div className="relative flex-1">
                <Search className="w-4 h-4 absolute left-3 top-3 text-slate-500" />
                <input
                  type="text"
                  value={searchId}
                  onChange={(e) => setSearchId(e.target.value)}
                  placeholder="e.g. 18102, 17850"
                  className="w-full pl-9 pr-3 py-2 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500"
                />
              </div>
              <button
                onClick={() => handleSearch()}
                disabled={isSearching}
                className="px-4 py-2 rounded-lg bg-sky-500 hover:bg-sky-600 text-white font-semibold text-xs transition-colors disabled:opacity-50"
              >
                {isSearching ? '...' : 'Search'}
              </button>
            </div>

            {searchError && (
              <div className="mt-3 p-3 rounded-lg bg-rose-500/10 border border-rose-500/20 text-rose-400 text-xs flex items-center gap-2">
                <AlertCircle className="w-4 h-4 shrink-0" />
                <span>{searchError}</span>
              </div>
            )}

            {searchedCustomer && (
              <div className="mt-5 space-y-3">
                <div className="flex items-center justify-between pb-3 border-b border-slate-800">
                  <div>
                    <span className="text-xs text-slate-400">Customer ID</span>
                    <p className="text-base font-bold text-white">#{searchedCustomer.CustomerID}</p>
                  </div>
                  <span className={`text-xs font-bold px-2.5 py-1 rounded-md border ${getSegmentColor(searchedCustomer.RFM_Segment)}`}>
                    {searchedCustomer.RFM_Segment}
                  </span>
                </div>

                <div className="grid grid-cols-3 gap-2 text-center">
                  <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-700/60">
                    <span className="text-[10px] text-slate-400">Recency</span>
                    <p className="text-xs font-bold text-slate-200 mt-0.5">{searchedCustomer.Recency}d</p>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-700/60">
                    <span className="text-[10px] text-slate-400">Orders</span>
                    <p className="text-xs font-bold text-slate-200 mt-0.5">{searchedCustomer.Frequency}</p>
                  </div>
                  <div className="p-2 rounded-lg bg-slate-800/60 border border-slate-700/60">
                    <span className="text-[10px] text-slate-400">Total Spend</span>
                    <p className="text-xs font-bold text-emerald-400 mt-0.5">£{Number(searchedCustomer.Monetary).toLocaleString()}</p>
                  </div>
                </div>

                <div className="p-3 rounded-xl bg-slate-800/80 border border-slate-700 text-xs">
                  <span className="font-semibold text-sky-400 flex items-center gap-1.5 mb-1">
                    <ShieldCheck className="w-3.5 h-3.5" />
                    Recommended Action Playbook:
                  </span>
                  <p className="text-slate-300 leading-relaxed text-[11px]">
                    {searchedCustomer.retention_playbook}
                  </p>
                </div>
              </div>
            )}
          </div>

          <div className="mt-4 pt-3 border-t border-slate-800 text-[11px] text-slate-500">
            K-Means Algorithm • Silhouette 0.3425 • 5 Distinct Clusters
          </div>
        </div>
      </div>
    </div>
  );
}


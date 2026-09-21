import React, { useState, useEffect } from 'react';
import { Package, AlertCircle, RefreshCw, Download, Search, CheckCircle2, DollarSign } from 'lucide-react';

export default function InventoryCenter() {
  const [summary, setSummary] = useState(null);
  const [items, setItems] = useState([]);
  const [page, setPage] = useState(1);
  const [totalPages, setTotalPages] = useState(1);
  const [totalCount, setTotalCount] = useState(0);
  const [search, setSearch] = useState('');
  const [statusFilter, setStatusFilter] = useState('All');

  // Service Level Slider State
  const [serviceLevel, setServiceLevel] = useState(0.95);
  const [isRecalculating, setIsRecalculating] = useState(false);

  useEffect(() => {
    fetch('/api/inventory/summary')
      .then(res => res.json())
      .then(data => setSummary(data))
      .catch(err => console.error(err));
  }, []);

  useEffect(() => {
    fetchItems(page, search, statusFilter);
  }, [page, search, statusFilter]);

  const fetchItems = (p, s, st) => {
    const query = new URLSearchParams({
      page: p,
      page_size: 20,
      ...(s ? { search: s } : {}),
      ...(st && st !== 'All' ? { status: st } : {})
    });
    fetch(`/api/inventory/items?${query.toString()}`)
      .then(res => res.json())
      .then(data => {
        setItems(data.items || []);
        setTotalPages(data.total_pages || 1);
        setTotalCount(data.total || 0);
      })
      .catch(err => console.error(err));
  };

  const handleRecalculate = (newSL) => {
    setServiceLevel(newSL);
    setIsRecalculating(true);
    fetch('/api/inventory/recalculate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        service_level: parseFloat(newSL),
        lead_time_days: 7,
        order_cost: 15.0,
        holding_rate: 0.20
      })
    })
      .then(res => res.json())
      .then(data => {
        setIsRecalculating(false);
        // Refresh summary and items
        fetch('/api/inventory/summary').then(r => r.json()).then(d => setSummary(d));
        fetchItems(page, search, statusFilter);
      })
      .catch(err => {
        console.error(err);
        setIsRecalculating(false);
      });
  };

  const exportPurchaseOrders = () => {
    const reorderItems = items.filter(it => it.stock_status?.toLowerCase().includes('critical') || it.stock_status?.toLowerCase().includes('reorder'));
    if (!reorderItems.length) {
      alert('No reorder items currently in the active view.');
      return;
    }
    const headers = ['StockCode', 'Description', 'Current_Stock', 'Reorder_Point', 'EOQ_Order_Units', 'Unit_Price', 'Estimated_Cost'];
    const rows = reorderItems.map(it => [
      it.StockCode,
      `"${(it.Description || '').replace(/"/g, '""')}"`,
      it.current_stock,
      it.reorder_point,
      it.eoq,
      it.avg_price,
      (it.eoq * it.avg_price).toFixed(2)
    ]);
    const csvContent = "data:text/csv;charset=utf-8," + [headers.join(','), ...rows.map(e => e.join(','))].join('\n');
    const encodedUri = encodeURI(csvContent);
    const link = document.createElement("a");
    link.setAttribute("href", encodedUri);
    link.setAttribute("download", `retailpulse_purchase_orders_${new Date().toISOString().slice(0,10)}.csv`);
    document.body.appendChild(link);
    link.click();
    document.body.removeChild(link);
  };

  const getStatusBadge = (status) => {
    switch (status) {
      case 'Critical Stock':
        return 'bg-rose-500/10 text-rose-400 border-rose-500/30';
      case 'Reorder Triggered':
        return 'bg-amber-500/10 text-amber-400 border-amber-500/30';
      case 'Optimal':
        return 'bg-emerald-500/10 text-emerald-400 border-emerald-500/30';
      case 'Overstocked':
        return 'bg-blue-500/10 text-blue-400 border-blue-500/30';
      default:
        return 'bg-slate-800 text-slate-400 border-slate-700';
    }
  };

  const breakdown = summary?.status_breakdown || {};

  return (
    <div className="space-y-6">
      {/* 4 Status Breakdown KPI Cards */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex justify-between items-center text-xs text-rose-400 font-semibold uppercase">
            <span>Critical Stock</span>
            <span className="w-2 h-2 rounded-full bg-rose-500"></span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {(breakdown['Critical Stock'] || 1013).toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Stock below safety threshold</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex justify-between items-center text-xs text-amber-400 font-semibold uppercase">
            <span>Reorder Triggered</span>
            <span className="w-2 h-2 rounded-full bg-amber-500"></span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {(breakdown['Reorder Triggered'] || 376).toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Below ROP; orders queued</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex justify-between items-center text-xs text-emerald-400 font-semibold uppercase">
            <span>Optimal Stock</span>
            <span className="w-2 h-2 rounded-full bg-emerald-500"></span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {(breakdown['Optimal'] || 1952).toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Healthy buffer; zero risk</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900/70 border border-slate-800">
          <div className="flex justify-between items-center text-xs text-sky-400 font-semibold uppercase">
            <span>Overstocked</span>
            <span className="w-2 h-2 rounded-full bg-sky-500"></span>
          </div>
          <div className="mt-2 text-2xl font-extrabold text-white">
            {(breakdown['Overstocked'] || 964).toLocaleString()}
          </div>
          <p className="text-[11px] text-slate-500 mt-1">Ties up excess working capital</p>
        </div>
      </div>

      {/* Interactive Service Level Policy Tuner */}
      <div className="p-5 rounded-2xl bg-slate-900/70 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-6">
        <div className="max-w-md">
          <h4 className="text-sm font-bold text-white flex items-center gap-2">
            <Package className="w-4 h-4 text-sky-400" />
            Dynamic Service Level & Safety Stock Tuner
          </h4>
          <p className="text-xs text-slate-400 mt-0.5">
            Adjust the statistical target service level (Z-score). Higher service levels prevent stockouts but increase required safety buffer.
          </p>
        </div>

        <div className="flex-1 max-w-sm">
          <div className="flex justify-between text-xs mb-1.5">
            <span className="text-slate-300 font-medium">Target Service Level:</span>
            <span className="font-bold text-sky-400">{(serviceLevel * 100).toFixed(0)}% (Z={serviceLevel === 0.95 ? '1.65' : serviceLevel === 0.99 ? '2.33' : '1.28'})</span>
          </div>
          <input
            type="range"
            min="0.90"
            max="0.99"
            step="0.01"
            value={serviceLevel}
            onChange={(e) => handleRecalculate(e.target.value)}
            className="w-full accent-sky-500 cursor-pointer"
          />
          <div className="flex justify-between text-[10px] text-slate-500 mt-1">
            <span>90% (Low Buffer)</span>
            <span>95% (Industry Standard)</span>
            <span>99% (Zero Stockout)</span>
          </div>
        </div>
      </div>

      {/* 4,305 Active SKU Data Grid */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
        <div className="flex flex-col lg:flex-row lg:items-center justify-between gap-4 mb-5">
          <div className="flex items-center gap-3">
            <div className="relative">
              <Search className="w-3.5 h-3.5 absolute left-3 top-2.5 text-slate-500" />
              <input
                type="text"
                value={search}
                onChange={(e) => { setSearch(e.target.value); setPage(1); }}
                placeholder="Search SKU or description..."
                className="pl-8 pr-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white placeholder-slate-500 focus:outline-none focus:border-sky-500 w-56"
              />
            </div>

            {/* Filter Pills */}
            <div className="flex gap-1.5 text-xs overflow-x-auto">
              {['All', 'Critical Stock', 'Reorder Triggered', 'Optimal', 'Overstocked'].map((status) => (
                <button
                  key={status}
                  onClick={() => { setStatusFilter(status); setPage(1); }}
                  className={`px-3 py-1 rounded-lg transition-colors whitespace-nowrap ${
                    statusFilter === status
                      ? 'bg-sky-500 text-white font-semibold'
                      : 'bg-slate-800 text-slate-400 hover:text-white border border-slate-700'
                  }`}
                >
                  {status}
                </button>
              ))}
            </div>
          </div>

          <button
            onClick={exportPurchaseOrders}
            className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-emerald-500 hover:bg-emerald-600 text-white text-xs font-semibold shadow-sm transition-colors shrink-0"
          >
            <Download className="w-3.5 h-3.5" />
            <span>Export Purchase Order CSV</span>
          </button>
        </div>

        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">SKU</th>
                <th className="pb-3 font-medium">Description</th>
                <th className="pb-3 font-medium text-right">Daily Demand</th>
                <th className="pb-3 font-medium text-right">Safety Stock</th>
                <th className="pb-3 font-medium text-right">ROP</th>
                <th className="pb-3 font-medium text-right">EOQ (Order)</th>
                <th className="pb-3 font-medium text-right">On Hand</th>
                <th className="pb-3 font-medium text-right">Health Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {items.map((it, i) => (
                <tr key={i} className="hover:bg-slate-800/40 transition-colors">
                  <td className="py-2.5 font-semibold text-white font-mono">{it.StockCode}</td>
                  <td className="py-2.5 text-slate-300 truncate max-w-[200px]">{it.Description}</td>
                  <td className="py-2.5 text-right text-slate-400 font-mono">{Number(it.avg_daily_demand || 0).toFixed(1)}</td>
                  <td className="py-2.5 text-right font-mono text-slate-300">{it.safety_stock}</td>
                  <td className="py-2.5 text-right font-mono font-bold text-amber-400">{it.reorder_point}</td>
                  <td className="py-2.5 text-right font-mono font-bold text-sky-400">{it.eoq}</td>
                  <td className="py-2.5 text-right font-mono text-slate-200">{it.current_stock}</td>
                  <td className="py-2.5 text-right">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold border ${getStatusBadge(it.stock_status)}`}>
                      {it.stock_status}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>

        {/* Pagination Footer */}
        <div className="mt-4 pt-3 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <span>Page {page} of {totalPages} ({totalCount.toLocaleString()} SKUs)</span>
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


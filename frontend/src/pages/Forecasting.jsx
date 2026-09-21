import React, { useState, useEffect } from 'react';
import {
  LineChart, Line, AreaChart, Area, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid, Legend
} from 'recharts';
import { TrendingUp, Sliders, Play, Award, CheckCircle2 } from 'lucide-react';

export default function Forecasting() {
  const [forecastData, setForecastData] = useState([]);
  const [availableModels, setAvailableModels] = useState([]);
  const [selectedModel, setSelectedModel] = useState('LSTM');
  const [metricsLeaderboard, setMetricsLeaderboard] = useState([]);

  // What-If Simulation State
  const [demandShock, setDemandShock] = useState(15);
  const [marketingBoost, setMarketingBoost] = useState(1.1);
  const [simulationResult, setSimulationResult] = useState(null);
  const [isSimulating, setIsSimulating] = useState(false);

  useEffect(() => {
    fetch('/api/forecasting/models')
      .then(res => res.json())
      .then(data => {
        setForecastData(data.trajectory || []);
        setAvailableModels(data.models_available || []);
        setMetricsLeaderboard(data.metrics_leaderboard || []);
      })
      .catch(err => console.error(err));

    // Run initial simulation
    runSimulation(15, 1.1, 'LSTM');
  }, []);

  const runSimulation = (shock, boost, model) => {
    setIsSimulating(true);
    fetch('/api/forecasting/simulate', {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify({
        demand_shock_pct: parseFloat(shock),
        marketing_multiplier: parseFloat(boost),
        model_choice: model
      })
    })
      .then(res => res.json())
      .then(data => {
        setSimulationResult(data);
        setIsSimulating(false);
      })
      .catch(err => {
        console.error(err);
        setIsSimulating(false);
      });
  };

  return (
    <div className="space-y-6">
      {/* Top Banner: Champion Model Highlight */}
      <div className="p-4 rounded-xl bg-gradient-to-r from-sky-500/15 via-indigo-500/10 to-transparent border border-sky-500/30 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-3">
          <div className="p-2 rounded-lg bg-sky-500 text-white">
            <Award className="w-5 h-5" />
          </div>
          <div>
            <h4 className="text-sm font-bold text-white">Champion Production Architecture: PyTorch Deep Learning LSTM</h4>
            <p className="text-xs text-slate-300">Achieves best-in-class 21.63% MAPE and £29,326 RMSE across 30-day forward test horizon.</p>
          </div>
        </div>
        <div className="flex items-center gap-2 text-xs">
          <span className="px-2.5 py-1 rounded-md bg-slate-800 text-emerald-400 font-semibold border border-slate-700">
            MAPE: 21.63%
          </span>
          <span className="px-2.5 py-1 rounded-md bg-slate-800 text-sky-400 font-semibold border border-slate-700">
            RMSE: £29.3k
          </span>
        </div>
      </div>

      {/* Main Forecast Chart: 30-Day Holdout */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
        <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-4 mb-6">
          <div>
            <h3 className="text-sm font-bold text-white tracking-tight flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-sky-400" />
              30-Day Forward Sales Trajectory vs Ground Truth
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Model predictions compared against actual holdout sales (£).</p>
          </div>

          {/* Model Selector */}
          <div className="flex items-center gap-2">
            <span className="text-xs text-slate-400">Model:</span>
            <select
              value={selectedModel}
              onChange={(e) => {
                setSelectedModel(e.target.value);
                runSimulation(demandShock, marketingBoost, e.target.value);
              }}
              className="px-3 py-1.5 rounded-lg bg-slate-800 border border-slate-700 text-xs text-white focus:outline-none focus:border-sky-500"
            >
              {availableModels.map(m => (
                <option key={m} value={m}>{m} {m === 'LSTM' ? '★ (Champion)' : ''}</option>
              ))}
            </select>
          </div>
        </div>

        <div className="h-72 w-full">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={forecastData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="Date" stroke="#64748b" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `£${(v / 1000).toFixed(0)}k`} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                formatter={(val, name) => [`£${Number(val).toLocaleString(undefined, { maximumFractionDigits: 0 })}`, name]}
              />
              <Legend wrapperStyle={{ fontSize: '12px' }} />
              <Line type="monotone" dataKey="Actual" stroke="#f8fafc" strokeWidth={3} dot={{ r: 3 }} name="Actual Ground Truth" />
              <Line type="monotone" dataKey={selectedModel} stroke="#0ea5e9" strokeWidth={2.5} strokeDasharray="4 4" dot={{ r: 3 }} name={`${selectedModel} Forecast`} />
              {selectedModel !== 'XGBoost' && forecastData[0]?.XGBoost && (
                <Line type="monotone" dataKey="XGBoost" stroke="#10b981" strokeWidth={1.5} dot={false} strokeOpacity={0.6} name="XGBoost Baseline" />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Interactive What-If Simulator + Scenario Projection */}
      <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 space-y-5">
        <div className="flex items-center justify-between border-b border-slate-800 pb-4">
          <div>
            <h3 className="text-sm font-bold text-white flex items-center gap-2">
              <Sliders className="w-4 h-4 text-purple-400" />
              Interactive "What-If" Demand & Promotion Simulator
            </h3>
            <p className="text-xs text-slate-400 mt-0.5">Stress-test market shifts, supply chain disruption, and holiday campaign lifts.</p>
          </div>
          {simulationResult && (
            <div className="flex items-center gap-3">
              <div className="text-right">
                <span className="text-[10px] text-slate-400 block">Projected 30D Revenue</span>
                <span className="text-sm font-extrabold text-emerald-400">
                  £{simulationResult.total_simulated_revenue?.toLocaleString()}
                </span>
              </div>
              <div className="text-right pl-3 border-l border-slate-800">
                <span className="text-[10px] text-slate-400 block">Net Impact</span>
                <span className={`text-sm font-extrabold ${simulationResult.revenue_delta >= 0 ? 'text-emerald-400' : 'text-rose-400'}`}>
                  {simulationResult.revenue_delta >= 0 ? '+' : ''}£{simulationResult.revenue_delta?.toLocaleString()} ({simulationResult.pct_change}%)
                </span>
              </div>
            </div>
          )}
        </div>

        {/* Controls Grid */}
        <div className="grid grid-cols-1 md:grid-cols-2 gap-6 p-4 rounded-xl bg-slate-800/40 border border-slate-700/60">
          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-slate-300 font-medium">Demand Shock / Market Shift</span>
              <span className="font-bold text-sky-400">{demandShock >= 0 ? `+${demandShock}%` : `${demandShock}%`}</span>
            </div>
            <input
              type="range"
              min="-40"
              max="50"
              step="5"
              value={demandShock}
              onChange={(e) => {
                setDemandShock(e.target.value);
                runSimulation(e.target.value, marketingBoost, selectedModel);
              }}
              className="w-full accent-sky-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>-40% Recession</span>
              <span>Baseline (0%)</span>
              <span>+50% Surge</span>
            </div>
          </div>

          <div>
            <div className="flex justify-between text-xs mb-2">
              <span className="text-slate-300 font-medium">Marketing Campaign Multiplier</span>
              <span className="font-bold text-purple-400">{(marketingBoost).toFixed(2)}x Boost</span>
            </div>
            <input
              type="range"
              min="0.8"
              max="1.5"
              step="0.05"
              value={marketingBoost}
              onChange={(e) => {
                setMarketingBoost(e.target.value);
                runSimulation(demandShock, e.target.value, selectedModel);
              }}
              className="w-full accent-purple-500 cursor-pointer"
            />
            <div className="flex justify-between text-[10px] text-slate-500 mt-1">
              <span>0.8x Ad Cut</span>
              <span>1.0x Normal</span>
              <span>1.5x Campaign Surge</span>
            </div>
          </div>
        </div>

        {/* Simulated Ribbon Area Chart */}
        {simulationResult?.simulated_trajectory && (
          <div className="h-64 w-full">
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={simulationResult.simulated_trajectory} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
                <defs>
                  <linearGradient id="simGradient" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="#8b5cf6" stopOpacity={0.4}/>
                    <stop offset="95%" stopColor="#8b5cf6" stopOpacity={0.0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                <XAxis dataKey="Date" stroke="#64748b" tick={{ fontSize: 11 }} />
                <YAxis stroke="#64748b" tick={{ fontSize: 11 }} tickFormatter={(v) => `£${(v / 1000).toFixed(0)}k`} />
                <Tooltip
                  contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }}
                  formatter={(val, name) => [`£${Number(val).toLocaleString(undefined, { maximumFractionDigits: 0 })}`, name]}
                />
                <Area type="monotone" dataKey="Upper_Bound" stroke="transparent" fill="#334155" fillOpacity={0.3} name="Upper 85% Buffer" />
                <Area type="monotone" dataKey="Simulated" stroke="#8b5cf6" strokeWidth={2.5} fill="url(#simGradient)" name="Simulated Demand" />
                <Area type="monotone" dataKey="Baseline" stroke="#0ea5e9" strokeWidth={1.5} strokeDasharray="3 3" fill="transparent" name="Original Baseline" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        )}
      </div>
    </div>
  );
}


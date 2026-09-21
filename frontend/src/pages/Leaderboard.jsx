import React, { useState, useEffect } from 'react';
import {
  BarChart, Bar, XAxis, YAxis, Tooltip, ResponsiveContainer, CartesianGrid
} from 'recharts';
import { Award, Trophy, CheckCircle, ShieldCheck } from 'lucide-react';

export default function Leaderboard() {
  const [leaderboards, setLeaderboards] = useState(null);
  const [activeDomain, setActiveDomain] = useState('churn'); // churn, forecasting, segmentation

  useEffect(() => {
    fetch('/api/leaderboard')
      .then(res => res.json())
      .then(data => setLeaderboards(data))
      .catch(err => console.error(err));
  }, []);

  const churnModels = leaderboards?.churn || [];
  const forecastingModels = leaderboards?.forecasting || [];
  const segmentationModels = leaderboards?.segmentation || [];

  return (
    <div className="space-y-6">
      {/* 3 Master Champions Summary Banner */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
        <div className="p-4 rounded-xl bg-gradient-to-br from-emerald-500/15 to-transparent border border-emerald-500/30">
          <div className="flex items-center gap-2 text-xs font-bold text-emerald-400 uppercase tracking-wide">
            <Trophy className="w-4 h-4" />
            <span>Segmentation Champion</span>
          </div>
          <div className="mt-2 text-lg font-extrabold text-white">K-Means Clustering</div>
          <p className="text-xs text-slate-400 mt-1">Silhouette: 0.3425 • Calinski-Harabasz: 4,848.2</p>
        </div>

        <div className="p-4 rounded-xl bg-gradient-to-br from-sky-500/15 to-transparent border border-sky-500/30">
          <div className="flex items-center gap-2 text-xs font-bold text-sky-400 uppercase tracking-wide">
            <Trophy className="w-4 h-4" />
            <span>Forecasting Champion</span>
          </div>
          <div className="mt-2 text-lg font-extrabold text-white">PyTorch LSTM</div>
          <p className="text-xs text-slate-400 mt-1">MAPE: 21.63% • RMSE: £29,326.38</p>
        </div>

        <div className="p-4 rounded-xl bg-gradient-to-br from-purple-500/15 to-transparent border border-purple-500/30">
          <div className="flex items-center gap-2 text-xs font-bold text-purple-400 uppercase tracking-wide">
            <Trophy className="w-4 h-4" />
            <span>Churn Classifier Champion</span>
          </div>
          <div className="mt-2 text-lg font-extrabold text-white">Random Forest</div>
          <p className="text-xs text-slate-400 mt-1">AUC-ROC: 0.8200 • Top 20% Precision: 82.13%</p>
        </div>
      </div>

      {/* Domain Tab Switcher */}
      <div className="flex border-b border-slate-800 gap-6 text-sm font-semibold">
        <button
          onClick={() => setActiveDomain('churn')}
          className={`pb-3 border-b-2 transition-colors ${
            activeDomain === 'churn' ? 'border-purple-500 text-purple-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Customer Churn (7 Classifiers)
        </button>
        <button
          onClick={() => setActiveDomain('forecasting')}
          className={`pb-3 border-b-2 transition-colors ${
            activeDomain === 'forecasting' ? 'border-sky-500 text-sky-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Demand Forecasting (7 Time-Series Models)
        </button>
        <button
          onClick={() => setActiveDomain('segmentation')}
          className={`pb-3 border-b-2 transition-colors ${
            activeDomain === 'segmentation' ? 'border-emerald-500 text-emerald-400' : 'border-transparent text-slate-400 hover:text-slate-200'
          }`}
        >
          Customer Segmentation (4 Clustering Models)
        </button>
      </div>

      {/* Content based on Active Domain */}
      {activeDomain === 'churn' && (
        <div className="space-y-6">
          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800">
            <h3 className="text-sm font-bold text-white mb-4">AUC-ROC vs Precision@Top20% Comparison</h3>
            <div className="h-64 w-full">
              <ResponsiveContainer width="100%" height="100%">
                <BarChart data={churnModels} margin={{ top: 10, right: 10, left: 0, bottom: 0 }}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="Model" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis domain={[0.65, 0.90]} stroke="#64748b" tick={{ fontSize: 11 }} />
                  <Tooltip contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '0.75rem', fontSize: '12px' }} />
                  <Bar dataKey="AUC_ROC" fill="#8b5cf6" name="AUC-ROC Score" radius={[4, 4, 0, 0]} />
                  <Bar dataKey="Precision_Top20" fill="#10b981" name="Precision @ Top 20%" radius={[4, 4, 0, 0]} />
                </BarChart>
              </ResponsiveContainer>
            </div>
          </div>

          <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 overflow-x-auto">
            <table className="w-full text-left text-xs">
              <thead>
                <tr className="border-b border-slate-800 text-slate-400">
                  <th className="pb-3 font-medium">Rank</th>
                  <th className="pb-3 font-medium">Algorithm</th>
                  <th className="pb-3 font-medium text-right">AUC-ROC</th>
                  <th className="pb-3 font-medium text-right">Accuracy</th>
                  <th className="pb-3 font-medium text-right">Recall</th>
                  <th className="pb-3 font-medium text-right">F1-Score</th>
                  <th className="pb-3 font-medium text-right">Precision@Top20%</th>
                  <th className="pb-3 font-medium text-right">Status</th>
                </tr>
              </thead>
              <tbody className="divide-y divide-slate-800/60 font-mono">
                {churnModels.map((m, i) => (
                  <tr key={i} className={`hover:bg-slate-800/40 ${m.Model === 'Random Forest' ? 'bg-purple-500/10' : ''}`}>
                    <td className="py-3 font-bold text-slate-400">#{i + 1}</td>
                    <td className="py-3 font-semibold text-white font-sans flex items-center gap-1.5">
                      {m.Model}
                      {m.Model === 'Random Forest' && <span className="text-[10px] px-1.5 py-0.2 rounded bg-purple-500 text-white font-bold">Champion</span>}
                    </td>
                    <td className="py-3 text-right text-purple-400 font-bold">{m.AUC_ROC?.toFixed(4)}</td>
                    <td className="py-3 text-right text-slate-300">{(m.Accuracy * 100)?.toFixed(1)}%</td>
                    <td className="py-3 text-right text-slate-300">{(m.Recall * 100)?.toFixed(1)}%</td>
                    <td className="py-3 text-right text-slate-300">{m.F1_Score?.toFixed(4)}</td>
                    <td className="py-3 text-right text-emerald-400 font-bold">{(m.Precision_Top20 * 100)?.toFixed(1)}%</td>
                    <td className="py-3 text-right font-sans">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${m.Model === 'Random Forest' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'text-slate-400'}`}>
                        {m.Model === 'Random Forest' ? 'Champion Selected' : 'Benchmarked'}
                      </span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      {activeDomain === 'forecasting' && (
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Rank</th>
                <th className="pb-3 font-medium">Architecture</th>
                <th className="pb-3 font-medium text-right">MAPE (%)</th>
                <th className="pb-3 font-medium text-right">RMSE (£)</th>
                <th className="pb-3 font-medium text-right">MAE (£)</th>
                <th className="pb-3 font-medium text-right">R² Score</th>
                <th className="pb-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {forecastingModels.map((m, i) => (
                <tr key={i} className={`hover:bg-slate-800/40 ${m.Model === 'LSTM' ? 'bg-sky-500/10' : ''}`}>
                  <td className="py-3 font-bold text-slate-400">#{i + 1}</td>
                  <td className="py-3 font-semibold text-white font-sans flex items-center gap-1.5">
                    {m.Model}
                    {m.Model === 'LSTM' && <span className="text-[10px] px-1.5 py-0.2 rounded bg-sky-500 text-white font-bold">Champion</span>}
                  </td>
                  <td className="py-3 text-right text-emerald-400 font-bold">{m.MAPE?.toFixed(2)}%</td>
                  <td className="py-3 text-right text-slate-300">£{Number(m.RMSE).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="py-3 text-right text-slate-300">£{Number(m.MAE).toLocaleString(undefined, { maximumFractionDigits: 0 })}</td>
                  <td className="py-3 text-right text-slate-300">{m.R2?.toFixed(4)}</td>
                  <td className="py-3 text-right font-sans">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${m.Model === 'LSTM' ? 'bg-sky-500/10 text-sky-400 border border-sky-500/30' : 'text-slate-400'}`}>
                      {m.Model === 'LSTM' ? 'Champion Selected' : 'Benchmarked'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}

      {activeDomain === 'segmentation' && (
        <div className="p-6 rounded-2xl bg-slate-900/70 border border-slate-800 overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead>
              <tr className="border-b border-slate-800 text-slate-400">
                <th className="pb-3 font-medium">Model</th>
                <th className="pb-3 font-medium text-right">Clusters</th>
                <th className="pb-3 font-medium text-right">Silhouette Score</th>
                <th className="pb-3 font-medium text-right">Calinski-Harabasz</th>
                <th className="pb-3 font-medium text-right">Davies-Bouldin</th>
                <th className="pb-3 font-medium text-right">Interpretability</th>
                <th className="pb-3 font-medium text-right">Status</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60 font-mono">
              {segmentationModels.map((m, i) => (
                <tr key={i} className={`hover:bg-slate-800/40 ${m.Model === 'K-Means' ? 'bg-emerald-500/10' : ''}`}>
                  <td className="py-3 font-semibold text-white font-sans flex items-center gap-1.5">
                    {m.Model}
                    {m.Model === 'K-Means' && <span className="text-[10px] px-1.5 py-0.2 rounded bg-emerald-500 text-white font-bold">Champion</span>}
                  </td>
                  <td className="py-3 text-right text-slate-300">{m.Clusters}</td>
                  <td className="py-3 text-right text-emerald-400 font-bold">{m.Silhouette_Score?.toFixed(4)}</td>
                  <td className="py-3 text-right text-slate-300">{Number(m.Calinski_Harabasz).toLocaleString()}</td>
                  <td className="py-3 text-right text-slate-300">{m.Davies_Bouldin?.toFixed(4)}</td>
                  <td className="py-3 text-right font-sans text-slate-300">{m.Interpretability}</td>
                  <td className="py-3 text-right font-sans">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${m.Model === 'K-Means' ? 'bg-emerald-500/10 text-emerald-400 border border-emerald-500/30' : 'text-slate-400'}`}>
                      {m.Model === 'K-Means' ? 'Champion Selected' : 'Benchmarked'}
                    </span>
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </div>
  );
}


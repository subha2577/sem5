import React, { useState } from 'react';
import { PlayCircle, ShieldCheck, AlertTriangle, RefreshCw, Info, CheckCircle2, ArrowRight } from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip, Legend, CartesianGrid
} from 'recharts';
import { api } from '../services/api';
import { SimulationResponse } from '../types';

export const SimulationPage: React.FC = () => {
  const [selectedTrajectory, setSelectedTrajectory] = useState('Group B - Temporary Variation');
  const [baselinePain, setBaselinePain] = useState(3.0);
  const [baselineTemp, setBaselineTemp] = useState(36.8);
  const [steps, setSteps] = useState(7);
  const [simResult, setSimResult] = useState<SimulationResponse | null>(null);
  const [loading, setLoading] = useState(false);

  const presets = [
    { id: 'Group A - Normal Recovery', label: '1. Normal Recovery', desc: 'Gradual post-op healing progression.' },
    { id: 'Group B - Temporary Variation', label: '2. Isolated Transient Spike', desc: 'Temporary pain/temp spike; tests alert suppression & "Why No Alert?".' },
    { id: 'Group C - Gradual Deterioration', label: '3. Gradual Deterioration', desc: 'Progressive multi-day upward trajectory in pain & wound score.' },
    { id: 'Group D - Wound Deterioration', label: '4. Wound-Dominant Deterioration', desc: 'Patient remains afebrile while wound inflammation worsens.' },
    { id: 'Group F - Multi-Signal Deterioration', label: '5. Multi-Signal Concurrent Breakdown', desc: 'Pain + Temp + Wound concordantly deteriorate.' },
    { id: 'Group G - Missing Data', label: '6. Monitoring Gap Detection', desc: 'Patient abruptly stops reporting home observations.' }
  ];

  const handleRunSimulation = async (presetId?: string) => {
    const group = presetId || selectedTrajectory;
    try {
      setLoading(true);
      const res = await api.runSimulation({
        trajectory_group: group,
        baseline_pain: baselinePain,
        baseline_temp: baselineTemp,
        observation_steps: steps
      });
      setSimResult(res);
    } catch (err) {
      console.error('Simulation failed:', err);
    } finally {
      setLoading(false);
    }
  };

  return (
    <div className="space-y-6">
      {/* Header */}
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Recovery Simulation Sandbox</h1>
        <p className="text-sm text-slate-400">
          Simulate clinical post-operative scenarios to test how RecoverAI reacts compared to traditional threshold monitoring.
        </p>
      </div>

      {/* Preset Scenario Cards */}
      <div className="grid grid-cols-1 md:grid-cols-3 gap-3">
        {presets.map((p) => {
          const isSelected = selectedTrajectory === p.id;
          return (
            <button
              key={p.id}
              onClick={() => {
                setSelectedTrajectory(p.id);
                handleRunSimulation(p.id);
              }}
              className={`p-3.5 rounded-xl border text-left transition-all ${
                isSelected
                  ? 'bg-cyan-600/20 border-cyan-500/50 text-white shadow-lg shadow-cyan-950/40'
                  : 'bg-slate-900 border-slate-800 text-slate-300 hover:bg-slate-800/60'
              }`}
            >
              <div className="font-semibold text-xs text-cyan-300">{p.label}</div>
              <div className="text-[11px] text-slate-400 mt-1 leading-snug">{p.desc}</div>
            </button>
          );
        })}
      </div>

      {/* Simulation Controls & Trigger Button */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-4">
        <div className="flex flex-wrap items-center gap-6 text-xs text-slate-300 w-full md:w-auto">
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">Baseline Pain ({baselinePain})</label>
            <input
              type="range"
              min="1"
              max="5"
              step="0.5"
              value={baselinePain}
              onChange={(e) => setBaselinePain(parseFloat(e.target.value))}
              className="w-32 accent-cyan-500"
            />
          </div>
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">Baseline Temp ({baselineTemp}°C)</label>
            <input
              type="range"
              min="36.5"
              max="37.2"
              step="0.1"
              value={baselineTemp}
              onChange={(e) => setBaselineTemp(parseFloat(e.target.value))}
              className="w-32 accent-cyan-500"
            />
          </div>
          <div>
            <label className="block text-[11px] text-slate-400 mb-1">Observation Steps ({steps})</label>
            <input
              type="range"
              min="5"
              max="10"
              value={steps}
              onChange={(e) => setSteps(parseInt(e.target.value))}
              className="w-28 accent-cyan-500"
            />
          </div>
        </div>

        <button
          onClick={() => handleRunSimulation()}
          disabled={loading}
          className="w-full md:w-auto px-5 py-2 rounded-lg bg-gradient-to-r from-cyan-600 to-indigo-600 hover:from-cyan-500 hover:to-indigo-500 text-white font-semibold text-xs flex items-center justify-center gap-2 shadow-md shadow-cyan-900/40 transition-all disabled:opacity-50"
        >
          <PlayCircle className={`w-4 h-4 ${loading ? 'animate-spin' : ''}`} />
          Run Realtime Simulation
        </button>
      </div>

      {/* Simulation Results Display */}
      {simResult && (
        <div className="space-y-6">
          {/* Simulated Trajectory Line Chart */}
          <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
            <div className="flex justify-between items-center">
              <div>
                <h3 className="text-sm font-bold text-white uppercase tracking-wider">Simulated Telemetry Stream</h3>
                <p className="text-xs text-slate-400">{simResult.trajectory_description}</p>
              </div>
              <span className="text-xs font-mono font-bold text-cyan-400 px-2 py-1 rounded bg-slate-950 border border-slate-800">
                {simResult.scenario_name}
              </span>
            </div>

            <div className="h-64 w-full pt-2">
              <ResponsiveContainer width="100%" height="100%">
                <LineChart data={simResult.observations}>
                  <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
                  <XAxis dataKey="observation_id" stroke="#64748b" tick={{ fontSize: 11 }} />
                  <YAxis stroke="#64748b" domain={[0, 10]} tick={{ fontSize: 11 }} />
                  <Tooltip
                    contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                    itemStyle={{ color: '#f1f5f9' }}
                  />
                  <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '8px' }} />
                  <Line type="monotone" dataKey="pain_score" name="Pain Score" stroke="#ef4444" strokeWidth={2.5} dot={{ r: 4 }} />
                  <Line type="monotone" dataKey="temperature" name="Temp (°C)" stroke="#f59e0b" strokeWidth={2} dot={{ r: 3 }} />
                  <Line type="monotone" dataKey="composite_wound_score" name="Wound Score" stroke="#a855f7" strokeWidth={2} dot={{ r: 3 }} />
                </LineChart>
              </ResponsiveContainer>
            </div>
          </div>

          {/* Side-by-Side Reaction Comparison */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            {/* Traditional Threshold Reaction */}
            <div className="p-5 rounded-xl bg-slate-900/80 border border-red-900/40 space-y-4">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-red-400">
                  <AlertTriangle className="w-4 h-4" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-white">Traditional Monitoring</h3>
                </div>
                <span className="text-[10px] font-bold px-2 py-0.5 rounded bg-red-950 text-red-400 border border-red-800">
                  Static Threshold Rule
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-2">
                <div className="flex justify-between items-center">
                  <span>Total Alerts Triggered:</span>
                  <span className="font-mono font-bold text-base text-red-400">
                    {simResult.simple_baseline_result.total_alerts_triggered} Alert(s)
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Alarm Fatigue Risk:</span>
                  <span className="font-semibold text-red-400">{simResult.simple_baseline_result.alert_fatigue_risk}</span>
                </div>
                <div className="text-[11px] text-slate-500 pt-1 border-t border-slate-800">
                  Rule: {simResult.simple_baseline_result.rule_description}
                </div>
              </div>
            </div>

            {/* RecoverAI Reaction */}
            <div className="p-5 rounded-xl bg-slate-900/80 border border-cyan-800/50 space-y-4 shadow-lg shadow-cyan-950/20">
              <div className="flex items-center justify-between">
                <div className="flex items-center gap-2 text-cyan-400">
                  <ShieldCheck className="w-4 h-4" />
                  <h3 className="text-sm font-bold uppercase tracking-wider text-white">RecoverAI Trend Engine</h3>
                </div>
                <span className={`text-[10px] font-bold px-2 py-0.5 rounded ${
                  simResult.recoverai_result.risk_category === 'High Priority' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                  simResult.recoverai_result.risk_category === 'Review' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                  simResult.recoverai_result.risk_category === 'Watch' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                  'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
                }`}>
                  {simResult.recoverai_result.risk_category} ({simResult.recoverai_result.risk_score}/100)
                </span>
              </div>

              <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800 text-xs text-slate-300 space-y-2">
                <div className="flex justify-between items-center">
                  <span>Actionable Alert Triggered?</span>
                  <span className={`font-bold ${simResult.recoverai_result.alert_triggered ? 'text-red-400' : 'text-emerald-400'}`}>
                    {simResult.recoverai_result.alert_triggered ? 'YES (Escalation Created)' : 'NO (Alarm Suppressed)'}
                  </span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Persistence Count:</span>
                  <span className="font-mono text-cyan-400">{simResult.recoverai_result.persistence_count} consecutive</span>
                </div>
                <div className="flex justify-between items-center">
                  <span>Multi-Signal Agreement:</span>
                  <span className="font-semibold text-slate-200">
                    {simResult.recoverai_result.multi_signal_agreement ? 'YES' : 'NO'}
                  </span>
                </div>
              </div>
            </div>
          </div>

          {/* Explainability Cards from Simulation */}
          <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <span className="text-xs font-bold text-cyan-400 uppercase tracking-wider">What Changed?</span>
              <div className="p-3 rounded-lg bg-slate-950 text-xs font-mono text-cyan-200 whitespace-pre-line border border-slate-800">
                {simResult.what_changed_summary}
              </div>
            </div>

            <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 space-y-2">
              <span className="text-xs font-bold text-emerald-400 uppercase tracking-wider">Why No Alert? (Fatigue Prevention)</span>
              <div className="p-3 rounded-lg bg-slate-950 text-xs font-mono text-emerald-300 whitespace-pre-line border border-slate-800">
                {simResult.why_no_alert_explanation || "Full alert criteria met; patient escalated due to persistent multi-signal trend."}
              </div>
            </div>
          </div>
        </div>
      )}
    </div>
  );
};

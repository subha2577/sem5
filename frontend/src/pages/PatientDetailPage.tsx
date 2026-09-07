import React, { useEffect, useState } from 'react';
import {
  ArrowLeft, Activity, ShieldCheck, AlertTriangle, Clock, CheckCircle2,
  TrendingUp, Info, UserCheck, Stethoscope, ChevronRight, MessageSquare
} from 'lucide-react';
import {
  ResponsiveContainer, LineChart, Line, XAxis, YAxis, Tooltip,
  Legend, ReferenceLine, CartesianGrid
} from 'recharts';
import { api } from '../services/api';
import { PatientDetail, Observation, Alert, Task } from '../types';

interface PatientDetailPageProps {
  patientId: string;
  onBack: () => void;
}

export const PatientDetailPage: React.FC<PatientDetailPageProps> = ({ patientId, onBack }) => {
  const [patient, setPatient] = useState<PatientDetail | null>(null);
  const [timeline, setTimeline] = useState<Observation[]>([]);
  const [loading, setLoading] = useState(true);
  const [selectedChartSignal, setSelectedChartSignal] = useState<'all' | 'pain' | 'temp' | 'wound'>('all');

  useEffect(() => {
    const fetchPatientData = async () => {
      try {
        setLoading(true);
        const [pData, tData] = await Promise.all([
          api.getPatientDetail(patientId),
          api.getPatientTimeline(patientId)
        ]);
        setPatient(pData);
        setTimeline(tData);
      } catch (err) {
        console.error('Failed to load patient detail:', err);
      } finally {
        setLoading(false);
      }
    };
    fetchPatientData();
  }, [patientId]);

  if (loading) {
    return (
      <div className="flex items-center justify-center h-96 text-slate-400">
        <div className="flex items-center gap-2">
          <Activity className="w-5 h-5 animate-spin text-cyan-400" />
          <span>Loading patient clinical telemetry and trajectory history...</span>
        </div>
      </div>
    );
  }

  if (!patient) {
    return (
      <div className="p-8 text-center text-slate-400">
        <p>Patient profile not found.</p>
        <button onClick={onBack} className="mt-4 px-4 py-2 bg-slate-800 rounded text-cyan-400 text-xs font-semibold">
          Return to Queue
        </button>
      </div>
    );
  }

  // Format timeline data for Recharts
  const chartData = timeline.map((obs, idx) => ({
    step: `Obs #${idx + 1}`,
    pod: `POD ${obs.postoperative_day}`,
    pain: obs.pain_score,
    temp: obs.temperature,
    wound: obs.composite_wound_score,
    baselinePain: patient.baseline?.baseline_pain || 3.0,
    baselineTemp: patient.baseline?.baseline_temperature || 36.8,
    isQuarantined: obs.is_quarantined
  }));

  return (
    <div className="space-y-6">
      {/* Navigation & Header */}
      <div className="flex items-center justify-between">
        <button
          onClick={onBack}
          className="flex items-center gap-2 text-xs font-medium text-slate-400 hover:text-white transition-colors"
        >
          <ArrowLeft className="w-4 h-4" /> Back to Priority Queue
        </button>
        <div className="flex items-center gap-2 text-xs text-slate-400">
          <span>Assigned Owner:</span>
          <span className="font-semibold text-cyan-300">{patient.assigned_owner}</span>
        </div>
      </div>

      {/* Patient Profile Header Card */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div className="flex items-center gap-4">
          <div className="w-12 h-12 rounded-xl bg-gradient-to-br from-cyan-600 to-slate-800 flex items-center justify-center text-white font-mono font-bold text-lg shadow-md">
            {patient.patient_id.substring(0, 3)}
          </div>
          <div>
            <div className="flex items-center gap-2">
              <h2 className="text-xl font-bold text-white font-mono">{patient.patient_id}</h2>
              <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                patient.current_priority === 'High Priority' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                patient.current_priority === 'Review' ? 'bg-orange-500/20 text-orange-300 border border-orange-500/30' :
                patient.current_priority === 'Watch' ? 'bg-amber-500/20 text-amber-300 border border-amber-500/30' :
                'bg-emerald-500/20 text-emerald-300 border border-emerald-500/30'
              }`}>
                {patient.current_priority}
              </span>
              <span className="text-xs px-2 py-0.5 rounded bg-slate-800 text-slate-300 border border-slate-700">
                POD {patient.postoperative_day}
              </span>
            </div>
            <p className="text-xs text-slate-400 mt-1">
              {patient.surgery_type} • Age: {patient.age_group} • {patient.assigned_care_team} • Contact: {patient.preferred_contact_method}
            </p>
          </div>
        </div>

        <div className="flex items-center gap-4">
          <div className="text-right">
            <div className="text-xs text-slate-400">Composite Risk Score</div>
            <div className={`text-3xl font-black font-mono ${
              patient.current_risk_score >= 75 ? 'text-red-400' :
              patient.current_risk_score >= 50 ? 'text-orange-400' :
              patient.current_risk_score >= 25 ? 'text-amber-400' : 'text-emerald-400'
            }`}>
              {patient.current_risk_score.toFixed(0)}<span className="text-xs text-slate-500 font-normal">/100</span>
            </div>
          </div>
          <div className="h-8 w-px bg-slate-800"></div>
          <div className="text-right">
            <div className="text-xs text-slate-400">Data Quality</div>
            <div className={`text-xl font-bold font-mono ${
              patient.latest_data_quality_score >= 80 ? 'text-emerald-400' : 'text-amber-400'
            }`}>
              {patient.latest_data_quality_score.toFixed(0)}%
            </div>
          </div>
        </div>
      </div>

      {/* Signature Recovery Trajectory Chart */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
        <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
          <div>
            <h3 className="text-base font-bold text-white tracking-tight flex items-center gap-2">
              <TrendingUp className="w-4 h-4 text-cyan-400" />
              Longitudinal Recovery Trajectory
            </h3>
            <p className="text-xs text-slate-400">
              Observations overlaid against personal baseline ($\Delta$) to reveal meaningful trajectory divergence.
            </p>
          </div>

          {/* Signal Filter Buttons */}
          <div className="flex items-center gap-1.5 p-1 rounded-lg bg-slate-950 border border-slate-800 text-xs">
            <button
              onClick={() => setSelectedChartSignal('all')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                selectedChartSignal === 'all' ? 'bg-cyan-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              All Signals
            </button>
            <button
              onClick={() => setSelectedChartSignal('pain')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                selectedChartSignal === 'pain' ? 'bg-red-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Pain vs Baseline
            </button>
            <button
              onClick={() => setSelectedChartSignal('temp')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                selectedChartSignal === 'temp' ? 'bg-amber-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Temperature
            </button>
            <button
              onClick={() => setSelectedChartSignal('wound')}
              className={`px-2.5 py-1 rounded font-medium transition-colors ${
                selectedChartSignal === 'wound' ? 'bg-purple-600 text-white' : 'text-slate-400 hover:text-slate-200'
              }`}
            >
              Wound Score
            </button>
          </div>
        </div>

        {/* Recharts Canvas */}
        <div className="h-72 w-full pt-2">
          <ResponsiveContainer width="100%" height="100%">
            <LineChart data={chartData} margin={{ top: 10, right: 20, left: 0, bottom: 0 }}>
              <CartesianGrid strokeDasharray="3 3" stroke="#1e293b" />
              <XAxis dataKey="step" stroke="#64748b" textAnchor="end" tick={{ fontSize: 11 }} />
              <YAxis stroke="#64748b" domain={[0, 10]} tick={{ fontSize: 11 }} />
              <Tooltip
                contentStyle={{ backgroundColor: '#0f172a', borderColor: '#334155', borderRadius: '8px', fontSize: '12px' }}
                itemStyle={{ color: '#f1f5f9' }}
              />
              <Legend wrapperStyle={{ fontSize: '12px', paddingTop: '10px' }} />

              {/* Personal Baseline Reference Line */}
              <ReferenceLine
                y={patient.baseline?.baseline_pain || 3.0}
                stroke="#f97316"
                strokeDasharray="4 4"
                label={{ value: `Pain Baseline (${patient.baseline?.baseline_pain || 3.0})`, fill: '#f97316', fontSize: 10, position: 'insideTopLeft' }}
              />

              {(selectedChartSignal === 'all' || selectedChartSignal === 'pain') && (
                <Line
                  type="monotone"
                  dataKey="pain"
                  name="Pain (0-10)"
                  stroke="#ef4444"
                  strokeWidth={2.5}
                  dot={{ r: 4, fill: '#ef4444' }}
                  activeDot={{ r: 6 }}
                />
              )}

              {(selectedChartSignal === 'all' || selectedChartSignal === 'temp') && (
                <Line
                  type="monotone"
                  dataKey="temp"
                  name="Temp (°C - normalized)"
                  stroke="#f59e0b"
                  strokeWidth={2}
                  dot={{ r: 3, fill: '#f59e0b' }}
                />
              )}

              {(selectedChartSignal === 'all' || selectedChartSignal === 'wound') && (
                <Line
                  type="monotone"
                  dataKey="wound"
                  name="Wound Score (0-10)"
                  stroke="#a855f7"
                  strokeWidth={2}
                  dot={{ r: 3, fill: '#a855f7' }}
                />
              )}
            </LineChart>
          </ResponsiveContainer>
        </div>
      </div>

      {/* Signature Product Features: What Changed? & Why No Alert? */}
      <div className="grid grid-cols-1 md:grid-cols-2 gap-6">
        {/* "What Changed?" Card */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-cyan-400">
            <Info className="w-4 h-4" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">Signature: What Changed?</h3>
          </div>
          <div className="text-xs text-slate-300 space-y-2">
            <p className="font-medium text-slate-200">
              Longitudinal analysis compared to personal baseline:
            </p>
            <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 font-mono text-xs whitespace-pre-line text-cyan-200 leading-relaxed">
              {patient.what_changed_summary || "• Telemetry is stable and tracking within historical personal baseline limits."}
            </div>
            <div className="text-[11px] text-slate-400">
              Baseline derived from {patient.baseline?.observation_count || 5} initial post-op readings (mean pain: {patient.baseline?.baseline_pain}, mean temp: {patient.baseline?.baseline_temperature}°C).
            </div>
          </div>
        </div>

        {/* "Why No Alert?" Fatigue Reduction Card */}
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
          <div className="flex items-center gap-2 text-emerald-400">
            <ShieldCheck className="w-4 h-4" />
            <h3 className="text-sm font-bold uppercase tracking-wider text-white">Signature: Why No Alert?</h3>
          </div>
          <div className="text-xs text-slate-300 space-y-2">
            <p className="font-medium text-slate-200">
              Alert fatigue prevention explanation:
            </p>
            {patient.why_no_alert_reason ? (
              <div className="p-3 rounded-lg bg-slate-950/70 border border-emerald-900/40 font-mono text-xs whitespace-pre-line text-emerald-300 leading-relaxed">
                {patient.why_no_alert_reason}
              </div>
            ) : patient.current_priority === 'High Priority' || patient.current_priority === 'Review' ? (
              <div className="p-3 rounded-lg bg-slate-950/70 border border-red-900/40 text-xs text-slate-300 space-y-1">
                <span className="text-red-400 font-bold">Alert Triggered:</span>
                <p>Criteria for clinical attention met. Concerning trajectory has persisted across multiple readings with concordant multi-signal indicators.</p>
              </div>
            ) : (
              <div className="p-3 rounded-lg bg-slate-950/70 border border-slate-800 text-xs text-slate-400">
                Patient is in stable recovery with no abnormal signals exceeding individual tolerance bounds.
              </div>
            )}
            <div className="text-[11px] text-slate-500">
              Suppresses isolated spikes without secondary signal agreement or persistence.
            </div>
          </div>
        </div>
      </div>

      {/* Risk Contributor Weights Decomposition */}
      {patient.risk_contributors && (
        <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-4">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">
            Risk Contributor Weight Decomposition ({patient.current_risk_score.toFixed(0)}/100)
          </h3>
          <div className="grid grid-cols-2 md:grid-cols-6 gap-3 text-xs">
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <div className="text-slate-400 text-[11px]">Baseline Delta</div>
              <div className="text-base font-bold text-cyan-400 mt-1">+{patient.risk_contributors.baseline_deviation.toFixed(1)}</div>
              <div className="text-[10px] text-slate-500">Max 30 pts</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <div className="text-slate-400 text-[11px]">Rate of Change</div>
              <div className="text-base font-bold text-cyan-400 mt-1">+{patient.risk_contributors.rate_of_change.toFixed(1)}</div>
              <div className="text-[10px] text-slate-500">Max 25 pts</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <div className="text-slate-400 text-[11px]">Persistence</div>
              <div className="text-base font-bold text-cyan-400 mt-1">+{patient.risk_contributors.persistence.toFixed(1)}</div>
              <div className="text-[10px] text-slate-500">Max 20 pts</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <div className="text-slate-400 text-[11px]">Multi-Signal</div>
              <div className="text-base font-bold text-cyan-400 mt-1">+{patient.risk_contributors.multi_signal.toFixed(1)}</div>
              <div className="text-[10px] text-slate-500">Max 15 pts</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <div className="text-slate-400 text-[11px]">Symptom Severity</div>
              <div className="text-base font-bold text-cyan-400 mt-1">+{patient.risk_contributors.symptom_severity.toFixed(1)}</div>
              <div className="text-[10px] text-slate-500">Max 10 pts</div>
            </div>
            <div className="p-3 rounded-lg bg-slate-950/60 border border-slate-800">
              <div className="text-slate-400 text-[11px]">Data Quality Adj</div>
              <div className="text-base font-bold text-amber-400 mt-1">{patient.risk_contributors.data_quality_adjustment.toFixed(1)}</div>
              <div className="text-[10px] text-slate-500">-5 to 0 pts</div>
            </div>
          </div>
        </div>
      )}

      {/* Raw Telemetry Observation History Table */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <div className="flex items-center justify-between">
          <h3 className="text-sm font-bold text-white uppercase tracking-wider">Longitudinal Telemetry Submissions</h3>
          <span className="text-xs text-slate-400">{timeline.length} readings recorded</span>
        </div>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] font-bold border-b border-slate-800">
              <tr>
                <th className="px-3 py-2">Time</th>
                <th className="px-3 py-2">POD</th>
                <th className="px-3 py-2">Pain (0-10)</th>
                <th className="px-3 py-2">Temp (°C)</th>
                <th className="px-3 py-2">Wound Composite</th>
                <th className="px-3 py-2">Fatigue</th>
                <th className="px-3 py-2">Mobility</th>
                <th className="px-3 py-2">Reported Concern</th>
                <th className="px-3 py-2">Quality</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {timeline.map((obs) => (
                <tr key={obs.observation_id} className="hover:bg-slate-800/30">
                  <td className="px-3 py-2 whitespace-nowrap text-slate-400 font-mono">
                    {new Date(obs.timestamp).toLocaleString([], { month: 'short', day: 'numeric', hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap font-medium text-slate-300">POD {obs.postoperative_day}</td>
                  <td className="px-3 py-2 whitespace-nowrap font-mono font-bold text-red-400">{obs.pain_score.toFixed(1)}</td>
                  <td className="px-3 py-2 whitespace-nowrap font-mono font-bold text-amber-400">{obs.temperature.toFixed(1)}°C</td>
                  <td className="px-3 py-2 whitespace-nowrap font-mono text-purple-400">{obs.composite_wound_score.toFixed(1)}</td>
                  <td className="px-3 py-2 whitespace-nowrap text-slate-300">{obs.fatigue_score.toFixed(1)}</td>
                  <td className="px-3 py-2 whitespace-nowrap text-slate-300">{obs.mobility_score.toFixed(1)}</td>
                  <td className="px-3 py-2 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                      obs.patient_reported_concern === 'Severe' ? 'bg-red-500/20 text-red-300' :
                      obs.patient_reported_concern === 'Moderate' ? 'bg-amber-500/20 text-amber-300' :
                      'bg-slate-800 text-slate-400'
                    }`}>
                      {obs.patient_reported_concern}
                    </span>
                  </td>
                  <td className="px-3 py-2 whitespace-nowrap">
                    {obs.is_quarantined ? (
                      <span className="px-1.5 py-0.5 rounded bg-red-950 text-red-400 border border-red-800 text-[10px] font-bold">
                        Quarantined
                      </span>
                    ) : (
                      <span className="text-[10px] text-emerald-400 font-medium">Valid</span>
                    )}
                  </td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

import React, { useEffect, useState } from 'react';
import { AlertTriangle, CheckCircle, ShieldCheck, Filter, Clock, Check, Eye } from 'lucide-react';
import { api } from '../services/api';
import { Alert } from '../types';

interface AlertsPageProps {
  onSelectPatient: (patientId: string) => void;
}

export const AlertsPage: React.FC<AlertsPageProps> = ({ onSelectPatient }) => {
  const [alerts, setAlerts] = useState<Alert[]>([]);
  const [loading, setLoading] = useState(true);
  const [severityFilter, setSeverityFilter] = useState('All');
  const [includeSuppressed, setIncludeSuppressed] = useState(false);

  const fetchAlerts = async () => {
    try {
      setLoading(true);
      const data = await api.getAlerts(severityFilter !== 'All' ? severityFilter : undefined, includeSuppressed);
      setAlerts(data);
    } catch (err) {
      console.error('Failed to load alerts:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchAlerts();
  }, [severityFilter, includeSuppressed]);

  const handleAcknowledge = async (alertId: string) => {
    try {
      await api.acknowledgeAlert(alertId, "Nurse Reviewer Sarah");
      fetchAlerts();
    } catch (err) {
      console.error('Failed to acknowledge alert:', err);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Alert Episode Management</h1>
          <p className="text-sm text-slate-400">
            Deduplicated into clinical episodes to prevent 20 identical notifications per deteriorating patient.
          </p>
        </div>

        {/* Filter Bar */}
        <div className="flex items-center gap-3">
          <select
            value={severityFilter}
            onChange={(e) => setSeverityFilter(e.target.value)}
            className="bg-slate-900 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Severities</option>
            <option value="High Priority">High Priority</option>
            <option value="Review">Review</option>
            <option value="Watch">Watch</option>
          </select>

          <label className="flex items-center gap-2 text-xs text-slate-300 cursor-pointer bg-slate-900 px-3 py-1.5 rounded-lg border border-slate-800">
            <input
              type="checkbox"
              checked={includeSuppressed}
              onChange={(e) => setIncludeSuppressed(e.target.checked)}
              className="rounded bg-slate-950 text-cyan-500 focus:ring-0"
            />
            <span>Show Suppressed Low-Value Alerts</span>
          </label>
        </div>
      </div>

      {/* Alerts Feed */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading alert queue...</div>
        ) : alerts.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-900 border border-slate-800 text-center text-slate-400">
            No alerts match the selected criteria.
          </div>
        ) : (
          alerts.map((alt) => (
            <div
              key={alt.alert_id}
              className={`p-4 rounded-xl border transition-all ${
                alt.is_suppressed
                  ? 'bg-slate-900/40 border-slate-800/60 opacity-70'
                  : alt.severity === 'High Priority'
                  ? 'bg-red-950/20 border-red-800/40 hover:border-red-600/60'
                  : 'bg-slate-900 border-slate-800 hover:border-cyan-700/50'
              }`}
            >
              <div className="flex flex-col md:flex-row md:items-center justify-between gap-2 mb-2">
                <div className="flex items-center gap-2">
                  <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                    alt.is_suppressed ? 'bg-slate-800 text-slate-400' :
                    alt.severity === 'High Priority' ? 'bg-red-500/20 text-red-400 border border-red-500/30' :
                    alt.severity === 'Review' ? 'bg-orange-500/20 text-orange-400 border border-orange-500/30' :
                    'bg-amber-500/20 text-amber-400 border border-amber-500/30'
                  }`}>
                    {alt.severity} {alt.is_suppressed ? '(Suppressed)' : ''}
                  </span>

                  <span className="font-mono font-bold text-xs text-cyan-400">{alt.patient_id}</span>
                  <span className="text-xs font-semibold text-white">{alt.title}</span>
                  {alt.episode_id && (
                    <span className="text-[10px] font-mono text-slate-500 px-1.5 py-0.5 rounded bg-slate-950 border border-slate-800">
                      Episode: {alt.episode_id}
                    </span>
                  )}
                </div>

                <div className="flex items-center gap-3">
                  <span className="text-xs text-slate-500 font-mono">
                    {new Date(alt.timestamp).toLocaleString()}
                  </span>
                  {!alt.acknowledged && !alt.is_suppressed && (
                    <button
                      onClick={() => handleAcknowledge(alt.alert_id)}
                      className="px-2.5 py-1 rounded bg-slate-800 hover:bg-emerald-800/40 hover:text-emerald-300 text-slate-300 border border-slate-700 text-xs font-medium transition-colors flex items-center gap-1"
                    >
                      <Check className="w-3.5 h-3.5" /> Acknowledge
                    </button>
                  )}
                  {alt.acknowledged && (
                    <span className="text-xs text-emerald-400 font-medium flex items-center gap-1">
                      <CheckCircle className="w-3.5 h-3.5" /> Acknowledged ({alt.acknowledged_by})
                    </span>
                  )}
                  <button
                    onClick={() => onSelectPatient(alt.patient_id)}
                    className="p-1 rounded text-slate-400 hover:text-white"
                    title="View Patient Profile"
                  >
                    <Eye className="w-4 h-4" />
                  </button>
                </div>
              </div>

              {/* Explanation & Reason text */}
              <div className="text-xs text-slate-300 whitespace-pre-line bg-slate-950/60 p-3 rounded-lg border border-slate-800/80 font-mono leading-relaxed mt-2">
                {alt.explanation}
              </div>

              {alt.is_suppressed && alt.suppression_reason && (
                <div className="mt-2 text-[11px] text-amber-400/90 font-medium flex items-center gap-1.5">
                  <ShieldCheck className="w-3.5 h-3.5 shrink-0" />
                  <span>Suppression Reason: {alt.suppression_reason}</span>
                </div>
              )}
            </div>
          ))
        )}
      </div>
    </div>
  );
};

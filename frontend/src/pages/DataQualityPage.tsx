import React, { useEffect, useState } from 'react';
import { Database, ShieldAlert, AlertTriangle, CheckCircle, Clock, RefreshCw, Eye } from 'lucide-react';
import { api } from '../services/api';

interface DataQualityPageProps {
  onSelectPatient: (patientId: string) => void;
}

export const DataQualityPage: React.FC<DataQualityPageProps> = ({ onSelectPatient }) => {
  const [summary, setSummary] = useState<any>(null);
  const [events, setEvents] = useState<any[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchData = async () => {
    try {
      setLoading(true);
      const [sum, ev] = await Promise.all([
        api.getDataQualitySummary(),
        api.getDataQualityEvents()
      ]);
      setSummary(sum);
      setEvents(ev);
    } catch (err) {
      console.error('Failed to load data quality telemetry:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchData();
  }, []);

  return (
    <div className="space-y-6">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Data Quality & Sensor Integrity Center</h1>
          <p className="text-sm text-slate-400">
            Automated boundary checks, sudden jump quarantine, duplicate suppression, and monitoring gap alerts.
          </p>
        </div>

        <button
          onClick={fetchData}
          className="flex items-center gap-2 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs font-medium border border-slate-700"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh
        </button>
      </div>

      {/* Summary KPI Cards */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Quarantined Records</div>
          <div className="text-2xl font-bold text-red-400 mt-1">{summary?.quarantined_records || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Physiologically invalid readings</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Monitoring Gaps</div>
          <div className="text-2xl font-bold text-amber-400 mt-1">{summary?.monitoring_gaps || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Patient inactive &gt; 36 hours</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Sudden Sensor Jumps</div>
          <div className="text-2xl font-bold text-orange-400 mt-1">{summary?.sudden_jumps || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">Flagged for spike dampening</p>
        </div>

        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Range Violations</div>
          <div className="text-2xl font-bold text-purple-400 mt-1">{summary?.range_violations || 0}</div>
          <p className="text-[11px] text-slate-500 mt-1">OutOfBounds values isolated</p>
        </div>
      </div>

      {/* Score Distribution */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Patient Cohort Quality Score Distribution</h3>
        <div className="grid grid-cols-1 md:grid-cols-3 gap-4 text-xs">
          <div className="p-3 rounded-lg bg-emerald-950/20 border border-emerald-800/40">
            <div className="text-emerald-400 font-bold">Good Quality (80-100%)</div>
            <div className="text-2xl font-bold text-white mt-1">{summary?.score_distribution?.['Good (80-100)'] || 0} patients</div>
            <p className="text-[11px] text-slate-400 mt-1">Full confidence for trend analysis</p>
          </div>
          <div className="p-3 rounded-lg bg-amber-950/20 border border-amber-800/40">
            <div className="text-amber-400 font-bold">Fair Quality (50-79%)</div>
            <div className="text-2xl font-bold text-white mt-1">{summary?.score_distribution?.['Fair (50-79)'] || 0} patients</div>
            <p className="text-[11px] text-slate-400 mt-1">Minor noise / reporting delays present</p>
          </div>
          <div className="p-3 rounded-lg bg-red-950/20 border border-red-800/40">
            <div className="text-red-400 font-bold">Poor Quality (&lt;50%)</div>
            <div className="text-2xl font-bold text-white mt-1">{summary?.score_distribution?.['Poor (<50)'] || 0} patients</div>
            <p className="text-[11px] text-slate-400 mt-1">Quarantined entries or severe reporting gaps</p>
          </div>
        </div>
      </div>

      {/* Data Quality Events Log Table */}
      <div className="p-5 rounded-xl bg-slate-900 border border-slate-800 space-y-3">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider">Flagged Data Quality Events Log</h3>
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] font-bold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Patient ID</th>
                <th className="px-4 py-3">Flag Type</th>
                <th className="px-4 py-3">Severity</th>
                <th className="px-4 py-3">Description</th>
                <th className="px-4 py-3">Quarantined?</th>
                <th className="px-4 py-3 text-center">Inspect</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {events.slice(0, 30).map((ev) => (
                <tr key={ev.event_id} className="hover:bg-slate-800/30">
                  <td className="px-4 py-2.5 font-mono text-slate-400 whitespace-nowrap">
                    {new Date(ev.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}
                  </td>
                  <td className="px-4 py-2.5 font-mono font-bold text-cyan-400 whitespace-nowrap">
                    {ev.patient_id}
                  </td>
                  <td className="px-4 py-2.5 whitespace-nowrap font-medium text-slate-300">
                    {ev.flag_type}
                  </td>
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    <span className={`px-2 py-0.5 rounded text-[10px] font-bold ${
                      ev.severity === 'Error' ? 'bg-red-500/20 text-red-300' : 'bg-amber-500/20 text-amber-300'
                    }`}>
                      {ev.severity}
                    </span>
                  </td>
                  <td className="px-4 py-2.5 text-slate-300 font-mono text-[11px]">
                    {ev.description}
                  </td>
                  <td className="px-4 py-2.5 whitespace-nowrap">
                    {ev.quarantined ? (
                      <span className="px-1.5 py-0.5 rounded bg-red-900/60 text-red-300 text-[10px] font-bold">YES</span>
                    ) : (
                      <span className="text-slate-500 text-[10px]">NO</span>
                    )}
                  </td>
                  <td className="px-4 py-2.5 text-center whitespace-nowrap">
                    <button
                      onClick={() => onSelectPatient(ev.patient_id)}
                      className="p-1 text-slate-400 hover:text-cyan-400"
                      title="Inspect Patient"
                    >
                      <Eye className="w-3.5 h-3.5" />
                    </button>
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

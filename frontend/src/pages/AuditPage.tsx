import React, { useEffect, useState } from 'react';
import { History, Shield, Filter, RefreshCw } from 'lucide-react';
import { api } from '../services/api';
import { AuditLog } from '../types';

export const AuditPage: React.FC = () => {
  const [logs, setLogs] = useState<AuditLog[]>([]);
  const [loading, setLoading] = useState(true);

  const fetchLogs = async () => {
    try {
      setLoading(true);
      const data = await api.getAuditLogs();
      setLogs(data);
    } catch (err) {
      console.error('Failed to load audit logs:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchLogs();
  }, []);

  return (
    <div className="space-y-4">
      <div className="flex items-center justify-between">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Clinical Governance & Audit Trail</h1>
          <p className="text-sm text-slate-400">
            Immutable chronological record of observation ingestion, alert evaluations, task assignments, and SLA escalations.
          </p>
        </div>
        <button
          onClick={fetchLogs}
          className="flex items-center gap-1.5 px-3 py-1.5 rounded-lg bg-slate-800 text-slate-300 hover:bg-slate-700 text-xs border border-slate-700 font-medium"
        >
          <RefreshCw className={`w-3.5 h-3.5 ${loading ? 'animate-spin' : ''}`} /> Refresh Trail
        </button>
      </div>

      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] font-bold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Timestamp</th>
                <th className="px-4 py-3">Actor</th>
                <th className="px-4 py-3">Event Type</th>
                <th className="px-4 py-3">Entity ID</th>
                <th className="px-4 py-3">Audit Details</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={5} className="text-center py-8 text-slate-500">Loading audit records...</td>
                </tr>
              ) : (
                logs.map((log) => (
                  <tr key={log.log_id} className="hover:bg-slate-800/30">
                    <td className="px-4 py-2.5 font-mono text-slate-400 whitespace-nowrap">
                      {new Date(log.timestamp).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit', second: '2-digit' })}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap font-medium text-cyan-400">
                      {log.actor}
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap font-semibold text-slate-300">
                      <span className="px-2 py-0.5 rounded bg-slate-800 border border-slate-700 font-mono text-[10px]">
                        {log.event_type}
                      </span>
                    </td>
                    <td className="px-4 py-2.5 whitespace-nowrap font-mono text-slate-400">
                      {log.entity_id || '—'}
                    </td>
                    <td className="px-4 py-2.5 text-slate-300 font-mono text-[11px]">
                      {log.description}
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  );
};

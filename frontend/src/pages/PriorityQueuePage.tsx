import React, { useEffect, useState } from 'react';
import { Search, Filter, ArrowUpRight, ArrowDownRight, Minus, AlertCircle, Clock, CheckCircle, ChevronLeft, ChevronRight } from 'lucide-react';
import { api } from '../services/api';
import { PatientListItem } from '../types';

interface PriorityQueuePageProps {
  onSelectPatient: (patientId: string) => void;
}

export const PriorityQueuePage: React.FC<PriorityQueuePageProps> = ({ onSelectPatient }) => {
  const [patients, setPatients] = useState<PatientListItem[]>([]);
  const [loading, setLoading] = useState(true);
  const [search, setSearch] = useState('');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [trendFilter, setTrendFilter] = useState('All');
  const [gapFilter, setGapFilter] = useState<boolean | undefined>(undefined);
  const [sortBy, setSortBy] = useState('risk_desc');

  const [page, setPage] = useState(1);
  const pageSize = 20;

  const fetchPatients = async () => {
    try {
      setLoading(true);
      const data = await api.getPatients({
        priority: priorityFilter !== 'All' ? priorityFilter : undefined,
        trend: trendFilter !== 'All' ? trendFilter : undefined,
        has_gap: gapFilter,
        search: search || undefined,
        limit: 100,
        sort_by: sortBy
      });
      setPatients(data);
    } catch (err) {
      console.error('Failed to load patients:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchPatients();
  }, [priorityFilter, trendFilter, gapFilter, sortBy]);

  const handleSearchSubmit = (e: React.FormEvent) => {
    e.preventDefault();
    fetchPatients();
  };

  const paginatedPatients = patients.slice((page - 1) * pageSize, page * pageSize);
  const totalPages = Math.ceil(patients.length / pageSize) || 1;

  const getPriorityBadge = (priority: string) => {
    switch (priority) {
      case 'High Priority':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-red-500/20 text-red-400 border border-red-500/30">High Priority</span>;
      case 'Review':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-orange-500/20 text-orange-400 border border-orange-500/30">Review</span>;
      case 'Watch':
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-amber-500/20 text-amber-400 border border-amber-500/30">Watch</span>;
      default:
        return <span className="px-2 py-0.5 text-[11px] font-bold rounded bg-emerald-500/20 text-emerald-400 border border-emerald-500/30">Stable</span>;
    }
  };

  const getTrendIcon = (trend: string) => {
    switch (trend) {
      case 'Worsening':
        return (
          <span className="flex items-center gap-1 text-orange-400 text-xs font-semibold">
            <ArrowUpRight className="w-4 h-4" /> Worsening
          </span>
        );
      case 'Improving':
        return (
          <span className="flex items-center gap-1 text-emerald-400 text-xs font-semibold">
            <ArrowDownRight className="w-4 h-4" /> Improving
          </span>
        );
      case 'Mixed':
        return (
          <span className="flex items-center gap-1 text-amber-400 text-xs font-semibold">
            <AlertCircle className="w-4 h-4" /> Mixed
          </span>
        );
      default:
        return (
          <span className="flex items-center gap-1 text-slate-400 text-xs font-medium">
            <Minus className="w-4 h-4" /> Stable
          </span>
        );
    }
  };

  return (
    <div className="space-y-4">
      {/* Header & Controls */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Clinical Priority Triage Queue</h1>
          <p className="text-sm text-slate-400">
            Prioritized by longitudinal delta from personal baseline, persistence count, and multi-signal concordance.
          </p>
        </div>
      </div>

      {/* Filter and Search Bar */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex flex-col md:flex-row items-center justify-between gap-3">
        <form onSubmit={handleSearchSubmit} className="relative w-full md:w-80">
          <Search className="w-4 h-4 text-slate-400 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder="Search patient ID, surgery, owner..."
            value={search}
            onChange={(e) => setSearch(e.target.value)}
            className="w-full pl-9 pr-3 py-1.5 text-xs bg-slate-950 border border-slate-800 rounded-lg text-slate-200 placeholder-slate-500 focus:outline-none focus:border-cyan-500"
          />
        </form>

        <div className="flex flex-wrap items-center gap-2 w-full md:w-auto">
          {/* Priority Filter */}
          <select
            value={priorityFilter}
            onChange={(e) => { setPriorityFilter(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Priorities</option>
            <option value="High Priority">High Priority</option>
            <option value="Review">Review</option>
            <option value="Watch">Watch</option>
            <option value="Stable">Stable</option>
          </select>

          {/* Trend Filter */}
          <select
            value={trendFilter}
            onChange={(e) => { setTrendFilter(e.target.value); setPage(1); }}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="All">All Trends</option>
            <option value="Worsening">Worsening</option>
            <option value="Stable">Stable</option>
            <option value="Improving">Improving</option>
            <option value="Mixed">Mixed</option>
          </select>

          {/* Monitoring Gap Filter */}
          <button
            type="button"
            onClick={() => {
              setGapFilter(gapFilter === true ? undefined : true);
              setPage(1);
            }}
            className={`px-3 py-1.5 rounded-lg text-xs font-medium border transition-colors ${
              gapFilter === true
                ? 'bg-amber-600/20 text-amber-300 border-amber-500/40'
                : 'bg-slate-950 text-slate-400 border-slate-800 hover:text-slate-200'
            }`}
          >
            Monitoring Gaps
          </button>

          {/* Sort */}
          <select
            value={sortBy}
            onChange={(e) => setSortBy(e.target.value)}
            className="bg-slate-950 border border-slate-800 rounded-lg px-2.5 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
          >
            <option value="risk_desc">Highest Risk Score</option>
            <option value="risk_asc">Lowest Risk Score</option>
            <option value="post_op_day">Post-Op Day</option>
          </select>
        </div>
      </div>

      {/* Main Priority Queue Table */}
      <div className="rounded-xl bg-slate-900 border border-slate-800 overflow-hidden shadow-xl">
        <div className="overflow-x-auto">
          <table className="w-full text-left text-xs">
            <thead className="bg-slate-950/80 text-slate-400 uppercase text-[10px] font-bold border-b border-slate-800">
              <tr>
                <th className="px-4 py-3">Priority</th>
                <th className="px-4 py-3">Patient ID</th>
                <th className="px-4 py-3">Surgery & Phase</th>
                <th className="px-4 py-3">Trajectory Trend</th>
                <th className="px-4 py-3">Main Signal / Reason</th>
                <th className="px-4 py-3 text-right">Risk Score</th>
                <th className="px-4 py-3">Care Team Owner</th>
                <th className="px-4 py-3">Data Quality</th>
                <th className="px-4 py-3 text-center">Action</th>
              </tr>
            </thead>
            <tbody className="divide-y divide-slate-800/60">
              {loading ? (
                <tr>
                  <td colSpan={9} className="text-center py-8 text-slate-500">
                    Loading clinical triage queue...
                  </td>
                </tr>
              ) : paginatedPatients.length === 0 ? (
                <tr>
                  <td colSpan={9} className="text-center py-8 text-slate-500">
                    No patients match current filter criteria.
                  </td>
                </tr>
              ) : (
                paginatedPatients.map((p) => (
                  <tr
                    key={p.patient_id}
                    onClick={() => onSelectPatient(p.patient_id)}
                    className="hover:bg-slate-800/40 cursor-pointer transition-colors"
                  >
                    <td className="px-4 py-3 whitespace-nowrap">
                      {getPriorityBadge(p.current_priority)}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap font-mono font-bold text-cyan-400">
                      {p.patient_id}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-slate-200 font-medium">{p.surgery_type}</div>
                      <div className="text-[10px] text-slate-400">POD {p.postoperative_day} • {p.recovery_phase}</div>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      {getTrendIcon(p.current_trend_direction)}
                    </td>
                    <td className="px-4 py-3">
                      <div className="text-slate-300 font-medium line-clamp-1">{p.primary_signal}</div>
                      {p.has_monitoring_gap && (
                        <span className="text-[10px] text-amber-400 font-semibold uppercase">Monitoring Gap Detected</span>
                      )}
                    </td>
                    <td className="px-4 py-3 text-right whitespace-nowrap">
                      <span className={`font-mono font-bold text-sm ${
                        p.current_risk_score >= 75 ? 'text-red-400' :
                        p.current_risk_score >= 50 ? 'text-orange-400' :
                        p.current_risk_score >= 25 ? 'text-amber-400' : 'text-emerald-400'
                      }`}>
                        {p.current_risk_score.toFixed(0)}
                      </span>
                      <span className="text-[10px] text-slate-500">/100</span>
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <div className="text-slate-300">{p.assigned_owner}</div>
                      {p.has_active_escalation && (
                        <span className="text-[10px] text-purple-400 font-bold uppercase">Supervisor Escalated</span>
                      )}
                    </td>
                    <td className="px-4 py-3 whitespace-nowrap">
                      <span className={`px-2 py-0.5 rounded text-[10px] font-semibold ${
                        p.latest_data_quality_score >= 80 ? 'bg-emerald-500/10 text-emerald-400' :
                        p.latest_data_quality_score >= 50 ? 'bg-amber-500/10 text-amber-400' : 'bg-red-500/10 text-red-400'
                      }`}>
                        {p.latest_data_quality_score.toFixed(0)}%
                      </span>
                    </td>
                    <td className="px-4 py-3 text-center whitespace-nowrap">
                      <button
                        onClick={(e) => {
                          e.stopPropagation();
                          onSelectPatient(p.patient_id);
                        }}
                        className="px-2.5 py-1 rounded bg-cyan-600/20 hover:bg-cyan-600/40 text-cyan-300 border border-cyan-500/30 font-medium text-xs transition-colors"
                      >
                        Inspect
                      </button>
                    </td>
                  </tr>
                ))
              )}
            </tbody>
          </table>
        </div>

        {/* Pagination Controls */}
        <div className="p-3 bg-slate-950/80 border-t border-slate-800 flex items-center justify-between text-xs text-slate-400">
          <div>
            Showing {(page - 1) * pageSize + 1} to {Math.min(page * pageSize, patients.length)} of {patients.length} patients
          </div>
          <div className="flex items-center gap-2">
            <button
              disabled={page <= 1}
              onClick={() => setPage(page - 1)}
              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700"
            >
              <ChevronLeft className="w-3.5 h-3.5" />
            </button>
            <span className="font-mono">Page {page} of {totalPages}</span>
            <button
              disabled={page >= totalPages}
              onClick={() => setPage(page + 1)}
              className="px-2 py-1 rounded bg-slate-800 border border-slate-700 disabled:opacity-40 disabled:cursor-not-allowed hover:bg-slate-700"
            >
              <ChevronRight className="w-3.5 h-3.5" />
            </button>
          </div>
        </div>
      </div>
    </div>
  );
};

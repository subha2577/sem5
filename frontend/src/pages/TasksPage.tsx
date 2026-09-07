import React, { useEffect, useState } from 'react';
import { CheckSquare, AlertTriangle, Clock, UserCheck, ShieldAlert, CheckCircle2, ChevronRight, Eye } from 'lucide-react';
import { api } from '../services/api';
import { Task } from '../types';

interface TasksPageProps {
  onSelectPatient: (patientId: string) => void;
}

export const TasksPage: React.FC<TasksPageProps> = ({ onSelectPatient }) => {
  const [tasks, setTasks] = useState<Task[]>([]);
  const [loading, setLoading] = useState(true);
  const [statusFilter, setStatusFilter] = useState('All');
  const [priorityFilter, setPriorityFilter] = useState('All');
  const [resolvingTaskId, setResolvingTaskId] = useState<string | null>(null);
  const [resolutionNote, setResolutionNote] = useState('');

  const fetchTasks = async () => {
    try {
      setLoading(true);
      const data = await api.getTasks(
        statusFilter !== 'All' ? statusFilter : undefined,
        priorityFilter !== 'All' ? priorityFilter : undefined
      );
      setTasks(data);
    } catch (err) {
      console.error('Failed to load tasks:', err);
    } finally {
      setLoading(false);
    }
  };

  useEffect(() => {
    fetchTasks();
  }, [statusFilter, priorityFilter]);

  const handleUpdateStatus = async (taskId: string, newStatus: string, note?: string) => {
    try {
      await api.updateTask(taskId, { status: newStatus, resolution_note: note });
      setResolvingTaskId(null);
      setResolutionNote('');
      fetchTasks();
    } catch (err) {
      console.error('Failed to update task:', err);
    }
  };

  const handleCheckEscalations = async () => {
    try {
      const res = await api.checkEscalations();
      alert(`Escalation scan completed: ${res.escalated_count} overdue task(s) auto-escalated.`);
      fetchTasks();
    } catch (err) {
      console.error('Failed to check escalations:', err);
    }
  };

  return (
    <div className="space-y-4">
      {/* Header */}
      <div className="flex flex-col md:flex-row md:items-center justify-between gap-4">
        <div>
          <h1 className="text-2xl font-bold text-white tracking-tight">Clinical Task & Escalation Queue</h1>
          <p className="text-sm text-slate-400">
            Ownership accountability, SLA due times, and automatic multi-tier supervisor escalation.
          </p>
        </div>

        <div className="flex items-center gap-3">
          <button
            onClick={handleCheckEscalations}
            className="px-3 py-1.5 rounded-lg bg-indigo-600/20 hover:bg-indigo-600/40 text-indigo-300 border border-indigo-500/30 text-xs font-semibold flex items-center gap-1.5 transition-colors"
          >
            <ShieldAlert className="w-3.5 h-3.5" /> Check Overdue Escalations
          </button>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="p-4 rounded-xl bg-slate-900 border border-slate-800 flex items-center gap-3">
        <select
          value={statusFilter}
          onChange={(e) => setStatusFilter(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
        >
          <option value="All">All Statuses</option>
          <option value="Assigned">Assigned</option>
          <option value="In Review">In Review</option>
          <option value="Escalated">Escalated</option>
          <option value="Resolved">Resolved</option>
        </select>

        <select
          value={priorityFilter}
          onChange={(e) => setPriorityFilter(e.target.value)}
          className="bg-slate-950 border border-slate-800 rounded-lg px-3 py-1.5 text-xs text-slate-300 focus:outline-none focus:border-cyan-500"
        >
          <option value="All">All Priorities</option>
          <option value="High Priority">High Priority</option>
          <option value="Review">Review</option>
          <option value="Watch">Watch</option>
        </select>
      </div>

      {/* Task List */}
      <div className="space-y-3">
        {loading ? (
          <div className="p-8 text-center text-slate-500">Loading task queue...</div>
        ) : tasks.length === 0 ? (
          <div className="p-8 rounded-xl bg-slate-900 border border-slate-800 text-center text-slate-400">
            No clinical tasks match current filters.
          </div>
        ) : (
          tasks.map((task) => {
            const isOverdue = new Date() > new Date(task.due_at) && task.status !== 'Resolved';
            return (
              <div
                key={task.task_id}
                className={`p-4 rounded-xl border transition-all ${
                  task.status === 'Resolved' ? 'bg-slate-900/40 border-slate-800 opacity-60' :
                  task.escalation_level >= 2 ? 'bg-purple-950/20 border-purple-800/50' :
                  task.priority === 'High Priority' ? 'bg-red-950/20 border-red-800/40' :
                  'bg-slate-900 border-slate-800'
                }`}
              >
                <div className="flex flex-col md:flex-row md:items-center justify-between gap-3">
                  <div className="flex items-center gap-3">
                    <span className={`px-2 py-0.5 text-xs font-bold rounded ${
                      task.priority === 'High Priority' ? 'bg-red-500/20 text-red-300 border border-red-500/30' :
                      'bg-orange-500/20 text-orange-300 border border-orange-500/30'
                    }`}>
                      {task.priority}
                    </span>

                    <span className="font-mono font-bold text-xs text-cyan-400">{task.patient_id}</span>

                    <span className={`text-[10px] font-bold uppercase px-2 py-0.5 rounded ${
                      task.escalation_level === 1 ? 'bg-slate-800 text-slate-300' :
                      task.escalation_level === 2 ? 'bg-purple-500/20 text-purple-300 border border-purple-500/30' :
                      'bg-red-500/20 text-red-300 border border-red-500/30'
                    }`}>
                      Level {task.escalation_level}: {task.assigned_role}
                    </span>

                    <span className="text-xs text-slate-300 font-medium">{task.assigned_to}</span>
                  </div>

                  <div className="flex items-center gap-3">
                    <div className="text-xs flex items-center gap-1.5">
                      <Clock className="w-3.5 h-3.5 text-slate-500" />
                      <span className={isOverdue ? 'text-red-400 font-bold' : 'text-slate-400'}>
                        {isOverdue ? 'OVERDUE (Escalating)' : `Due: ${new Date(task.due_at).toLocaleTimeString([], { hour: '2-digit', minute: '2-digit' })}`}
                      </span>
                    </div>

                    <span className={`px-2 py-0.5 rounded text-[11px] font-bold ${
                      task.status === 'Resolved' ? 'bg-emerald-500/20 text-emerald-400' :
                      task.status === 'Escalated' ? 'bg-purple-500/20 text-purple-300' :
                      task.status === 'In Review' ? 'bg-cyan-500/20 text-cyan-300' :
                      'bg-slate-800 text-slate-300'
                    }`}>
                      {task.status}
                    </span>

                    <button
                      onClick={() => onSelectPatient(task.patient_id)}
                      className="p-1 rounded text-slate-400 hover:text-white"
                      title="Inspect Patient"
                    >
                      <Eye className="w-4 h-4" />
                    </button>
                  </div>
                </div>

                {/* Actions & Resolution Note */}
                <div className="mt-3 pt-3 border-t border-slate-800/80 flex flex-col md:flex-row items-start md:items-center justify-between gap-3 text-xs">
                  <div className="text-slate-400 font-mono text-[11px]">
                    Task ID: {task.task_id} {task.alert_id ? `• Linked Alert: ${task.alert_id}` : ''}
                  </div>

                  {task.status !== 'Resolved' && (
                    <div className="flex items-center gap-2">
                      {task.status === 'Assigned' && (
                        <button
                          onClick={() => handleUpdateStatus(task.task_id, 'In Review')}
                          className="px-2.5 py-1 rounded bg-slate-800 hover:bg-slate-700 text-slate-200 border border-slate-700"
                        >
                          Mark In Review
                        </button>
                      )}
                      <button
                        onClick={() => setResolvingTaskId(task.task_id)}
                        className="px-2.5 py-1 rounded bg-emerald-600/20 hover:bg-emerald-600/40 text-emerald-300 border border-emerald-500/30 font-medium"
                      >
                        Resolve Task
                      </button>
                    </div>
                  )}

                  {task.status === 'Resolved' && task.resolution_note && (
                    <div className="text-emerald-400/90 text-xs">
                      Note: {task.resolution_note}
                    </div>
                  )}
                </div>

                {/* Inline Resolution Modal / Box */}
                {resolvingTaskId === task.task_id && (
                  <div className="mt-3 p-3 rounded-lg bg-slate-950 border border-cyan-800/50 space-y-2">
                    <label className="text-xs font-semibold text-slate-300 block">Clinical Resolution Note</label>
                    <textarea
                      value={resolutionNote}
                      onChange={(e) => setResolutionNote(e.target.value)}
                      placeholder="e.g. Patient contacted via telehealth; wound dressing adjusted, oral analgesics re-evaluated. Symptoms stabilized."
                      className="w-full text-xs p-2 rounded bg-slate-900 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
                      rows={2}
                    />
                    <div className="flex justify-end gap-2">
                      <button
                        onClick={() => setResolvingTaskId(null)}
                        className="px-2.5 py-1 text-xs text-slate-400 hover:text-slate-200"
                      >
                        Cancel
                      </button>
                      <button
                        onClick={() => handleUpdateStatus(task.task_id, 'Resolved', resolutionNote || 'Clinical triage confirmed resolution.')}
                        className="px-3 py-1 text-xs bg-emerald-600 hover:bg-emerald-500 text-white rounded font-medium"
                      >
                        Confirm Resolution
                      </button>
                    </div>
                  </div>
                )}
              </div>
            );
          })
        )}
      </div>
    </div>
  );
};

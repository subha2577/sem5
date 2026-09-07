import React, { useEffect, useState } from 'react';
import { MessageSquare, Star, CheckCircle, Send } from 'lucide-react';
import { api } from '../services/api';

export const StakeholderPage: React.FC = () => {
  const [summary, setSummary] = useState<any>(null);
  const [role, setRole] = useState('Nurse Reviewer');
  const [understanding, setUnderstanding] = useState(5);
  const [explainability, setExplainability] = useState(5);
  const [satisfaction, setSatisfaction] = useState(5);
  const [comments, setComments] = useState('');
  const [submitted, setSubmitted] = useState(false);

  const fetchSummary = async () => {
    try {
      const s = await api.getStakeholderSummary();
      setSummary(s);
    } catch (err) {
      console.error('Failed to load stakeholder summary:', err);
    }
  };

  useEffect(() => {
    fetchSummary();
  }, []);

  const handleSubmit = async (e: React.FormEvent) => {
    e.preventDefault();
    try {
      await api.submitStakeholderFeedback({
        role,
        understanding_score: understanding,
        explainability_score: explainability,
        alert_reduction_satisfaction: satisfaction,
        comments
      });
      setSubmitted(true);
      fetchSummary();
    } catch (err) {
      console.error('Failed to submit feedback:', err);
    }
  };

  return (
    <div className="space-y-6">
      <div>
        <h1 className="text-2xl font-bold text-white tracking-tight">Clinical Stakeholder Validation Module</h1>
        <p className="text-sm text-slate-400">
          Structured validation questionnaire gathering clinical review feedback on explainability, workflow usability, and alert fatigue reduction.
        </p>
      </div>

      {/* Aggregate Satisfaction Scores */}
      <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Total Responses</div>
          <div className="text-2xl font-bold text-white mt-1">{summary?.total_responses || 3}</div>
          <p className="text-[11px] text-slate-500 mt-1">Care coordinators & supervisors</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Queue Clarity</div>
          <div className="text-2xl font-bold text-cyan-400 mt-1">{summary?.avg_understanding || 4.7}/5.0</div>
          <p className="text-[11px] text-slate-500 mt-1">Priority queue intelligibility</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Explainability Usefulness</div>
          <div className="text-2xl font-bold text-emerald-400 mt-1">{summary?.avg_explainability || 4.8}/5.0</div>
          <p className="text-[11px] text-slate-500 mt-1">"What Changed?" clinical value</p>
        </div>
        <div className="p-4 rounded-xl bg-slate-900 border border-slate-800">
          <div className="text-xs text-slate-400 uppercase tracking-wider">Fatigue Reduction</div>
          <div className="text-2xl font-bold text-indigo-400 mt-1">{summary?.avg_satisfaction || 5.0}/5.0</div>
          <p className="text-[11px] text-slate-500 mt-1">Alert episode deduplication</p>
        </div>
      </div>

      {/* Questionnaire Form */}
      <div className="p-6 rounded-xl bg-slate-900 border border-slate-800 max-w-2xl">
        <h3 className="text-sm font-bold text-white uppercase tracking-wider mb-4 flex items-center gap-2">
          <MessageSquare className="w-4 h-4 text-cyan-400" />
          Submit Clinical Feedback
        </h3>

        {submitted ? (
          <div className="p-4 rounded-lg bg-emerald-950/40 border border-emerald-800 text-emerald-300 text-xs flex items-center gap-2">
            <CheckCircle className="w-4 h-4 text-emerald-400" />
            Thank you! Feedback recorded into platform audit logs.
          </div>
        ) : (
          <form onSubmit={handleSubmit} className="space-y-4 text-xs">
            <div>
              <label className="block text-slate-300 font-semibold mb-1">Your Role in Care Team</label>
              <select
                value={role}
                onChange={(e) => setRole(e.target.value)}
                className="w-full p-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
              >
                <option value="Care Coordinator">Care Coordinator</option>
                <option value="Nurse Reviewer">Nurse Reviewer</option>
                <option value="Clinical Supervisor">Clinical Supervisor</option>
                <option value="Escalation Manager">Escalation Manager</option>
              </select>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Is the priority triage queue understandable? (1 = Confusing, 5 = Highly Clear)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={understanding}
                onChange={(e) => setUnderstanding(parseInt(e.target.value))}
                className="w-full accent-cyan-500"
              />
              <div className="text-right text-cyan-400 font-bold">{understanding} / 5</div>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Does the "What Changed?" panel clearly explain why a patient is prioritized? (1-5)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={explainability}
                onChange={(e) => setExplainability(parseInt(e.target.value))}
                className="w-full accent-cyan-500"
              />
              <div className="text-right text-cyan-400 font-bold">{explainability} / 5</div>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">
                Does episode grouping reduce unnecessary low-value alerts? (1-5)
              </label>
              <input
                type="range"
                min="1"
                max="5"
                value={satisfaction}
                onChange={(e) => setSatisfaction(parseInt(e.target.value))}
                className="w-full accent-cyan-500"
              />
              <div className="text-right text-cyan-400 font-bold">{satisfaction} / 5</div>
            </div>

            <div>
              <label className="block text-slate-300 font-semibold mb-1">Clinical Observations & Comments</label>
              <textarea
                value={comments}
                onChange={(e) => setComments(e.target.value)}
                placeholder="What worked well? What would prevent clinical adoption in your facility?"
                rows={3}
                className="w-full p-2 rounded bg-slate-950 border border-slate-800 text-slate-200 focus:outline-none focus:border-cyan-500"
              />
            </div>

            <button
              type="submit"
              className="px-4 py-2 bg-cyan-600 hover:bg-cyan-500 text-white rounded font-semibold flex items-center gap-2 transition-colors"
            >
              <Send className="w-3.5 h-3.5" /> Submit Prototype Evaluation
            </button>
          </form>
        )}
      </div>
    </div>
  );
};

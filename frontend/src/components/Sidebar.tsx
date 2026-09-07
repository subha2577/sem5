import React from 'react';
import {
  Activity, Users, AlertCircle, CheckSquare, BarChart3,
  Cpu, Database, PlayCircle, MessageSquare, History, HeartPulse, Stethoscope
} from 'lucide-react';

interface SidebarProps {
  currentTab: string;
  onSelectTab: (tab: string) => void;
  unresolvedCount?: number;
  activeAlertsCount?: number;
}

export const Sidebar: React.FC<SidebarProps> = ({
  currentTab,
  onSelectTab,
  unresolvedCount = 0,
  activeAlertsCount = 0
}) => {
  const menuItems = [
    { id: 'overview', label: 'Overview', icon: Activity },
    { id: 'queue', label: 'Priority Queue', icon: Users },
    { id: 'patient', label: 'Patient Profile', icon: Stethoscope },
    { id: 'alerts', label: 'Alert Episodes', icon: AlertCircle, badge: activeAlertsCount },
    { id: 'tasks', label: 'Tasks & Escalations', icon: CheckSquare, badge: unresolvedCount },
    { id: 'analytics', label: 'Alert Analytics', icon: BarChart3 },
    { id: 'model', label: 'Model Performance', icon: Cpu },
    { id: 'data-quality', label: 'Data Quality', icon: Database },
    { id: 'simulation', label: 'Simulation Sandbox', icon: PlayCircle },
    { id: 'stakeholder', label: 'Stakeholder Review', icon: MessageSquare },
    { id: 'audit', label: 'Audit Trail', icon: History },
    { id: 'health', label: 'System Health', icon: HeartPulse }
  ];

  return (
    <aside className="w-64 bg-slate-900 border-r border-slate-800 flex flex-col shrink-0 h-screen sticky top-0">
      {/* Brand Identity */}
      <div className="p-4 border-b border-slate-800 flex items-center gap-3">
        <div className="w-9 h-9 rounded-lg bg-gradient-to-tr from-cyan-600 to-indigo-600 flex items-center justify-center text-white shadow-lg shadow-cyan-900/30">
          <Activity className="w-5 h-5" />
        </div>
        <div>
          <div className="flex items-center gap-1.5">
            <span className="font-bold tracking-tight text-white text-base">Recover<span className="text-cyan-400">AI</span></span>
            <span className="text-[10px] uppercase font-bold bg-cyan-950 text-cyan-400 px-1.5 py-0.5 rounded border border-cyan-800/50">v1.0</span>
          </div>
          <p className="text-[11px] text-slate-400 leading-tight">Post-Op Recovery Intelligence</p>
        </div>
      </div>

      {/* Navigation Links */}
      <nav className="p-3 space-y-1 overflow-y-auto flex-1 text-sm">
        {menuItems.map((item) => {
          const Icon = item.icon;
          const isActive = currentTab === item.id;
          return (
            <button
              key={item.id}
              onClick={() => onSelectTab(item.id)}
              className={`w-full flex items-center justify-between px-3 py-2 rounded-lg text-left transition-colors ${
                isActive
                  ? 'bg-cyan-600/20 text-cyan-300 font-medium border border-cyan-500/30'
                  : 'text-slate-400 hover:text-slate-200 hover:bg-slate-800/60'
              }`}
            >
              <div className="flex items-center gap-3">
                <Icon className={`w-4 h-4 ${isActive ? 'text-cyan-400' : 'text-slate-500'}`} />
                <span>{item.label}</span>
              </div>
              {item.badge !== undefined && item.badge > 0 && (
                <span className={`text-[10px] font-bold px-1.5 py-0.5 rounded-full ${
                  item.id === 'tasks' ? 'bg-amber-500/20 text-amber-300' : 'bg-red-500/20 text-red-300'
                }`}>
                  {item.badge}
                </span>
              )}
            </button>
          );
        })}
      </nav>

      {/* System Status Footer */}
      <div className="p-3 border-t border-slate-800 bg-slate-950/40 text-xs">
        <div className="flex items-center justify-between text-slate-400">
          <span className="flex items-center gap-1.5">
            <span className="w-2 h-2 rounded-full bg-emerald-500 animate-pulse"></span>
            Monitoring Engine
          </span>
          <span className="text-[11px] text-emerald-400 font-medium">ONLINE</span>
        </div>
      </div>
    </aside>
  );
};

import React from 'react';
import { AlertTriangle, ShieldCheck } from 'lucide-react';

export const SafetyBanner: React.FC = () => {
  return (
    <div className="bg-amber-950/40 border-b border-amber-600/30 px-4 py-2 flex items-center justify-between text-xs text-amber-200">
      <div className="flex items-center gap-2">
        <AlertTriangle className="w-4 h-4 text-amber-400 shrink-0" />
        <span>
          <strong className="font-semibold text-amber-300">CLINICAL SAFETY NOTICE:</strong> Prototype decision-support system. Outputs require qualified clinical review and must not replace professional medical judgement.
        </span>
      </div>
      <div className="hidden md:flex items-center gap-2 text-slate-400">
        <ShieldCheck className="w-3.5 h-3.5 text-emerald-400" />
        <span>Hybrid Deterministic & Trend ML Guardrails Active</span>
      </div>
    </div>
  );
};

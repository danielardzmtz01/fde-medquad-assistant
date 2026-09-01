import React from 'react';
import { ShieldCheck, Cpu, DollarSign, Clock, CheckCircle } from 'lucide-react';

interface TelemetryProps {
  promptTokens: number;
  completionTokens: number;
  cachedTokens: number;
  estimatedCost: number;
  latencyMs: number;
  guardrailStatus: string;
}

export const TelemetryBar: React.FC<TelemetryProps> = ({
  promptTokens,
  completionTokens,
  cachedTokens,
  estimatedCost,
  latencyMs,
  guardrailStatus,
}) => {
  return (
    <div className="bg-slate-900 text-slate-300 px-4 py-2 text-xs flex flex-wrap items-center justify-between border-t border-slate-800">
      <div className="flex items-center space-x-4">
        <div className="flex items-center space-x-1.5">
          <ShieldCheck className="w-4 h-4 text-emerald-400" />
          <span className="text-slate-400">Model Armor:</span>
          <span className="font-semibold text-emerald-400">{guardrailStatus}</span>
        </div>
        <div className="flex items-center space-x-1.5">
          <Cpu className="w-4 h-4 text-blue-400" />
          <span className="text-slate-400">Tokens:</span>
          <span className="font-mono text-white">
            {promptTokens + completionTokens} (Prompt: {promptTokens}, Comp: {completionTokens}, Cached: {cachedTokens})
          </span>
        </div>
      </div>

      <div className="flex items-center space-x-4 mt-1 sm:mt-0">
        <div className="flex items-center space-x-1">
          <Clock className="w-3.5 h-3.5 text-amber-400" />
          <span className="text-slate-400">Latency:</span>
          <span className="font-mono text-white">{latencyMs.toFixed(0)} ms</span>
        </div>
        <div className="flex items-center space-x-1">
          <DollarSign className="w-3.5 h-3.5 text-emerald-400" />
          <span className="text-slate-400">Est. Cost:</span>
          <span className="font-mono text-emerald-400">${estimatedCost.toFixed(6)}</span>
        </div>
      </div>
    </div>
  );
};

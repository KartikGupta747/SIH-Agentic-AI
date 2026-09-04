import React from 'react';
import { motion } from 'framer-motion';
import type { AgentStatus } from '../workflow/workflowTypes';
import { AGENTS } from '../workflow/agentRegistry';

interface AgentNodeProps {
    agentId: string;
    status: AgentStatus;
    isActive: boolean;
    hasOutput?: boolean;
    onViewOutput?: (agentId: string) => void;
}

export const AgentNode: React.FC<AgentNodeProps> = ({ agentId, status, isActive, hasOutput, onViewOutput }) => {
    const agent = AGENTS[agentId];
    if (!agent) return null;

    const Icon = agent.icon;

    const getStatusColor = () => {
        switch (status) {
            case 'queued': return 'border-slate-800 text-slate-600 bg-[#05070B]';
            case 'active': return 'border-blue-500 text-blue-400 bg-[#080D14] shadow-[0_0_20px_rgba(59,130,246,0.4)]';
            case 'complete': return 'border-cyan-500 text-cyan-400 bg-[#080D14] shadow-[0_0_10px_rgba(34,211,238,0.2)]';
            case 'failed': return 'border-red-500 text-red-500 bg-[#1F0A0A] shadow-[0_0_20px_rgba(239,68,68,0.4)]';
            case 'skipped': return 'border-slate-800 text-slate-700 bg-[#05070B] opacity-50';
            default: return 'border-slate-800 text-slate-600 bg-[#05070B]';
        }
    };

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0, scale: isActive ? 1.05 : 1 }}
            transition={{ duration: 0.5 }}
            className="flex flex-col items-center gap-4"
        >
            <div className={`relative flex items-center justify-center w-20 h-20 rounded-xl border ${getStatusColor()} transition-all duration-500`}>
                <Icon size={32} className="relative z-10" />
                
                {status === 'active' && (
                    <motion.div 
                        animate={{ rotate: 360 }}
                        transition={{ duration: 4, repeat: Infinity, ease: "linear" }}
                        className="absolute inset-[-4px] border border-blue-500/50 rounded-xl border-dashed opacity-50"
                    />
                )}
            </div>

            <div className="text-center flex flex-col items-center gap-1">
                <h3 className="text-sm font-semibold tracking-widest uppercase text-slate-200">
                    {agent.label}
                </h3>
                
                {status === 'active' && (
                    <p className="text-[10px] text-blue-400 font-mono flex items-center gap-1">
                        <span className="w-1.5 h-1.5 bg-blue-500 rounded-full animate-pulse"></span> ACTIVE
                    </p>
                )}
                
                {status === 'complete' && !hasOutput && (
                    <p className="text-[10px] text-cyan-400 font-mono">
                        ✓ COMPLETE
                    </p>
                )}

                {status === 'complete' && hasOutput && (
                    <div className="flex flex-col items-center gap-1 mt-1">
                        <p className="text-[10px] text-cyan-400 font-mono">✓ COMPLETE</p>
                        <p className="text-[9px] text-green-400 font-mono tracking-wider animate-pulse">OUTPUT READY</p>
                        <button 
                            onClick={() => onViewOutput && onViewOutput(agentId)}
                            className="mt-1 px-3 py-1 bg-cyan-900/40 hover:bg-cyan-800/60 border border-cyan-500/50 rounded text-[10px] text-cyan-100 uppercase tracking-widest transition"
                        >
                            [ OPEN ]
                        </button>
                    </div>
                )}
                
                {status === 'failed' && (
                    <p className="text-[10px] text-red-500 font-mono">
                        ✕ FAILED
                    </p>
                )}
                {status === 'queued' && (
                    <p className="text-[10px] text-slate-500 font-mono">
                        QUEUED
                    </p>
                )}
            </div>
        </motion.div>
    );
};

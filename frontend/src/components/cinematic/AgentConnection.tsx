import React from 'react';
import { motion } from 'framer-motion';

interface AgentConnectionProps {
    isActive: boolean;
    isComplete: boolean;
}

export const AgentConnection: React.FC<AgentConnectionProps> = ({ isActive, isComplete }) => {
    
    return (
        <div className="flex-1 flex items-center justify-center relative min-w-[60px] mx-2">
            {/* Base line */}
            <div className={`absolute inset-0 flex items-center`}>
                <div className={`w-full h-[1px] ${isComplete ? 'bg-cyan-500/50' : isActive ? 'bg-blue-500/50' : 'bg-slate-800'}`} />
            </div>

            {/* Signal Particle */}
            {isActive && (
                <motion.div
                    initial={{ x: "-100%", opacity: 0 }}
                    animate={{ x: "100%", opacity: [0, 1, 0] }}
                    transition={{ duration: 1.5, repeat: Infinity, ease: "linear" }}
                    className="absolute w-8 h-[1px] bg-gradient-to-r from-transparent via-blue-400 to-transparent shadow-[0_0_8px_rgba(96,165,250,0.8)]"
                />
            )}
            
            {/* Arrow head */}
            <div className={`absolute right-0 w-2 h-2 border-t border-r transform rotate-45 ${isComplete ? 'border-cyan-500/50' : isActive ? 'border-blue-500/50' : 'border-slate-800'}`} />
        </div>
    );
};

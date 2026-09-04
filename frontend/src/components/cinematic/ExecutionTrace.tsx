import React, { useEffect, useRef } from 'react';
import { motion } from 'framer-motion';

export const ExecutionTrace: React.FC<{ traces: string[] }> = ({ traces }) => {
    const traceRef = useRef<HTMLDivElement>(null);

    useEffect(() => {
        if (traceRef.current) {
            traceRef.current.scrollTop = traceRef.current.scrollHeight;
        }
    }, [traces]);

    return (
        <motion.div 
            initial={{ opacity: 0, y: 20 }}
            animate={{ opacity: 1, y: 0 }}
            className="absolute bottom-8 left-8 w-96 border border-slate-800/50 bg-[#05070B]/80 backdrop-blur-md p-4 font-mono text-xs text-slate-400 rounded-lg"
        >
            <div className="text-[10px] uppercase tracking-widest text-blue-500/70 mb-4 border-b border-slate-800/50 pb-2">
                System Trace
            </div>
            
            <div ref={traceRef} className="h-32 overflow-y-auto space-y-2 pr-2 scrollbar-thin scrollbar-thumb-slate-800">
                {traces.map((trace, i) => (
                    <motion.div 
                        key={i}
                        initial={{ opacity: 0, x: -10 }}
                        animate={{ opacity: 1, x: 0 }}
                    >
                        <span className="text-blue-500/50 mr-2">{(new Date()).toISOString().split('T')[1].substring(0, 8)}</span>
                        <span className="text-slate-300">{trace}</span>
                    </motion.div>
                ))}
            </div>
        </motion.div>
    );
};

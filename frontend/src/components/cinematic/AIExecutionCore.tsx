import React from 'react';
import { motion } from 'framer-motion';
import type { WorkflowState } from '../workflow/workflowTypes';

export const AIExecutionCore: React.FC<{ state: WorkflowState }> = ({ state }) => {
    
    // Core animation variants based on state
    const coreVariants = {
        idle: { scale: 0.8, opacity: 0, boxShadow: '0 0 0px rgba(59, 130, 246, 0)' },
        initializing: { scale: 0.9, opacity: 0.5, boxShadow: '0 0 20px rgba(59, 130, 246, 0.2)' },
        supervisor_processing: { scale: 1, opacity: 1, boxShadow: '0 0 60px rgba(59, 130, 246, 0.6)' },
        plan_ready: { scale: 1, opacity: 0.8, boxShadow: '0 0 40px rgba(59, 130, 246, 0.4)' },
        agent_processing: { scale: 0.95, opacity: 0.7, boxShadow: '0 0 30px rgba(59, 130, 246, 0.3)' },
        workflow_complete: { scale: 1, opacity: 1, boxShadow: '0 0 80px rgba(34, 197, 94, 0.4)' }, // Success glow
        results: { scale: 0.8, opacity: 0, boxShadow: '0 0 0px rgba(59, 130, 246, 0)' }
    };

    return (
        <div className="relative flex items-center justify-center w-64 h-64">
            {/* Outer orbital ring */}
            <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 40, repeat: Infinity, ease: "linear" }}
                className="absolute inset-0 border border-blue-500/10 rounded-full"
            />
            {/* Fine technical ring */}
            <motion.div 
                animate={{ rotate: -360 }}
                transition={{ duration: 30, repeat: Infinity, ease: "linear" }}
                className="absolute inset-4 border border-cyan-500/20 rounded-full border-dashed"
            />
            {/* Inner ring */}
            <motion.div 
                animate={{ rotate: 360 }}
                transition={{ duration: 20, repeat: Infinity, ease: "linear" }}
                className="absolute inset-10 border border-blue-400/30 rounded-full border-t-transparent"
            />
            
            {/* Central node */}
            <motion.div 
                variants={coreVariants}
                initial="idle"
                animate={state}
                transition={{ duration: 1, ease: "easeInOut" }}
                className="absolute flex items-center justify-center w-24 h-24 bg-[#0B1220] border-2 border-blue-500/50 rounded-full z-10"
            >
                {state === 'workflow_complete' ? (
                    <motion.div 
                        initial={{ scale: 0 }}
                        animate={{ scale: 1 }}
                        className="w-12 h-12 bg-green-500 rounded-full blur-md opacity-50"
                    />
                ) : (
                    <motion.div 
                        animate={state === 'supervisor_processing' ? { scale: [1, 1.2, 1] } : { scale: 1 }}
                        transition={{ duration: 2, repeat: Infinity }}
                        className="w-12 h-12 bg-blue-500 rounded-full blur-md opacity-50"
                    />
                )}
            </motion.div>
        </div>
    );
};

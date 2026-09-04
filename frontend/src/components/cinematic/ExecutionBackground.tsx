import React from 'react';
import { motion } from 'framer-motion';

export const ExecutionBackground: React.FC<{ children: React.ReactNode }> = ({ children }) => {
    return (
        <motion.div 
            initial={{ opacity: 0 }}
            animate={{ opacity: 1 }}
            exit={{ opacity: 0 }}
            transition={{ duration: 1 }}
            className="fixed inset-0 z-50 bg-[#02050A] text-slate-300 overflow-hidden font-sans"
        >
            {/* Extremely subtle grid */}
            <div 
                className="absolute inset-0 opacity-10 pointer-events-none"
                style={{
                    backgroundImage: `
                        linear-gradient(to right, rgba(34, 211, 238, 0.05) 1px, transparent 1px),
                        linear-gradient(to bottom, rgba(34, 211, 238, 0.05) 1px, transparent 1px)
                    `,
                    backgroundSize: '40px 40px'
                }}
            />
            {/* Subtle radial field */}
            <div className="absolute inset-0 bg-[radial-gradient(ellipse_at_center,_var(--tw-gradient-stops))] from-blue-900/10 via-[#02050A]/80 to-[#02050A] pointer-events-none" />
            
            {/* Main content layer */}
            <div className="relative z-10 w-full h-full flex flex-col">
                {children}
            </div>
        </motion.div>
    );
};

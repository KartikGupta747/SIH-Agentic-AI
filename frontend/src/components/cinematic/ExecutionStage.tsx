import React, { useState } from 'react';
import { motion, AnimatePresence } from 'framer-motion';
import { ExecutionBackground } from './ExecutionBackground';
import { AIExecutionCore } from './AIExecutionCore';
import { AgentGraph } from './AgentGraph';
import { ExecutionTrace } from './ExecutionTrace';
import { useWorkflowStateMachine } from '../workflow/WorkflowStateMachine';
import { ShieldCheck, Activity, X } from 'lucide-react';
import { AGENTS } from '../workflow/agentRegistry';

interface ExecutionStageProps {
    workflowStateMachine: ReturnType<typeof useWorkflowStateMachine>;
}

export const ExecutionStage: React.FC<ExecutionStageProps> = ({ workflowStateMachine }) => {
    const { 
        state, 
        plan, 
        activeAgent, 
        agentStatuses, 
        traces,
        executions,
        showResults
    } = workflowStateMachine;

    const [selectedOutput, setSelectedOutput] = useState<string | null>(null);

    return (
        <ExecutionBackground>
            {/* Header */}
            <div className="absolute top-8 left-8 right-8 flex justify-between items-center z-20">
                <div className="flex items-center gap-3 text-slate-300 tracking-widest text-xs font-semibold">
                    <ShieldCheck size={16} className="text-blue-500" />
                    <span>MRPL SOVEREIGN AI WORKBENCH</span>
                </div>
                <div className="flex items-center gap-6 text-[10px] uppercase font-mono tracking-wider">
                    <div className="flex items-center gap-2 text-cyan-400">
                        <Activity size={12} />
                        <span>LOCAL EXECUTION</span>
                    </div>
                    <div className="text-slate-500">AIR-GAPPED</div>
                </div>
            </div>

            {/* Main Stage */}
            <div className="flex-1 flex flex-col items-center justify-center relative z-10 w-full">
                
                {/* Core */}
                <div className="mb-20">
                    <AIExecutionCore state={state} />
                    
                    <div className="absolute top-1/2 left-1/2 transform -translate-x-1/2 -translate-y-1/2 mt-32 text-center flex flex-col items-center gap-4">
                        <AnimatePresence mode="wait">
                            {state === 'initializing' && (
                                <motion.div key="init" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="text-slate-400 tracking-widest text-sm uppercase">SECURE EXECUTION CHANNEL INITIALIZING</motion.div>
                            )}
                            {state === 'supervisor_processing' && (
                                <motion.div key="sup" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="text-blue-400 tracking-widest text-sm uppercase">INTERPRETING REQUEST</motion.div>
                            )}
                            {state === 'plan_ready' && (
                                <motion.div key="plan" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="text-cyan-400 tracking-widest text-sm uppercase">EXECUTION PLAN GENERATED</motion.div>
                            )}
                            {state === 'workflow_complete' && (
                                <motion.div key="comp" initial={{opacity:0}} animate={{opacity:1}} exit={{opacity:0}} className="text-green-400 tracking-widest text-sm uppercase font-semibold">ALL AGENTS COMPLETE</motion.div>
                            )}
                        </AnimatePresence>

                        {/* Final Summary Button */}
                        {(state === 'workflow_complete' || state === 'workflow_failed') && (
                            <motion.button 
                                initial={{opacity: 0, y: 10}}
                                animate={{opacity: 1, y: 0}}
                                onClick={showResults}
                                className="px-6 py-2 bg-blue-600 hover:bg-blue-500 text-white font-medium rounded tracking-wide transition shadow-lg"
                            >
                                VIEW FINAL SUMMARY
                            </motion.button>
                        )}
                    </div>
                </div>

                {/* Graph */}
                <div className="w-full h-40 flex items-center justify-center">
                    <AnimatePresence>
                        {(state === 'plan_ready' || state === 'agent_processing' || state === 'workflow_complete') && (
                            <AgentGraph 
                                plan={plan} 
                                agentStatuses={agentStatuses} 
                                activeAgent={activeAgent} 
                                onViewOutput={setSelectedOutput} 
                            />
                        )}
                    </AnimatePresence>
                </div>

            </div>

            {/* Trace */}
            <ExecutionTrace traces={traces} />
            
            {/* Progressive Output Drawer */}
            <AnimatePresence>
                {selectedOutput && (
                    <motion.div 
                        initial={{ x: 400, opacity: 0 }}
                        animate={{ x: 0, opacity: 1 }}
                        exit={{ x: 400, opacity: 0 }}
                        transition={{ type: "spring", damping: 25, stiffness: 200 }}
                        className="fixed right-0 top-0 bottom-0 w-[400px] bg-[#05070B] border-l border-blue-900/50 shadow-[-20px_0_40px_rgba(0,0,0,0.5)] z-50 flex flex-col"
                    >
                        <div className="flex items-center justify-between p-6 border-b border-blue-900/30">
                            <h2 className="text-sm font-semibold tracking-widest text-cyan-400 uppercase">
                                {AGENTS[selectedOutput]?.label || selectedOutput} OUTPUT
                            </h2>
                            <button onClick={() => setSelectedOutput(null)} className="text-slate-500 hover:text-white transition">
                                <X size={20} />
                            </button>
                        </div>
                        <div className="flex-1 overflow-auto p-6 text-sm text-slate-300 font-mono whitespace-pre-wrap">
                            {(() => {
                                const agentExecs = executions[selectedOutput] || [];
                                const lastExec = agentExecs[agentExecs.length - 1];
                                if (!lastExec) return 'No output found.';
                                if (lastExec.status === 'failed') return `Error: ${lastExec.error}`;
                                return JSON.stringify(lastExec.output, null, 2);
                            })()}
                        </div>
                    </motion.div>
                )}
            </AnimatePresence>
        </ExecutionBackground>
    );
};

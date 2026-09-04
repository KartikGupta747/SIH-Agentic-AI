import React from 'react';
import { motion } from 'framer-motion';
import { AgentNode } from './AgentNode';
import { AgentConnection } from './AgentConnection';
import type { AgentStatus } from '../workflow/workflowTypes';

interface AgentGraphProps {
    plan: string[];
    agentStatuses: Record<string, AgentStatus>;
    activeAgent: string | null;
    onViewOutput?: (agentId: string) => void;
}

const VISIBLE_OUTPUT_AGENTS = ["vision", "rag", "coder", "deliverable"];

export const AgentGraph: React.FC<AgentGraphProps> = ({ plan, agentStatuses, activeAgent, onViewOutput }) => {
    
    if (!plan || plan.length === 0) return null;

    return (
        <motion.div 
            initial={{ opacity: 0, scale: 0.95 }}
            animate={{ opacity: 1, scale: 1 }}
            transition={{ duration: 0.8 }}
            className="flex items-center justify-center w-full max-w-5xl mx-auto px-8"
        >
            {plan.map((agentId, index) => {
                const status = agentStatuses[agentId] || 'queued';
                const isActive = activeAgent === agentId;
                const isLast = index === plan.length - 1;
                const hasOutput = VISIBLE_OUTPUT_AGENTS.includes(agentId);
                
                return (
                    <React.Fragment key={agentId}>
                        <AgentNode 
                            agentId={agentId} 
                            status={status} 
                            isActive={isActive}
                            hasOutput={hasOutput}
                            onViewOutput={onViewOutput}
                        />
                        {!isLast && (
                            <AgentConnection 
                                isActive={status === 'active' || (status === 'complete' && agentStatuses[plan[index+1]] === 'active')} 
                                isComplete={status === 'complete' && agentStatuses[plan[index+1]] !== 'active'}
                            />
                        )}
                    </React.Fragment>
                );
            })}
        </motion.div>
    );
};

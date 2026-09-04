export type AgentStatus = 'queued' | 'active' | 'complete' | 'failed' | 'skipped';

export interface AgentExecution {
    agent: string;
    status: AgentStatus;
    output?: any;
    error?: string;
    attempt?: number;
}

export type WorkflowState = 
    | 'idle'
    | 'initializing'
    | 'supervisor_processing'
    | 'plan_ready'
    | 'agent_processing'
    | 'workflow_complete'
    | 'workflow_failed'
    | 'results';

export interface WorkflowEvent {
    type: 'workflow_started' | 'agent_started' | 'agent_completed' | 'agent_failed' | 'plan_created' | 'workflow_completed' | 'workflow_failed';
    run_id: string;
    timestamp: number;
    agent?: string;
    plan?: string[];
    output?: any;
    error?: string;
    final_state?: any;
}


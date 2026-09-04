import { useState, useCallback, useRef } from 'react';
import type { WorkflowState, AgentStatus, AgentExecution, WorkflowEvent } from './workflowTypes';
import { AGENTS } from './agentRegistry';
import { startWorkflowRun, subscribeToWorkflow } from '../../api/client';

export function useWorkflowStateMachine() {
    const [state, setState] = useState<WorkflowState>('idle');
    const [plan, setPlan] = useState<string[]>([]);
    const [activeAgent, setActiveAgent] = useState<string | null>(null);
    const [agentStatuses, setAgentStatuses] = useState<Record<string, AgentStatus>>({});
    const [traces, setTraces] = useState<string[]>([]);
    const [executions, setExecutions] = useState<Record<string, AgentExecution[]>>({});
    const [finalResult, setFinalResult] = useState<any>(null);
    const [runId, setRunId] = useState<string | null>(null);

    const cleanupRef = useRef<(() => void) | null>(null);

    const addTrace = useCallback((trace: string) => {
        setTraces(prev => [...prev, `> ${trace}`]);
    }, []);

    const reset = useCallback(() => {
        if (cleanupRef.current) cleanupRef.current();
        setState('idle');
        setPlan([]);
        setActiveAgent(null);
        setAgentStatuses({});
        setTraces([]);
        setExecutions({});
        setFinalResult(null);
        setRunId(null);
    }, []);

    const handleEvent = useCallback((event: WorkflowEvent) => {
        switch (event.type) {
            case 'workflow_started':
                setState('initializing');
                addTrace(`Initializing sovereign execution context [RUN: ${event.run_id.substring(0,8)}]`);
                setRunId(event.run_id);
                break;

            case 'agent_started':
                if (event.agent === 'supervisor') {
                    setState('supervisor_processing');
                    setActiveAgent('supervisor');
                    setAgentStatuses(prev => ({ ...prev, supervisor: 'active' }));
                    addTrace('Supervisor activated - Interpreting request');
                } else {
                    setState('agent_processing');
                    setActiveAgent(event.agent!);
                    setAgentStatuses(prev => ({ ...prev, [event.agent!]: 'active' }));
                    addTrace(`${AGENTS[event.agent!]?.label || event.agent} stage active`);
                }
                break;

            case 'plan_created':
                setPlan(event.plan!);
                setState('plan_ready');
                setAgentStatuses(prev => ({ ...prev, supervisor: 'complete' }));
                setActiveAgent(null);
                addTrace('Execution plan generated');
                event.plan!.forEach(agent => {
                    setAgentStatuses(prev => ({ ...prev, [agent]: 'queued' }));
                });
                break;

            case 'agent_completed':
                setAgentStatuses(prev => ({ ...prev, [event.agent!]: 'complete' }));
                addTrace(`${AGENTS[event.agent!]?.label || event.agent} stage complete`);
                setExecutions(prev => {
                    const agentExecs = prev[event.agent!] || [];
                    return {
                        ...prev,
                        [event.agent!]: [...agentExecs, { agent: event.agent!, status: 'complete', output: event.output }]
                    };
                });
                break;
                
            case 'agent_failed':
                setAgentStatuses(prev => ({ ...prev, [event.agent!]: 'failed' }));
                addTrace(`${AGENTS[event.agent!]?.label || event.agent} stage failed: ${event.error}`);
                setExecutions(prev => {
                    const agentExecs = prev[event.agent!] || [];
                    return {
                        ...prev,
                        [event.agent!]: [...agentExecs, { agent: event.agent!, status: 'failed', error: event.error }]
                    };
                });
                break;

            case 'workflow_completed':
                setState('workflow_complete');
                setActiveAgent(null);
                setFinalResult(event.final_state);
                addTrace('All required operations complete');
                break;

            case 'workflow_failed':
                setState('workflow_failed');
                setActiveAgent(null);
                addTrace(`Workflow failed: ${event.error}`);
                break;
        }
    }, [addTrace]);

    const startExecution = useCallback(async (query: string, file: File) => {
        reset();
        setState('initializing');
        addTrace('Submitting request...');
        try {
            const newRunId = await startWorkflowRun(query, file);
            cleanupRef.current = subscribeToWorkflow(
                newRunId,
                (msg) => handleEvent(msg),
                (_err) => {
                    addTrace('Connection interrupted or stream ended.');
                }
            );
        } catch (err: any) {
            setState('workflow_failed');
            addTrace(`Failed to start workflow: ${err.message}`);
        }
    }, [reset, handleEvent, addTrace]);

    const showResults = useCallback(() => {
        setState('results');
    }, []);

    return {
        state,
        plan,
        activeAgent,
        agentStatuses,
        traces,
        executions,
        finalResult,
        runId,
        startExecution,
        showResults,
        reset
    };
}

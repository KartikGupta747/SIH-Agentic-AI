import { Search, FileText, Terminal, CheckCircle, Download, BrainCircuit } from 'lucide-react';

export const AGENTS: Record<string, any> = {
    supervisor: {
        id: 'supervisor',
        label: "Supervisor",
        description: "Interpreting request and constructing execution plan",
        icon: BrainCircuit
    },
    vision: {
        id: 'vision',
        label: "Vision",
        description: "Analyzing engineering imagery",
        icon: Search
    },
    rag: {
        id: 'rag',
        label: "Knowledge Retrieval",
        description: "Retrieving local technical standards",
        icon: FileText
    },
    coder: {
        id: 'coder',
        label: "Calculation Engine",
        description: "Executing deterministic calculations",
        icon: Terminal
    },
    evaluator: {
        id: 'evaluator',
        label: "Evaluator",
        description: "Validating workflow output",
        icon: CheckCircle
    },
    deliverable: {
        id: 'deliverable',
        label: "Deliverable",
        description: "Generating engineering approval note",
        icon: Download
    },
};

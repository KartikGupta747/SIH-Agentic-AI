import { useState } from 'react';
import { UploadCloud, Play, FileText, CheckCircle, XCircle, Search, Terminal, Download, ShieldCheck } from 'lucide-react';
import { ExecutionStage } from '../components/cinematic/ExecutionStage';
import { useWorkflowStateMachine } from '../components/workflow/WorkflowStateMachine';
import { AGENTS } from '../components/workflow/agentRegistry';

export default function AnalysisPage() {
  const [file, setFile] = useState<File | null>(null);
  const [preview, setPreview] = useState<string | null>(null);
  const [query, setQuery] = useState('Extract the data from the scan, calculate minimum required thickness per API 510, and generate the final approval note.');
  
  const workflowMachine = useWorkflowStateMachine();

  const handleDrop = (e: React.DragEvent) => {
    e.preventDefault();
    if (e.dataTransfer.files && e.dataTransfer.files[0]) {
      handleFile(e.dataTransfer.files[0]);
    }
  };

  const handleFile = (f: File) => {
    setFile(f);
    setPreview(URL.createObjectURL(f));
  };

  const executeRun = () => {
    if (!file) return;
    workflowMachine.startExecution(query, file);
  };

  if (workflowMachine.state === 'results') {
    return <ResultsView result={workflowMachine.finalResult} executions={workflowMachine.executions} reset={workflowMachine.reset} />;
  }

  if (workflowMachine.state !== 'idle') {
    return <ExecutionStage workflowStateMachine={workflowMachine} />;
  }

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex items-center justify-between">
         <h1 className="text-3xl font-light tracking-tight text-white">Create Engineering Analysis</h1>
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="space-y-6">
          <div className="bg-panel border border-slate-800 rounded-lg p-6 flex flex-col gap-4">
             <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Input Document</h2>
             
             {!preview ? (
               <label 
                 onDragOver={(e) => e.preventDefault()}
                 onDrop={handleDrop}
                 className="border-2 border-dashed border-slate-700 hover:border-primary/50 bg-slate-900/50 rounded-lg h-64 flex flex-col items-center justify-center cursor-pointer transition-colors"
               >
                 <UploadCloud className="w-10 h-10 text-slate-500 mb-4" />
                 <span className="text-sm text-gray-300">Drag & drop inspection report</span>
                 <span className="text-xs text-slate-500 mt-2">PNG, JPG up to 10MB</span>
                 <input type="file" className="hidden" accept="image/*" onChange={e => e.target.files && handleFile(e.target.files[0])} />
               </label>
             ) : (
               <div className="relative border border-slate-700 bg-black rounded-lg h-64 overflow-hidden group">
                 <img src={preview} alt="Preview" className="w-full h-full object-contain" />
                 <button onClick={() => {setPreview(null); setFile(null);}} className="absolute top-2 right-2 bg-black/70 hover:bg-danger/80 text-white p-1.5 rounded transition">
                   <XCircle size={18} />
                 </button>
               </div>
             )}
          </div>

          <div className="bg-panel border border-slate-800 rounded-lg p-6 flex flex-col gap-4">
             <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Task Definition</h2>
             <textarea 
               value={query}
               onChange={e => setQuery(e.target.value)}
               className="w-full bg-slate-900/50 border border-slate-700 rounded p-4 text-sm focus:outline-none focus:border-primary transition-colors resize-none h-32"
             />
             <button 
               onClick={executeRun}
               disabled={!file}
               className="w-full bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 rounded flex items-center justify-center gap-2 transition-colors"
             >
               <span className="flex items-center gap-2"><Play size={18} /> Run Sovereign Analysis</span>
             </button>
          </div>
        </div>

        <div className="bg-panel border border-slate-800 rounded-lg p-6">
           <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-6">Workflow Execution</h2>
           <div className="space-y-6">
              <WorkflowStep icon={<ShieldCheck />} title="Supervisor" desc="Routing required agents" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<Search />} title="Vision Analysis" desc="Extracting equipment and measurement data" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<FileText />} title="Knowledge Retrieval" desc="Searching local engineering knowledge base" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<Terminal />} title="Calculation Engine" desc="Running deterministic calculation" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<CheckCircle />} title="QA / Evaluation" desc="Validating generated result" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<Download />} title="Deliverable" desc="Generating engineering approval note" />
           </div>
        </div>
      </div>
    </div>
  );
}

function WorkflowStep({ icon, title, desc }: any) {
  return (
    <div className={`flex gap-4 opacity-40`}>
       <div className={`w-10 h-10 rounded-full flex items-center justify-center bg-slate-800 text-slate-500`}>
         {icon}
       </div>
       <div>
         <h3 className="font-medium text-white">{title}</h3>
         <p className="text-xs text-gray-400 mt-1">{desc}</p>
       </div>
    </div>
  )
}

function ResultsView({ result, executions, reset }: { result: any, executions: any, reset: () => void }) {
  const payload = result?.payload_json || {};
  const [activeTab, setActiveTab] = useState('Overview');
  
  const VISIBLE_OUTPUT_AGENTS = ["vision", "rag", "coder", "deliverable"];
  const executedAgents = Object.keys(executions || {}).filter(a => VISIBLE_OUTPUT_AGENTS.includes(a));
  
  const tabs = ['Overview', ...executedAgents.map(a => AGENTS[a]?.label || a)];
  
  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500 pb-12">
      <div className="flex items-center justify-between">
         <h1 className="text-3xl font-light tracking-tight text-white flex items-center gap-3">
           <CheckCircle className="text-success w-8 h-8" />
           ANALYSIS COMPLETE
         </h1>
         <div className="flex items-center gap-4">
             {result?.security?.status === "VERIFIED_AIR_GAPPED" && (
                 <span className="flex items-center gap-1 text-xs text-success border border-success/30 bg-success/10 px-2 py-1 rounded">
                     <ShieldCheck size={14} /> AIR-GAPPED VERIFIED
                 </span>
             )}
             <button onClick={reset} className="text-sm text-gray-400 hover:text-white transition">New Analysis</button>
         </div>
      </div>
      
      <div className="flex gap-2 overflow-x-auto pb-2 border-b border-slate-800">
        {tabs.map(tab => (
            <button 
                key={tab} 
                onClick={() => setActiveTab(tab)}
                className={`px-4 py-2 text-sm whitespace-nowrap transition-colors ${activeTab === tab ? 'text-primary border-b-2 border-primary font-medium' : 'text-slate-500 hover:text-slate-300'}`}
            >
                {tab}
            </button>
        ))}
      </div>

      {activeTab === 'Overview' && (
          <div className="space-y-8 animate-in fade-in">
              <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                <MetricCard label="Equipment" value={payload.equipment_id || 'N/A'} />
                <MetricCard label="Measured Thickness" value={payload.measured_thickness ? `${payload.measured_thickness} mm` : 'N/A'} />
                <MetricCard label="Retirement Limit" value={payload.retirement_limit ? `${payload.retirement_limit} mm` : 'N/A'} />
                <MetricCard label="Remaining Life" value={payload.remaining_life ? `${payload.remaining_life} yrs` : 'N/A'} highlight />
              </div>

              <div className="bg-panel border border-slate-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Final Engineering Deliverable</h2>
                  {result?.final_deliverable_path && result.final_deliverable_path !== "None" && (
                    <a 
                      href={`http://localhost:8000/api/download?path=${result.final_deliverable_path}`}
                      download
                      className="bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30 px-4 py-2 rounded text-sm font-medium flex items-center gap-2 transition"
                    >
                      <Download size={16} /> Download Approval Note
                    </a>
                  )}
                </div>
              </div>
          </div>
      )}
      
      {activeTab !== 'Overview' && (
          <div className="bg-panel border border-slate-800 rounded-lg p-6 animate-in fade-in">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">{activeTab} OUTPUT</h2>
              <div className="bg-[#05070B] border border-slate-800 p-4 rounded text-sm font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                  {(() => {
                      const agentId = Object.keys(AGENTS).find(k => AGENTS[k].label === activeTab) || activeTab;
                      const agentExecs = executions[agentId] || [];
                      return JSON.stringify(agentExecs[agentExecs.length - 1]?.output, null, 2) || 'No output captured.';
                  })()}
              </div>
          </div>
      )}

    </div>
  )
}

function MetricCard({ label, value, highlight = false }: any) {
  return (
    <div className={`p-6 rounded-lg border ${highlight ? 'bg-primary/10 border-primary/30' : 'bg-panel border-slate-800'}`}>
      <div className={`text-xs uppercase tracking-wider mb-2 ${highlight ? 'text-primary' : 'text-gray-500'}`}>{label}</div>
      <div className={`text-2xl font-light ${highlight ? 'text-white' : 'text-gray-200'}`}>{value}</div>
    </div>
  )
}

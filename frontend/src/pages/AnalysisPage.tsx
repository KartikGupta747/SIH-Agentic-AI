import { useState } from 'react';
import { UploadCloud, Play, FileText, CheckCircle, XCircle, Search, Terminal, Download, ShieldCheck, BrainCircuit, Copy, Check } from 'lucide-react';
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
    if (query.trim().length === 0) return;
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
             <div className="flex items-center justify-between">
                <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Reference Image</h2>
                <span className="text-[10px] text-slate-500 font-mono tracking-widest uppercase">Optional</span>
             </div>
             
             {!preview ? (
               <label 
                 onDragOver={(e) => e.preventDefault()}
                 onDrop={handleDrop}
                 className="border-2 border-dashed border-slate-700 hover:border-primary/50 bg-slate-900/50 rounded-lg h-64 flex flex-col items-center justify-center cursor-pointer transition-colors px-6 text-center"
               >
                 <UploadCloud className="w-10 h-10 text-slate-500 mb-4" />
                 <span className="text-sm text-gray-300">Drag & drop an inspection image</span>
                 <span className="text-sm text-gray-300 mb-2">or click to browse</span>
                 <span className="text-xs text-slate-500">PNG / JPG / JPEG</span>
                 
                 <div className="mt-8 border-t border-slate-700/50 pt-4 w-full">
                    <span className="block text-xs text-slate-400 mb-1">No image?</span>
                    <span className="block text-xs text-slate-500">You can run a text-only engineering query.</span>
                 </div>
                 <input type="file" className="hidden" accept="image/*" onChange={e => e.target.files && handleFile(e.target.files[0])} />
               </label>
             ) : (
               <div className="relative border border-slate-700 bg-black rounded-lg h-64 overflow-hidden group">
                 <img src={preview} alt="Preview" className="w-full h-full object-contain" />
                 <div className="absolute top-0 left-0 right-0 p-3 bg-gradient-to-b from-black/80 to-transparent flex justify-between items-center">
                    <span className="text-xs text-green-400 font-mono">✓ Ready for analysis</span>
                    <button onClick={() => {setPreview(null); setFile(null);}} className="bg-black/70 hover:bg-red-500/80 text-white p-1.5 rounded transition">
                      <XCircle size={18} />
                    </button>
                 </div>
               </div>
             )}
          </div>

          <div className="bg-panel border border-slate-800 rounded-lg p-6 flex flex-col gap-4">
             <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Engineering Task</h2>
             <textarea 
               value={query}
               onChange={e => setQuery(e.target.value)}
               className="w-full bg-slate-900/50 border border-slate-700 rounded p-4 text-sm focus:outline-none focus:border-primary transition-colors resize-none h-32"
               placeholder="Enter engineering query..."
             />
             <button 
               onClick={executeRun}
               disabled={query.trim().length === 0}
               className="w-full bg-primary hover:bg-primary/90 disabled:opacity-50 disabled:cursor-not-allowed text-white font-medium py-3 rounded flex items-center justify-center gap-2 transition-colors"
             >
               <span className="flex items-center gap-2"><Play size={18} /> Run Sovereign Analysis</span>
             </button>
          </div>
        </div>

        <div className="bg-panel border border-slate-800 rounded-lg p-6">
           <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-6">Workflow Execution</h2>
           <div className="space-y-6">
              <WorkflowStep icon={<ShieldCheck />} title="Supervisor" desc="Routing required agents based on intent" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<Search />} title="Vision Analysis" desc="Extracting data from engineering imagery" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<FileText />} title="Knowledge Retrieval" desc="Retrieving local policy and technical standards" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<BrainCircuit />} title="Policy & Governance" desc="Verifying compliance and required approvals" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<Terminal />} title="Calculation Engine" desc="Running deterministic calculation models" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<CheckCircle />} title="QA / Evaluation" desc="Validating generated findings" />
              <div className="w-0.5 h-6 bg-slate-800 ml-5 -my-4"></div>
              <WorkflowStep icon={<Download />} title="Deliverable" desc="Generating specific task document" />
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
  
  const VISIBLE_OUTPUT_AGENTS = ["vision", "rag", "coder", "approval_analysis", "deliverable"];
  const executedAgents = Object.keys(executions || {}).filter(a => VISIBLE_OUTPUT_AGENTS.includes(a));
  
  const tabs = ['Overview', ...executedAgents.map(a => a === 'coder' ? 'Generated Code' : (AGENTS[a]?.label || a))];
  
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
              {result?.task_type === 'CALCULATION' && (
                <div className="grid grid-cols-1 md:grid-cols-4 gap-4">
                  <MetricCard label="Equipment" value={payload.equipment_id || 'N/A'} />
                  <MetricCard label="Measured Thickness" value={payload.measured_thickness ? `${payload.measured_thickness} mm` : 'N/A'} />
                  <MetricCard label="Retirement Limit" value={payload.retirement_limit ? `${payload.retirement_limit} mm` : 'N/A'} />
                  <MetricCard label="Remaining Life" value={payload.remaining_life ? `${payload.remaining_life} yrs` : 'N/A'} highlight />
                </div>
              )}
              
              {(result?.task_type === 'APPROVAL_VERIFICATION' || result?.task_type === 'POLICY_COMPLIANCE' || result?.task_type === 'PROCUREMENT_VERIFICATION') && result?.approval_verification && (
                <div className="grid grid-cols-1 md:grid-cols-3 gap-4">
                  <MetricCard label="Compliance Status" value={result.approval_verification.compliance_status || 'UNKNOWN'} highlight={result.approval_verification.compliance_status === 'COMPLIANT'} />
                  <MetricCard label="Financial Value" value={result.approval_verification.financial_value || 'N/A'} />
                  <MetricCard label="Authority Required" value={result.approval_verification.authority_requirement || 'N/A'} />
                </div>
              )}
              
              {result?.task_type === 'KNOWLEDGE_QUERY' && (
                 <div className="bg-panel border border-slate-800 rounded-lg p-6">
                    <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">Final Response</h2>
                    <div className="text-gray-300 whitespace-pre-wrap">{result.final_response || "No response generated."}</div>
                 </div>
              )}

              <div className="bg-panel border border-slate-800 rounded-lg p-6">
                <div className="flex items-center justify-between mb-4">
                  <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest">Final Deliverable</h2>
                  {result?.final_deliverable_path && result.final_deliverable_path !== "None" ? (
                    <a 
                      href={`http://localhost:8000/api/download?path=${result.final_deliverable_path}`}
                      download
                      className="bg-primary/20 hover:bg-primary/30 text-primary border border-primary/30 px-4 py-2 rounded text-sm font-medium flex items-center gap-2 transition"
                    >
                      <Download size={16} /> Download Document
                    </a>
                  ) : (
                    <span className="text-xs text-gray-500 font-mono">NO DOCUMENT GENERATED</span>
                  )}
                </div>
              </div>
          </div>
      )}
      
      {activeTab !== 'Overview' && (
          <div className="bg-panel border border-slate-800 rounded-lg p-6 animate-in fade-in">
              <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-4">
                  {activeTab === 'Generated Code' ? 'GENERATED CODE' : `${activeTab} OUTPUT`}
              </h2>
              {activeTab === 'Generated Code' ? (
                  <CodeViewer code={result?.sandbox_code || ""} />
              ) : (
                  <div className="bg-[#05070B] border border-slate-800 p-4 rounded text-sm font-mono text-slate-300 overflow-x-auto whitespace-pre-wrap">
                      {(() => {
                          const agentId = Object.keys(AGENTS).find(k => (k === 'coder' ? 'Generated Code' : AGENTS[k].label) === activeTab) || activeTab;
                          const agentExecs = executions[agentId] || [];
                          return JSON.stringify(agentExecs[agentExecs.length - 1]?.output, null, 2) || 'No output captured.';
                      })()}
                  </div>
              )}
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

function CodeViewer({ code }: { code: string }) {
  const [copied, setCopied] = useState(false);
  
  const handleCopy = () => {
    navigator.clipboard.writeText(code);
    setCopied(true);
    setTimeout(() => setCopied(false), 2000);
  };
  
  return (
    <div className="border border-slate-700 rounded-lg overflow-hidden bg-[#0A0D14] mt-2">
      <div className="flex items-center justify-between px-4 py-2 border-b border-slate-700 bg-slate-900">
        <span className="text-xs text-slate-400 font-mono">Python</span>
        <button 
          onClick={handleCopy}
          className="flex items-center gap-1.5 text-xs text-slate-400 hover:text-white transition-colors"
        >
          {copied ? <Check size={14} className="text-green-500" /> : <Copy size={14} />}
          {copied ? "Copied" : "Copy"}
        </button>
      </div>
      <div className="p-4 overflow-x-auto">
        <pre className="text-sm font-mono">
          <code>
            {code.split("\n").map((line, i) => (
              <div key={i} className="flex gap-4">
                <span className="text-slate-600 select-none min-w-[1.5rem] text-right">{i + 1}</span>
                <span className={line.trim().startsWith("#") ? "text-slate-500" : "text-blue-300"}>{line}</span>
              </div>
            ))}
          </code>
        </pre>
      </div>
    </div>
  );
}

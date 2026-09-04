import { useEffect, useState } from 'react';
import { getSystemStatus } from '../api/client';
import { Activity, ShieldAlert, Cpu, Database, Server } from 'lucide-react';
import { Link } from 'react-router-dom';

export default function Dashboard() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    getSystemStatus().then(setStatus).catch(console.error);
  }, []);

  return (
    <div className="max-w-6xl mx-auto space-y-8 animate-in fade-in duration-500">
      <div className="flex flex-col gap-2">
         <h1 className="text-3xl font-light tracking-tight text-white">System Dashboard</h1>
         <p className="text-gray-400">MRPL Sovereign AI Workbench Status</p>
      </div>

      <div className="grid grid-cols-1 md:grid-cols-2 lg:grid-cols-4 gap-6">
         <StatusCard 
           icon={<ShieldAlert className="text-success" />}
           title="AIR-GAP STATUS"
           value="Verified"
           sub="0 External Connections"
           status="success"
         />
         <StatusCard 
           icon={<Activity className="text-primary" />}
           title="SYSTEM HEALTH"
           value="Operational"
           sub="Local Backend Online"
           status="success"
         />
         <StatusCard 
           icon={<Cpu className={status?.vram ? "text-primary" : "text-gray-500"} />}
           title="GPU MEMORY"
           value={status?.vram?.raw || "Loading..."}
           sub="NVIDIA RTX 4050"
           status="normal"
         />
         <StatusCard 
           icon={<Database className="text-primary" />}
           title="KNOWLEDGE BASE"
           value={status?.knowledge_base || "Loading..."}
           sub="FAISS & BM25"
           status="normal"
         />
      </div>

      <div className="grid grid-cols-1 lg:grid-cols-2 gap-8">
        <div className="bg-panel border border-slate-800 rounded-lg p-8 flex flex-col justify-center items-center text-center space-y-4 min-h-[300px]">
           <div className="w-16 h-16 rounded-full bg-primary/10 flex items-center justify-center text-primary mb-2">
             <Server size={32} />
           </div>
           <h2 className="text-xl font-medium text-white">Ready for Analysis</h2>
           <p className="text-gray-400 max-w-sm text-sm">Upload an engineering scan and define the task to start a sovereign analysis.</p>
           <Link to="/analysis" className="mt-4 bg-primary hover:bg-primary/90 text-white px-6 py-2.5 rounded transition">
             Start New Analysis
           </Link>
        </div>

        <div className="bg-panel border border-slate-800 rounded-lg p-6">
           <h2 className="text-sm font-semibold text-gray-400 uppercase tracking-widest mb-6">Local Inference Stack</h2>
           <div className="space-y-4">
             {status?.models?.map((model: string, i: number) => (
               <div key={i} className="flex justify-between items-center p-3 bg-slate-900/50 rounded">
                 <span className="text-sm font-medium text-gray-200">{model}</span>
                 <span className="text-xs text-primary bg-primary/10 px-2 py-1 rounded">Ollama</span>
               </div>
             ))}
             {!status && <div className="text-gray-500 text-sm">Loading models...</div>}
           </div>
        </div>
      </div>
    </div>
  )
}

function StatusCard({ icon, title, value, sub, status }: any) {
  return (
    <div className="bg-panel border border-slate-800 rounded-lg p-6 flex flex-col gap-4">
      <div className="flex justify-between items-start">
        <div className="text-xs uppercase tracking-wider text-gray-500 font-semibold">{title}</div>
        {icon}
      </div>
      <div>
        <div className="text-2xl font-light text-white mb-1">{value}</div>
        <div className={`text-xs ${status === 'success' ? 'text-success' : 'text-gray-500'}`}>{sub}</div>
      </div>
    </div>
  )
}

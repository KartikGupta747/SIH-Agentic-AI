import { Outlet, NavLink } from 'react-router-dom';
import { ShieldAlert, Activity, Cpu, FileBox, Hexagon, BarChart3, Database } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useEffect, useState } from 'react';
import { getSystemStatus } from '../../api/client';

export default function Layout() {
  const [status, setStatus] = useState<any>(null);

  useEffect(() => {
    getSystemStatus().then(setStatus).catch(console.error);
  }, []);

  return (
    <div className="flex h-screen w-full bg-background overflow-hidden text-gray-300 font-sans">
      {/* Sidebar */}
      <aside className="w-64 border-r border-slate-800 bg-panel flex flex-col">
        <div className="p-6 flex items-center gap-3 text-white border-b border-slate-800">
          <Hexagon className="text-primary w-8 h-8" />
          <div>
            <h1 className="font-bold text-sm tracking-widest uppercase">MRPL Sovereign</h1>
            <p className="text-[10px] text-gray-400 uppercase tracking-wider">AI Workbench</p>
          </div>
        </div>

        <nav className="flex-1 p-4 space-y-1 overflow-y-auto">
          <NavItem to="/" icon={<Activity size={18} />} label="Dashboard" />
          <NavItem to="/analysis" icon={<BarChart3 size={18} />} label="New Analysis" />
          <NavItem to="/knowledge" icon={<Database size={18} />} label="Knowledge Base" />
        </nav>

        <div className="p-4 border-t border-slate-800 text-xs">
          <div className="flex items-center gap-2 mb-2 text-success font-semibold tracking-wide">
            <ShieldAlert size={14} /> AIR-GAPPED
          </div>
          <div className="flex items-center gap-2 mb-2 text-gray-400">
            <Cpu size={14} /> GPU: {status?.vram?.raw || "Loading..."}
          </div>
          <div className="flex items-center gap-2 text-gray-400">
            <FileBox size={14} /> K-Base: {status?.knowledge_base || "Loading..."}
          </div>
        </div>
      </aside>

      {/* Main Content */}
      <main className="flex-1 flex flex-col relative h-full overflow-hidden">
        <header className="h-14 border-b border-slate-800 bg-panel/50 backdrop-blur-sm flex items-center justify-between px-6 z-10">
           <div className="text-sm font-medium tracking-wide text-gray-400">
             CONFIDENTIAL INDUSTRIAL DATA ONLY
           </div>
           <div className="flex items-center gap-4 text-xs">
             <span className="flex items-center gap-1.5"><div className="w-2 h-2 rounded-full bg-success"></div> Operational</span>
           </div>
        </header>
        <div className="flex-1 overflow-y-auto p-8 relative">
          <Outlet />
        </div>
      </main>
    </div>
  );
}

function NavItem({ to, icon, label }: { to: string, icon: React.ReactNode, label: string }) {
  return (
    <NavLink
      to={to}
      className={({ isActive }) => cn(
        "flex items-center gap-3 px-3 py-2.5 rounded-md transition-colors text-sm font-medium",
        isActive 
          ? "bg-primary/10 text-primary border border-primary/20" 
          : "text-gray-400 hover:bg-slate-800/50 hover:text-white"
      )}
    >
      {icon}
      {label}
    </NavLink>
  );
}

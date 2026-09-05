import { Outlet, NavLink } from 'react-router-dom';
import { ShieldAlert, Activity, Cpu, Hexagon, BarChart3 } from 'lucide-react';
import { cn } from '../../lib/utils';
import { useEffect } from 'react';
import { getSystemStatus } from '../../api/client';

export default function Layout() {
  useEffect(() => {
    // Optionally fetch system status in background to warm up API
    getSystemStatus().catch(console.error);
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
          <NavItem to="/analysis" icon={<BarChart3 size={18} />} label="New Analysis" />
          <NavItem to="/runs" icon={<Activity size={18} />} label="Runs" />
          <NavItem to="/system" icon={<Cpu size={18} />} label="System" />
          <NavItem to="/security" icon={<ShieldAlert size={18} />} label="Security" />
        </nav>
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

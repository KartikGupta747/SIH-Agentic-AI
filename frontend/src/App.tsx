import { BrowserRouter, Routes, Route, Navigate } from 'react-router-dom';
import Layout from './components/layout/Layout';
import AnalysisPage from './pages/AnalysisPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Navigate to="/analysis" replace />} />
          <Route path="analysis" element={<AnalysisPage />} />
          <Route path="runs" element={<div className="text-gray-400 p-8 text-center border border-dashed border-slate-800 rounded-lg">Runs history coming soon.</div>} />
          <Route path="system" element={<div className="text-gray-400 p-8 text-center border border-dashed border-slate-800 rounded-lg">System configuration coming soon.</div>} />
          <Route path="security" element={<div className="text-gray-400 p-8 text-center border border-dashed border-slate-800 rounded-lg">Security audit logs coming soon.</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

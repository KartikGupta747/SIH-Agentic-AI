import { BrowserRouter, Routes, Route } from 'react-router-dom';
import Layout from './components/layout/Layout';
import Dashboard from './pages/Dashboard';
import AnalysisPage from './pages/AnalysisPage';

export default function App() {
  return (
    <BrowserRouter>
      <Routes>
        <Route path="/" element={<Layout />}>
          <Route index element={<Dashboard />} />
          <Route path="analysis" element={<AnalysisPage />} />
          <Route path="knowledge" element={<div className="text-gray-400 p-8 text-center border border-dashed border-slate-800 rounded-lg">Knowledge Base indexing and visualization coming soon.</div>} />
        </Route>
      </Routes>
    </BrowserRouter>
  );
}

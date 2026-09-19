import { BrowserRouter, Routes, Route, NavLink, useLocation } from 'react-router-dom';
import { LayoutDashboard, Brain, Activity, ShieldCheck, Bell } from 'lucide-react';
import Dashboard from './pages/Dashboard';
import ActiveLearning from './pages/ActiveLearning';
import DataQuality from './pages/DataQuality';
import DriftDetection from './pages/DriftDetection';

function Sidebar() {
  return (
    <div className="sidebar">
      <div className="sidebar-brand">
        <Brain className="text-primary" size={28} color="#6366f1" />
        <span>DCA Studio</span>
      </div>

      <div className="nav-menu">
        <NavLink to="/" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`} end>
          <LayoutDashboard size={20} />
          <span>Dashboard</span>
        </NavLink>
        <NavLink to="/active-learning" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Brain size={20} />
          <span>Active Learning</span>
        </NavLink>
        <NavLink to="/data-quality" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <ShieldCheck size={20} />
          <span>Data Quality</span>
        </NavLink>
        <NavLink to="/drift-detection" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <Activity size={20} />
          <span>Drift Detection</span>
        </NavLink>
        {/*
        <NavLink to="/version-control" className={({ isActive }) => `nav-link ${isActive ? 'active' : ''}`}>
          <GitBranch size={20} />
          <span>Versioning</span>
        </NavLink>
        */}
      </div>

      <div style={{ marginTop: 'auto' }}>
        <div className="card" style={{ padding: '1rem', display: 'flex', alignItems: 'center', gap: '0.75rem' }}>
          <div style={{ width: '8px', height: '8px', borderRadius: '50%', background: 'var(--success)' }}></div>
          <span style={{ fontSize: '0.875rem' }}>System Online</span>
        </div>
      </div>
    </div>
  );
}

function Topbar() {
  const location = useLocation();
  const titleMap: Record<string, string> = {
    '/': 'Dashboard Overview',
    '/active-learning': 'Active Learning Controls',
    '/data-quality': 'Data Quality Assessment',
    '/drift-detection': 'Drift Detection Monitor',
    '/version-control': 'Data Versioning',
  };

  return (
    <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center', marginBottom: '2rem' }}>
      <h1 className="page-title">{titleMap[location.pathname] || 'Dashboard'}</h1>
      <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
        <button className="btn btn-outline" style={{ padding: '0.5rem', borderRadius: '50%' }}>
          <Bell size={20} />
        </button>
        <div style={{ width: '40px', height: '40px', borderRadius: '50%', background: 'var(--primary)', display: 'flex', alignItems: 'center', justifyContent: 'center', fontWeight: 'bold', color: 'white' }}>
          AD
        </div>
      </div>
    </div>
  );
}

function App() {
  return (
    <BrowserRouter>
      <div className="app-container">
        <Sidebar />
        <main className="main-content">
          <Topbar />
          <Routes>
            <Route path="/" element={<Dashboard />} />
            <Route path="/active-learning" element={<ActiveLearning />} />
            <Route path="/data-quality" element={<DataQuality />} />
            <Route path="/drift-detection" element={<DriftDetection />} />
          </Routes>
        </main>
      </div>
    </BrowserRouter>
  );
}

export default App;

import { ShieldCheck, AlertTriangle, Search } from 'lucide-react';

export default function DataQuality() {
  return (
    <div className="animate-fade-in">
      <div className="grid grid-cols-4 dashboard-metrics">
        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>Overall Quality</span>
            <div style={{ padding: '0.5rem', background: 'var(--glass-bg)', borderRadius: '0.5rem' }}>
              <ShieldCheck size={20} className="text-primary" />
            </div>
          </div>
          <div className="metric-value">92.5%</div>
          <div className="progress-bg" style={{ marginTop: '1rem' }}>
            <div className="progress-fill" style={{ width: '92.5%', background: 'var(--primary)' }}></div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>Annotator Agreement</span>
            <div className="badge badge-success">High</div>
          </div>
          <div className="metric-value">88.2%</div>
          <div className="progress-bg" style={{ marginTop: '1rem' }}>
            <div className="progress-fill" style={{ width: '88.2%', background: 'var(--success)' }}></div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>Label Consistency</span>
            <div className="badge badge-primary">Stable</div>
          </div>
          <div className="metric-value">94.1%</div>
          <div className="progress-bg" style={{ marginTop: '1rem' }}>
            <div className="progress-fill" style={{ width: '94.1%', background: 'var(--primary)' }}></div>
          </div>
        </div>

        <div className="card">
          <div className="card-header">
            <span className="card-title" style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>Critical Issues</span>
            <div className="badge badge-danger">Action Req</div>
          </div>
          <div className="metric-value" style={{ color: 'var(--danger)' }}>12</div>
          <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.875rem', marginTop: '0.5rem', color: 'var(--text-muted)' }}>
            <span>Across 4 tasks</span>
          </div>
        </div>
      </div>

      <div className="grid grid-cols-1" style={{ marginTop: '2rem' }}>
        <div className="card">
          <div className="card-header">
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <AlertTriangle size={20} className="text-warning" />
              Detected Issues
            </h2>
            <div style={{ display: 'flex', gap: '1rem', alignItems: 'center' }}>
              <div style={{ position: 'relative' }}>
                <Search size={16} style={{ position: 'absolute', left: '0.75rem', top: '50%', transform: 'translateY(-50%)', color: 'var(--text-muted)' }} />
                <input
                  type="text"
                  placeholder="Search issues..."
                  style={{
                    padding: '0.5rem 0.5rem 0.5rem 2.25rem',
                    borderRadius: '0.5rem',
                    background: 'var(--glass-bg)',
                    border: '1px solid var(--border)',
                    color: 'var(--text-main)',
                    fontSize: '0.875rem',
                    outline: 'none'
                  }}
                />
              </div>
              <button className="btn btn-outline" style={{ padding: '0.5rem 1rem', fontSize: '0.875rem' }}>Filter</button>
            </div>
          </div>

          <div className="table-container" style={{ marginTop: '1rem' }}>
            <table>
              <thead>
                <tr>
                  <th>ID</th>
                  <th>Type</th>
                  <th>Severity</th>
                  <th>Description</th>
                  <th>Task ID</th>
                  <th>Actions</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { id: 1042, type: 'Conflict', sev: 'Critical', desc: 'Annotators severely disagreed on primary bounding box.', task: 8943 },
                  { id: 1041, type: 'Missing', sev: 'High', desc: 'Required metadata label missing from payload.', task: 8931 },
                  { id: 1040, type: 'Speed Anomaly', sev: 'Medium', desc: 'Task completed in 0.5s (average is 14s).', task: 8890 },
                  { id: 1039, type: 'Bias', sev: 'Low', desc: 'Annotator 4 consistently selects class B.', task: 8821 },
                ].map((row) => (
                  <tr key={row.id}>
                    <td style={{ fontWeight: 600 }}>#{row.id}</td>
                    <td>{row.type}</td>
                    <td>
                      <span className={`badge ${
                        row.sev === 'Critical' ? 'badge-danger' :
                        row.sev === 'High' ? 'badge-warning' :
                        row.sev === 'Medium' ? 'badge-primary' : 'badge-success'
                      }`}>
                        {row.sev}
                      </span>
                    </td>
                    <td style={{ color: 'var(--text-muted)' }}>{row.desc}</td>
                    <td><a href="#">T-{row.task}</a></td>
                    <td>
                      <button className="btn btn-outline" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>Resolve</button>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      </div>
    </div>
  );
}

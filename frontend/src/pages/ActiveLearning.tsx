import { useState } from 'react';
import { Brain, Settings, Play, CheckCircle2, PauseCircle } from 'lucide-react';

export default function ActiveLearning() {
  const [isEnabled, setIsEnabled] = useState(true);
  const [strategy, setStrategy] = useState('uncertainty');

  return (
    <div className="animate-fade-in">
      <div className="grid grid-cols-3">

        {/* Controls Card */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Settings size={20} className="text-primary" />
              Configuration
            </h2>
            <div className={`badge ${isEnabled ? 'badge-success' : 'badge-warning'}`}>
              {isEnabled ? 'Running' : 'Paused'}
            </div>
          </div>

          <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Sampling Strategy</label>
              <select
                value={strategy}
                onChange={(e) => setStrategy(e.target.value)}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  background: 'var(--glass-bg)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-main)',
                  outline: 'none'
                }}
              >
                <option value="uncertainty">Uncertainty Sampling</option>
                <option value="diversity">Diversity (Core-Set)</option>
                <option value="committee">Query by Committee</option>
                <option value="hybrid">Hybrid Approach</option>
              </select>
            </div>

            <div>
              <label style={{ display: 'block', marginBottom: '0.5rem', fontSize: '0.875rem', color: 'var(--text-muted)' }}>Batch Size</label>
              <input
                type="number"
                defaultValue={50}
                style={{
                  width: '100%',
                  padding: '0.75rem',
                  borderRadius: '0.5rem',
                  background: 'var(--glass-bg)',
                  border: '1px solid var(--border)',
                  color: 'var(--text-main)',
                  outline: 'none'
                }}
              />
            </div>

            <div style={{ display: 'flex', gap: '1rem', marginTop: '1rem' }}>
              <button
                className={`btn ${isEnabled ? 'btn-outline' : 'btn-primary'}`}
                style={{ flex: 1, justifyContent: 'center' }}
                onClick={() => setIsEnabled(!isEnabled)}
              >
                {isEnabled ? <><PauseCircle size={18} /> Pause</> : <><Play size={18} /> Enable</>}
              </button>
              <button className="btn btn-primary" style={{ flex: 1, justifyContent: 'center' }}>
                Save Config
              </button>
            </div>
          </div>
        </div>

        {/* History / Rounds */}
        <div className="card" style={{ gridColumn: 'span 2' }}>
          <div className="card-header">
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Brain size={20} className="text-primary" />
              Recent Sampling Rounds
            </h2>
            <button className="btn btn-outline" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>
              Run Manual Sample
            </button>
          </div>

          <div className="table-container" style={{ marginTop: '1rem' }}>
            <table>
              <thead>
                <tr>
                  <th>Round</th>
                  <th>Date</th>
                  <th>Strategy</th>
                  <th>Tasks Selected</th>
                  <th>Avg Uncertainty</th>
                  <th>Status</th>
                </tr>
              </thead>
              <tbody>
                {[
                  { id: 12, date: '2026-09-18 14:30', strategy: 'Uncertainty', tasks: 50, score: '0.82', status: 'Completed' },
                  { id: 11, date: '2026-09-17 09:15', strategy: 'Hybrid', tasks: 100, score: '0.76', status: 'Completed' },
                  { id: 10, date: '2026-09-15 16:45', strategy: 'Diversity', tasks: 25, score: '0.64', status: 'Completed' },
                  { id: 9, date: '2026-09-14 11:20', strategy: 'Uncertainty', tasks: 50, score: '0.88', status: 'Completed' },
                ].map((row) => (
                  <tr key={row.id}>
                    <td style={{ fontWeight: 600 }}>#{row.id}</td>
                    <td style={{ color: 'var(--text-muted)' }}>{row.date}</td>
                    <td><span className="badge badge-primary">{row.strategy}</span></td>
                    <td>{row.tasks}</td>
                    <td>{row.score}</td>
                    <td>
                      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', color: 'var(--success)', fontSize: '0.875rem' }}>
                        <CheckCircle2 size={16} /> {row.status}
                      </div>
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

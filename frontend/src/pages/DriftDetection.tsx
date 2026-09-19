import { Activity, AlertOctagon } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const driftData = [
  { name: '10am', feature: 0.12, label: 0.05 },
  { name: '11am', feature: 0.15, label: 0.08 },
  { name: '12pm', feature: 0.22, label: 0.10 },
  { name: '1pm', feature: 0.45, label: 0.12 },
  { name: '2pm', feature: 0.68, label: 0.15 },
  { name: '3pm', feature: 0.72, label: 0.25 },
  { name: '4pm', feature: 0.81, label: 0.30 },
];

export default function DriftDetection() {
  return (
    <div className="animate-fade-in">
      <div className="grid grid-cols-3" style={{ gridTemplateColumns: '2fr 1fr' }}>
        
        {/* Main Chart */}
        <div className="card">
          <div className="card-header">
            <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem' }}>
              <Activity size={20} className="text-primary" />
              Drift Monitoring (Real-time)
            </h2>
            <div className="badge badge-warning">Elevated Risk</div>
          </div>
          
          <div style={{ height: '350px', width: '100%', marginTop: '1rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={driftData} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorFeature" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--danger)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--danger)" stopOpacity={0}/>
                  </linearGradient>
                  <linearGradient id="colorLabel" x1="0" y1="0" x2="0" y2="1">
                    <stop offset="5%" stopColor="var(--primary)" stopOpacity={0.3}/>
                    <stop offset="95%" stopColor="var(--primary)" stopOpacity={0}/>
                  </linearGradient>
                </defs>
                <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.05)" vertical={false} />
                <XAxis dataKey="name" stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <YAxis stroke="var(--text-muted)" tick={{ fill: 'var(--text-muted)' }} axisLine={false} tickLine={false} />
                <Tooltip 
                  contentStyle={{ background: 'var(--bg-card)', border: 'var(--glass-border)', borderRadius: '0.5rem', backdropFilter: 'blur(12px)' }}
                  itemStyle={{ color: 'var(--text-main)' }}
                />
                <Area type="monotone" dataKey="feature" name="Feature Drift" stroke="var(--danger)" strokeWidth={3} fillOpacity={1} fill="url(#colorFeature)" />
                <Area type="monotone" dataKey="label" name="Label Drift" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorLabel)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        {/* Status / Alerts */}
        <div style={{ display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
          <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
              <h2 className="card-title">Active Baselines</h2>
              <button className="btn btn-outline" style={{ padding: '0.25rem 0.5rem' }}>+ New</button>
            </div>
            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ padding: '1rem', background: 'var(--glass-bg)', borderRadius: '0.5rem', border: '1px solid var(--border)' }}>
                <div style={{ display: 'flex', justifyContent: 'space-between', alignItems: 'center' }}>
                  <div style={{ fontWeight: 600 }}>v1.2 Production Set</div>
                  <div className="badge badge-success">Active</div>
                </div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.5rem' }}>
                  15,000 samples • Created Sep 10
                </div>
              </div>
            </div>
          </div>

          <div className="card" style={{ flex: 1 }}>
            <div className="card-header">
              <h2 className="card-title" style={{ display: 'flex', alignItems: 'center', gap: '0.5rem', color: 'var(--warning)' }}>
                <AlertOctagon size={20} />
                Recent Alerts
              </h2>
            </div>
            
            <div style={{ marginTop: '1rem', display: 'flex', flexDirection: 'column', gap: '1rem' }}>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ width: '2px', background: 'var(--danger)', borderRadius: '2px' }}></div>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>Critical Feature Drift</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Drift score 0.81 exceeds threshold 0.70</div>
                </div>
              </div>
              <div style={{ display: 'flex', gap: '1rem' }}>
                <div style={{ width: '2px', background: 'var(--warning)', borderRadius: '2px' }}></div>
                <div>
                  <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>Label Distribution Shift</div>
                  <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Class 'Background' increased by 20%</div>
                </div>
              </div>
            </div>
          </div>
        </div>

      </div>
    </div>
  );
}

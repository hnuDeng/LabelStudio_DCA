import { Activity, Brain, ShieldCheck, Target, ArrowUpRight, ArrowDownRight } from 'lucide-react';
import { AreaChart, Area, XAxis, YAxis, CartesianGrid, Tooltip, ResponsiveContainer } from 'recharts';

const data = [
  { name: 'Mon', score: 0.82 },
  { name: 'Tue', score: 0.85 },
  { name: 'Wed', score: 0.84 },
  { name: 'Thu', score: 0.89 },
  { name: 'Fri', score: 0.91 },
  { name: 'Sat', score: 0.90 },
  { name: 'Sun', score: 0.93 },
];

function MetricCard({ title, value, change, icon: Icon, trend }: any) {
  const isPositive = trend === 'up';
  return (
    <div className="card animate-fade-in">
      <div className="card-header">
        <span className="card-title" style={{ fontSize: '0.875rem', fontWeight: 600, color: 'var(--text-muted)' }}>{title}</span>
        <div style={{ padding: '0.5rem', background: 'var(--glass-bg)', borderRadius: '0.5rem' }}>
          <Icon size={20} className="text-primary" />
        </div>
      </div>
      <div className="metric-value">{value}</div>
      <div style={{ display: 'flex', alignItems: 'center', gap: '0.25rem', fontSize: '0.875rem', marginTop: '0.5rem', color: isPositive ? 'var(--success)' : 'var(--danger)' }}>
        {isPositive ? <ArrowUpRight size={16} /> : <ArrowDownRight size={16} />}
        <span>{change}</span>
        <span style={{ color: 'var(--text-muted)' }}>vs last week</span>
      </div>
    </div>
  );
}

export default function Dashboard() {
  return (
    <div className="dashboard">
      <div className="grid grid-cols-4 dashboard-metrics">
        <MetricCard title="Active Learning Rounds" value="24" change="+3" icon={Brain} trend="up" />
        <MetricCard title="Overall Quality Score" value="92.5%" change="+2.1%" icon={ShieldCheck} trend="up" />
        <MetricCard title="Drift Risk Level" value="Low" change="-12%" icon={Activity} trend="down" />
        <MetricCard title="Annotations Saved" value="1,402" change="+140" icon={Target} trend="up" />
      </div>

      <div className="grid grid-cols-3" style={{ gridTemplateColumns: '2fr 1fr' }}>
        <div className="card animate-fade-in delay-1">
          <div className="card-header">
            <h2 className="card-title">Model Performance Trend</h2>
            <button className="btn btn-outline" style={{ padding: '0.25rem 0.75rem', fontSize: '0.75rem' }}>This Week</button>
          </div>
          <div style={{ height: '300px', width: '100%', marginTop: '1rem' }}>
            <ResponsiveContainer width="100%" height="100%">
              <AreaChart data={data} margin={{ top: 10, right: 10, left: -20, bottom: 0 }}>
                <defs>
                  <linearGradient id="colorScore" x1="0" y1="0" x2="0" y2="1">
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
                <Area type="monotone" dataKey="score" stroke="var(--primary)" strokeWidth={3} fillOpacity={1} fill="url(#colorScore)" />
              </AreaChart>
            </ResponsiveContainer>
          </div>
        </div>

        <div className="card animate-fade-in delay-2" style={{ display: 'flex', flexDirection: 'column' }}>
          <h2 className="card-title">Recent Activity</h2>
          <div style={{ marginTop: '1.5rem', display: 'flex', flexDirection: 'column', gap: '1.5rem' }}>
            
            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ width: '2px', background: 'var(--primary)', borderRadius: '2px' }}></div>
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>Active Learning Triggered</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Uncertainty Strategy selected 150 tasks</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>2 hours ago</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ width: '2px', background: 'var(--warning)', borderRadius: '2px' }}></div>
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>Drift Alert</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Feature drift detected in 'image_brightness'</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>5 hours ago</div>
              </div>
            </div>

            <div style={{ display: 'flex', gap: '1rem' }}>
              <div style={{ width: '2px', background: 'var(--success)', borderRadius: '2px' }}></div>
              <div>
                <div style={{ fontSize: '0.875rem', fontWeight: 600 }}>Quality Report Generated</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Consistency score reached 95%</div>
                <div style={{ fontSize: '0.75rem', color: 'var(--text-muted)', marginTop: '0.25rem' }}>Yesterday</div>
              </div>
            </div>
            
          </div>
          
          <button className="btn btn-outline" style={{ marginTop: 'auto', width: '100%', justifyContent: 'center' }}>
            View All Logs
          </button>
        </div>
      </div>
    </div>
  );
}

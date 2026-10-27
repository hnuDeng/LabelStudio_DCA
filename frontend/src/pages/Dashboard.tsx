import { useEffect, useState } from 'react';
import type { FormEvent } from 'react';

type Report = {
  project_id: number;
  has_data: true;
  report_id: number;
  completeness_score: number;
  tasks_analyzed: number;
  annotations_analyzed: number;
  created_at: string;
};
type DashboardState =
  | { kind: 'loading' }
  | { kind: 'empty' }
  | { kind: 'error'; message: string }
  | { kind: 'data'; report: Report };

export async function loadQualityReport(projectId: number, baseUrl = import.meta.env?.VITE_API_BASE_URL || 'http://127.0.0.1:8000', signal?: AbortSignal): Promise<DashboardState> {
  try {
    const response = await fetch(`${baseUrl}/api/projects/${projectId}/quality-report`, { signal });
    if (!response.ok) throw new Error(`Server returned ${response.status}`);
    const data = await response.json();
    if (data.project_id !== projectId || typeof data.has_data !== 'boolean') throw new Error('Invalid report response');
    if (!data.has_data) return { kind: 'empty' };
    if (!Number.isFinite(data.completeness_score) || !Number.isInteger(data.tasks_analyzed) || !Number.isInteger(data.annotations_analyzed) || typeof data.created_at !== 'string' || !Number.isInteger(data.report_id)) throw new Error('Invalid report response');
    return { kind: 'data', report: data as Report };
  } catch (error) {
    return { kind: 'error', message: error instanceof Error ? error.message : 'Unable to load report' };
  }
}

export function DashboardView({ state }: { state: DashboardState }) {
  if (state.kind === 'loading') return <p role="status">Loading quality report…</p>;
  if (state.kind === 'empty') return <p>No quality report for this project yet.</p>;
  if (state.kind === 'error') return <p role="alert">Unable to load quality report: {state.message}</p>;
  const { report } = state;
  return <div className="card">
    <h2 className="card-title">Latest annotation event assessment</h2>
    <p>This report covers the task and annotation in one webhook event; it is not a project-wide assessment.</p>
    <div className="grid grid-cols-3 dashboard-metrics">
      <div><h3>Completeness</h3><div className="metric-value">{(report.completeness_score * 100).toFixed(1)}%</div></div>
      <div><h3>Tasks assessed</h3><div className="metric-value">{report.tasks_analyzed}</div></div>
      <div><h3>Annotations assessed</h3><div className="metric-value">{report.annotations_analyzed}</div></div>
    </div>
    <p>Report #{report.report_id} · {report.created_at} UTC</p>
  </div>;
}

export default function Dashboard() {
  const [selection, setSelection] = useState({ projectId: 1, revision: 0 });
  const [input, setInput] = useState('1');
  const [state, setState] = useState<DashboardState>({ kind: 'loading' });
  useEffect(() => {
    const controller = new AbortController();
    loadQualityReport(selection.projectId, undefined, controller.signal).then((result) => {
      if (!controller.signal.aborted) setState(result);
    });
    return () => controller.abort();
  }, [selection]);
  function selectProject(event: FormEvent) {
    event.preventDefault();
    const id = Number(input);
    if (Number.isSafeInteger(id) && id > 0) {
      setState({ kind: 'loading' });
      setSelection((current) => ({ projectId: id, revision: current.revision + 1 }));
    }
  }
  return <div className="dashboard">
    <form onSubmit={selectProject} style={{ marginBottom: '1.5rem' }}>
      <label htmlFor="project-id">Project ID </label>
      <input id="project-id" type="number" min="1" step="1" required value={input} onChange={(event) => setInput(event.target.value)} />
      <button className="btn btn-outline" type="submit">Load project</button>
    </form>
    <DashboardView state={state} />
  </div>;
}

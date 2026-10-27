import test from 'node:test';
import assert from 'node:assert/strict';
import { readFile } from 'node:fs/promises';
import { createServer } from 'node:http';
import { createServer as createTcpServer } from 'node:net';
import { spawn } from 'node:child_process';
import { join } from 'node:path';
import { fileURLToPath, pathToFileURL } from 'node:url';
import React from 'react';
import { renderToStaticMarkup } from 'react-dom/server';
import ts from 'typescript';
import { withTemporaryModule, createDashboardTemp, removeDashboardTemp, observeChild } from './dashboard-test-support.mjs';

const source = new URL('../src/pages/Dashboard.tsx', import.meta.url);
const compiled = ts.transpileModule(await readFile(source, 'utf8'), {
  compilerOptions: { module: ts.ModuleKind.ESNext, jsx: ts.JsxEmit.ReactJSX, target: ts.ScriptTarget.ES2022 },
}).outputText;
const dashboard = await withTemporaryModule(fileURLToPath(new URL('../src/pages/', import.meta.url)), compiled,
  (path) => import(pathToFileURL(path).href));

test('renders loading, empty, error and fetched report states', async () => {
  assert.equal(typeof dashboard.DashboardView, 'function');
  const render = (state) => renderToStaticMarkup(React.createElement(dashboard.DashboardView, { state }));
  assert.match(render({ kind: 'loading' }), /Loading/i);
  assert.match(render({ kind: 'empty' }), /No quality report/i);
  assert.match(render({ kind: 'error', message: 'Unavailable' }), /Unavailable/);
  const server = createServer((req, res) => {
    assert.equal(req.url, '/api/projects/7/quality-report');
    res.setHeader('Content-Type', 'application/json');
    res.end(JSON.stringify({ project_id: 7, has_data: true, report_id: 42, completeness_score: 0.75, tasks_analyzed: 4, annotations_analyzed: 3, created_at: '2026-10-27T10:00:00' }));
  });
  await new Promise((resolve) => server.listen(0, '127.0.0.1', resolve));
  try {
    const state = await dashboard.loadQualityReport(7, `http://127.0.0.1:${server.address().port}`);
    const html = render(state);
    assert.match(html, /75\.0%/);
    assert.match(html, /4/);
    assert.match(html, /3/);
    assert.doesNotMatch(html, /92\.5%|1,402|Drift Risk/);
  } finally {
    await new Promise((resolve) => server.close(resolve));
  }
});

test('a real local webhook report reaches the rendered dashboard', async () => {
  const temp = await createDashboardTemp();
  let backend;
  let exited;
  let termination;
  try {
  const socket = createTcpServer();
  await new Promise((resolve) => socket.listen(0, '127.0.0.1', resolve));
  const port = socket.address().port;
  await new Promise((resolve) => socket.close(resolve));
  const root = fileURLToPath(new URL('../../', import.meta.url));
  const env = { ...process.env, PYTHONPATH: root, DCA_DATABASE_URL: `sqlite:///${join(temp.path, 'test.db').replaceAll('\\', '/')}`, LABEL_STUDIO_WEBHOOK_SECRET: 'local-test-secret' };
  delete env.TESTING;
  backend = spawn('python', ['-m', 'uvicorn', 'backend.server:app', '--host', '127.0.0.1', '--port', String(port)], { cwd: temp.path, env, stdio: 'ignore' });
  exited = observeChild(backend).then((result) => { termination = result; return result; });
  const base = `http://127.0.0.1:${port}`;
    let ready = false;
    for (let attempt = 0; attempt < 100 && !ready; attempt++) {
      if (termination) throw new Error(`Local backend exited: ${termination.error || termination.code}`);
      try { ready = (await fetch(`${base}/api/health`)).ok; } catch { await new Promise((resolve) => setTimeout(resolve, 100)); }
    }
    assert.ok(ready, 'local backend started');
    const response = await fetch(`${base}/api/webhooks/label-studio`, {
      method: 'POST', headers: { 'Content-Type': 'application/json', Authorization: 'Bearer local-test-secret' },
      body: JSON.stringify({ action: 'ANNOTATION_CREATED', project: { id: 79 }, task: { id: 10 }, annotation: { id: 20, result: [{ value: { choices: ['yes'] } }] } }),
    });
    assert.equal((await response.json()).status, 'processed');
    const state = await dashboard.loadQualityReport(79, base);
    const html = renderToStaticMarkup(React.createElement(dashboard.DashboardView, { state }));
    assert.match(html, /100\.0%/);
    assert.match(html, /Tasks assessed/);
    assert.match(html, /Annotations assessed/);
    assert.equal((await dashboard.loadQualityReport(80, base)).kind, 'empty');
  } finally {
    if (backend && exited) {
      if (!termination) backend.kill();
      await exited;
    }
    await removeDashboardTemp(temp);
  }
});

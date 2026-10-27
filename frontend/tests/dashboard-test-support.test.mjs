import test from 'node:test';
import assert from 'node:assert/strict';
import { access, mkdir, mkdtemp, rename, rmdir } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, join } from 'node:path';
import { spawn } from 'node:child_process';

const support = await import('./dashboard-test-support.mjs').catch(() => ({}));

test('temporary module is unique and removed even when its callback fails', async () => {
  assert.equal(typeof support.withTemporaryModule, 'function');
  const directory = await mkdtemp(join(tmpdir(), 'dca-module-test-'));
  let created;
  try {
    await assert.rejects(support.withTemporaryModule(directory, 'export default 1', async (path) => {
      created = path;
      assert.match(basename(path), /^\.dashboard-test-[0-9a-f-]+\.mjs$/);
      await access(path);
      throw new Error('callback failed');
    }), /callback failed/);
    await assert.rejects(access(created), { code: 'ENOENT' });
  } finally {
    await rmdir(directory);
  }
});

test('recursive cleanup accepts only a directory created by this helper and checks its identity', async () => {
  assert.equal(typeof support.removeDashboardTemp, 'function');
  assert.equal(typeof support.createDashboardTemp, 'function');
  const outsideScope = await mkdtemp(join(tmpdir(), 'dca-unrelated-'));
  const foreign = await mkdtemp(join(tmpdir(), 'dca-dashboard-'));
  const intended = await support.createDashboardTemp();
  const displaced = `${intended.path}-displaced`;
  try {
    await assert.rejects(support.removeDashboardTemp(tmpdir()));
    await assert.rejects(support.removeDashboardTemp(outsideScope));
    await assert.rejects(support.removeDashboardTemp(foreign));
    await access(outsideScope);
    await rename(intended.path, displaced);
    await mkdir(intended.path);
    await assert.rejects(support.removeDashboardTemp(intended));
    await rmdir(intended.path);
    await rename(displaced, intended.path);
    await support.removeDashboardTemp(intended);
    await assert.rejects(access(intended.path), { code: 'ENOENT' });
  } finally {
    await rmdir(outsideScope);
    await rmdir(foreign);
  }
});

test('child exit and spawn failure are observed even before awaiting', async () => {
  assert.equal(typeof support.observeChild, 'function');
  const child = spawn(process.execPath, ['-e', 'process.exit(0)']);
  const exited = support.observeChild(child);
  await new Promise((resolve) => setTimeout(resolve, 300));
  assert.equal((await exited).code, 0);
  const missing = spawn(join(tmpdir(), 'nonexistent-dca-test-executable'));
  const failed = support.observeChild(missing);
  await new Promise((resolve) => setTimeout(resolve, 100));
  assert.equal((await failed).error.code, 'ENOENT');
});

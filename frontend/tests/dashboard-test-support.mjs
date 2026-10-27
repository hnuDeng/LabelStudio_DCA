import { randomUUID } from 'node:crypto';
import { mkdtemp, open, realpath, rm, stat, unlink } from 'node:fs/promises';
import { tmpdir } from 'node:os';
import { basename, dirname, join } from 'node:path';

export async function withTemporaryModule(directory, source, callback) {
  const path = join(directory, `.dashboard-test-${randomUUID()}.mjs`);
  const file = await open(path, 'wx');
  try {
    await file.writeFile(source);
    return await callback(path);
  } finally {
    try {
      await file.close();
    } finally {
      await unlink(path);
    }
  }
}

const createdDirectories = new WeakMap();

export async function createDashboardTemp() {
  const path = await mkdtemp(join(tmpdir(), 'dca-dashboard-'));
  const resolved = await realpath(path);
  const identity = await stat(resolved, { bigint: true });
  const handle = Object.freeze({ path });
  createdDirectories.set(handle, { resolved, dev: identity.dev, ino: identity.ino });
  return handle;
}

export async function removeDashboardTemp(handle) {
  const created = createdDirectories.get(handle);
  if (!created) throw new Error('Directory was not created by this test');
  const root = await realpath(tmpdir());
  const target = await realpath(handle.path);
  const identity = await stat(target, { bigint: true });
  if (target !== created.resolved || identity.dev !== created.dev || identity.ino !== created.ino
      || dirname(target) !== root || !basename(target).startsWith('dca-dashboard-')) {
    throw new Error('Refusing to remove a directory outside the dashboard test temp scope');
  }
  await rm(target, { recursive: true, force: true });
  createdDirectories.delete(handle);
}

export function observeChild(child) {
  return new Promise((resolve) => {
    child.once('error', (error) => resolve({ error }));
    child.once('exit', (code, signal) => resolve({ code, signal }));
  });
}

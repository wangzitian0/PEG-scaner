#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');

const ROOT = path.resolve(__dirname, '../../');
const WEB_PORT = process.env.MOBILE_WEB_PORT || '5173';
const MOBILE_DIR = path.join(ROOT, 'apps/mobile');

const backend = spawn('npx', ['nx', 'run', 'backend:start'], {
  cwd: ROOT,
  stdio: 'inherit',
});

const cleanUp = () => {
  if (!backend.killed) backend.kill('SIGINT');
};

const run = async () => {
  try {
    await waitForUrl(`http://127.0.0.1:8000/api/ping/`);
    await exec('npx', ['playwright', 'install', 'chromium'], {
      cwd: MOBILE_DIR,
      stdio: 'inherit',
    });
    await exec('npx', ['playwright', 'test'], {
      cwd: MOBILE_DIR,
      stdio: 'inherit',
      env: { ...process.env, MOBILE_WEB_PORT: WEB_PORT },
    });
  } finally {
    cleanUp();
  }
};

function exec(cmd, args, options) {
  return new Promise((resolve, reject) => {
    const child = spawn(cmd, args, options);
    child.on('exit', (code) => {
      if (code === 0) resolve();
      else reject(new Error(`${cmd} ${args.join(' ')} exited with code ${code}`));
    });
  });
}

function waitForUrl(url, timeoutMs = 45000) {
  return new Promise((resolve, reject) => {
    const start = Date.now();
    const attempt = async () => {
      try {
        const res = await fetch(url);
        if (res.ok) {
          resolve();
          return;
        }
      } catch (err) {
        // ignore until timeout
      }
      if (Date.now() - start > timeoutMs) {
        reject(new Error(`Timed out waiting for ${url}`));
      } else {
        setTimeout(attempt, 1000);
      }
    };
    attempt();
  });
}

run().catch((err) => {
  console.error('[web-e2e] failed:', err.message);
  cleanUp();
  process.exit(1);
});

#!/usr/bin/env node
const { spawn } = require('child_process');
const fs = require('fs');
const path = require('path');
const { startNeo4j, waitForNeo4j, stopNeo4j } = require('./neo4j');

const ROOT = path.resolve(__dirname, '../../');
const WEB_HOST = process.env.MOBILE_WEB_HOST || '127.0.0.1';
const WEB_PORT = process.env.MOBILE_WEB_PORT || '5173';
const BASE_URL = `http://${WEB_HOST}:${WEB_PORT}`;
const MOBILE_DIR = path.join(ROOT, 'apps/mobile');
const VITE_CACHE_DIR = path.join(MOBILE_DIR, 'node_modules', '.vite');
let previewServer;
let backend;
let shuttingDown = false;
let neo4jState = null;

const clearViteCache = () => {
  try {
    fs.rmSync(VITE_CACHE_DIR, { recursive: true, force: true });
  } catch (err) {
    console.warn('[web-e2e] failed to clear Vite cache:', err.message);
  }
};

const cleanUp = () => {
  shuttingDown = true;
  if (backend && !backend.killed) backend.kill('SIGINT');
  if (previewServer && !previewServer.killed) {
    previewServer.kill('SIGINT');
  }
  stopNeo4j(neo4jState);
};

clearViteCache();

const run = async () => {
  try {
    console.log('[web-e2e] starting Neo4j container…');
    neo4jState = startNeo4j();
    await waitForNeo4j();
    backend = spawn('npx', ['nx', 'run', 'backend:start'], {
      cwd: ROOT,
      stdio: 'inherit',
    });
    backend.on('exit', (code, signal) => {
      if (shuttingDown) return;
      if ((code !== null && code !== 0) || signal) {
        console.error('[web-e2e] backend exited unexpectedly');
        process.exitCode = 1;
      }
    });
    await exec('npx', ['vite', 'build'], {
      cwd: MOBILE_DIR,
      stdio: 'inherit',
    });
    await waitForUrl(`http://127.0.0.1:8000/graphql`);
    previewServer = spawn(
      'npx',
      ['vite', 'preview', '--host', WEB_HOST, '--port', WEB_PORT],
      {
        cwd: MOBILE_DIR,
        stdio: 'inherit',
      },
    );
    await waitForUrl(BASE_URL);
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
  process.exit(1);
});

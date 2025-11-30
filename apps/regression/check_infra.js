#!/usr/bin/env node
const { spawn } = require('child_process');
const path = require('path');
const { startNeo4j, waitForNeo4j, stopNeo4j } = require('./neo4j');

const ROOT = path.resolve(__dirname, '../../');
const WEB_PORT = Number(process.env.MOBILE_WEB_PORT || 5173);
const BACKEND_URL = process.env.PEGSCANNER_GRAPHQL_URL || 'http://127.0.0.1:8000/graphql';
const WEB_URL = `http://127.0.0.1:${WEB_PORT}/`;

const children = [];
let shuttingDown = false;
let neo4jState = null;

function startTarget(target) {
  const child = spawn('npx', ['nx', 'run', target], {
    cwd: ROOT,
    stdio: 'inherit',
    shell: false,
    detached: true,  // Create new process group
  });
  children.push(child);
  return child;
}

function stopAll() {
  shuttingDown = true;
  for (const child of children) {
    if (child && child.pid && !child.killed) {
      try {
        // Kill entire process group (negative pid)
        process.kill(-child.pid, 'SIGTERM');
      } catch (e) {
        // Process might already be dead
      }
    }
  }
}

function sleep(ms) {
  return new Promise((resolve) => setTimeout(resolve, ms));
}

async function waitForUrl(url, timeoutMs = 45000) {
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.ok) return;
    } catch (err) {
      // ignore until timeout
    }
    await sleep(1000);
  }
  throw new Error(`Timed out waiting for ${url}`);
}

(async () => {
  console.log('[infra] starting Neo4j container…');
  neo4jState = startNeo4j();
  await waitForNeo4j();
  console.log('[infra] starting backend server…');
  const backend = startTarget('backend:start');
  backend.on('exit', (code, signal) => {
    if (shuttingDown) {
      return;
    }
    if ((code !== null && code !== 0) || signal) {
      console.error('[infra] backend exited prematurely');
      process.exitCode = 1;
    }
  });

  await waitForUrl(BACKEND_URL);
  console.log('[infra] backend ping reachable');

  console.log('[infra] starting web (Vite) server…');
  const web = startTarget('mobile:serve');
  web.on('exit', (code, signal) => {
    if (shuttingDown) {
      return;
    }
    if ((code !== null && code !== 0) || signal) {
      console.error('[infra] web server exited prematurely');
      process.exitCode = 1;
    }
  });

  await waitForUrl(WEB_URL);
  console.log('[infra] web bundle reachable at', WEB_URL);

  console.log('[infra] verifying ping endpoint again…');
  await waitForUrl(BACKEND_URL);

  console.log('[infra] regression case passed – backend + web are reachable.');
})()
  .catch((err) => {
    console.error('[infra] regression failed:', err.message);
    process.exitCode = 1;
  })
  .finally(async () => {
    stopAll();
    stopNeo4j(neo4jState);
    // Give processes time to exit gracefully
    await sleep(1000);
    process.exit(process.exitCode || 0);
  });

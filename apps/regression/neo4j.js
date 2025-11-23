#!/usr/bin/env node
const { spawnSync } = require('child_process');
const path = require('path');
const fs = require('fs');

const ROOT = path.resolve(__dirname, '../../');
const TOOLS_BIN = path.join(ROOT, 'tools', 'bin');
if (!process.env.PATH?.includes(TOOLS_BIN)) {
  process.env.PATH = `${TOOLS_BIN}:${process.env.PATH || ''}`;
}

const DOCKER_BIN = process.env.DOCKER_BIN || 'docker';
const DEFAULT_CONTAINER = 'pegscanner_regression_neo4j';
const NEO4J_CONTAINER = process.env.NEO4J_CONTAINER || DEFAULT_CONTAINER;
const NEO4J_HTTP_PORT = process.env.NEO4J_HTTP_PORT || '7474';
const NEO4J_BOLT_PORT = process.env.NEO4J_BOLT_PORT || '7687';
const NEO4J_AUTH = process.env.NEO4J_AUTH || 'neo4j/pegscanner';
const NEO4J_IMAGE = process.env.NEO4J_DOCKER_IMAGE || 'neo4j:5';
const DATA_DIR = process.env.NEO4J_DATA_DIR
  ? path.resolve(process.env.NEO4J_DATA_DIR)
  : path.join(ROOT, 'x-data', 'neo4j');
const shouldSkip = process.env.SKIP_NEO4J_CONTAINER === '1';

function runDocker(args, stdio = 'inherit') {
  const result = spawnSync(DOCKER_BIN, args, { stdio });
  if (result.status !== 0) {
    const stderr = result.stderr ? result.stderr.toString().trim() : '';
    throw new Error(`docker ${args.join(' ')} failed${stderr ? `: ${stderr}` : ''}`);
  }
}

function startNeo4j() {
  if (shouldSkip) {
    console.log('[neo4j] SKIP_NEO4J_CONTAINER=1 → assuming external Neo4j');
    return { started: false };
  }
  console.log(`[neo4j] ensuring container ${NEO4J_CONTAINER} is running…`);
  fs.mkdirSync(DATA_DIR, { recursive: true });
  try {
    runDocker(['rm', '-f', NEO4J_CONTAINER], 'ignore');
  } catch (err) {
    // ignore cleanup errors
  }
  runDocker([
    'run',
    '-d',
    '--name',
    NEO4J_CONTAINER,
    '-p',
    `${NEO4J_HTTP_PORT}:7474`,
    '-p',
    `${NEO4J_BOLT_PORT}:7687`,
    '-v',
    `${DATA_DIR}:/data`,
    '-e',
    `NEO4J_AUTH=${NEO4J_AUTH}`,
    '-e',
    'NEO4J_PLUGINS=[]',
    NEO4J_IMAGE,
  ]);
  return { started: true };
}

async function waitForNeo4j(timeoutMs = 60000) {
  if (shouldSkip) {
    return;
  }
  const url = `http://127.0.0.1:${NEO4J_HTTP_PORT}`;
  const start = Date.now();
  while (Date.now() - start < timeoutMs) {
    try {
      const res = await fetch(url);
      if (res.status < 500) {
        return;
      }
    } catch (err) {
      // ignore until timeout
    }
    await new Promise((resolve) => setTimeout(resolve, 1000));
  }
  throw new Error(`Neo4j at ${url} did not become ready within ${timeoutMs}ms`);
}

function stopNeo4j(state) {
  if (!state?.started || shouldSkip) {
    return;
  }
  try {
    console.log(`[neo4j] stopping container ${NEO4J_CONTAINER}`);
    runDocker(['rm', '-f', NEO4J_CONTAINER], 'ignore');
  } catch (err) {
    // ignore cleanup failures
  }
}

module.exports = {
  startNeo4j,
  waitForNeo4j,
  stopNeo4j,
};

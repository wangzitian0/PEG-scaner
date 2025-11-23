#!/usr/bin/env node
/**
 * Removes the Vite optimize cache so dev/preview servers don't serve stale deps
 * (fixes ERR_ABORTED 504 Outdated Optimize Dep issues).
 */
const fs = require('fs');
const path = require('path');

const cacheDir = path.resolve(__dirname, '../apps/mobile/node_modules/.vite');

try {
  fs.rmSync(cacheDir, { recursive: true, force: true });
  console.log(`[clear-vite-cache] removed ${cacheDir}`);
} catch (err) {
  console.warn(`[clear-vite-cache] failed to remove cache: ${err.message}`);
}

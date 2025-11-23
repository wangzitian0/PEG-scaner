import { defineConfig, devices } from '@playwright/test';

const WEB_HOST = process.env.MOBILE_WEB_HOST || '127.0.0.1';
const WEB_PORT = Number(process.env.MOBILE_WEB_PORT || 5173);
const BASE_URL = `http://${WEB_HOST}:${WEB_PORT}`;

export default defineConfig({
  testDir: './tests',
  fullyParallel: true,
  forbidOnly: !!process.env.CI,
  retries: process.env.CI ? 2 : 0,
  workers: process.env.CI ? 1 : undefined,
  reporter: 'list',
  use: {
    baseURL: BASE_URL,
    trace: 'on-first-retry',
  },
  projects: [
    {
      name: 'chromium',
      use: { ...devices['Desktop Chrome'] },
    },
  ],
});

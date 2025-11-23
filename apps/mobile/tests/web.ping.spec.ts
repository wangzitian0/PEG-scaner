import { test, expect } from '@playwright/test';

const PING_SELECTOR = '[data-testid="ping-indicator"]';

test('web ping indicator reflects backend status', async ({ page }) => {
  await page.goto('/');
  const indicator = page.locator(PING_SELECTOR);
  await expect(indicator).toHaveAttribute('aria-label', /Backend status/);
});

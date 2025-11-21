import { test, expect } from '@playwright/test';

const PING_SELECTOR = '[data-pingstatus]';

test('web ping indicator reflects backend status', async ({ page }) => {
  await page.goto('/');
  const indicator = page.locator(PING_SELECTOR);
  await expect(indicator).toHaveAttribute('data-pingstatus', /checking|ok|error/);
});

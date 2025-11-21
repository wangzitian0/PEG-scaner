import { test, expect } from '@playwright/test';

test('should display the PEG scanner page with stock data', async ({ page }) => {
  // Navigate to the app
  await page.goto('/');

  // Check for the header
  await expect(page.locator('text=PEG Scanner')).toBeVisible();

  // Wait for the API call to finish
  await page.waitForResponse(response => response.url().includes('/api/peg-stocks/') && response.status() === 200);

  // Check that at least one stock item is rendered
  const stockItems = await page.locator('text=P/E:').count();
  expect(stockItems).toBeGreaterThan(0);

  // Check for key text in the first item
  const firstItem = page.locator('.item').first();
  await expect(firstItem.locator('text=PEG:')).toBeVisible();
  await expect(firstItem.locator('text=P/E:')).toBeVisible();
  await expect(firstItem.locator('text=Growth:')).toBeVisible();
});

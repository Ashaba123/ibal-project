import { test, expect } from '@playwright/test';

test.describe('Chat Application', () => {
  test('should show welcome page with correct elements', async ({ page }) => {
    await page.goto('/');
    await expect(page.getByText('Welcome to IBAL Chat')).toBeVisible();
    await expect(page.getByText('Your intelligent conversation partner')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Login' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Register' })).toBeVisible();
  });
}); 
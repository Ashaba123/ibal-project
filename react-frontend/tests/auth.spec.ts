import { test, expect } from '@playwright/test';

test.describe('Authentication', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('http://localhost:5173');
  });

  test('should show welcome page with login and register buttons', async ({ page }) => {
    await expect(page.getByText('Welcome to IBAL Chat')).toBeVisible();
    await expect(page.getByText('Your intelligent conversation partner')).toBeVisible();
    await expect(page.getByRole('link', { name: 'Login' })).toBeVisible();
    await expect(page.getByRole('link', { name: 'Register' })).toBeVisible();
  });

  test('should register a new user', async ({ page }) => {
    // Mock the registration API call
    await page.route('**/api/auth/register/', async (route) => {
      await route.fulfill({
        status: 201,
        body: JSON.stringify({ message: 'User registered successfully' }),
      });
    });

    // Navigate to register page
    await page.click('text=Register');
    
    // Fill in registration form
    await page.fill('input[name="username"]', 'testuser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword123');
    
    // Submit form
    await page.click('button:has-text("Create Account")');
    
    // Wait for navigation to login page (registration redirects to login)
    await page.waitForURL('**/login');
    await expect(page).toHaveURL('/login');
  });

  test('should handle registration error for existing username', async ({ page }) => {
    // Mock the registration API call to return error
    await page.route('**/api/auth/register/', async (route) => {
      await route.fulfill({
        status: 400,
        body: JSON.stringify({ error: 'Username already exists' }),
      });
    });

    // Navigate to register page
    await page.click('text=Register');
    
    // Fill in registration form
    await page.fill('input[name="username"]', 'existinguser');
    await page.fill('input[name="email"]', 'test@example.com');
    await page.fill('input[name="password"]', 'testpassword123');
    
    // Submit form
    await page.click('button:has-text("Create Account")');
    
    // Verify error message
    await expect(page.getByText('This username is already taken. Please try a different one.')).toBeVisible();
  });

  test('should navigate to login page', async ({ page }) => {
    await page.click('text=Login');
    await expect(page).toHaveURL('/login');
    await expect(page.getByText('Welcome Back')).toBeVisible();
  });

  test('should login with existing user', async ({ page }) => {
    // Mock the login API call
    await page.route('**/api/auth/login/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          access: 'mock-access-token',
          refresh: 'mock-refresh-token'
        }),
      });
    });

    // Mock the user info API call
    await page.route('**/api/auth/user/', async (route) => {
      await route.fulfill({
        status: 200,
        body: JSON.stringify({
          id: 1,
          username: 'testuser',
          email: 'test@example.com'
        }),
      });
    });

    // Navigate to login page
    await page.click('text=Login');
    
    // Fill in login form
    await page.fill('input[id="username"]', 'testuser');
    await page.fill('input[id="password"]', 'testpassword123');
    
    // Submit form
    await page.click('button:has-text("Login")');
    
    // Wait for navigation to chat page
    await page.waitForURL('**/chat');
    await expect(page).toHaveURL('/chat');
  });

  test('should toggle password visibility in login form', async ({ page }) => {
    await page.click('text=Login');
    
    const passwordInput = page.locator('input[id="password"]');
    const toggleButton = page.locator('button.password-toggle');
    
    // Initially password should be hidden
    await expect(passwordInput).toHaveAttribute('type', 'password');
    
    // Click toggle to show password
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'text');
    await expect(toggleButton).toHaveText('Hide');
    
    // Click toggle to hide password again
    await toggleButton.click();
    await expect(passwordInput).toHaveAttribute('type', 'password');
    await expect(toggleButton).toHaveText('Show');
  });

  test('should navigate between login and register pages', async ({ page }) => {
    // Go to login page
    await page.click('text=Login');
    await expect(page).toHaveURL('/login');
    
    // Click register link
    await page.click('text=Register here');
    await expect(page).toHaveURL('/register');
    
    // Click sign in link
    await page.click('text=Sign in');
    await expect(page).toHaveURL('/login');
  });
}); 
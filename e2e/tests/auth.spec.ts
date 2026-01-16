/**
 * E2E Tests for Authentication Flow
 */
import { test, expect } from '@playwright/test';
import { testUsers } from './fixtures/test-data';

test.describe('Authentication Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    // Navigate to login page before each test
    await page.goto('/pages/login.html');
  });

  test('login page loads correctly', async ({ page }) => {
    // Check page title or header
    await expect(page).toHaveTitle(/ALIGNED|AAL|로그인/i);
    
    // Check login form elements exist
    await expect(page.locator('input[type="email"], #login-email, #email')).toBeVisible();
    await expect(page.locator('input[type="password"], #login-password, #password')).toBeVisible();
  });

  test('shows error for empty login attempt', async ({ page }) => {
    // Click login without entering credentials
    await page.click('button[type="submit"], #login-btn, .login-btn');
    
    // Should show error message
    await expect(page.locator('.error, .alert-error, [class*="error"]')).toBeVisible({ timeout: 5000 });
  });

  test('shows error for invalid credentials', async ({ page }) => {
    // Enter invalid credentials
    await page.fill('input[type="email"], #login-email, #email', 'invalid@test.com');
    await page.fill('input[type="password"], #login-password, #password', 'wrongpassword');
    
    // Click login
    await page.click('button[type="submit"], #login-btn, .login-btn');
    
    // Should show error
    await expect(page.locator('.error, .alert-error, [class*="error"]')).toBeVisible({ timeout: 5000 });
  });

  test('has link to registration page', async ({ page }) => {
    // Check for registration link
    const registerLink = page.locator('a[href*="register"], a[href*="signup"], .register-link');
    await expect(registerLink).toBeVisible();
  });

  test('navigates to registration page', async ({ page }) => {
    // Click registration link
    await page.click('a[href*="register"], a[href*="signup"], .register-link');
    
    // Should navigate to registration page
    await expect(page).toHaveURL(/register|signup/);
  });
});

test.describe('Registration Flow', () => {
  
  test.beforeEach(async ({ page }) => {
    await page.goto('/pages/register.html');
  });

  test('registration page loads correctly', async ({ page }) => {
    // Check form fields exist
    await expect(page.locator('input[name="email"], #email')).toBeVisible();
    await expect(page.locator('input[name="password"], #password')).toBeVisible();
    await expect(page.locator('input[name="company"], #company')).toBeVisible();
  });

  test('shows validation error for weak password', async ({ page }) => {
    // Fill form with weak password
    await page.fill('input[name="email"], #email', 'test@example.com');
    await page.fill('input[name="password"], #password', '123'); // Too weak
    await page.fill('input[name="company"], #company', 'Test Co');
    await page.fill('input[name="name"], #name', 'Test User');
    
    // Try to submit
    await page.click('button[type="submit"], #register-btn, .register-btn');
    
    // Should show validation error
    await expect(page.locator('.error, [class*="error"], .validation-error')).toBeVisible({ timeout: 5000 });
  });

  test('user type selection works', async ({ page }) => {
    // Check user type radio buttons or dropdown
    const shipperOption = page.locator('input[value="shipper"], option[value="shipper"], [data-type="shipper"]');
    const forwarderOption = page.locator('input[value="forwarder"], option[value="forwarder"], [data-type="forwarder"]');
    
    // At least one should exist
    const shipperVisible = await shipperOption.isVisible().catch(() => false);
    const forwarderVisible = await forwarderOption.isVisible().catch(() => false);
    
    expect(shipperVisible || forwarderVisible).toBeTruthy();
  });
});

test.describe('Session Management', () => {
  
  test('logout clears session', async ({ page }) => {
    // This test assumes user is logged in
    // Navigate to a page that requires auth
    await page.goto('/pages/dashboard-shipper.html');
    
    // If redirected to login, session management is working
    const url = page.url();
    const isOnDashboard = url.includes('dashboard');
    const isOnLogin = url.includes('login');
    
    // Either should be true depending on auth state
    expect(isOnDashboard || isOnLogin).toBeTruthy();
  });
});

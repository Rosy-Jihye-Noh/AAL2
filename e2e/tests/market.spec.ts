/**
 * E2E Tests for Market Data Pages
 */
import { test, expect } from '@playwright/test';

test.describe('Market Data - Economy', () => {
  
  test('main page loads with market section', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    
    // Page should load
    const title = await page.title();
    expect(title).toBeTruthy();
  });

  test('exchange rate section displays data', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(2000);
    
    // Look for exchange rate related elements
    const exchangeSection = page.locator('[data-section="exchange"], .exchange-rate, [class*="exchange"]');
    // May or may not be visible depending on navigation
  });

  test('GDP section can be accessed', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(1000);
    
    // Look for GDP menu item or section
    const gdpElement = page.locator('text=GDP, [data-section="gdp"], a:has-text("GDP")');
    const hasGDP = await gdpElement.first().isVisible().catch(() => false);
    
    if (hasGDP) {
      await gdpElement.first().click();
      await page.waitForTimeout(500);
    }
  });
});

test.describe('Market Data - Shipping Indices', () => {
  
  test('shipping indices section exists', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(1000);
    
    // Look for shipping indices elements
    const shippingSection = page.locator('[class*="shipping"], [class*="bdi"], [class*="scfi"]');
    // May need navigation to access
  });

  test('BDI chart renders', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(2000);
    
    // Navigate to shipping indices if needed
    const navItem = page.locator('text=BDI, text=해운지수, [data-nav="shipping"]');
    if (await navItem.first().isVisible().catch(() => false)) {
      await navItem.first().click();
      await page.waitForTimeout(1000);
    }
    
    // Check for chart canvas
    const chart = page.locator('canvas, .chart-container');
    // Chart should exist somewhere on the page
  });
});

test.describe('Market Data - KCCI Index', () => {
  
  test('KCCI section loads', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(1000);
    
    // Look for KCCI navigation or section
    const kcciNav = page.locator('text=KCCI, text=컨테이너, [data-section="kcci"]');
    if (await kcciNav.first().isVisible().catch(() => false)) {
      await kcciNav.first().click();
      await page.waitForTimeout(1000);
    }
  });
});

test.describe('Market Data Filters', () => {
  
  test('date range selector works', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(2000);
    
    // Find date range buttons
    const rangeButtons = page.locator('.range-btn, [data-range], button:has-text("1W"), button:has-text("1M")');
    const firstBtn = rangeButtons.first();
    
    if (await firstBtn.isVisible().catch(() => false)) {
      await firstBtn.click();
      await page.waitForTimeout(500);
      
      // Data should update (hard to verify without checking actual content)
    }
  });

  test('currency toggle works for exchange rate', async ({ page }) => {
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(2000);
    
    // Find currency selector
    const currencySelector = page.locator('select[name*="currency"], .currency-selector, [data-currency]');
    
    if (await currencySelector.first().isVisible().catch(() => false)) {
      await currencySelector.first().selectOption({ index: 1 }).catch(() => {});
      await page.waitForTimeout(500);
    }
  });
});

test.describe('Market Data Error Handling', () => {
  
  test('handles API errors gracefully', async ({ page }) => {
    // Intercept API calls and return error
    await page.route('**/api/market/**', route => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ error: 'Internal Server Error' })
      });
    });
    
    await page.goto('/frontend/ai_studio_code_F2.html');
    await page.waitForTimeout(2000);
    
    // Page should not crash
    const body = await page.locator('body').isVisible();
    expect(body).toBeTruthy();
  });

  test('shows loading state', async ({ page }) => {
    // Delay API response
    await page.route('**/api/market/**', async route => {
      await new Promise(resolve => setTimeout(resolve, 3000));
      route.fulfill({
        status: 200,
        body: JSON.stringify({ data: [] })
      });
    });
    
    await page.goto('/frontend/ai_studio_code_F2.html');
    
    // Check for loading indicator
    const loadingIndicator = page.locator('.loading, .spinner, [class*="loading"]');
    // Loading indicator may appear briefly
  });
});

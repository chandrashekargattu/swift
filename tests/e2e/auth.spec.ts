import { test, expect, type Page } from '@playwright/test';

test.describe('Authentication Flow', () => {
  test.beforeEach(async ({ page }) => {
    await page.goto('/');
  });

  test('should display sign in button in header', async ({ page }) => {
    const signInButton = page.getByRole('link', { name: /sign in/i });
    await expect(signInButton).toBeVisible();
  });

  test('should navigate to sign in page', async ({ page }) => {
    await page.getByRole('link', { name: /sign in/i }).click();
    await expect(page).toHaveURL('/signin');
    await expect(page.getByRole('heading', { name: /sign in to rideswift/i })).toBeVisible();
  });

  test('should switch between sign in and sign up forms', async ({ page }) => {
    await page.goto('/signin');
    
    // Initially should show sign in form
    await expect(page.getByRole('heading', { name: /sign in to rideswift/i })).toBeVisible();
    await expect(page.getByLabel(/email address/i)).toBeVisible();
    await expect(page.getByLabel(/^password$/i)).toBeVisible();
    
    // Click sign up link
    await page.getByRole('button', { name: /sign up/i }).click();
    
    // Should show sign up form
    await expect(page.getByRole('heading', { name: /create your rideswift account/i })).toBeVisible();
    await expect(page.getByLabel(/full name/i)).toBeVisible();
    await expect(page.getByLabel(/phone number/i)).toBeVisible();
    await expect(page.getByLabel(/confirm password/i)).toBeVisible();
  });

  test('should show validation errors for empty form', async ({ page }) => {
    await page.goto('/signin');
    
    // Try to submit empty form
    await page.getByRole('button', { name: /^sign in$/i }).click();
    
    // Should show browser validation
    const emailInput = page.getByLabel(/email address/i);
    const emailValidation = await emailInput.evaluate((el: HTMLInputElement) => el.validationMessage);
    expect(emailValidation).toBeTruthy();
  });

  test('should show error for invalid credentials', async ({ page }) => {
    await page.goto('/signin');
    
    // Fill in invalid credentials
    await page.getByLabel(/email address/i).fill('nonexistent@example.com');
    await page.getByLabel(/^password$/i).fill('WrongPassword123!');
    
    // Submit form
    await page.getByRole('button', { name: /^sign in$/i }).click();
    
    // Should show error message
    await expect(page.getByText(/invalid email or password/i)).toBeVisible();
  });

  test('should successfully sign up a new user', async ({ page }) => {
    await page.goto('/signin');
    
    // Switch to sign up
    await page.getByRole('button', { name: /sign up/i }).click();
    
    // Fill in sign up form
    const timestamp = Date.now();
    const testEmail = `test${timestamp}@example.com`;
    
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill(testEmail);
    await page.getByLabel(/phone number/i).fill('8143243584');
    await page.getByLabel(/^password$/i).fill('StrongPass123!');
    await page.getByLabel(/confirm password/i).fill('StrongPass123!');
    
    // Submit form
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Should show success message and redirect
    await expect(page.getByText(/registration successful/i)).toBeVisible();
    await expect(page).toHaveURL('/');
    
    // Should show user name in header
    await expect(page.getByText('Test')).toBeVisible();
  });

  test('should show password mismatch error', async ({ page }) => {
    await page.goto('/signin');
    
    // Switch to sign up
    await page.getByRole('button', { name: /sign up/i }).click();
    
    // Fill in sign up form with mismatched passwords
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/phone number/i).fill('8143243584');
    await page.getByLabel(/^password$/i).fill('StrongPass123!');
    await page.getByLabel(/confirm password/i).fill('DifferentPass123!');
    
    // Submit form
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Should show error message
    await expect(page.getByText(/passwords do not match/i)).toBeVisible();
  });

  test('should sign out user', async ({ page }) => {
    // First sign up
    await page.goto('/signin');
    await page.getByRole('button', { name: /sign up/i }).click();
    
    const timestamp = Date.now();
    const testEmail = `test${timestamp}@example.com`;
    
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill(testEmail);
    await page.getByLabel(/phone number/i).fill('8143243584');
    await page.getByLabel(/^password$/i).fill('StrongPass123!');
    await page.getByLabel(/confirm password/i).fill('StrongPass123!');
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Wait for redirect
    await expect(page).toHaveURL('/');
    
    // Click on user menu
    await page.getByText('Test').click();
    
    // Click sign out
    await page.getByRole('button', { name: /sign out/i }).click();
    
    // Should show sign in button again
    await expect(page.getByRole('link', { name: /sign in/i })).toBeVisible();
  });

  test('should persist session after page refresh', async ({ page }) => {
    // First sign up
    await page.goto('/signin');
    await page.getByRole('button', { name: /sign up/i }).click();
    
    const timestamp = Date.now();
    const testEmail = `test${timestamp}@example.com`;
    
    await page.getByLabel(/full name/i).fill('Test User');
    await page.getByLabel(/email address/i).fill(testEmail);
    await page.getByLabel(/phone number/i).fill('8143243584');
    await page.getByLabel(/^password$/i).fill('StrongPass123!');
    await page.getByLabel(/confirm password/i).fill('StrongPass123!');
    await page.getByRole('button', { name: /create account/i }).click();
    
    // Wait for redirect
    await expect(page).toHaveURL('/');
    await expect(page.getByText('Test')).toBeVisible();
    
    // Refresh page
    await page.reload();
    
    // Should still be signed in
    await expect(page.getByText('Test')).toBeVisible();
  });

  test('should handle API errors gracefully', async ({ page, context }) => {
    // Block API requests to simulate server error
    await context.route('**/api/v1/auth/login', (route) => {
      route.fulfill({
        status: 500,
        body: JSON.stringify({ detail: 'Internal server error' }),
      });
    });
    
    await page.goto('/signin');
    
    // Fill in form
    await page.getByLabel(/email address/i).fill('test@example.com');
    await page.getByLabel(/^password$/i).fill('StrongPass123!');
    
    // Submit form
    await page.getByRole('button', { name: /^sign in$/i }).click();
    
    // Should show error message
    await expect(page.getByText(/internal server error/i)).toBeVisible();
  });
});

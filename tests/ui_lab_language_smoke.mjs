// Real Vite app, not mocked UI. English URLs survive reload and native history.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 820 } });
    try {
      await page.goto(origin + '#/map', { waitUntil: 'domcontentloaded' });
      await page.getByRole('button', { name: 'English' }).click();
      await page.waitForFunction(() => document.documentElement.lang === 'en');
      assert.equal(new URL(page.url()).searchParams.get('lang'), 'en');
      await page.waitForFunction(() => document.title.startsWith('Tracking & Map'));
      await page.evaluate(() => { window.location.hash = '#/inverse'; });
      await page.waitForFunction(() => document.title.startsWith('Inverse scenarios'));
      assert.equal(new URL(page.url()).searchParams.get('lang'), 'en');
      await page.goBack();
      await page.waitForFunction(() => document.title.startsWith('Tracking & Map'));
      assert.equal(await page.evaluate(() => document.documentElement.lang), 'en');
      await page.reload();
      await page.waitForFunction(() => document.title.startsWith('Tracking & Map'));
      assert.equal(await page.evaluate(() => document.documentElement.lang), 'en');
      await page.getByRole('button', { name: 'Português (Brasil)' }).click();
      await page.waitForFunction(() => document.documentElement.lang === 'pt-BR');
      assert.equal(new URL(page.url()).searchParams.has('lang'), false);
      await page.goto(origin + '?lang=en&lang=pt#/map');
      await page.waitForFunction(() => document.title.startsWith('Rastreamento & Mapa'));
      assert.equal(await page.evaluate(() => document.documentElement.lang), 'pt-BR');
      console.log('PASS lab language share/reload/history ' + width + 'px');
    } finally { await page.close(); }
  }
} finally { await browser.close(); }

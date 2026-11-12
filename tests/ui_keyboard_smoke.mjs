// Browser-level keyboard, landmark, language and narrow-viewport smoke.
// Run against the local PR HEAD. Screenshots are evidence, not visual approval.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const findings = [];
try {
  for (const viewport of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 375, height: 812 }]) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(origin, { waitUntil: 'domcontentloaded', timeout: 30000 });
    assert(response?.ok(), `initial page HTTP ${response?.status()}`);
    await page.getByRole('heading', { level: 1 }).first().waitFor({ timeout: 20000 });
    const before = new URL(page.url()).hash;
    await page.keyboard.press('Tab');
    const first = await page.evaluate(() => ({
      text: document.activeElement?.textContent?.trim(),
      tag: document.activeElement?.tagName,
      visible: !!document.activeElement?.getClientRects().length,
    }));
    assert.equal(first.tag, 'A', 'first tab stop should be native skip link');
    assert.match(first.text || '', /Pular para o conteúdo/);
    assert(first.visible, 'skip link should be visible when keyboard-focused');
    await page.keyboard.press('Enter');
    const focused = await page.evaluate(() => ({
      tag: document.activeElement?.tagName,
      id: document.activeElement?.id,
      hash: window.location.hash,
    }));
    assert.equal(focused.tag, 'MAIN');
    assert.equal(focused.id, 'main-content');
    assert.equal(focused.hash, before, 'skip link must not replace the hash-router route');
    await page.getByRole('navigation', { name: 'Seções do laboratório' })
      .getByRole('link', { name: /Rastreamento & Mapa/ }).click();
    assert.equal(new URL(page.url()).hash, '#/map');
    // Hash changes synchronously; React state and aria-current update on a later tick.
    await page.waitForFunction(() => document.querySelector('nav a[aria-current="page"]')?.textContent?.includes('Rastreamento & Mapa'));
    const current = await page.getByRole('navigation', { name: 'Seções do laboratório' })
      .locator('[aria-current="page"]').textContent();
    assert.match(current || '', /Rastreamento & Mapa/);
    await page.getByRole('button', { name: 'English' }).click();
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    assert.equal(await page.getByRole('link', { name: 'Skip to main content' }).count(), 1);
    await page.getByRole('navigation', { name: 'Laboratory sections' })
      .getByRole('link', { name: /Summary & limits/ }).click();
    const horizontal = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      document: document.documentElement.scrollWidth,
    }));
    assert(horizontal.document <= horizontal.viewport + 1,
      `body overflow on ${viewport.name}: ${JSON.stringify(horizontal)}`);
    await page.screenshot({ path: `${out}/${viewport.name}-summary.png`, fullPage: true });

    // Verify modal name, focus entry/loop, Escape dismissal and trigger focus restoration.
    const exportTrigger = page.getByRole('button', { name: 'Python Script' }).first();
    await exportTrigger.click();
    const dialog = page.getByRole('dialog', { name: 'norad528_reconstruction.py' });
    await dialog.waitFor();
    const close = dialog.getByRole('button', { name: 'Close export dialog' });
    const copy = dialog.getByRole('button', { name: 'Copy code' });
    assert(await close.evaluate(element => document.activeElement === element),
      'opening the export dialog must focus its close control');
    await page.keyboard.press('Tab');
    assert(await copy.evaluate(element => document.activeElement === element),
      'Tab from last control must wrap to first control');
    await page.keyboard.press('Shift+Tab');
    assert(await close.evaluate(element => document.activeElement === element),
      'Shift+Tab from first control must wrap to last control');
    await page.screenshot({ path: `${out}/${viewport.name}-python-dialog.png` });
    await page.keyboard.press('Escape');
    await dialog.waitFor({ state: 'hidden' });
    assert(await exportTrigger.evaluate(element => document.activeElement === element),
      'Escape must close export dialog and restore trigger focus');

    assert.equal(errors.length, 0, `uncaught page errors: ${errors.join('; ')}`);
    findings.push({ viewport: viewport.name, skip_target: focused.id, hash_preserved: true, nav_hash: '#/map', html_lang: 'en', overflow_px: horizontal.document - horizontal.viewport });
    await page.close();
  }
  await fs.writeFile(`${out}/findings.json`, JSON.stringify({ origin, findings }, null, 2) + '\n');
  console.log(JSON.stringify({ result: 'PASS', findings }, null, 2));
} finally {
  await browser.close();
}

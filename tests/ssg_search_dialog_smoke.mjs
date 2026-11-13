// Chromium exercise of the real SSG-built search, not an isolated fixture.
// Viewport/reflow proxies are not native zoom, physical touch or screen readers.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const origin = process.env.SSG_SEARCH_AUDIT_URL || 'http://127.0.0.1:4173/conde-incident/';
await mkdir('test-results/ui', { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 375, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 820 }, hasTouch: true });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(origin, { waitUntil: 'domcontentloaded' });
    assert(response?.ok(), `SSG homepage HTTP ${response?.status()}`);
    const trigger = page.locator('#ssg-search-btn');
    const dialog = page.locator('#ssg-search-overlay');
    const input = page.locator('#ssg-search-input');
    const close = page.locator('#ssg-search-close');
    assert.equal(await dialog.getAttribute('aria-modal'), 'true');
    assert.equal(await close.getAttribute('aria-label'), 'Fechar pesquisa');
    await trigger.click();
    await dialog.locator('input:focus').waitFor();
    assert.equal(await dialog.evaluate(el => el.classList.contains('active')), true);
    const rect = await close.boundingBox();
    assert(rect && rect.width >= 44 && rect.height >= 44,
      `close tap target under 44x44 at ${width}px: ${JSON.stringify(rect)}`);
    assert(rect.x >= 0 && rect.x + rect.width <= width + 1,
      `close outside viewport at ${width}px: ${JSON.stringify(rect)}`);
    await page.keyboard.press('Shift+Tab');
    assert.equal(await close.evaluate(el => document.activeElement === el), true,
      `Shift+Tab must wrap from input to close at ${width}px`);
    await page.keyboard.press('Tab');
    assert.equal(await input.evaluate(el => document.activeElement === el), true,
      `Tab must wrap back to input at ${width}px`);
    await close.focus();
    await page.keyboard.press('Enter');
    assert.equal(await dialog.evaluate(el => el.classList.contains('active')), false,
      `Enter on close must close rather than select search result at ${width}px`);
    assert.equal(await trigger.evaluate(el => document.activeElement === el), true,
      `close via Enter must return focus at ${width}px`);
    await page.keyboard.press('Control+k');
    await dialog.locator('input:focus').waitFor();
    await page.keyboard.press('Escape');
    assert.equal(await trigger.evaluate(el => document.activeElement === el), true,
      `Escape must restore search trigger focus at ${width}px`);
    await trigger.click();
    await dialog.locator('input:focus').waitFor();
    await close.tap();
    assert.equal(await trigger.evaluate(el => document.activeElement === el), true,
      `touch on close must restore focus at ${width}px`);
    await trigger.click();
    await dialog.locator('input:focus').waitFor();
    await page.screenshot({ path: `test-results/ui/ssg-search-${width}.png` });
    assert.deepEqual(errors, [], `SSG runtime errors at ${width}px`);
    await page.close();
  }
} finally { await browser.close(); }

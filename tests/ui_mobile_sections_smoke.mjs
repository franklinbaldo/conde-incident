// Chromium: native mobile section disclosure, keyboard, hash and reflow.
// Runs against the actual Vite app, not a mocked component.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  // Deep links name the current section in the closed mobile menu.
  // Keyboard can reveal all eight destinations and preserve Back/Forward.
  for (const width of [320, 375, 640]) {
    const page = await browser.newPage({ viewport: { width, height: 800 } });
    try {
      await page.goto(origin + '#/documents', { waitUntil: 'domcontentloaded' });
      const nav = page.getByRole('navigation', { name: 'Seções do laboratório' });
      const chooser = nav.locator('summary');
      await chooser.waitFor();
      assert.match(await chooser.innerText(), /Arquivo e proveniência/);
      await chooser.focus();
      await page.keyboard.press('Enter');
      assert.notEqual(await nav.locator('details').getAttribute('open'), null);
      assert.equal(await nav.locator('[data-mobile-tabs] a').count(), 8);
      const active = nav.locator('[data-mobile-tabs] [aria-current="page"]');
      assert.match(await active.innerText(), /Arquivo e proveniência/);
      for (const link of await nav.locator('[data-mobile-tabs] a').all()) {
        const rect = await link.boundingBox();
        assert(rect && rect.height >= 44 && rect.x >= -1 && rect.x + rect.width <= width + 1,
          'section option clipped or smaller than 44px at ' + width + ': ' + JSON.stringify(rect));
      }
      await nav.getByRole('link', { name: /Rastreamento & Mapa/ }).click();
      assert.equal(new URL(page.url()).hash, '#/map');
      assert.equal(await nav.locator('details').getAttribute('open'), null);
      assert.match(await chooser.innerText(), /Rastreamento & Mapa/);
      assert(await chooser.evaluate(el => document.activeElement === el),
        'closing mobile section list must preserve keyboard focus');
      await page.goBack();
      assert.match(await chooser.innerText(), /Arquivo e proveniência/);
      if (width === 640) {
        await page.setViewportSize({ width: 320, height: 800 });
        assert.match(await chooser.innerText(), /Arquivo e proveniência/);
      }
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true);
      await page.screenshot({ path: out + '/deep-link-documents-' + width + '.png' });
    } finally {
      await page.close();
    }
  }
 } finally {
  await browser.close();
}

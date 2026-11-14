// UI regression for exploratory inverse filter at 200% text; not native browser zoom.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const base = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 375, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 812 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', e => errors.push(e.message));
    try {
      const response = await page.goto(base.replace(/#.*$/, '') + '#/inverse', { waitUntil: 'domcontentloaded' });
      assert(response?.ok(), 'Inverse laboratory HTTP failed');
      await page.getByRole('heading', { name: /Teste Inverso/, level: 1 }).waitFor();
      await page.addStyleTag({ content: 'html {font-size:200% !important}' });
      for (const lang of ['pt', 'en']) {
        if (lang === 'en') {
          await page.getByRole('button', { name: 'English' }).click();
          await page.getByRole('heading', { name: /Inverse Test/, level: 1 }).waitFor();
        }
        const filter = page.getByRole('group', {
          name: lang === 'pt' ? 'Filtrar dia do cenário' : 'Filter scenario day',
        });
        const all = filter.getByRole('button', { name: lang === 'pt' ? /Todas/ : /All/ });
        await all.click();
        assert.equal(await all.getAttribute('aria-pressed'), 'true', 'all-days filter must activate');
        const day8 = filter.getByRole('button', { name: lang === 'pt' ? /08\/11/ : /08 Nov/ });
        await day8.click();
        assert.equal(await day8.getAttribute('aria-pressed'), 'true', 'catalog-day filter must activate');
        const size = await page.evaluate(() => ({
          width: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth,
        }));
        assert(size.scroll <= size.width + 1, `${lang} ${width}: horizontal scroll ${JSON.stringify(size)}`);
        const box = await filter.boundingBox();
        assert(box && box.width > 100 && box.x >= -1 && box.x + box.width <= width + 1,
          `${lang} ${width}: clipped date filter ${JSON.stringify(box)}`);
        await page.screenshot({path: `${out}/inverse-200-${lang}-${width}.png`, fullPage: false});
      }
      assert.deepEqual(errors, [], 'Unexpected inverse laboratory JS error');
    } finally { await page.close(); }
  }
} finally { await browser.close(); }

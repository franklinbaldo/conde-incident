// Map-only regression for UX-01/UX-02: preserve the drawable SVG and controls
// at narrow widths with 200% text. This is CSS text scaling, NOT native zoom.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 375, 390, 640]) {
    const page = await browser.newPage({ viewport: { width, height: 844 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    try {
      const response = await page.goto(origin.replace(/#.*$/, '') + '#/map', { waitUntil: 'domcontentloaded' });
      assert(response?.ok(), `HTTP ${response?.status()} on /#/map`);
      await page.getByRole('heading', { name: 'Mapa orbital exploratório' }).waitFor();
      // Deliberately stress long UTC timestamps, the native date input and
      // scientific legend without hiding any of the actual orbit graphic.
      await page.addStyleTag({ content: 'html { font-size: 200% !important; }' });
      for (const lang of ['pt', 'en']) {
        if (lang === 'en') {
          await page.getByRole('button', { name: 'English' }).click();
          await page.getByRole('heading', { name: 'Exploratory orbit map' }).waitFor();
        }
        const svg = page.getByRole('img', {
          name: lang === 'pt' ? /Mapa orbital esquemático/ : /Schematic orbital map/,
        });
        const rect = await svg.boundingBox();
        assert(rect && rect.width >= 120 && rect.x >= -1 && rect.x + rect.width <= width + 1,
          `map graphic squeezed or clipped at ${width}px/${lang}: ${JSON.stringify(rect)}`);
        for (const control of [
          page.locator('input[type="date"]'),
          page.locator('input[type="range"]'),
          page.getByRole('button', { name: lang === 'pt' ? 'Aproximar' : 'Zoom in' }),
        ]) {
          const box = await control.boundingBox();
          assert(box && box.width > 0 && box.x >= -1 && box.x + box.width <= width + 1,
            `map control beyond viewport ${width}px/${lang}: ${JSON.stringify(box)}`);
        }
        const dimensions = await page.evaluate(() => ({
          viewport: document.documentElement.clientWidth,
          scrollWidth: document.documentElement.scrollWidth,
          // Failures show the actual boxes involved, not a guessed CSS cause.
          offenders: [...document.querySelectorAll('main *')].filter(el => {
            const r = el.getBoundingClientRect();
            return r.width > 0 && (r.left < -1 || r.right > innerWidth + 1);
          }).slice(0, 6).map(el => ({ tag: el.tagName, id: el.id,
            class: String(el.getAttribute('class') || '').slice(0, 100),
            right: Math.round(el.getBoundingClientRect().right) })),
        }));
        assert(dimensions.scrollWidth <= dimensions.viewport + 1,
          `map document-wide 200% text overflow at ${width}px/${lang}: ${JSON.stringify(dimensions)}`);
        const date = page.locator('input[type="date"]');
        await date.fill('1963-10-28');
        assert.equal(await date.inputValue(), '1963-10-28', 'date control must remain functional');
        await page.getByRole('button', { name: lang === 'pt' ? 'Aproximar' : 'Zoom in' }).click();
        assert.equal(await svg.getAttribute('viewBox'), '0 0 960 480',
          'map must retain the full plot, not crop it to avoid overflow');
        await page.screenshot({ path: `${out}/map-reflow-200pct-${lang}-${width}.png` });
      }
      assert.deepEqual(errors, [], `uncaught map error at ${width}px`);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

// The global editorial link must wrap at 200% text, while long TLE lines
// scroll only within their focusable code panels. CSS text scaling is a
// proxy for reflow, NOT native OS/browser zoom or screen-reader certification.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base = (process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/').replace(/#.*$/, '');
const browser = await chromium.launch({ headless: true });
const routes = ['tles', 'triangulation', 'map'];

try {
  for (const route of routes) {
    for (const width of [320, 375, 1440]) {
      const page = await browser.newPage({
        viewport: { width, height: 900 },
        reducedMotion: 'reduce',
      });
      const errors = [];
      page.on('pageerror', error => errors.push(error.message));

      try {
        const response = await page.goto(base + '#/' + route, { waitUntil: 'domcontentloaded' });
        assert(response?.ok(), `${route}: laboratory HTTP failed`);
        await page.locator('main h1').first().waitFor();
        await page.addStyleTag({ content: 'html { font-size: 200% !important; }' });

        for (const lang of ['pt', 'en']) {
          if (lang === 'en') {
            await page.getByRole('button', { name: 'English' }).click();
          }
          const nav = page.locator(
            'header a[aria-label^="Abrir no Caderno"], header a[aria-label^="Open in Notebook"]',
          );
          assert.equal(await nav.count(), 1, `${route}/${lang}: missing editorial context link`);
          const linkRect = await nav.boundingBox();
          assert(linkRect && linkRect.width > 0 && linkRect.x >= -1 &&
            linkRect.x + linkRect.width <= width + 1,
            `${route}/${lang}/${width}: editorial link is clipped ${JSON.stringify(linkRect)}`);

          const dimensions = await page.evaluate(() => ({
            client: document.documentElement.clientWidth,
            scroll: document.documentElement.scrollWidth,
          }));
          assert(dimensions.scroll <= dimensions.client + 1,
            `${route}/${lang}/${width}: horizontal document overflow ${JSON.stringify(dimensions)}`);

          if (route === 'tles' || route === 'map') {
            const note = page.locator('main aside[role="note"]');
            assert.equal(await note.count(), 1,
              `${route}/${lang}: source/limits must be notes, not nested complementary landmarks`);
            assert.equal(await page.locator('main aside:not([role="note"])').count(), 0);
          }
          if (route === 'tles') {
            const codePanel = page.locator('main pre[tabindex="0"]').first();
            assert(await codePanel.isVisible(), 'TLE text must remain focusable and scrollable');
            const code = await codePanel.evaluate(pre => ({
              scroll: pre.scrollWidth, width: pre.clientWidth,
              overflow: getComputedStyle(pre).overflowX,
            }));
            assert.equal(code.overflow, 'auto', 'TLE code panel must preserve local scroll');
            if (width === 320) {
              assert(code.scroll > code.width, 'TLE code must not wrap or be truncated');
            }
          }
        }
        assert.deepEqual(errors, [], `${route}/${width}: JS exceptions`);
      } finally {
        await page.close();
      }
    }
  }
} finally {
  await browser.close();
}

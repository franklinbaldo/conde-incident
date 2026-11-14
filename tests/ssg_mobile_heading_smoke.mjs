// Chromium regression against the fully built SSG Pages artifact, not a CSS fixture.
// Visual issue reproduced in the published 320px home on 2026-11-14:
// the final word "documentada" occupied two line boxes, leaving a lone "a".
// This tests browser layout; it does not claim native zoom or screen-reader coverage.
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
import { chromium } from 'playwright';

const base = process.env.SSG_MOBILE_TITLE_URL || 'http://127.0.0.1:4173/conde-incident/';
const routes = ['', 'evidencias/', 'stories/', 'cronologia/'];
await mkdir('test-results/ui', { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const route of routes) {
    for (const width of [320, 375, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 820 } });
      const errors = [];
      page.on('pageerror', err => errors.push(err.message));
      try {
        const response = await page.goto(new URL(route, base).href, { waitUntil: 'domcontentloaded' });
        assert(response?.ok(), `SSG ${route} HTTP ${response?.status()}`);
        const result = await page.evaluate(() => {
          const h = document.querySelector('main h1');
          if (!h) return { heading: false };
          const text = h.textContent.trim();
          const last = text.split(/\s+/).at(-1);
          const node = h.firstChild;
          let lastWordLines = null;
          if (node?.nodeType === Node.TEXT_NODE && node.textContent.includes(last)) {
            const start = node.textContent.lastIndexOf(last);
            const range = document.createRange();
            range.setStart(node, start);
            range.setEnd(node, start + last.length);
            lastWordLines = [...range.getClientRects()].filter(rect => rect.width > 0).length;
          }
          return {
            heading: true, title: text, last, lastWordLines,
            fontSize: parseFloat(getComputedStyle(h).fontSize),
            viewport: document.documentElement.clientWidth,
            scrollWidth: document.documentElement.scrollWidth,
          };
        });
        assert(result.heading, `missing main h1 ${route} ${width}px`);
        assert(result.scrollWidth <= result.viewport + 1,
          `document overflow ${route} ${width}px: ${JSON.stringify(result)}`);
        if (!route && width === 320) {
          assert.equal(result.last, 'documentada', 'unexpected homepage title; revisit orphan regression');
          assert.equal(result.lastWordLines, 1,
            `orphaned last letter at 320px: ${JSON.stringify(result)}`);
          assert(result.fontSize >= 31 && result.fontSize <= 33,
            `mobile headline font should adapt to 320px: ${JSON.stringify(result)}`);
        }
        assert.deepEqual(errors, [], `browser errors ${route} ${width}px`);
        if (width === 320 && ['', 'evidencias/'].includes(route)) {
          const shot = route ? 'evidencias' : 'home';
          await page.screenshot({ path: `test-results/ui/ssg-mobile-heading-${shot}-${width}.png` });
        }
        console.log(`PASS SSG editorial heading ${route || 'home'} at ${width}px`);
      } finally {
        await page.close();
      }
    }
  }
} finally {
  await browser.close();
}

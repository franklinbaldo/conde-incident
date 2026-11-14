// Browser regression for #635, preserving the literal source URL and record ID.
// Reflow in Chromium is not equivalent to native zoom or a screen-reader test.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

const base = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const source = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 375, 390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 844 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', (error) => errors.push(error.message));
    const response = await page.goto(base.replace(/#.*$/, '') + '#/documents', { waitUntil: 'domcontentloaded' });
    assert(response?.ok(), `Lab HTTP status on ${width}px: ${response?.status()}`);
    await page.getByRole('heading', { name: 'Documentos, relatos e lacunas' }).waitFor();
    const occurrence = page.getByText('C197#1', { exact: true }).first();
    assert(await occurrence.isVisible(), `C197#1 must remain identifiable at ${width}px`);
    const paragraph = page.locator('p').filter({ hasText: 'NASA-TM-X-51205' }).first();
    const pdf = paragraph.getByRole('link', { name: 'PDF primário', exact: true });
    await pdf.waitFor();
    assert.equal(await pdf.getAttribute('href'), source, 'literal NASA citation URL must not be rewritten');
    assert.equal(await pdf.getAttribute('rel'), 'noopener noreferrer');
    assert(!(/\[PDF primário\]\(/.test(await paragraph.innerText())), 'Markdown must render as a native link');
    for (const locale of ['pt', 'en']) {
      if (locale === 'en') await page.getByRole('button', { name: 'English' }).click();
      const url = page.locator('p').filter({ hasText: 'NASA-TM-X-51205' }).first()
        .getByRole('link', { name: 'PDF primário', exact: true });
      assert.equal(await url.getAttribute('href'), source);
      const dimensions = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        scrollWidth: document.documentElement.scrollWidth,
      }));
      assert(dimensions.scrollWidth <= dimensions.viewport + 1,
        `horizontal overflow on ${width}px in ${locale}: ${JSON.stringify(dimensions)}`);
    }
    // At 200% text size, native form controls and documentary IDs must
    // remain inside narrow viewports. The default input min-content width
    // previously pushed a 375px viewport to 464 CSS pixels.
    if (width <= 390) {
      await page.addStyleTag({ content: 'html { font-size: 200% !important; }' });
      // The whole document, not only the input, must reflow at doubled text.
      // The published archive previously scrolled to 428px at viewport 320px
      // and 375px because its heading and long documentary strings were unbreakable.
      for (const locale of ['en', 'pt']) {
        if (locale === 'pt') {
          await page.getByRole('button', { name: 'Português (Brasil)' }).click();
          await page.getByRole('heading', { name: 'Documentos, relatos e lacunas' }).waitFor();
        }
        const dimensions = await page.evaluate(() => ({
          viewport: document.documentElement.clientWidth,
          scrollWidth: document.documentElement.scrollWidth,
        }));
        assert(dimensions.scrollWidth <= dimensions.viewport + 1,
          `documentary archive 200% text overflow at ${width}px in ${locale}: ${JSON.stringify(dimensions)}`);
        // A zero-overflow page can still squeeze each menu label into a
        // two-character column. Require usable widths for both labels.
        const chooser = page.locator('nav summary');
        const labels = await chooser.evaluate(el => ({
          width: el.getBoundingClientRect().width,
          spans: [...el.querySelectorAll(':scope > span')].map(node => node.getBoundingClientRect().width),
        }));
        assert(labels.spans.length === 2 && labels.spans.every(w => w >= labels.width * 0.6),
          `mobile chooser squeezed at 200% / ${width}px in ${locale}: ${JSON.stringify(labels)}`);
        await page.screenshot({ path: `${out}/documentary-archive-reflow-200pct-${locale}-${width}.png` });
      }
      const citation = page.locator('#source-citations-heading').locator('xpath=..');
      // The feed can legitimately be unavailable in dev: its runtime error state
      // must not block checking the always-rendered input. Check records when served.
      const selectors = ['label[for="citation-occurrence"]', '#citation-occurrence'];
      if (await citation.locator('dl').count()) selectors.push('dl dt', 'dl dd');
      for (const selector of selectors) {
        for (const element of await citation.locator(selector).all()) {
          const rect = await element.boundingBox();
          assert(rect && rect.x >= -1 && rect.x + rect.width <= width + 1,
            `documentary ${selector} clipped at 200% / ${width}px: ${JSON.stringify(rect)}`);
        }
      }
      await page.screenshot({ path: `${out}/documentary-archive-reflow-200pct-${width}.png` });
    }
    await page.screenshot({ path: `${out}/documentary-archive-${width}.png`, fullPage: true });
    assert.deepEqual(errors, [], `console page errors at ${width}px`);
    await page.close();
  }
} finally {
  await browser.close();
}

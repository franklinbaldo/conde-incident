// Browser-CI regression for Monte Carlo at 200% text, not native zoom.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';
const base = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 375, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 900 }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    try {
      const response = await page.goto(base.replace(/#.*$/, '') + '#/montecarlo', { waitUntil: 'domcontentloaded' });
      assert(response?.ok(), 'HTTP failed at Monte Carlo');
      await page.getByRole('heading', { name: /Simulação Monte Carlo/, level: 1 }).waitFor();
      await page.addStyleTag({ content: 'html { font-size: 200% !important; }' });
      for (const lang of ['pt', 'en']) {
        if (lang === 'en') {
          await page.getByRole('button', { name: 'English' }).click();
          await page.getByRole('heading', { name: /Monte Carlo Simulation/, level: 1 }).waitFor();
        }
        const selector = page.getByRole('combobox', {
          name: lang === 'pt' ? 'Número de trajetórias' : 'Number of trajectories',
        });
        await selector.waitFor();
        const rect = await selector.boundingBox();
        assert(rect && rect.width > 80 && rect.x >= -1 && rect.x + rect.width <= width + 1,
          'selector clipped ' + width + '/' + lang + ': ' + JSON.stringify(rect));
        const run = page.getByRole('button', { name: lang === 'pt' ? /Re-executar/ : /Run again/ });
        const runBox = await run.boundingBox();
        assert(runBox && runBox.x >= -1 && runBox.x + runBox.width <= width + 1,
          'run button clipped ' + width + '/' + lang + ': ' + JSON.stringify(runBox));
        const tableRegion = page.getByRole('region', {
          name: lang === 'pt' ? 'Tabela de incerteza da data de decaimento' : 'Decay date uncertainty table',
        });
        assert.equal(await tableRegion.getAttribute('tabindex'), '0',
          'overflowing table should be keyboard-reachable');
        const dims = await page.evaluate(() => ({
          scroll: document.documentElement.scrollWidth,
          viewport: document.documentElement.clientWidth,
        }));
        assert(dims.scroll <= dims.viewport + 1,
          'document-wide overflow ' + width + '/' + lang + ': ' + JSON.stringify(dims));
        await page.screenshot({ path: out + '/montecarlo-reflow-' + lang + '-' + width + '.png', fullPage: false });
      }
      assert.deepEqual(errors, [], 'uncaught Monte Carlo error at ' + width);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}


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
    const remoteMapRequests = [];
    page.on('pageerror', error => errors.push(error.message));
    // A quota-free SVG map must never silently fall back to a hosted tile/API SDK.
    // Google Fonts is not a map provider; matching is intentionally host-specific.
    page.on('request', request => {
      const host = new URL(request.url()).hostname.toLowerCase();
      if (/^(?:maps\.googleapis\.com|maps\.gstatic\.com|tile\.openstreetmap\.org|api\.mapbox\.com|api\.maptiler\.com)$/.test(host)) {
        remoteMapRequests.push(request.url());
      }
    });
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
        if (width === 320) {
          // Exercise real DOM state, not merely source-level aria attributes.
          const coastline = page.locator('g[data-layer="coastline"]');
          const grid = page.locator('g[data-layer="graticule"]');
          const coastToggle = page.getByRole('checkbox', {
            name: lang === 'pt' ? 'Mostrar litoral generalizado' : 'Show generalized coastline',
          });
          const gridToggle = page.getByRole('checkbox', {
            name: lang === 'pt' ? 'Mostrar grade geográfica' : 'Show geographic grid',
          });
          assert.equal(await coastline.count(), 1);
          await coastToggle.uncheck();
          assert.equal(await coastline.count(), 0, 'coastline persists when disabled');
          await coastToggle.check();
          assert.equal(await coastline.count(), 1);
          assert.equal(await grid.count(), 1);
          await gridToggle.uncheck();
          assert.equal(await grid.count(), 0, 'graticule persists when disabled');
          await gridToggle.check();
          assert.equal(await grid.count(), 1);

          const sisters = page.getByRole('checkbox', {
            name: lang === 'pt' ? 'Cenários 527/529' : '527/529 scenarios',
          });
          const connectors = page.getByRole('checkbox', {
            name: lang === 'pt' ? 'Conexões geométricas de cenários' : 'Scenario geometry connections',
          });
          await connectors.check();
          await sisters.uncheck();
          assert.equal(await page.locator('[data-layer="scenario-track"][data-satellite="527"]').count(), 0);
          assert.equal(await page.locator('[data-layer="scenario-track"][data-satellite="529"]').count(), 0);
          assert.equal(await page.locator('[data-layer="scenario-marker"][data-satellite="527"]').count(), 0);
          assert.equal(await page.locator('[data-layer="scenario-marker"][data-satellite="529"]').count(), 0);
          assert.equal(await page.locator('[data-layer="scenario-connections"]').count(), 0,
            'connections must not survive hidden 527/529 scenarios');
          await sisters.check();
          assert.equal(await page.locator('[data-layer="scenario-track"][data-satellite="527"]').count(), 1);
          assert.equal(await page.locator('[data-layer="scenario-track"][data-satellite="529"]').count(), 1);

          // Globe deliberately omits heuristic 2D rails: do not leave a
          // checked, operable switch claiming that invisible geometry is shown.
          const bounds = page.getByRole('checkbox', {
            name: lang === 'pt' ? 'Trilhas-limite hipotéticas' : 'Hypothetical envelope rails',
          });
          await bounds.check();
          await page.getByRole('button', { name: lang === 'pt' ? 'Globo 3D' : '3D globe' }).click();
          assert.equal(await bounds.isDisabled(), true);
          assert.equal(await bounds.isChecked(), false);
          assert(await page.getByText(lang === 'pt'
            ? 'As faixas hipotéticas só podem ser visualizadas no mapa 2D.'
            : 'Hypothetical envelope rails can only be displayed on the 2D map.').isVisible());
          await page.getByRole('button', { name: lang === 'pt' ? 'Mapa 2D' : '2D map' }).click();
          assert.equal(await bounds.isDisabled(), false);
          assert.equal(await bounds.isChecked(), true, '2D rail preference should be retained');
        }
        await page.screenshot({ path: `${out}/map-reflow-200pct-${lang}-${width}.png` });
      }
      assert.deepEqual(errors, [], `uncaught map error at ${width}px`);
      assert.deepEqual(remoteMapRequests, [], `remote map/tile provider requests at ${width}px`);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

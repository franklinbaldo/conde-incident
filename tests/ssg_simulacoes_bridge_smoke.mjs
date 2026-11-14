// Chromium checks the actual combined SSG + Vite artifact at its Pages prefix.
// This is not a physical-device, native 200% zoom, or screen-reader test.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';
import { mkdir } from 'node:fs/promises';

const origin = process.env.SSG_SEARCH_AUDIT_URL || 'http://127.0.0.1:4173/conde-incident/';
const routes = {
  summary: '/',
  map: '/mapa/',
  inverse: '/simulacoes/inverso/',
  triangulation: '/simulacoes/triangulacao/',
  sensitivity: '/simulacoes/sensibilidade/',
  montecarlo: '/simulacoes/montecarlo/',
  tles: '/simulacoes/tles/custodia/',
  documents: '/evidencias/arquivo/',
};
const prefix = '/conde-incident';
await mkdir('test-results/ui', { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 840 } });
    const exceptions = [];
    page.on('pageerror', error => exceptions.push(error.message));
    try {
      for (const [tab, context] of Object.entries(routes)) {
        const res = await page.goto(new URL('simulacoes/', origin).toString(), { waitUntil: 'domcontentloaded' });
        assert(res?.ok(), 'SSG simulations index did not load');
        const card = page.locator('.instrument-grid > li[data-lab-tab="' + tab + '"]');
        assert.equal(await card.count(), 1, 'missing or duplicated instrument card: ' + tab);
        const links = card.getByRole('link');
        assert.equal(await links.count(), 2, 'each card has exactly two destinations: ' + tab);
        assert.equal(await links.nth(0).getAttribute('href'), prefix + context);
        assert.equal(await links.nth(1).getAttribute('href'), prefix + '/lab/#/' + tab);
        if (tab === 'summary') await page.screenshot({ path: 'test-results/ui/ssg-simulacoes-' + width + '.png' });
        assert(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1),
          'SSG index overflows the ' + width + 'px viewport');
        for (const link of await links.all()) {
          const rect = await link.boundingBox();
          assert(rect && rect.height >= 44 && rect.x >= -1 && rect.x + rect.width <= width + 1,
            'instrument link is clipped or too small: ' + tab + ' at ' + width + 'px');
        }
        await links.nth(1).click();
        assert.equal(new URL(page.url()).hash, '#/' + tab);
        await page.getByRole('navigation', { name: 'Seções do laboratório' }).waitFor();
        await page.waitForFunction(() => document.title.includes('NORAD 528'));
        assert.equal(await page.locator('nav[aria-label="Seções do laboratório"] a[aria-current="page"][href="#/' + tab + '"]').count(), 2,
          'mobile and desktop navigation should identify the same active view');
        const backToContext = tab === 'summary'
          ? page.getByRole('link', { name: 'Voltar ao Caderno' })
          : page.getByRole('link', { name: /^Abrir no Caderno:/ });
        const contextHref = new URL(await backToContext.getAttribute('href'), page.url());
        assert.equal(contextHref.pathname, prefix + context);
        assert.equal(contextHref.origin, new URL(origin).origin,
          'return must stay inside the same deployed SSG + lab artifact');
        await backToContext.click();
        assert.equal(new URL(page.url()).pathname, prefix + context, 'SSG counterpart route: ' + tab);
        await page.locator('main#main').waitFor();
        await page.goBack({ waitUntil: 'domcontentloaded' });
        assert.equal(new URL(page.url()).hash, '#/' + tab, 'history must return to the same lab instrument');
        await page.goBack({ waitUntil: 'domcontentloaded' });
        assert.equal(new URL(page.url()).pathname, prefix + '/simulacoes/', 'history must restore SSG index');
      }
      assert.deepEqual(exceptions, [], 'JS exceptions in cross-architecture journey at ' + width + 'px');
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

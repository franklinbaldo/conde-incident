// Browser validation against the assembled SSG Pages artifact at the real path.
// Text 200% is a simulation, not native browser zoom or an assistive-tech test.
import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base = process.env.SSG_MOBILE_NAV_URL || 'http://127.0.0.1:4173/conde-incident/';
const routes = ['', 'stories/', 'evidencias/fontes/', 'evidencias/matriz/'];
const expected = ['','stories/','cronologia/','evidencias/','hipoteses/',
  'mapa/','simulacoes/','metodo/','lab/'].map(s => '/conde-incident/' + s);
const browser = await chromium.launch({ headless: true });
try {
  for (const route of routes) for (const [width, zoom] of [[320,1], [320,2], [375,2], [1440,1]]) {
    const page = await browser.newPage({ viewport: {width, height: 812}, javaScriptEnabled: false, bypassCSP: true });
    try {
      const url = new URL(route, base).href;
      // JavaScript is intentionally disabled. Playwright addStyleTag() never
      // resolves in this context, so modify only the test response HTML.
      if (zoom === 2) await page.route(url, async request => {
        const response = await request.fetch();
        const html = await response.text();
        assert.match(html, /<\/head>/i, 'SSG page is missing its head');
        await request.fulfill({response, body: html.replace(/<\/head>/i,
          '<style>html {font-size: 200%}</style></head>')});
      });
      const res = await page.goto(url, {waitUntil: 'domcontentloaded'});
      assert(res?.ok(), `HTML unavailable: ${route} ${res?.status()}`);
      const stats = await page.evaluate(() => ({
        width: document.documentElement.clientWidth,
        scroll: document.documentElement.scrollWidth,
        header: Math.round(document.querySelector('.masthead').getBoundingClientRect().height),
        heading: Math.round(document.querySelector('main h1').getBoundingClientRect().top),
      }));
      assert(stats.scroll <= stats.width + 1, `horizontal overflow ${route}: ${JSON.stringify(stats)}`);
      const desktop = page.locator('.desktop-navigation nav');
      const mobile = page.locator('details.mobile-navigation');
      const visible = width <= 720 ? mobile.locator('nav') : desktop;
      assert.equal(await desktop.locator('a').count(), 9);
      assert.equal(await mobile.locator('a').count(), 9);
      if (width <= 720) {
        assert(await mobile.isVisible() && !(await desktop.isVisible()), 'mobile disclosure not active');
        assert(stats.header <= 200, `mobile header too tall: ${route} ${width} ${zoom} ${stats.header}`);
        assert.equal(await mobile.getAttribute('open'), null);
        assert.equal(await visible.locator('a:visible').count(), 0, 'collapsed links must be hidden');
        await mobile.locator('summary').focus();
        await page.keyboard.press('Space');
        assert.equal(await mobile.getAttribute('open'), '', 'Space must open mobile menu');
        assert.deepEqual(await visible.locator('a').evaluateAll(a => a.map(x => x.getAttribute('href'))), expected);
        assert.equal(await visible.locator('a[aria-current]').count(), 1, 'active section missing');
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => document.activeElement?.getAttribute('href')), expected[0]);
        await mobile.locator('summary').focus();
        await page.keyboard.press('Enter');
        assert.equal(await mobile.getAttribute('open'), null, 'Enter must close mobile menu');
      } else {
        assert(await desktop.isVisible() && !(await mobile.isVisible()), 'desktop nav not active');
        assert.deepEqual(await desktop.locator('a').evaluateAll(a => a.map(x=>x.getAttribute('href'))), expected);
        assert.equal(await desktop.locator('a[aria-current]').count(), 1);
      }
      console.log('PASS SSG mobile nav', route || '/', width, zoom*100+'%', stats);
    } finally { await page.close(); }
  }
} finally { await browser.close(); }

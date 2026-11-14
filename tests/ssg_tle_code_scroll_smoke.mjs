// Chromium proof on the actual SSG+Vite Pages artifact, not a synthetic fixture.
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {mkdir} from 'node:fs/promises';
import {chromium} from 'playwright';

const base = process.env.UI_SSG_BASE || 'http://127.0.0.1:4173/conde-incident/';
const url = new URL('simulacoes/tles/custodia/', base).toString();
const literal = readFileSync('research/tle_custody/mirror_528_1963-10-27.tle', 'utf8').trimEnd().split('\n');
assert.equal(literal.length, 2);
assert(literal.every(line => line.length === 69), 'Pinned source must contain 69-column TLE lines');
await mkdir('test-results/ui', {recursive: true});

const browser = await chromium.launch({headless: true});
try {
  for (const width of [320, 375, 640, 1440]) {
    const page = await browser.newPage({viewport: {width, height: width < 1000 ? 812 : 900}});
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    try {
      const response = await page.goto(url, {waitUntil: 'domcontentloaded', timeout: 30000});
      assert.equal(response?.status(), 200, 'Published-prefix TLE custody URL must resolve');
      const pre = page.locator('main pre.tle-source-lines');
      assert.equal(await pre.count(), 1, 'Expected a single, labelled scroll region from real SSG output');
      assert.equal(await pre.getAttribute('tabindex'), '0', 'Scrollable source must be reachable by Tab');
      assert.equal(await pre.getAttribute('role'), 'region');
      assert.match(await pre.getAttribute('aria-label') || '', /TLE secundário NORAD 528/);
      assert.deepEqual((await pre.locator('code').textContent()).trimEnd().split('\n'), literal,
        'Visual fix must not wrap, replace or truncate either scientific source line');
      const dims = await pre.evaluate(el => ({
        root: document.documentElement.scrollWidth,
        right: el.getBoundingClientRect().right,
        left: el.getBoundingClientRect().left,
        client: el.clientWidth,
        scroll: el.scrollWidth,
        overflowX: getComputedStyle(el).overflowX,
      }));
      assert(dims.root <= width + 1, 'Horizontal document overflow at ' + width + ': ' + JSON.stringify(dims));
      assert(dims.left >= -1 && dims.right <= width + 1, 'Code region spills out of viewport: ' + JSON.stringify(dims));
      assert.equal(dims.overflowX, 'auto', 'Code region must manage its own overflow');
      if (width <= 640) {
        assert(dims.scroll > dims.client, 'Narrow viewport must preserve fixed-column lines in nested scroller');
        await page.keyboard.press('Tab'); // first interactive element is skip-to-content
        await page.keyboard.press('Enter');
        let reached = false;
        for (let i = 0; i < 85; i++) {
          await page.keyboard.press('Tab');
          if (await pre.evaluate(el => el === document.activeElement)) { reached = true; break; }
        }
        assert(reached, 'Code region is unreachable by sequential keyboard navigation at ' + width);
        const focus = await pre.evaluate(el => el.matches(':focus-visible'));
        assert(focus, 'No visible keyboard focus state on code region');
        const scrolled = await pre.evaluate(el => { el.scrollLeft = el.scrollWidth; return el.scrollLeft; });
        assert(scrolled > 0, 'Full 69-column source must remain accessible by horizontal scrolling');
      }
      assert.deepEqual(errors, [], 'No page JS errors permitted');
      if (width === 320 || width === 1440)
        await page.screenshot({path: 'test-results/ui/tle-custodia-' + width + '.png', fullPage: true});
      console.log('TLE mobile code PASS', width, dims.root, dims.client, dims.scroll);
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

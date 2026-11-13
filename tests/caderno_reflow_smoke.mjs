// Chromium regression against the actual SSG template navigation and site CSS.
// This is a LOCAL TEMPLATE test, not a claim about the deployed Pages experience.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';

const css = await fs.readFile('static/css/site.css', 'utf8');
const sources = ['templates/template.html', 'templates/page.html', 'templates/index.html', 'templates/post.html', 'templates/tera/base.html'];
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await fs.mkdir(out, { recursive: true });

const browser = await chromium.launch({ headless: true });
try {
  for (const path of sources) {
    const source = await fs.readFile(path, 'utf8');
    const header = source.match(/<header class="masthead">[\s\S]*?<\/header>/)?.[0];
    const skip = source.match(/<a\b[^>]*class="skip-link"[^>]*>[^<]+<\/a>/)?.[0];
    const main = source.match(/<main\b[^>]*>/)?.[0];
    assert(header && skip && main, `missing real header/skip-link/main markup: ${path}`);

    for (const width of [320, 375, 1440]) {
      const page = await browser.newPage({ viewport: { width, height: 800 }, reducedMotion: 'reduce' });
      try {
        await page.setContent(`<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>${skip}${header}${main}<h1>Caderno de histórias</h1><a href="#primeiro-link">Primeira fonte</a></main></body></html>`);
        await page.addStyleTag({ content: css });
        const before = await page.locator('.skip-link').boundingBox();
        assert(before && before.y < 0, `skip link must be visually tucked away before focus: ${path} ${width}`);

        const layout = await page.evaluate(() => ({
          viewport: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth,
          anchors: [...document.querySelectorAll('.masthead nav a')].map(a => ({
            width: a.clientWidth, scroll: a.scrollWidth, whiteSpace: getComputedStyle(a).whiteSpace,
            top: Math.round(a.getBoundingClientRect().top), href: a.getAttribute('href')
          }))
        }));
        assert(layout.scroll <= layout.viewport + 1, `horizontal overflow ${path} ${width}: ${JSON.stringify(layout)}`);
        assert.deepEqual(layout.anchors.map(a => a.href), [
          '/conde-incident/', '/conde-incident/stories/', '/conde-incident/cronologia/',
          '/conde-incident/evidencias/', '/conde-incident/hipoteses/',
          '/conde-incident/simulacoes/', '/conde-incident/metodo/', '/conde-incident/lab/'
        ], `all eight SSG navigation destinations must remain keyboard-accessible: ${path} ${width}`);
        assert(layout.anchors.every(a => a.whiteSpace === 'nowrap' && a.scroll <= a.width + 1),
          `broken navigation labels ${path} ${width}: ${JSON.stringify(layout)}`);
        if (width === 320) assert(new Set(layout.anchors.map(a => a.top)).size > 1,
          `nav should wrap into rows rather than squeeze labels: ${path}`);

        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => document.activeElement?.className), 'skip-link',
          `skip link should be the first tab stop: ${path} ${width}`);
        const focused = await page.locator('.skip-link').boundingBox();
        const focusStyle = await page.locator('.skip-link').evaluate(el => {
          const s = getComputedStyle(el);
          return { outline: s.outlineStyle, width: parseFloat(s.outlineWidth) };
        });
        assert(focused && focused.y >= 0 && focused.y < 100, `focused skip link offscreen: ${path} ${width}`);
        assert(focusStyle.outline !== 'none' && focusStyle.width >= 2,
          `skip link missing visible focus ring: ${path} ${width}`);
        await page.keyboard.press('Enter');
        const destination = await page.evaluate(() => ({
          tag: document.activeElement?.tagName,
          id: document.activeElement?.id,
          hash: location.hash,
        }));
        assert.deepEqual(destination, { tag: 'MAIN', id: 'main', hash: '#main' },
          `skip link must move actual keyboard focus to main: ${path} ${width}`);
        await page.keyboard.press('Tab');
        assert.equal(await page.evaluate(() => document.activeElement?.getAttribute('href')),
          '#primeiro-link', `next Tab must continue within main: ${path} ${width}`);
        await page.screenshot({ path: `${out}/caderno-${path.replace(/\W/g, '-')}-${width}.png` });
        console.log(`PASS: ${path}, ${width}px: nav reflow, skip-link focus target, next Tab and focus ring`);
      } finally { await page.close(); }
    }
  }
} finally { await browser.close(); }

// Chromium regression against the actual SSG template navigation and site CSS.
// This is a LOCAL TEMPLATE test, not a claim about the deployed Pages experience.
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';
import { chromium } from 'playwright';
import { archivePages } from '../scripts/ssg-documentary-archive.mjs';

const css = await fs.readFile('static/css/site.css', 'utf8');
const citations = JSON.parse(await fs.readFile('public/data/conde-source-citations.json', 'utf8'));
const ancestry = JSON.parse(await fs.readFile('public/data/conde-declared-dependence.json', 'utf8'));
const familySource = archivePages(citations, ancestry).get('familias/bluebook-derivative-catalogues/index.md');
assert(familySource, 'curated family page missing');
const familyTitle = JSON.parse(familySource.match(/^title: (.+)$/m)?.[1] || 'null');
assert.match(familyTitle, /BLUEBOOK_DERIVATIVE_CATALOGUES/);
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

    for (const [width, zoom] of [[320, 1], [320, 2], [375, 1], [375, 2], [1440, 1]]) {
      const page = await browser.newPage({ viewport: { width, height: 800 }, reducedMotion: 'reduce' });
      try {
        await page.setContent(`<!doctype html><html lang="pt-BR"><head><meta name="viewport" content="width=device-width,initial-scale=1"></head><body>${skip}${header}${main}<h1>${familyTitle}</h1><a href="#primeiro-link">Primeira fonte</a></main></body></html>`);
        await page.addStyleTag({ content: css });
        if (zoom === 2) await page.addStyleTag({ content: 'html{font-size:200%}' });
        const before = await page.locator('.skip-link').boundingBox();
        assert(before && before.y < 0, `skip link must be visually tucked away before focus: ${path} ${width}`);

        const layout = await page.evaluate(() => ({
          heading: {left: document.querySelector('h1').getBoundingClientRect().left, right: document.querySelector('h1').getBoundingClientRect().right, scroll: document.querySelector('h1').scrollWidth, width: document.querySelector('h1').clientWidth},
          viewport: document.documentElement.clientWidth,
          scroll: document.documentElement.scrollWidth,
          anchors: [...document.querySelectorAll('.masthead nav a')].filter(a => a.getClientRects().length > 0).map(a => ({
            width: a.clientWidth, scroll: a.scrollWidth, whiteSpace: getComputedStyle(a).whiteSpace,
            top: Math.round(a.getBoundingClientRect().top), href: a.getAttribute('href')
          }))
        }));
        assert(layout.scroll <= layout.viewport + 1, `horizontal overflow ${path} ${width}: ${JSON.stringify(layout)}`);
        assert(layout.heading.scroll <= layout.heading.width + 1,
          `long real documentary family title overflows at ${width}px: ${JSON.stringify(layout.heading)}`);
        // Some authored Page variants expose an additional static Map route.
        // Verify the eight shared destinations in order, without rejecting a
        // legitimate ninth destination or silently dropping its label.
        const hrefs = [...await page.locator('.masthead .desktop-navigation nav a').evaluateAll(links => links.map(a => a.getAttribute('href')))];
        const mapHref = '/conde-incident/mapa/';
        if (hrefs.includes(mapHref)) {
          assert.equal(hrefs.indexOf(mapHref), 5,
            `the optional Map link must follow hypotheses: ${path} ${width}`);
        }
        assert.deepEqual(hrefs.filter(href => href !== mapHref), [
          '/conde-incident/', '/conde-incident/stories/', '/conde-incident/cronologia/',
          '/conde-incident/evidencias/', '/conde-incident/hipoteses/',
          '/conde-incident/simulacoes/', '/conde-incident/metodo/', '/conde-incident/lab/'
        ], `all eight core SSG destinations must remain keyboard-accessible: ${path} ${width}`);
        assert(layout.anchors.every(a => a.scroll <= a.width + 1),
          `broken navigation labels ${path} ${width}: ${JSON.stringify(layout)}`);

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
        const mobile = await page.locator('details.mobile-navigation').isVisible();
        assert.equal(mobile, width <= 720, `wrong responsive navigation: ${path} ${width}`);
        if (mobile) {
          assert.equal(await page.locator('details.mobile-navigation').getAttribute('open'), null,
            'Mobile navigation must start closed');
          const headerHeight = await page.locator('header.masthead').evaluate(el => el.getBoundingClientRect().height);
          assert(headerHeight <= 200, `mobile header obscures first content: ${path} ${width} ${zoom} ${headerHeight}`);
          assert.equal(layout.anchors.length, 0, `closed menu has exposed nav links: ${path} ${width}`);
          await page.locator('details.mobile-navigation summary').focus();
          await page.keyboard.press('Enter');
          assert.equal(await page.locator('details.mobile-navigation').getAttribute('open'), '',
            'Enter must open native mobile menu');
          assert.equal(await page.locator('details.mobile-navigation nav a').count(), 9);
          await page.keyboard.press('Tab');
          assert.equal(await page.evaluate(() => document.activeElement?.getAttribute('href')), '/conde-incident/',
            'Tab from summary must reach first destination');
          await page.locator('details.mobile-navigation summary').focus();
          await page.keyboard.press('Enter');
          assert.equal(await page.locator('details.mobile-navigation').getAttribute('open'), null,
            'Enter must close the menu');
        } else {
          assert.equal(layout.anchors.length, 9, `desktop must expose all nine links: ${path}`);
        }

        await page.screenshot({ path: `${out}/caderno-${path.replace(/\W/g, '-')}-${width}-${zoom * 100}pct.png` });
        console.log(`PASS: ${path}, ${width}px: responsive nav disclosure, heading reflow, skip-link focus and keyboard order`);
      } finally { await page.close(); }
    }
  }
} finally { await browser.close(); }

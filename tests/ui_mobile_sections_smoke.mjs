// Chromium: native mobile section disclosure, keyboard, hash and reflow.
// Runs against the actual Vite app, not a mocked component.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await mkdir(out, { recursive: true });

// Small PT/EN labels require >=4.5:1 WCAG AA; measure rendered Tailwind v4
// oklch colors through a canvas rather than approximating RGB from CSS text.
async function assertLanguageContrast(page, name, width) {
  const sample = await page.getByRole('button', { name }).evaluate(el => {
    const style = getComputedStyle(el);
    const canvas = document.createElement('canvas');
    canvas.width = canvas.height = 1;
    const ctx = canvas.getContext('2d', { willReadFrequently: true });
    if (!ctx) throw new Error('Canvas unavailable for WCAG measurement');
    const rgb = css => {
      ctx.clearRect(0, 0, 1, 1);
      ctx.fillStyle = css;
      ctx.fillRect(0, 0, 1, 1);
      return [...ctx.getImageData(0, 0, 1, 1).data].slice(0, 3);
    };
    const luminance = css => rgb(css).map(v => v / 255).map(v =>
      v <= 0.04045 ? v / 12.92 : ((v + 0.055) / 1.055) ** 2.4
    ).reduce((sum, v, i) => sum + v * [0.2126, 0.7152, 0.0722][i], 0);
    const foreground = luminance(style.color);
    const background = luminance(style.backgroundColor);
    return (Math.max(foreground, background) + 0.05) /
      (Math.min(foreground, background) + 0.05);
  });
  assert(sample >= 4.5,
    \`WCAG AA contrast failed for \${name} at \${width}px: \${sample.toFixed(2)}:1\`);
}

const browser = await chromium.launch({ headless: true });
try {
  // Deep links name the current section in the closed mobile menu.
  // Keyboard can reveal all eight destinations and preserve Back/Forward.
  for (const width of [320, 375, 640]) {
    const page = await browser.newPage({ viewport: { width, height: 800 } });
    try {
      await page.goto(origin + '#/documents', { waitUntil: 'domcontentloaded' });
      const nav = page.getByRole('navigation', { name: 'Seções do laboratório' });
      const chooser = nav.locator('summary');
      await chooser.waitFor();
      await assertLanguageContrast(page, 'Português (Brasil)', width);
      await page.waitForFunction(() => document.title.startsWith('Arquivo e proveniência |'));
      assert.match(await page.title(), /NORAD 528 · Caso Conde \(1963\)$/);
      assert.match(await chooser.innerText(), /Arquivo e proveniência/);
      await chooser.focus();
      await page.keyboard.press('Enter');
      assert.notEqual(await nav.locator('details').getAttribute('open'), null);
      assert.equal(await nav.locator('[data-mobile-tabs] a').count(), 8);
      const active = nav.locator('[data-mobile-tabs] [aria-current="page"]');
      assert.match(await active.innerText(), /Arquivo e proveniência/);
      // Regression: a literal escaped JSX interpolation was shipped in className.
      // All eight mobile links then lost their active/inactive color hierarchy,
      // despite correct aria-current and correct navigation behavior.
      const activeClass = await active.getAttribute('class');
      assert(!activeClass?.includes('${'), 'escaped JSX expression leaked into the published CSS class');
      assert.match(activeClass || '', /\bbg-zinc-800\b/);
      assert.match(activeClass || '', /\btext-cyan-300\b/);
      const inactive = nav.locator('[data-mobile-tabs] a:not([aria-current])').first();
      const inactiveClass = await inactive.getAttribute('class');
      assert.match(inactiveClass || '', /\bbg-zinc-950\b/);
      assert.notEqual(
        await active.evaluate(el => getComputedStyle(el).backgroundColor),
        await inactive.evaluate(el => getComputedStyle(el).backgroundColor),
        'the active mobile destination must have a distinguishable rendered background');
      for (const link of await nav.locator('[data-mobile-tabs] a').all()) {
        const rect = await link.boundingBox();
        assert(rect && rect.height >= 44 && rect.x >= -1 && rect.x + rect.width <= width + 1,
          'section option clipped or smaller than 44px at ' + width + ': ' + JSON.stringify(rect));
      }
      await nav.getByRole('link', { name: /Rastreamento & Mapa/ }).click();
      assert.equal(new URL(page.url()).hash, '#/map');
      await page.waitForFunction(() => document.title.startsWith('Rastreamento & Mapa |'));
      assert.equal(await nav.locator('details').getAttribute('open'), null);
      await page.waitForFunction(() => document.querySelector('nav summary')?.textContent?.includes('Rastreamento & Mapa'));
      assert.match(await chooser.innerText(), /Rastreamento & Mapa/);
      assert(await chooser.evaluate(el => document.activeElement === el),
        'closing mobile section list must preserve keyboard focus');
      await page.goBack();
      await page.waitForFunction(() => document.querySelector('nav summary')?.textContent?.includes('Arquivo e proveniência'));
      await page.waitForFunction(() => document.title.startsWith('Arquivo e proveniência |'));
      assert.match(await chooser.innerText(), /Arquivo e proveniência/);
      if (width === 640) {
        await page.setViewportSize({ width: 320, height: 800 });
        assert.match(await chooser.innerText(), /Arquivo e proveniência/);
      }
      if (width === 320) {
        await page.getByRole('button', { name: 'English' }).click();
        await page.waitForTimeout(250); // wait for transition-colors to settle
        await assertLanguageContrast(page, 'English', width);
        await page.waitForFunction(() => document.title.startsWith('Archive & provenance |'));
        assert.match(await page.title(), /Conde case \(1963\)$/);
        await page.getByRole('button', { name: 'Português (Brasil)' }).click();
        await page.waitForFunction(() => document.title.startsWith('Arquivo e proveniência |'));
      }
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= window.innerWidth + 1), true);
      await page.screenshot({ path: out + '/deep-link-documents-' + width + '.png' });
    } finally {
      await page.close();
    }
  }
 } finally {
  await browser.close();
}

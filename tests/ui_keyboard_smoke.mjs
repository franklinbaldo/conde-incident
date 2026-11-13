// Browser-level keyboard, landmark, language and narrow-viewport smoke.
// Run against the local PR HEAD. Screenshots are evidence, not visual approval.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
const findings = [];
try {
  for (const viewport of [{ name: 'desktop', width: 1440, height: 900 }, { name: 'mobile', width: 375, height: 812 }, { name: 'mobile-320', width: 320, height: 700 }, { name: 'reflow-640-css-px', width: 640, height: 720 }]) {
    const page = await browser.newPage({ viewport: { width: viewport.width, height: viewport.height }, reducedMotion: 'reduce' });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    const response = await page.goto(origin, { waitUntil: 'domcontentloaded', timeout: 30000 });
    assert(response?.ok(), `initial page HTTP ${response?.status()}`);
    await page.getByRole('heading', { level: 1 }).first().waitFor({ timeout: 20000 });
    assert.equal(await page.getByRole('heading', { level: 1 }).count(), 1,
      'SPA must expose exactly one route-specific H1, not a duplicate static heading');
    // In a 1280 px desktop browser at 200% zoom, layout can approach 640 CSS px.
    // This emulates the reflow width, NOT native browser zoom or screen-reader QA.
    const headerLayout = await page.locator('header').first().evaluate(el => ({
      position: getComputedStyle(el).position,
      height: el.getBoundingClientRect().height,
      viewportHeight: window.innerHeight,
    }));
    assert.equal(headerLayout.position, viewport.width < 768 ? 'static' : 'sticky',
      'Lab header must not cover reading content at narrow/reflow widths: ' + JSON.stringify(headerLayout));
    assert(headerLayout.height < headerLayout.viewportHeight * 0.75,
      'Lab header takes over too much of the available height: ' + JSON.stringify(headerLayout));
    // The laboratory is a separate SPA: users need a visible way back to the
    // published editorial Caderno, including on the narrowest mobile layout.
    const backToCaderno = page.getByRole('link', { name: 'Voltar ao Caderno' });
    assert.equal(await backToCaderno.count(), 1, 'missing accessible return to Caderno');
    assert.equal(await backToCaderno.getAttribute('href'),
      'https://franklinbaldo.github.io/conde-incident/');
    const backRect = await backToCaderno.boundingBox();
    assert(backRect && backRect.x >= 0 && backRect.x + backRect.width <= viewport.width + 1,
      'Caderno return link is clipped off screen at ' + viewport.name + ': ' + JSON.stringify(backRect));
    const before = new URL(page.url()).hash;
    await page.keyboard.press('Tab');
    const first = await page.evaluate(() => ({
      text: document.activeElement?.textContent?.trim(),
      tag: document.activeElement?.tagName,
      visible: !!document.activeElement?.getClientRects().length,
    }));
    assert.equal(first.tag, 'A', 'first tab stop should be native skip link');
    assert.match(first.text || '', /Pular para o conteúdo/);
    assert(first.visible, 'skip link should be visible when keyboard-focused');
    await page.keyboard.press('Enter');
    const focused = await page.evaluate(() => ({
      tag: document.activeElement?.tagName,
      id: document.activeElement?.id,
      hash: window.location.hash,
    }));
    assert.equal(focused.tag, 'MAIN');
    assert.equal(focused.id, 'main-content');
    assert.equal(focused.hash, before, 'skip link must not replace the hash-router route');
    await page.getByRole('navigation', { name: 'Seções do laboratório' })
      .getByRole('link', { name: /Rastreamento & Mapa/ }).click();
    assert.equal(new URL(page.url()).hash, '#/map');
    // Hash changes synchronously; React state and aria-current update on a later tick.
    await page.waitForFunction(() => document.querySelector('nav a[aria-current="page"]')?.textContent?.includes('Rastreamento & Mapa'));
    const current = await page.getByRole('navigation', { name: 'Seções do laboratório' })
      .locator('[aria-current="page"]').textContent();
    assert.match(current || '', /Rastreamento & Mapa/);
    // Real DOM check of independent, keyboard-operable context layers.
    const mapSvg = page.getByRole('img', { name: /Mapa orbital esquemático/ });
    await mapSvg.waitFor();
    const coast = page.getByRole('checkbox', { name: 'Mostrar litoral generalizado' });
    const grid = page.getByRole('checkbox', { name: 'Mostrar grade geográfica' });
    assert.equal(await mapSvg.locator('[data-layer="coastline"]').count(), 1);
    assert.equal(await mapSvg.locator('[data-layer="graticule"]').count(), 1);
    await coast.uncheck();
    assert.equal(await mapSvg.locator('[data-layer="coastline"]').count(), 0);
    assert.equal(await mapSvg.locator('[data-layer="graticule"]').count(), 1,
      'hiding coastlines must leave the graticule visible');
    await grid.uncheck();
    assert.equal(await mapSvg.locator('[data-layer="graticule"]').count(), 0);
    await coast.check();
    await grid.check();
    assert.equal(await mapSvg.locator('[data-layer="coastline"]').count(), 1);
    assert.equal(await mapSvg.locator('[data-layer="graticule"]').count(), 1);
    assert.equal(await mapSvg.locator('rect[fill="#fb7185"]').count(), 1,
      'Conde must remain a square reference marker, not an impact circle');

    // Scenario permalink must survive a reload and browser Back/Forward, without
    // claiming the timestamp is a historical observation.
    const dateInput = page.locator('input[type="date"]');
    await dateInput.fill('1963-10-28');
    const link = page.getByRole('link', { name: /Link para este instante do cenário/ });
    const href = await link.getAttribute('href');
    assert.match(href || '', /^#\/map\?at=1963-10-28T12%3A00%3A00\.000Z$/);
    await link.click();
    assert.equal(new URL(page.url()).hash, href);
    await page.reload({ waitUntil: 'domcontentloaded' });
    await page.getByRole('heading', { name: 'Mapa orbital exploratório' }).waitFor();
    assert.equal(await page.locator('input[type="date"]').inputValue(), '1963-10-28');
    await page.goBack({ waitUntil: 'domcontentloaded' });
    await page.getByRole('heading', { name: 'Mapa orbital exploratório' }).waitFor();
    await page.goForward({ waitUntil: 'domcontentloaded' });
    await page.getByRole('heading', { name: 'Mapa orbital exploratório' }).waitFor();
    assert.equal(await page.locator('input[type="date"]').inputValue(), '1963-10-28');

    await page.getByRole('button', { name: 'English' }).click();
    assert.equal(await page.locator('html').getAttribute('lang'), 'en');
    assert.equal(await page.getByRole('link', { name: 'Back to the Notebook' }).count(), 1,
      'editorial return link must follow the selected language');
    assert.equal(await page.getByRole('link', { name: 'Skip to main content' }).count(), 1);
    // Switching locale must also translate badges, export controls and footer,
    // not only the tab headings or the root html[lang] attribute.
    const englishNav = page.getByRole('navigation', { name: 'Laboratory sections' });
    for (const badge of ['Sources', 'Synthetic', 'Syntax ≠ origin', 'Documents']) {
      assert.equal(await englishNav.getByText(badge, { exact: true }).count(), 1,
        `untranslated badge in English UI: ${badge}`);
    }
    assert.equal(await englishNav.getByText('Fontes', { exact: true }).count(), 0);
    assert.equal(await page.getByRole('button', { name: 'Python Script' }).first()
      .getAttribute('title'), 'Export reproducible Python code');
    assert.equal(await page.getByRole('button', { name: 'Export Python' }).count(), 1);
    assert.equal(await page.getByText('Models: SGP4, WGS84, J2, Solar-Min Thermosphere 1963', { exact: true }).count(), 1);
    assert.equal(await page.getByText('NRO mission 7153 (Thor-Agena D / OPS 0180)', { exact: true }).count(), 1);
    await page.getByRole('navigation', { name: 'Laboratory sections' })
      .getByRole('link', { name: /Summary & limits/ }).click();
    const horizontal = await page.evaluate(() => ({
      viewport: document.documentElement.clientWidth,
      document: document.documentElement.scrollWidth,
    }));
    assert(horizontal.document <= horizontal.viewport + 1,
      `body overflow on ${viewport.name}: ${JSON.stringify(horizontal)}`);
    await page.screenshot({ path: `${out}/${viewport.name}-summary.png`, fullPage: true });

    // Verify modal name, focus entry/loop, Escape dismissal and trigger focus restoration.
    const exportTrigger = page.getByRole('button', { name: 'Python Script' }).first();
    await exportTrigger.click();
    const dialog = page.getByRole('dialog', { name: 'norad528_reconstruction.py' });
    await dialog.waitFor();
    // At mobile/reflow widths, all three modal actions must remain reachable.
    // A wide filename and a non-wrapping toolbar previously pushed close
    // and download beyond the visible dialog, even though keyboard focus worked.
    const mobileLayout = await dialog.evaluate(node => {
      const header = node.children[0];
      const instructions = node.children[1];
      const rect = node.getBoundingClientRect();
      return {
        viewport: window.innerWidth,
        dialog: { left: rect.left, right: rect.right },
        header: { scroll: header.scrollWidth, client: header.clientWidth },
        instructions: { scroll: instructions.scrollWidth, client: instructions.clientWidth },
        controls: Array.from(node.querySelectorAll('button')).map(button => {
          const box = button.getBoundingClientRect();
          return { left: box.left, right: box.right, label: button.getAttribute('aria-label') || button.textContent?.trim() };
        }),
      };
    });
    assert(mobileLayout.header.scroll <= mobileLayout.header.client + 1,
      'export toolbar overflows at ' + viewport.name + ': ' + JSON.stringify(mobileLayout));
    assert(mobileLayout.instructions.scroll <= mobileLayout.instructions.client + 1,
      'export instructions overflow at ' + viewport.name + ': ' + JSON.stringify(mobileLayout));
    assert.equal(mobileLayout.controls.length, 3, 'expected copy, download and close actions');
    for (const control of mobileLayout.controls) {
      assert(control.left >= Math.max(0, mobileLayout.dialog.left) - 1 &&
        control.right <= Math.min(mobileLayout.viewport, mobileLayout.dialog.right) + 1,
      'export action clipped at ' + viewport.name + ': ' + JSON.stringify(mobileLayout));
    }
    const close = dialog.getByRole('button', { name: 'Close export dialog' });
    const copy = dialog.getByRole('button', { name: 'Copy code' });
    assert(await close.evaluate(element => document.activeElement === element),
      'opening the export dialog must focus its close control');
    await page.keyboard.press('Tab');
    assert(await copy.evaluate(element => document.activeElement === element),
      'Tab from last control must wrap to first control');
    await page.keyboard.press('Shift+Tab');
    assert(await close.evaluate(element => document.activeElement === element),
      'Shift+Tab from first control must wrap to last control');
    await page.screenshot({ path: `${out}/${viewport.name}-python-dialog.png` });
    await page.keyboard.press('Escape');
    await dialog.waitFor({ state: 'hidden' });
    assert(await exportTrigger.evaluate(element => document.activeElement === element),
      'Escape must close export dialog and restore trigger focus');

    // Check computed contrast in the browser, not just source CSS or a fixture.
    // These small labels distinguish model results and must meet WCAG AA 4.5:1.
    await page.getByRole('navigation', { name: 'Laboratory sections' })
      .getByRole('link', { name: /Inverse scenarios/ }).click();
    await page.getByRole('heading', { name: /Inverse Test:/ }).waitFor();
    const inverseLabel = page.getByText('Tempo do cenário UTC:', { exact: true });
    await inverseLabel.waitFor();
    const samples = [
      await inverseLabel.evaluate(el => ({
        fg: getComputedStyle(el).color, bg: getComputedStyle(el.parentElement).backgroundColor,
        fontSize: getComputedStyle(el).fontSize,
      })),
      await page.locator('footer').evaluate(el => ({
        fg: getComputedStyle(el).color, bg: getComputedStyle(el).backgroundColor,
        fontSize: getComputedStyle(el).fontSize,
      })),
    ];
    // Tailwind v4 resolves these classes to oklch() in Chromium. Convert actual
    // rendered colors through a 1px sRGB canvas rather than parsing CSS strings
    // as if every getComputedStyle(color) returned rgb().
    const sampleRgb = await page.evaluate(samples => {
      const canvas = document.createElement('canvas');
      canvas.width = canvas.height = 1;
      const ctx = canvas.getContext('2d', { willReadFrequently: true });
      if (!ctx) throw new Error('Canvas unavailable for color conversion');
      return samples.map(sample => [sample.fg, sample.bg].map(color => {
        ctx.clearRect(0, 0, 1, 1);
        ctx.fillStyle = color;
        ctx.fillRect(0, 0, 1, 1);
        return Array.from(ctx.getImageData(0, 0, 1, 1).data).slice(0, 3);
      }));
    }, samples);
    const luminance = rgb => rgb.map(n => n / 255).map(n =>
      n <= 0.04045 ? n / 12.92 : ((n + 0.055) / 1.055) ** 2.4
    ).reduce((total, n, i) => total + n * [0.2126, 0.7152, 0.0722][i], 0);
    for (const [i, sample] of samples.entries()) {
      const a = luminance(sampleRgb[i][0]), b = luminance(sampleRgb[i][1]);
      const ratio = (Math.max(a, b) + 0.05) / (Math.min(a, b) + 0.05);
      assert(ratio >= 4.5, 'WCAG AA small-text contrast failure in ' +
        (i ? 'footer' : 'inverse scenario label') + ': ' + ratio.toFixed(2) +
        ':1; ' + JSON.stringify(sample));
    }
    await page.screenshot({ path: out + '/' + viewport.name + '-inverse-contrast.png', fullPage: true });

    assert.equal(errors.length, 0, `uncaught page errors: ${errors.join('; ')}`);
    findings.push({ viewport: viewport.name, skip_target: focused.id, hash_preserved: true, nav_hash: '#/map', html_lang: 'en', overflow_px: horizontal.document - horizontal.viewport });
    await page.close();
  }
  // Verify the real HTML entrypoint with scripts disabled. This is a browser
  // fallback test, not a screen-reader evaluation or native 200% zoom test.
  for (const viewport of [
    { name: 'desktop', width: 1440, height: 900 },
    { name: 'mobile', width: 375, height: 812 },
  ]) {
    const context = await browser.newContext({
      javaScriptEnabled: false,
      viewport: { width: viewport.width, height: viewport.height },
    });
    try {
      const page = await context.newPage();
      const response = await page.goto(origin, { waitUntil: 'domcontentloaded' });
      assert(response?.ok(), 'no-script entrypoint failed to load');
      await page.getByRole('heading', {
        level: 1,
        name: 'Laboratório indisponível sem JavaScript',
      }).waitFor();
      assert.equal(await page.getByRole('main').count(), 1,
        'no-script visitor needs a main landmark');
      assert.equal(await page.getByRole('heading', { level: 1 }).count(), 1,
        'no-script entrypoint should have exactly one H1');
      const notebook = page.getByRole('link', { name: 'Ir ao Caderno' });
      const evidence = page.getByRole('link', { name: 'Consultar evidências' });
      assert.equal(await notebook.getAttribute('href'), '/conde-incident/');
      assert.equal(await evidence.getAttribute('href'), '/conde-incident/evidencias/');
      assert.equal(await page.locator('#root').innerHTML(), '',
        'React must not be required to render the no-script fallback');
      const horizontal = await page.evaluate(() => ({
        viewport: document.documentElement.clientWidth,
        document: document.documentElement.scrollWidth,
      }));
      assert(horizontal.document <= horizontal.viewport + 1,
        'no-script fallback overflows at ' + viewport.name);
      await page.screenshot({ path: out + '/' + viewport.name + '-noscript.png', fullPage: true });
      findings.push({ viewport: viewport.name, javascript: false, fallback: 'PASS' });
    } finally {
      await context.close();
    }
  }
  await fs.writeFile(`${out}/findings.json`, JSON.stringify({ origin, findings }, null, 2) + '\n');
  console.log(JSON.stringify({ result: 'PASS', findings }, null, 2));
} finally {
  await browser.close();
}

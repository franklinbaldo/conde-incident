import assert from 'node:assert/strict';
import { chromium } from 'playwright';

const base = process.env.SSG_SEARCH_AUDIT_URL || 'http://127.0.0.1:4173/conde-incident/';
const browser = await chromium.launch({ headless: true });
const makeLine = (n, id) => {
  const chars = (n + ' ' + String(id).padStart(5, '0')).padEnd(68, ' ');
  const digit = [...chars].reduce((s, c) => s + (/\d/.test(c) ? Number(c) : c === '-' ? 1 : 0), 0) % 10;
  return chars + digit;
};
try {
  for (const width of [320, 390, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 820 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    try {
      const response = await page.goto(new URL('simulacoes/tles/', base).toString(), { waitUntil: 'networkidle' });
      assert(response?.ok(), 'SSG TLE page HTTP failure');
      await page.locator('#ssg-tle-audit').waitFor({ state: 'visible' });
      // Simulate a real clipboard payload (including Windows CRLF and a final
      // terminator) while retaining every character inside each TLE line.
      await page.getByLabel('Linha 1').focus();
      await page.evaluate(text => {
        const clipboard = new DataTransfer();
        clipboard.setData('text/plain', text);
        const event = new ClipboardEvent('paste', { bubbles: true, cancelable: true, clipboardData: clipboard });
        document.getElementById('ssg-tle-line1').dispatchEvent(event);
        if (!event.defaultPrevented) throw new Error('paired paste was not handled');
      }, makeLine(1, 528) + '\r\n' + makeLine(2, 528) + '\r\n');
      assert.equal(await page.getByLabel('Linha 1').inputValue(), makeLine(1, 528));
      assert.equal(await page.getByLabel('Linha 2').inputValue(), makeLine(2, 528));
      assert.equal(await page.evaluate(() => document.activeElement.id), 'ssg-tle-line2');
      // Three-line files include an optional untrusted name line. It is shown
      // as text only, and cleared when the actual orbital bytes change.
      await page.getByLabel('Linha 1').focus();
      await page.evaluate(text => {
        const clipboard = new DataTransfer();
        clipboard.setData('text/plain', text);
        const event = new ClipboardEvent('paste', {bubbles: true, cancelable: true, clipboardData: clipboard});
        document.getElementById('ssg-tle-line1').dispatchEvent(event);
        if (!event.defaultPrevented) throw new Error('three-line paste was not handled');
      }, '0 <img src=x onerror=alert(1)>\r\n' + makeLine(1, 528) + '\r\n' + makeLine(2, 528) + '\r\n');
      assert.equal(await page.getByLabel('Linha 1').inputValue(), makeLine(1, 528));
      assert.equal(await page.getByLabel('Linha 2').inputValue(), makeLine(2, 528));
      assert.match(await page.locator('#ssg-tle-import-note').innerText(), /não autenticado/);
      assert.equal(await page.locator('#ssg-tle-import-note img').count(), 0, 'untrusted title must be text, not HTML');
      const button = page.getByRole('button', { name: 'Verificar duas linhas' });
      const box = await button.boundingBox();
      assert(box && box.height >= 44, 'touch target below 44 CSS px');
      await button.click();
      assert.match(await page.locator('#ssg-tle-results').innerText(), /NÃO autentica os dados/);
      assert.equal(await page.evaluate(() => document.activeElement.id), 'ssg-tle-results');
      assert.equal(await page.getByLabel('Linha 1').getAttribute('aria-invalid'), null);
      assert.equal(await page.getByLabel('Linha 2').getAttribute('aria-invalid'), null);
      // Edits invalidate the old success rather than leaving a stale PASS
      // visible to keyboard and screen-reader users.
      await page.getByLabel('Linha 2').fill(makeLine(2, 527));
      assert.equal(await page.locator('#ssg-tle-results').innerText(), '');
      assert.equal(await page.locator('#ssg-tle-import-note').isVisible(), false,
        'editing must remove stale copied-name attribution');
      assert.equal(await page.getByLabel('Linha 2').getAttribute('aria-invalid'), null,
        'editing removes stale invalid state');
      await button.click();
      assert.match(await page.locator('#ssg-tle-results').innerText(), /não passaram/);
      assert.equal(await page.getByLabel('Linha 1').getAttribute('aria-invalid'), null);
      assert.equal(await page.getByLabel('Linha 2').getAttribute('aria-invalid'), 'true');
      assert.match(await page.getByLabel('Linha 2').getAttribute('aria-describedby') || '',
        /ssg-tle-result-line2/);
      assert.match(await page.locator('#ssg-tle-result-line2').innerText(), /Inconsistente/);
      await page.getByLabel('Linha 2').fill(makeLine(2, 528));
      assert.equal(await page.getByLabel('Linha 2').getAttribute('aria-invalid'), null);
      assert.equal(await page.getByLabel('Linha 2').getAttribute('aria-describedby'), 'ssg-tle-instructions');
      assert.equal(await page.locator('#ssg-tle-results').innerText(), '');
      assert.equal(await page.evaluate(() => document.documentElement.scrollWidth <= innerWidth + 1), true, 'horizontal overflow');
      assert.deepEqual(errors, [], 'runtime exceptions');
    } finally { await page.close(); }
  }
  const context = await browser.newContext({ javaScriptEnabled: false });
  try {
    const page = await context.newPage();
    await page.goto(new URL('simulacoes/tles/', base).toString(), { waitUntil: 'domcontentloaded' });
    assert.equal(await page.locator('#ssg-tle-audit').isVisible(), false);
    assert.equal(await page.getByRole('link', { name: /ficha estática de custódia/i }).count(), 1);
  } finally { await context.close(); }
} finally { await browser.close(); }

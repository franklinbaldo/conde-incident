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
      await page.getByLabel('Linha 1').fill(makeLine(1, 528));
      await page.getByLabel('Linha 2').fill(makeLine(2, 528));
      const button = page.getByRole('button', { name: 'Verificar duas linhas' });
      const box = await button.boundingBox();
      assert(box && box.height >= 44, 'touch target below 44 CSS px');
      await button.click();
      assert.match(await page.locator('#ssg-tle-results').innerText(), /NÃO autentica os dados/);
      assert.equal(await page.evaluate(() => document.activeElement.id), 'ssg-tle-results');
      await page.getByLabel('Linha 2').fill(makeLine(2, 527));
      await button.click();
      assert.match(await page.locator('#ssg-tle-results').innerText(), /não passaram/);
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

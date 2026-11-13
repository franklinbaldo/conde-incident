// Network-failure regression for a lazy laboratory instrument.
// Runs in Chromium against the PR HEAD's actual Vite app, not a mock React tree.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import fs from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await fs.mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const specimen of [
    { width: 375, lang: 'pt', tab: /Rastreamento & Mapa/, title: 'Não foi possível carregar esta seção', back: 'Voltar à síntese' },
    { width: 1440, lang: 'en', tab: /Tracking & Map/, title: 'This section could not be loaded', back: 'Back to summary' },
  ]) {
    const page = await browser.newPage({ viewport: { width: specimen.width, height: 812 }, reducedMotion: 'reduce' });
    let abortedModules = 0;
    await page.route(/\/src\/components\/OrbitalMap\.tsx(?:\?.*)?$/, route => {
      abortedModules += 1;
      return route.abort('failed');
    });
    try {
      const response = await page.goto(origin, { waitUntil: 'domcontentloaded' });
      assert(response?.ok(), 'laboratory root must load');
      await page.getByRole('heading', { level: 1 }).waitFor();
      if (specimen.lang === 'en') await page.getByRole('button', { name: 'English' }).click();
      const navigation = page.getByRole('navigation', {
        name: specimen.lang === 'pt' ? 'Seções do laboratório' : 'Laboratory sections',
      });
      await navigation.getByRole('link', { name: specimen.tab }).click();
      const alert = page.getByRole('alert', { name: specimen.title });
      await alert.waitFor({ timeout: 15000 });
      assert(abortedModules > 0, 'the requested lazy module must really be blocked');
      assert.equal(await page.getByRole('heading', { level: 1 }).count(), 1);
      assert.equal(await page.locator('header').count(), 1, 'failed import must not unmount navigation');
      assert.equal(await navigation.locator('[aria-current="page"]').count(), 1);
      await page.screenshot({ path: `${out}/lazy-failure-${specimen.lang}-${specimen.width}.png` });
      await alert.getByRole('link', { name: specimen.back }).click();
      await page.getByRole('heading', { level: 1, name: specimen.lang === 'pt' ? /O que sabemos/ : /What we know/ }).waitFor({ timeout: 15000 });
      assert.equal(await page.getByRole('alert').count(), 0, 'recovering to summary must reset the route boundary');
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}

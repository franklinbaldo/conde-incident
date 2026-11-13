// Browser-level audit of real export controls, not a CSS-source approximation.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir, writeFile } from 'node:fs/promises';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const out = process.env.UI_AUDIT_OUT || 'test-results/ui';
await mkdir(out, { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const { width, lang } of [
    { width: 320, lang: 'pt' }, { width: 375, lang: 'en' },
    { width: 640, lang: 'pt' }, { width: 1440, lang: 'en' },
  ]) {
    const page = await browser.newPage({ viewport: { width, height: 812 }, reducedMotion: 'reduce' });
    try {
      const response = await page.goto(origin, { waitUntil: 'domcontentloaded' });
      assert(response?.ok(), 'laboratory must load');
      if (lang === 'en') await page.getByRole('button', { name: 'English' }).click();
      const opener = page.getByRole('button', { name: lang === 'pt' ? 'Script Python' : 'Python Script' }).first();
      await opener.click();
      const dialog = page.getByRole('dialog', { name: 'norad528_reconstruction.py' });
      await dialog.waitFor({ timeout: 15000 });
      const names = lang === 'pt'
        ? ['Copiar código', 'Baixar .py', 'Fechar janela de exportação']
        : ['Copy code', 'Download .py', 'Close export dialog'];
      const rects = [];
      for (const name of names) {
        const control = dialog.getByRole('button', { name });
        const rect = await control.boundingBox();
        assert(rect && rect.width >= 44 && rect.height >= 44,
          `undersized "${name}" at ${width}px: ${JSON.stringify(rect)}`);
        rects.push({ name, width: rect.width, height: rect.height });
      }
      const horizontal = await dialog.evaluate(el => ({
        viewport: document.documentElement.clientWidth,
        page: document.documentElement.scrollWidth,
        dialog: el.clientWidth,
        contents: el.scrollWidth,
      }));
      assert(horizontal.page <= horizontal.viewport + 1,
        `export dialog causes horizontal page overflow at ${width}px: ${JSON.stringify(horizontal)}`);
      const close = dialog.getByRole('button', { name: names[2] });
      assert(await close.evaluate(el => document.activeElement === el), 'initial focus must be on Close');
      await page.keyboard.press('Shift+Tab');
      assert(await dialog.getByRole('button', { name: names[1] }).evaluate(el => document.activeElement === el),
        'reverse Tab should reach Download');
      const outline = await dialog.getByRole('button', { name: names[1] })
        .evaluate(el => ({ style: getComputedStyle(el).outlineStyle, width: getComputedStyle(el).outlineWidth }));
      assert(outline.style !== 'none' && parseFloat(outline.width) >= 2,
        `keyboard focus is not visible: ${JSON.stringify(outline)}`);
      await page.screenshot({ path: `${out}/python-touch-modal-${lang}-${width}.png` });
      await page.keyboard.press('Escape');
      await dialog.waitFor({ state: 'hidden' });
      assert(await opener.evaluate(el => document.activeElement === el), 'Escape must return focus to the opener');
      await page.screenshot({ path: `${out}/python-touch-return-${lang}-${width}.png` });
      await writeFile(`${out}/python-touch-targets-${width}.json`, JSON.stringify({ width, lang, rects, horizontal, outline }, null, 2));
    } finally {
      await page.close();
    }
  }
} finally {
  await browser.close();
}
console.log('PASS: Python export action targets, focus ring, reflow and Escape in Chromium');

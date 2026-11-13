// Adversarial browser test: rejecting the lazy Python export must not strand a reader.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';

const origin = process.env.UI_AUDIT_URL || 'http://127.0.0.1:3000/';
const browser = await chromium.launch({ headless: true });
try {
  for (const { width, lang, trigger, close, message } of [
    { width: 320, lang: 'pt', trigger: 'Python Script', close: 'Fechar exportação', message: /Não foi possível carregar/ },
    { width: 1440, lang: 'en', trigger: 'Python Script', close: 'Close export', message: /could not be loaded/ },
  ]) {
    const page = await browser.newPage({ viewport: { width, height: 800 } });
    // Vite dev URL; only the requested chunk fails. No production failure is asserted.
    let intercepted = 0;
    await page.route(/\/src\/components\/PythonScriptModal\.tsx(?:\?.*)?$/, route => {
      intercepted++;
      return route.abort('failed');
    });
    await page.goto(origin, { waitUntil: 'domcontentloaded' });
    await page.getByRole('heading', { level: 1 }).first().waitFor();
    if (lang === 'en') await page.getByRole('button', { name: 'English' }).click();
    const opener = page.getByRole('button', { name: trigger }).first();
    await opener.click();
    const dialog = page.getByRole('dialog', { name: lang === 'pt' ? 'Exportação Python' : 'Python export' });
    await dialog.getByRole('alert').waitFor({ timeout: 20000 });
    assert.match(await dialog.getByRole('alert').innerText(), message);
    assert(intercepted > 0, 'the real lazy module request must be rejected');
    assert.equal(await dialog.getAttribute('aria-modal'), 'true');
    const closeButton = dialog.getByRole('button', { name: close });
    assert(await closeButton.evaluate(el => document.activeElement === el), 'failure dialog must focus Close');
    const rect = await closeButton.boundingBox();
    assert(rect && rect.height >= 44 && rect.width >= 44, 'close action must be a 44px touch target');
    assert.equal(await page.getByRole('heading', { level: 1 }).count(), 1, 'the site must retain its heading');
    await page.keyboard.press('Escape');
    await dialog.waitFor({ state: 'hidden' });
    assert(await opener.evaluate(el => document.activeElement === el), 'Escape must restore export opener focus');
    // Error state is disposed when closed; reopening retains a usable exit.
    await opener.click();
    await dialog.getByRole('alert').waitFor({ timeout: 20000 });
    assert.match(await dialog.getByRole('alert').innerText(), message);
    await closeButton.click();
    await dialog.waitFor({ state: 'hidden' });
    assert(await opener.evaluate(el => document.activeElement === el));
    await page.close();
  }
} finally {
  await browser.close();
}
console.log('PASS: lazy Python module failure retains a usable, localized and keyboard-accessible exit');

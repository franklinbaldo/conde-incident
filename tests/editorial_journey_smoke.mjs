// Cross-architecture journey against one assembled SSG + Vite Pages artifact.
// Chromium/reflow checks do not claim physical-device or screen-reader coverage.
import { chromium } from 'playwright';
import assert from 'node:assert/strict';
import { mkdir } from 'node:fs/promises';

const origin = process.env.SSG_SEARCH_AUDIT_URL || 'http://127.0.0.1:4173/conde-incident/';
await mkdir('test-results/ui', { recursive: true });
const browser = await chromium.launch({ headless: true });
try {
  for (const width of [320, 1440]) {
    const page = await browser.newPage({ viewport: { width, height: 820 } });
    const errors = [];
    page.on('pageerror', error => errors.push(error.message));
    let response = await page.goto(origin);
    assert(response?.ok(), 'SSG home must load at Pages prefix');
    const primary = page.getByRole('navigation', { name: 'Navegação principal' });
    await primary.getByRole('link', { name: 'Laboratório' }).click();
    await page.getByRole('navigation', { name: 'Seções do laboratório' }).waitFor();
    assert.match(new URL(page.url()).pathname, /\/conde-incident\/lab\/$/);

    for (const [tab, label, expected] of [
      ['Rastreamento & Mapa', 'Contexto do mapa', '/conde-incident/mapa/'],
      ['Arquivo e proveniência', 'Arquivo documental', '/conde-incident/evidencias/arquivo/'],
      ['Auditoria de TLEs', 'Custódia documental dos TLEs', '/conde-incident/simulacoes/tles/custodia/'],
    ]) {
      await page.getByRole('navigation', { name: 'Seções do laboratório' })
        .getByRole('link', { name: new RegExp(tab) }).click();
      const link = page.getByRole('link', { name: 'Abrir no Caderno: ' + label });
      await link.waitFor();
      assert.equal(await link.getAttribute('href'), expected);
      const box = await link.boundingBox();
      assert(box && box.x >= -1 && box.x + box.width <= width + 1,
        'context link clipped at ' + width + 'px: ' + label);
      await link.click();
      assert.equal(new URL(page.url()).pathname, expected);
      await page.locator('main#main').waitFor();
      assert.equal(await page.locator('html').getAttribute('lang'), 'pt-BR');
      assert.equal(await page.getByRole('navigation', { name: 'Navegação principal' }).count(), 1);
      await page.getByRole('navigation', { name: 'Navegação principal' })
        .getByRole('link', { name: 'Laboratório' }).click();
      await page.getByRole('navigation', { name: 'Seções do laboratório' }).waitFor();
    }
    await page.screenshot({ path: 'test-results/ui/editorial-lab-' + width + '.png' });
    // The reader's documentary path is in the public artifact, not only an index.
    const chapterPath = '/conde-incident/stories/2026-11-11-o-dia-em-que-dois-relatos-se-cruzaram/';
    const chapterUrl = new URL(chapterPath, origin).toString();
    for (const { label, occurrence, source, id } of [
      { label: 'ocorrência C131#1 no arquivo curado', occurrence: '/conde-incident/evidencias/arquivo/c131-1/', source: '/conde-incident/evidencias/arquivo/fontes/nasa-ssr-19631115/', id: 'NASA_SSR_19631115' },
      { label: 'ocorrência C01#1 no arquivo curado', occurrence: '/conde-incident/evidencias/arquivo/c01-1/', source: '/conde-incident/evidencias/arquivo/fontes/fbis-eop-uap-d001/', id: 'FBIS_EOP_UAP_D001' },
    ]) {
      response = await page.goto(chapterUrl);
      assert(response?.ok(), 'chapter must load from assembled Pages artifact');
      const claimLink = page.getByRole('link', { name: label });
      assert.equal(await claimLink.getAttribute('href'), occurrence);
      const bounds = await claimLink.boundingBox();
      assert(bounds && bounds.x >= -1 && bounds.x + bounds.width <= width + 1,
        'source traceability link clipped at ' + width + 'px: ' + label);
      await claimLink.click();
      assert.equal(new URL(page.url()).pathname, occurrence);
      const sourceLink = page.getByRole('link', { name: id, exact: true });
      await sourceLink.click();
      assert.equal(new URL(page.url()).pathname, source);
      assert(await page.getByRole('link', { name: 'Ocorrência e genealogia' }).count() > 0,
        'source sheet must offer a return to its documented occurrence');
      if (width === 320) {
        await page.screenshot({ path: 'test-results/ui/editorial-source-' + id.toLowerCase() + '-320.png' });
      }
      await page.goBack();
      assert.equal(new URL(page.url()).pathname, occurrence);
      await page.goBack();
      assert.equal(new URL(page.url()).pathname, chapterPath);
    }
    assert.deepEqual(errors, [], 'JS errors during SSG ↔ lab navigation at ' + width);
    await page.close();
  }
} finally {
  await browser.close();
}

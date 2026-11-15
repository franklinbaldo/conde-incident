// Browser assertions run from the laboratory smoke test in both languages.
import assert from 'node:assert/strict';

export async function checkSensitivityA11y(page, viewport, locale) {
  const headingLevels = await page.locator('main h1, main h2, main h3').evaluateAll(
    nodes => nodes.map(node => Number(node.tagName.slice(1))),
  );
  assert.deepEqual(headingLevels, [1, 2, 2, 2],
    `sensitivity heading levels must be H1/H2/H2/H2 (${viewport.name}, ${locale})`);
  const sliders = await page.locator('input[type="range"]').evaluateAll(inputs =>
    inputs.map(input => ({ id: input.id, label: input.labels?.[0]?.textContent?.trim(), valueText: input.getAttribute('aria-valuetext') }))
  );
  assert.equal(sliders.length, 3, 'expected three physical sensitivity controls');
  assert(sliders.every(slider => slider.id && slider.label && slider.valueText),
    'all physical sliders must expose name and unit-bearing value');
  const expectedNames = locale === 'pt'
    ? ['Escala de Altura Termoesférica', 'Fluxo Solar', 'Coeficiente Balístico']
    : ['Thermospheric Scale Height', 'Solar Flux', 'Ballistic Coefficient'];
  for (let i = 0; i < sliders.length; i++) {
    assert(sliders[i].label.includes(expectedNames[i]),
      `slider ${i} untranslated or unlabelled (${locale}): ${sliders[i].label}`);
    assert(sliders[i].valueText.includes(['km', 'sfu', 'm²/kg'][i]),
      `slider ${i} missing unit (${locale}): ${sliders[i].valueText}`);
  }
  const text = await page.getByRole('main').textContent(); // CSS text-transform must not change the tested translation
  assert(text.includes(locale === 'pt' ? 'Resultado do modelo simplificado' : 'Simplified model result'),
    `simplified-formula explanation must match locale ${locale}`);
  assert(text.includes(locale === 'pt' ? 'Cenários ilustrativos de sensibilidade' : 'Illustrative sensitivity scenarios'),
    `illustrative scenario heading must match locale ${locale}`);
  assert(!text.includes('Resultado da Integração Numérica') && !text.includes('Numerical Integration Result'),
    'closed-form scenario must not be announced as numerical integration');
  const first = page.locator('input[type="range"]').first();
  const before = Number(await first.inputValue());
  await first.focus();
  await page.keyboard.press('ArrowRight');
  assert.equal(Number(await first.inputValue()), before + 1, 'keyboard must adjust scale height');
  assert.equal(await first.getAttribute('aria-valuetext'), `${before + 1} km`,
    'assistive value must follow keyboard adjustments');

  const choices = page.getByRole('group', { name: locale === 'pt'
    ? 'Selecionar escala de altura ilustrativa' : 'Select illustrative scale height' });
  assert.equal(await choices.getByRole('button').count(), 4, 'all four legacy scenarios must be selectable');
  const selected = choices.getByRole('button', { name: /H = 60 km/ });
  await selected.focus();
  await page.keyboard.press('Enter');
  assert.equal(await first.inputValue(), '60', 'scenario button must update the actual physics control');
  assert.equal(await first.getAttribute('aria-valuetext'), '60 km', 'assistive value must reflect the selected scenario');
  assert.equal(await selected.getAttribute('aria-pressed'), 'true', 'selected scenario must expose state');
  assert.equal(await choices.getByRole('button', { name: /H = 45 km/ }).getAttribute('aria-pressed'),
    'false', 'reference scenario must not remain selected after a change');
  const copy = (await page.getByRole('main').textContent()) ?? '';
  assert(copy.includes(locale === 'pt' ? 'não são resultados da fórmula interativa' : 'not outputs of the interactive formula'),
    'legacy dates must be explicitly distinguished from interactive calculations');

  const reset = page.getByRole('button', { name: locale === 'pt'
    ? 'Restaurar parâmetros de referência' : 'Reset reference parameters' });
  assert(await reset.isEnabled(), 'reset must become available when parameters differ from reference');
  await reset.focus();
  await page.keyboard.press('Enter');
  assert.deepEqual(await page.locator('input[type="range"]').evaluateAll(nodes => nodes.map(n => n.value)),
    ['45', '76.5', '0.022'], 'reset must restore all three reference parameters');
  assert(await reset.isDisabled(), 'reset must be disabled when no change remains');
  assert.equal(await choices.getByRole('button', { name: /H = 45 km/ }).getAttribute('aria-pressed'),
    'true', 'reference scenario must be selected after reset');
  await page.addStyleTag({ content: ':root { font-size: 200% !important; }' });
  const reflow = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  assert(reflow.scroll <= reflow.viewport + 1,
    `sensitivity horizontal overflow at 200% text (${viewport.name}, ${locale}): ${JSON.stringify(reflow)}`);
}

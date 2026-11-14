// Browser assertions run from the laboratory smoke test in both languages.
import assert from 'node:assert/strict';

export async function checkSensitivityA11y(page, viewport, locale) {
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
  const text = await page.getByRole('main').innerText();
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
  await page.addStyleTag({ content: ':root { font-size: 200% !important; }' });
  const reflow = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  assert(reflow.scroll <= reflow.viewport + 1,
    `sensitivity horizontal overflow at 200% text (${viewport.name}, ${locale}): ${JSON.stringify(reflow)}`);
}

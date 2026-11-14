// Browser assertions run from the laboratory smoke test in both languages.
import assert from 'node:assert/strict';

export async function checkSensitivityA11y(page, viewport, locale) {
  const sliders = await page.locator('input[type="range"]').evaluateAll(inputs =>
    inputs.map(input => ({ id: input.id, label: input.labels?.[0]?.textContent?.trim() }))
  );
  assert.equal(sliders.length, 3, 'expected three physical sensitivity controls');
  assert(sliders.every(slider => slider.id && slider.label),
    'all physical sliders must have programmatically associated visible labels');
  await page.addStyleTag({ content: ':root { font-size: 200% !important; }' });
  const reflow = await page.evaluate(() => ({
    viewport: document.documentElement.clientWidth,
    scroll: document.documentElement.scrollWidth,
  }));
  assert(reflow.scroll <= reflow.viewport + 1,
    `sensitivity horizontal overflow at 200% text (${viewport.name}, ${locale}): ${JSON.stringify(reflow)}`);
}

/**
 * Minimal NORAD TLE syntax checks, equivalent to the legacy auditTleSyntax.
 * A valid modulo-10 digit does not authenticate an epoch, sensor, orbit or source.
 * Deliberately do not trim, pad, normalize, or repair the user's input bytes.
 */
export function auditTleSyntax(line, expectedLine, expectedNoradId) {
  const length = line.length;
  const prefixMatches = line[0] === String(expectedLine)
    && line[1] === ' '
    && /^\d{5}$/.test(line.slice(2, 7))
    && Number(line.slice(2, 7)) === expectedNoradId;
  const actualChecksum = length === 69 && /^\d$/.test(line[68]) ? Number(line[68]) : null;
  const computedChecksum = length === 69
    ? [...line.slice(0, 68)].reduce(
        (sum, character) => sum + (/^\d$/.test(character) ? Number(character) : character === '-' ? 1 : 0),
        0,
      ) % 10
    : null;
  return {
    length, expectedLine, prefixMatches, actualChecksum, computedChecksum,
    valid: length === 69 && prefixMatches
      && actualChecksum !== null && computedChecksum === actualChecksum,
  };
}

export function auditTlePair(line1, line2) {
  const catalogId = /^1 \d{5}/.test(line1) ? Number(line1.slice(2, 7)) : null;
  const first = auditTleSyntax(line1, 1, catalogId);
  const second = auditTleSyntax(line2, 2, catalogId);
  return { catalogId, first, second, valid: catalogId !== null && first.valid && second.valid };
}

/**
 * Accept a copied two-line TLE block without changing either 69-column line.
 * Only line separators are consumed; headers, extra lines and stray CRs do
 * not qualify. Each line still goes through the minimal audit on submit.
 */
export function splitTlePairPaste(raw) {
  const match = /^([^\r\n]*)\r?\n([^\r\n]*)(?:\r?\n)?$/.exec(raw);
  return match ? [match[1], match[2]] : null;
}

function attachChecker() {
  const form = document.getElementById('ssg-tle-audit');
  const output = document.getElementById('ssg-tle-results');
  if (!form || !output) return;
  form.hidden = false;
  const firstInput = form.elements.namedItem('line1');
  const secondInput = form.elements.namedItem('line2');
  // A previous PASS belongs to the previous bytes, never to edited input.
  form.addEventListener('input', event => {
    if (event.target === firstInput || event.target === secondInput) output.replaceChildren();
  });
  firstInput.addEventListener('paste', event => {
    const pair = splitTlePairPaste(event.clipboardData?.getData('text/plain') ?? '');
    if (!pair) return; // Retain native paste for a single line or malformed block.
    event.preventDefault();
    firstInput.value = pair[0];
    secondInput.value = pair[1];
    output.replaceChildren();
    secondInput.focus();
  });
  form.addEventListener('submit', event => {
    event.preventDefault();
    const line1 = form.elements.namedItem('line1').value;
    const line2 = form.elements.namedItem('line2').value;
    const result = auditTlePair(line1, line2);
    const heading = document.createElement('p');
    heading.textContent = result.valid
      ? 'As duas linhas passaram na verificação mínima de comprimento, identificação e checksum. Isso NÃO autentica os dados.'
      : 'Uma ou ambas as linhas não passaram na verificação mínima de sintaxe.';
    const list = document.createElement('ul');
    for (const [label, data] of [['Linha 1', result.first], ['Linha 2', result.second]]) {
      const item = document.createElement('li');
      item.textContent = label + ': ' + data.length + '/69 caracteres; prefixo/NORAD ' + (data.prefixMatches ? 'confere' : 'não confere')
        + '; dígito informado ' + (data.actualChecksum ?? 'indisponível') + ', calculado ' + (data.computedChecksum ?? 'indisponível')
        + '. ' + (data.valid ? 'Checksum confere.' : 'Inconsistente.');
      list.append(item);
    }
    const limit = document.createElement('p');
    limit.textContent = 'Resultado estritamente sintático. Não testa campos orbitais completos, proveniência, calibração nem reentrada.';
    output.replaceChildren(heading, list, limit);
    output.focus();
  });
}
if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', attachChecker, { once: true });
  else attachChecker();
}

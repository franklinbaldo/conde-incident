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

/**
 * A standard two-line clipboard block may have one *untrusted* name line.
 * Keep the 69-column orbital lines byte-for-byte; the heading is merely a
 * user-supplied label, not NORAD provenance or an authenticated source.
 */
export function parseTleClipboard(raw) {
  const pair = splitTlePairPaste(raw);
  if (pair) return { lines: pair, title: null };
  const triple = /^([^\r\n]+)\r?\n([^\r\n]*)\r?\n([^\r\n]*)(?:\r?\n)?$/.exec(raw);
  if (!triple) return null;
  const [, title, first, second] = triple;
  if (title.length > 120 || /[\x00-\x1f\x7f]/.test(title)
      || /^[12] /.test(title) || !first.startsWith('1 ') || !second.startsWith('2 ')) return null;
  return { lines: [first, second], title };
}

function attachChecker() {
  const form = document.getElementById('ssg-tle-audit');
  const output = document.getElementById('ssg-tle-results');
  if (!form || !output) return;
  const importNote = document.getElementById('ssg-tle-import-note');
  if (!importNote) return;
  form.hidden = false;
  const firstInput = form.elements.namedItem('line1');
  const secondInput = form.elements.namedItem('line2');
  // Never leave invalid states referencing a verdict for previous bytes.
  function clearVerdict() {
    output.replaceChildren();
    importNote.hidden = true;
    importNote.textContent = '';
    for (const input of [firstInput, secondInput]) {
      input.removeAttribute('aria-invalid');
      input.setAttribute('aria-describedby', 'ssg-tle-instructions');
    }
  }
  form.addEventListener('input', event => {
    if (event.target === firstInput || event.target === secondInput) clearVerdict();
  });
  firstInput.addEventListener('paste', event => {
    const imported = parseTleClipboard(event.clipboardData?.getData('text/plain') ?? '');
    if (!imported) return; // Native paste for a single line or malformed block.
    event.preventDefault();
    firstInput.value = imported.lines[0];
    secondInput.value = imported.lines[1];
    clearVerdict();
    if (imported.title !== null) {
      importNote.textContent = 'Título copiado (não autenticado): ' + imported.title;
      importNote.hidden = false;
    }
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
    for (const [label, data, input, id] of [
      ['Linha 1', result.first, firstInput, 'ssg-tle-result-line1'],
      ['Linha 2', result.second, secondInput, 'ssg-tle-result-line2'],
    ]) {
      const item = document.createElement('li');
      item.id = id;
      item.textContent = label + ': ' + data.length + '/69 caracteres; prefixo/NORAD ' + (data.prefixMatches ? 'confere' : 'não confere')
        + '; dígito informado ' + (data.actualChecksum ?? 'indisponível') + ', calculado ' + (data.computedChecksum ?? 'indisponível')
        + '. ' + (data.valid ? 'Checksum confere.' : 'Inconsistente.');
      input.removeAttribute('aria-invalid');
      input.setAttribute('aria-describedby', 'ssg-tle-instructions');
      if (!data.valid) {
        input.setAttribute('aria-invalid', 'true');
        input.setAttribute('aria-describedby', 'ssg-tle-instructions ' + id);
      }
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

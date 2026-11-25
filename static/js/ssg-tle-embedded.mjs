import { HISTORICAL_ORBITAL_DATA } from './orbital-data.mjs';
import { auditTleSyntax } from './tle-checksum.mjs';

const labels = {
  pt: {
    heading: 'Inspeção dos conjuntos incorporados',
    notice: '528: espelho secundário, sem origem instrumental autenticada. 527/529: cenários ilustrativos, não observações.',
    select: 'Objeto', language: 'Idioma da inspeção', copy: 'Copiar as duas linhas',
    copied: 'Linhas copiadas', failed: 'Não foi possível copiar. Selecione o texto manualmente.',
    line: 'Linha', length: 'Comprimento', prefix: 'Número da linha e NORAD',
    digit: 'Dígito calculado / informado', pass: 'Confere', fail: 'Não confere',
    valid: 'Formato mínimo compatível, sem autenticação', invalid: 'Formato ou checksum inconsistente',
    unavailable: 'Indisponível', parameters: 'Parâmetros do modelo, não medições validadas',
    epoch: 'Época declarada', raan: 'RAAN no conjunto', bstar: 'BSTAR no conjunto',
    scenario: 'Não autenticado (cenário)',
    limits: 'BSTAR zero não prova arrasto físico nulo. O boletim NASA de 15/11/1963 registra somente o dia 08/11 para o decaimento de 528; não estabelece hora, local terminal ou impacto. Resultado científico indeterminado.',
    source: 'Custódia e fontes do 528', nasa: 'Boletim NASA (dia catalogado)', nasa527: 'NASA 30/06/1964: 527 em órbita, não valida TLE do cenário',
  },
  en: {
    heading: 'Inspect embedded datasets',
    notice: '528: secondary mirror, original tracking source unauthenticated. 527/529: illustrative scenarios, not observations.',
    select: 'Object', language: 'Inspection language', copy: 'Copy both lines',
    copied: 'Lines copied', failed: 'Could not copy. Select text manually.',
    line: 'Line', length: 'Length', prefix: 'Line number and NORAD ID',
    digit: 'Computed / supplied digit', pass: 'Matches', fail: 'Does not match',
    valid: 'Minimal format consistent; no authentication', invalid: 'Format or checksum inconsistent',
    unavailable: 'Unavailable', parameters: 'Model inputs, not validated measurements',
    epoch: 'Declared epoch', raan: 'RAAN in dataset', bstar: 'BSTAR in dataset',
    scenario: 'Unauthenticated (scenario)',
    limits: 'Zero BSTAR does not prove zero physical drag. The NASA bulletin of 15 Nov 1963 records only 8 Nov as the decay day for 528; it establishes neither terminal time, location nor impact. Scientific outcome undetermined.',
    source: '528 custody and sources', nasa: 'NASA bulletin (cataloged day)', nasa527: 'NASA 30 Jun 1964: 527 in orbit, not validation of this scenario TLE',
  },
};

// A change of selection, language or request invalidates earlier feedback.
// This controls status only; it cannot order writes to the physical clipboard.
export function createCopyFeedback(write, report) {
  let generation = 0;
  const invalidate = () => { generation++; report(''); };
  return {
    invalidate,
    async copy(text) {
      invalidate();
      const current = generation;
      let status;
      try { await write(text); status = 'copied'; }
      catch { status = 'failed'; }
      if (current === generation) report(status);
    },
  };
}

function attach() {
  const root = document.getElementById('ssg-tle-embedded');
  if (!root) return;
  const select = root.querySelector('#ssg-tle-object');
  const language = root.querySelector('#ssg-tle-language');
  const detail = root.querySelector('#ssg-tle-embedded-details');
  const status = root.querySelector('#ssg-tle-copy-status');
  const copy = root.querySelector('#ssg-tle-copy');
  const feedback = createCopyFeedback(text => navigator.clipboard.writeText(text),
    state => { status.textContent = state ? labels[language.value][state] : ''; });
  const element = (tag, text) => {
    const node = document.createElement(tag);
    node.textContent = text;
    return node;
  };
  function render() {
    feedback.invalidate();
    const t = labels[language.value];
    const sat = HISTORICAL_ORBITAL_DATA[Number(select.value)];
    root.lang = language.value === 'pt' ? 'pt-BR' : 'en';
    root.querySelector('h2').textContent = t.heading;
    root.querySelector('#ssg-tle-embedded-notice').textContent = t.notice;
    root.querySelector('label[for="ssg-tle-object"]').textContent = t.select;
    root.querySelector('label[for="ssg-tle-language"]').textContent = t.language;
    copy.textContent = t.copy;
    const nodes = [element('h3', sat.intlDesignator + ' · NORAD ' + sat.noradId)];
    for (const [number, line] of [[1, sat.line1], [2, sat.line2]]) {
      const audit = auditTleSyntax(line, number, sat.noradId);
      const heading = element('h4', t.line + ' ' + number);
      const pre = element('pre', '');
      pre.className = 'tle-source-lines';
      pre.tabIndex = 0;
      pre.setAttribute('role', 'region');
      pre.setAttribute('aria-label', heading.textContent);
      pre.append(element('code', line));
      nodes.push(heading, pre, element('p', t.length + ': ' + audit.length + '/69; ' +
        t.prefix + ': ' + (audit.prefixMatches ? t.pass : t.fail) + '; ' +
        t.digit + ': ' + (audit.computedChecksum ?? t.unavailable) + ' / ' +
        (audit.actualChecksum ?? t.unavailable) + '. ' + (audit.valid ? t.valid : t.invalid)));
    }
    const dl = element('dl', '');
    for (const [key, value] of [[t.epoch, sat.epochStr], [t.raan, sat.noradId === 528 ? sat.raanDeg.toFixed(4) + '°' : t.scenario], [t.bstar, sat.bstar.toExponential(3)]]) {
      dl.append(element('dt', key), element('dd', value));
    }
    nodes.push(element('h4', t.parameters), dl, element('p', t.limits));
    const list = element('ul', '');
    for (const [label, href] of [[t.source, '/conde-incident/simulacoes/tles/custodia/'], [t.nasa, 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10'], [t.nasa527, 'https://ntrs.nasa.gov/api/citations/19640019314/downloads/19640019314.pdf#page=7']]) {
      const li = element('li', '');
      const link = element('a', label);
      link.href = href;
      li.append(link);
      list.append(li);
    }
    nodes.push(list);
    detail.replaceChildren(...nodes);
  }
  select.addEventListener('change', render);
  language.addEventListener('change', render);
  copy.addEventListener('click', () => {
    const sat = HISTORICAL_ORBITAL_DATA[Number(select.value)];
    void feedback.copy(sat.line1 + '\n' + sat.line2);
  });
  render();
  root.hidden = false;
}

if (typeof document !== 'undefined') {
  if (document.readyState === 'loading') document.addEventListener('DOMContentLoaded', attach, { once: true });
  else attach();
}

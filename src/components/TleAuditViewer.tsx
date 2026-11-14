import React, { useState } from 'react';
import { HISTORICAL_ORBITAL_DATA } from '../lib/constants';
import { auditTleSyntax } from '../lib/tleChecksum';

interface TleAuditViewerProps {
  lang: 'pt' | 'en';
}

type Lang = 'pt' | 'en';
const MATRIX = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md';
const MATRIX_C179 = MATRIX + '#L839';
const MATRIX_C197 = MATRIX + '#L905-L910';
const MATRIX_COLLISIONS = MATRIX + '#L164-L177';
const NASA_BULLETIN = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10';
const NASA_527_1964 = 'https://ntrs.nasa.gov/api/citations/19640019314/downloads/19640019314.pdf#page=7';

const labels = {
  pt: {
    heading: 'Linhas TLE em auditoria de custódia',
    subtitle: 'Verificação sintática local, não autenticação de elementos orbitais de 1963.',
    notice: 'As linhas exibidas pertencem ao conjunto incorporado no laboratório. Não foi demonstrado que sejam transcrições fiéis dos TLEs históricos originais. Checksums válidos podem ser gerados para dados inteiramente hipotéticos.',
    select: 'Selecionar objeto para inspecionar',
    target: 'objeto investigado',
    lines: 'Linhas incorporadas, não autenticadas',
    first: 'Linha 1: identificação e época codificada',
    second: 'Linha 2: elementos codificados',
    copy: 'Copiar as duas linhas',
    copied: 'Linhas copiadas',
    failed: 'Não foi possível copiar. Selecione o texto manualmente.',
    audit: 'Auditoria limitada de formato',
    length: 'Comprimento',
    prefix: 'Número da linha e NORAD',
    check: 'Dígito módulo 10',
    pass: 'Confere',
    fail: 'Não confere',
    noDigit: 'Indisponível',
    label: 'Resultado sintático',
    valid: 'Formato mínimo e checksum compatíveis, sem autenticação',
    invalid: 'Formato ou checksum inconsistente',
    data: 'Parâmetros exibidos pelo modelo, não medições validadas',
    epoch: 'Época declarada no conjunto',
    raan: 'RAAN no conjunto',
    unverified: 'Não autenticado (cenário)',
    catalog527: 'NASA 30/06/1964: 527 em órbita (não valida TLE deste cenário)',
    bstar: 'BSTAR no conjunto',
    assumptions: 'Premissas e limitações',
    status: 'C179#1 registra um par TLE secundário do 528, mas não comprova sua origem instrumental. Os vetores 527/529 são cenários sem TLE primário autenticado. O boletim NASA de 30/06/1964 documenta 527 em órbita, não confirma os elementos ou épocas usados neste simulador.',
    drag: 'BSTAR = 0 não demonstra arrasto físico nulo. Um valor não zero tampouco certifica calibração histórica.',
    nasa: 'O boletim NASA de 15/11/1963 documenta o dia 08/11 para o decaimento de 1963-003B. Não autentica estas linhas nem informa hora ou local terminal. Reentrada não comprova impacto.',
    conclusion: 'Resultado científico: indeterminado. Não há domínio admissível não vazio e reduzido ou intervalo físico certificado para hora, posição e impacto.',
    links: 'Verificar fontes e restrições',
    matrix: 'Matriz cumulativa C001–C238 (snapshot da PR #1)',
    primary: 'Boletim NASA (C197; documento primário para o dia)',
    custody: 'Custódia e conflito RAAN (PR #14)',
    evidence: 'C179: espelho TLE secundário (matriz)',
    decay: 'C197–C202: dia documentado (matriz)',
    holdout: 'C44–C46: IDs com duas ocorrências (matriz)',
    map: 'Fluxo científico proposto (PR #28; não integrado)',
  },
  en: {
    heading: 'TLE lines awaiting provenance audit',
    subtitle: 'Local syntax check, not authentication of 1963 orbital elements.',
    notice: 'These lines come from the laboratory’s embedded dataset. They have not been shown to be faithful transcriptions of original historical TLEs. Even entirely hypothetical values can carry valid checksums.',
    select: 'Select an object to inspect',
    target: 'target object',
    lines: 'Embedded lines, not authenticated',
    first: 'Line 1: identifier and encoded epoch',
    second: 'Line 2: encoded orbital elements',
    copy: 'Copy both lines',
    copied: 'Lines copied',
    failed: 'Could not copy. Select text manually.',
    audit: 'Limited format audit',
    length: 'Length',
    prefix: 'Line number and NORAD ID',
    check: 'Modulo-10 check digit',
    pass: 'Matches',
    fail: 'Does not match',
    noDigit: 'Unavailable',
    label: 'Syntax result',
    valid: 'Minimal format and checksum consistent; no authentication',
    invalid: 'Format or checksum inconsistent',
    data: 'Model inputs, not validated measurements',
    epoch: 'Epoch declared in dataset',
    raan: 'RAAN in dataset',
    unverified: 'Unauthenticated (scenario)',
    catalog527: 'NASA 30 Jun 1964: 527 in orbit (not this scenario TLE)',
    bstar: 'BSTAR in dataset',
    assumptions: 'Assumptions and limits',
    status: 'C179#1 records a secondary TLE pair for 528, without authentication of its original tracking source. The 527/529 vectors are scenarios lacking authenticated primary TLEs. NASA’s 30 June 1964 bulletin documents 527 in orbit, not the epochs or elements used by this simulator.',
    drag: 'BSTAR = 0 does not measure zero physical drag. A nonzero value also does not certify historical calibration.',
    nasa: 'The NASA bulletin of November 15, 1963 records November 8 as the decay day for 1963-003B. It does not authenticate these lines or establish terminal time or location. Reentry is not proof of ground impact.',
    conclusion: 'Scientific outcome: undetermined. No established nonempty reduced admissible domain or certified physical interval for time, position or impact.',
    links: 'Sources and constraints',
    matrix: 'Cumulative C001–C238 matrix (PR #1 snapshot)',
    primary: 'NASA bulletin (C197; primary document for the day)',
    custody: 'Custody and RAAN conflict (PR #14)',
    evidence: 'C179: secondary TLE mirror (matrix)',
    decay: 'C197–C202: documented decay day (matrix)',
    holdout: 'C44–C46: duplicated occurrence IDs (matrix)',
    map: 'Proposed scientific workflow (PR #28; not integrated)',
  },
} satisfies Record<Lang, Record<string, string>>;

export const TleAuditViewer: React.FC<TleAuditViewerProps> = ({ lang }) => {
  const t = labels[lang];
  const [selectedId, setSelectedId] = useState<527 | 528 | 529>(528);
  const [copyState, setCopyState] = useState<'idle' | 'copied' | 'failed'>('idle');
  const sat = HISTORICAL_ORBITAL_DATA[selectedId];
  const lines = [
    { line: sat.line1, expected: 1 as const, heading: t.first },
    { line: sat.line2, expected: 2 as const, heading: t.second },
  ];

  const copyTle = async () => {
    try {
      await navigator.clipboard.writeText(sat.line1 + '\n' + sat.line2);
      setCopyState('copied');
    } catch {
      setCopyState('failed');
    }
  };

  return (
    <section aria-labelledby="tle-title" className="space-y-6 text-zinc-200">
      <header className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 sm:p-6">
        <h1 id="tle-title" className="text-xl font-semibold text-zinc-50">{t.heading}</h1>
        <p className="mt-2 text-sm text-zinc-300">{t.subtitle}</p>
        <p className="mt-3 rounded-lg border border-amber-700/70 bg-amber-950/30 p-3 text-sm text-amber-100">{t.notice}</p>
        <div role="group" aria-label={t.select} className="mt-5 flex flex-wrap gap-2">
          {([527, 528, 529] as const).map((id) => (
            <button
              key={id}
              type="button"
              aria-pressed={selectedId === id}
              aria-controls="tle-details"
              onClick={() => { setSelectedId(id); setCopyState('idle'); }}
              className={'rounded-lg border px-3 py-2 text-sm font-medium focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300 ' +
                (selectedId === id ? 'border-cyan-300 bg-cyan-800 text-white' : 'border-zinc-600 bg-zinc-950 text-zinc-200 hover:bg-zinc-800')}
            >
              NORAD {id}{id === 528 ? ' (' + t.target + ')' : ''}
            </button>
          ))}
        </div>
      </header>

      <div id="tle-details" aria-live="polite" className="space-y-5 rounded-xl border border-zinc-700 bg-zinc-900 p-4 sm:p-6">
        <h3 className="text-lg font-semibold">{sat.intlDesignator} · NORAD {selectedId}</h3>
        <h4 className="font-semibold text-zinc-100">{t.lines}</h4>
        {lines.map(({ line, expected, heading }) => {
          const result = auditTleSyntax(line, expected, selectedId);
          return (
            <div key={expected} className="space-y-2 rounded-lg border border-zinc-700 bg-zinc-950 p-3">
              <h5 className="text-sm font-semibold text-zinc-100">{heading}</h5>
              <pre className="max-w-full overflow-x-auto whitespace-pre rounded bg-zinc-900 p-3 font-mono text-xs text-cyan-200" tabIndex={0}><code>{line}</code></pre>
              <dl className="grid gap-2 text-xs text-zinc-300 sm:grid-cols-3">
                <div><dt>{t.length}</dt><dd className="font-mono text-zinc-100">{result.length}/69</dd></div>
                <div><dt>{t.prefix}</dt><dd className="font-semibold">{result.prefixMatches ? t.pass : t.fail}</dd></div>
                <div><dt>{t.check}</dt><dd className="font-mono text-zinc-100">{result.computedChecksum ?? t.noDigit} / {result.actualChecksum ?? t.noDigit}</dd></div>
              </dl>
              <p className={'text-xs font-semibold ' + (result.valid ? 'text-cyan-200' : 'text-rose-300')}>
                {t.label}: {result.valid ? t.valid : t.invalid}
              </p>
            </div>
          );
        })}
        <button type="button" onClick={copyTle} className="rounded border border-cyan-500 px-3 py-2 text-sm text-cyan-200 hover:bg-cyan-950 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2 focus-visible:outline-cyan-300">{t.copy}</button>
        <span role="status" className="ml-3 text-sm text-zinc-300">{copyState === 'copied' ? t.copied : copyState === 'failed' ? t.failed : ''}</span>

        <div className="rounded-lg border border-zinc-700 p-4">
          <h4 className="mb-3 font-semibold">{t.data}</h4>
          <dl className="grid gap-3 text-sm sm:grid-cols-3">
            <div><dt className="text-zinc-400">{t.epoch}</dt><dd className="mt-1 break-words font-mono text-zinc-100">{sat.epochStr}</dd></div>
            <div><dt className="text-zinc-400">{t.raan}</dt><dd className="mt-1 font-mono text-zinc-100">{selectedId === 528 ? `${sat.raanDeg.toFixed(4)}°` : t.unverified}</dd></div>
            <div><dt className="text-zinc-400">{t.bstar}</dt><dd className="mt-1 font-mono text-zinc-100">{sat.bstar.toExponential(3)}</dd></div>
          </dl>
        </div>
      </div>

      <aside aria-labelledby="tle-limit-title" className="rounded-xl border border-amber-800 bg-zinc-950 p-4 sm:p-6">
        <h3 id="tle-limit-title" className="font-semibold">{t.assumptions}</h3>
        <p className="mt-3 text-sm leading-relaxed text-zinc-300">{t.status}</p>
        <p className="mt-3 text-sm leading-relaxed text-zinc-300">{t.drag}</p>
        <p className="mt-3 text-sm leading-relaxed text-zinc-300">{t.nasa}</p>
        <p className="mt-3 font-semibold text-amber-200">{t.conclusion}</p>
        <nav aria-label={t.links} className="mt-4 flex flex-wrap gap-x-5 gap-y-3 text-sm">
          {[
            [t.matrix, MATRIX],
            [t.primary, NASA_BULLETIN],
            [t.catalog527, NASA_527_1964],
            [t.custody, 'https://github.com/franklinbaldo/conde-incident/pull/14'],
            [t.evidence, MATRIX_C179],
            [t.decay, MATRIX_C197],
            [t.holdout, MATRIX_COLLISIONS],
            [t.map, 'https://github.com/franklinbaldo/conde-incident/pull/28'],
          ].map(([label, href]) => (
            <a key={href} href={href} className="text-cyan-300 underline underline-offset-4 focus-visible:outline focus-visible:outline-2 focus-visible:outline-offset-2" {...(href.startsWith('https://') ? { target: '_blank', rel: 'noopener noreferrer' } : {})}>{label}</a>
          ))}
        </nav>
      </aside>
    </section>
  );
};

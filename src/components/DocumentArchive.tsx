import React from 'react';
import { ExternalLink, FileText, ShieldAlert } from 'lucide-react';
import { SourceCitationFeed } from './SourceCitationFeed';
import custody from '../../research/archive/wayback_pilot_2026-11-12.json';
import { negativeArchiveLabel } from '../lib/archiveCustodyLabel';
import { matrixOccurrenceUrl } from '../lib/sourceCitationAudit';

type Language = 'pt' | 'en';

// This guide is deliberately limited to established *documentary* claims.
// Line numbers refer to the immutable matrix snapshot used by SourceCitationFeed.
const guides = [
  {
    occurrence: 'C01#1',
    line: 19,
    title: { pt: 'Rádio Tupi, transcrita pelo FBIS', en: 'Radio Tupi, transcribed by FBIS' },
    finding: {
      pt: 'Há um relato de esfera em Conde. A transcrição comprova a circulação do relato, não uma observação física da esfera.',
      en: 'A sphere was reported in Conde. The transcript establishes circulation of the report, not physical observation of a sphere.',
    },
  },
  {
    occurrence: 'C05#1',
    line: 23,
    title: { pt: 'Despacho consular A-628', en: 'Consular dispatch A-628' },
    finding: {
      pt: 'O despacho menciona recortes baianos ainda não recuperados. Sua referência não equivale à leitura do jornal original.',
      en: 'The dispatch mentions Bahia clippings that have not been recovered. Its citation is not an inspection of the original newspaper.',
    },
  },
  {
    occurrence: 'C197#1',
    line: 905,
    title: { pt: 'NASA, Situation Report de 15/11/1963', en: 'NASA, Situation Report of 15 Nov 1963' },
    finding: {
      pt: 'A seção DECAYED OBJECTS registra 8 NOV 63 para 1963-003B. É uma data catalogada, sem horário ou localização de reentrada.',
      en: 'The DECAYED OBJECTS section records 8 NOV 63 for 1963-003B. This is a catalogued date, without a reentry time or location.',
    },
  },
] as const;

export const DocumentArchive: React.FC<{ lang: Language }> = ({ lang }) => {
  const pt = lang === 'pt';
  return (
    <section className="space-y-6 pb-10 [overflow-wrap:anywhere]" aria-labelledby="archive-heading">
      <header className="rounded-xl border border-zinc-700 bg-zinc-900 p-5 sm:p-7">
        <p className="flex items-center gap-2 text-xs font-mono uppercase tracking-wide text-cyan-300">
          <FileText className="h-4 w-4" aria-hidden="true" />
          {pt ? 'Arquivo e crítica de fontes' : 'Archive and source criticism'}
        </p>
        <h1 id="archive-heading" className="mt-2 text-2xl font-semibold text-zinc-50 sm:text-3xl">
          {pt ? 'Documentos, relatos e lacunas' : 'Documents, reports and gaps'}
        </h1>
        <p className="mt-3 max-w-3xl text-sm leading-relaxed text-zinc-300">
          {pt
            ? 'Este arquivo consulta ocorrências documentadas na matriz cumulativa, sem reproduzir citações literais que não foram cotejadas com o fac-símile. A autoria de uma notícia, a custódia de um documento e uma observação física são coisas diferentes.'
            : 'This archive uses documented occurrences in the cumulative matrix and does not reproduce quotations without checking them against a facsimile. News authorship, document custody and a physical observation are different things.'}
        </p>
        <p className="mt-3 flex items-start gap-2 text-sm leading-relaxed text-amber-200" role="note">
          <ShieldAlert className="mt-0.5 h-4 w-4 shrink-0" aria-hidden="true" />
          <span>{pt
            ? 'Estado científico: indeterminado. Nenhuma hora, coordenada, probabilidade ou impacto em Conde foi validado. Provas Lean são condicionais às premissas.'
            : 'Scientific status: undetermined. No reentry time, coordinates, probability or impact in Conde has been validated. Lean proofs are conditional on their premises.'}</span>
        </p>
      </header>

      <section className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 sm:p-6" aria-labelledby="archive-guide-heading">
        <h2 id="archive-guide-heading" className="text-lg font-semibold text-zinc-100">
          {pt ? 'Três leituras documentais, três limites' : 'Three documentary readings, three limits'}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-zinc-300">
          {pt
            ? 'São pontos de entrada para a matriz, não três testemunhas independentes nem estimativas orbitais.'
            : 'These are entry points into the matrix, not three independent witnesses or orbital estimates.'}
        </p>
        <div className="mt-4 grid gap-3 md:grid-cols-3">
          {guides.map((item) => (
            <article key={item.occurrence} className="rounded-lg border border-zinc-700 bg-zinc-950 p-4">
              <p className="font-mono text-xs text-cyan-300">{item.occurrence}</p>
              <h3 className="mt-1 text-sm font-semibold leading-snug text-zinc-100">{item.title[lang]}</h3>
              <p className="mt-2 text-sm leading-relaxed text-zinc-300">{item.finding[lang]}</p>
              <a href={matrixOccurrenceUrl(item.line)} target="_blank" rel="noopener noreferrer"
                className="mt-3 inline-flex items-center gap-1 text-sm text-cyan-300 underline underline-offset-4 hover:text-cyan-100 focus-visible:outline-2 focus-visible:outline-cyan-300">
                {pt ? 'Ver ocorrência na matriz' : 'Read occurrence in matrix'}
                <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
              </a>
            </article>
          ))}
        </div>
      </section>

      <SourceCitationFeed lang={lang} />

      <section aria-labelledby="custody-heading" className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 sm:p-6 space-y-4">
        <h2 id="custody-heading" className="text-lg font-semibold text-zinc-100">
          {pt ? 'Custódia digital não é nova testemunha' : 'Digital custody is not new testimony'}
        </h2>
        <p className="text-sm text-zinc-300">
          {pt ? 'Capturas Wayback preservam PDFs, mas não verificam sensores de 1963 ou eventos em Conde.'
              : 'Wayback captures preserve PDFs but do not verify 1963 sensors or events in Conde.'}
        </p>
        <ul className="grid gap-3 md:grid-cols-2">
          {custody.records.filter(r => r.status === 'VERIFIED_REPLAY' && r.archived_url).map(r => (
            <li key={r.id} className="rounded-lg border border-zinc-700 bg-zinc-950 p-4 space-y-2">
              <h3 className="text-sm font-semibold text-zinc-100">
                {r.id === 'WB-NORAD-1963-H2' ? (pt ? 'Resumo institucional NORAD' : 'NORAD institutional summary')
                  : (pt ? 'Inventário Smithsonian RU301' : 'Smithsonian RU301 inventory')}
              </h3>
              <p className="text-xs text-zinc-300">{pt ? 'Capturado em ' : 'Captured at '}
                <time dateTime={r.capture_utc ?? undefined}>{r.capture_utc?.replace('T', ' ').replace('Z', ' UTC')}</time>
              </p>
              <a href={r.archived_url ?? undefined} target="_blank" rel="noopener noreferrer"
                className="text-sm text-cyan-300 underline focus-visible:outline-2 focus-visible:outline-cyan-300">
                {pt ? 'Abrir cópia preservada' : 'Open preserved copy'}
              </a>
              <details className="text-xs text-zinc-300">
                <summary className="cursor-pointer">{pt ? 'Proveniência e SHA-256' : 'Provenance and SHA-256'}</summary>
                <p className="mt-2 font-mono break-all">{r.replay?.sha256}</p>
                <a href={r.original_url} target="_blank" rel="noopener noreferrer" className="break-all underline">{r.original_url}</a>
              </details>
            </li>
          ))}
        </ul>
        {custody.records.filter(r => r.status === 'NO_EXACT_CAPTURE_IN_QUERIED_INDEX').map(r => (
          <p key={r.id} role="note" className="rounded border border-amber-900 p-3 text-sm text-amber-100">
            <strong>{negativeArchiveLabel(r)}:</strong> {pt
              ? 'sem captura da URL exata nos índices consultados; isso não prova ausência do documento.'
              : 'no exact-URL capture in queried indexes; this does not prove the document is absent.'}
          </p>
        ))}
        <p className="text-xs text-zinc-400">
          {pt ? 'Auditoria em ' : 'Audit at '}<time dateTime={custody.audit_utc}>{custody.audit_utc.replace('T', ' ').replace('Z', ' UTC')}</time>.
          {' '}<a href="https://github.com/franklinbaldo/conde-incident/blob/main/research/archive/wayback_pilot_2026-11-12.json"
            target="_blank" rel="noopener noreferrer" className="text-cyan-300 underline">
            {pt ? 'Manifesto e limitações' : 'Manifest and limitations'}
          </a>
        </p>
      </section>



      <section className="rounded-xl border border-zinc-700 bg-zinc-900 p-4 sm:p-6" aria-labelledby="archive-gaps-heading">
        <h2 id="archive-gaps-heading" className="text-lg font-semibold text-zinc-100">
          {pt ? 'Fontes e verificações ainda abertas' : 'Sources and checks still outstanding'}
        </h2>
        <p className="mt-2 text-sm leading-relaxed text-zinc-300">
          {pt
            ? 'O dossiê Blue Book de Conde foi localizado na NARA (NAID 302531012), com três imagens da mesma unidade documental. A ficha administrativa e as mensagens não são três testemunhas nem comprovam exame físico em Conde. A edição original de O Globo de 08/11/1963, mencionada em mensagem de 14/11, continua por recuperar.'
            : 'The Conde Blue Book file was located at NARA (NAID 302531012), with three images of one documentary unit. Its administrative card and messages are not three witnesses or proof of a physical examination in Conde. The original 8 Nov 1963 O Globo issue, mentioned in a 14 Nov message, remains unrecovered.'}
        </p>
        <a href="https://catalog.archives.gov/id/302531012" target="_blank" rel="noopener noreferrer"
          className="mt-3 inline-flex items-center gap-1 text-sm text-cyan-300 underline underline-offset-4 focus-visible:outline-2 focus-visible:outline-cyan-300">
          {pt ? 'Abrir unidade documental NARA' : 'Open NARA documentary unit'}
          <ExternalLink className="h-3.5 w-3.5" aria-hidden="true" />
        </a>
      </section>
    </section>
  );
};

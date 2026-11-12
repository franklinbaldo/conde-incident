import React, { useState } from 'react';
import {
  FileText,
  ShieldCheck,
  Search,
  ExternalLink,
  Tag,
  AlertTriangle,
  Info,
  Calendar,
  Building,
  CheckCircle2,
  HelpCircle,
} from 'lucide-react';
import { EPISTEMIC_AUDIT_LOG } from '../lib/constants';
import { SourceCitationFeed } from './SourceCitationFeed';
import { EpistemicClassification } from '../types/astrodynamics';

interface DocumentArchiveProps {
  lang: 'pt' | 'en';
}

interface HistoricalDoc {
  id: string;
  titlePt: string;
  titleEn: string;
  dateStr: string;
  authorAgency: string;
  classification: EpistemicClassification;
  summaryPt: string;
  summaryEn: string;
  transcriptExcerpt: string;
  epistemicAnalysisPt: string;
  epistemicAnalysisEn: string;
}

export const DocumentArchive: React.FC<DocumentArchiveProps> = ({ lang }) => {
  const isPt = lang === 'pt';
  const [filterClass, setFilterClass] = useState<string>('ALL');
  const [searchTerm, setSearchTerm] = useState<string>('');

  const documents: HistoricalDoc[] = [
    {
      id: 'DOC-01',
      titlePt: 'NASA Satellite Situation Report (Vol. 3, No. 22)',
      titleEn: 'NASA Satellite Situation Report (Vol. 3, No. 22)',
      dateStr: '1963-11-15',
      authorAgency: 'NASA Goddard Space Flight Center',
      classification: 'DOCUMENTO_PRIMARIO_VERIFICADO',
      summaryPt: 'Boletim quinzenal oficial que lista todos os objetos em órbita conhecidos até 15 de novembro de 1963.',
      summaryEn: 'Official bi-weekly bulletin listing all active objects in Earth orbit as of 15 November 1963.',
      transcriptExcerpt: 'Page 4: 1963-003A (OPS 0180) listed in orbit. 1963-003C listed in orbit. 1963-003B is ABSENT from the active table.',
      epistemicAnalysisPt: 'A ausência do 528 confirma que seu decaimento já havia sido reconhecido antes de 15 de novembro. Contudo, NÃO prova que a reentrada ocorreu precisamente em 08 de novembro — tal data deriva de catálogo retrospectivo.',
      epistemicAnalysisEn: 'The absence of 528 confirms its decay had occurred prior to Nov 15. However, it does NOT independently prove decay occurred precisely on Nov 8; that date stems from retrospective catalogs.',
    },
    {
      id: 'DOC-02',
      titlePt: 'Telegrama Diplomático: Embaixada dos EUA no Rio de Janeiro',
      titleEn: 'Diplomatic Cable: US Embassy Rio de Janeiro',
      dateStr: '1963-11-14',
      authorAgency: 'U.S. Department of State / Foreign Service',
      classification: 'DOCUMENTO_PRIMARIO_VERIFICADO',
      summaryPt: 'Primeira comunicação confidencial entre a embaixada no Rio e o Departamento de Estado após a repercussão da notícia da Rádio Tupi.',
      summaryEn: 'First confidential communication between Rio Embassy and State Dept following Radio Tupi broadcast news.',
      transcriptExcerpt: 'TO SECSTATE WASHDC: Press reports from Rio de Janeiro allege discovery of metallic sphere near Conde, Bahia. Requesting immediate verification from Consulate Salvador and Brazilian Air Force contacts.',
      epistemicAnalysisPt: 'Documento primário verificado. Demonstra que o governo americano tomou conhecimento da história via rádio comercial e iniciou averiguação de segurança de imediato.',
      epistemicAnalysisEn: 'Verified primary document. Proves the US government learned of the claim through commercial radio and immediately initiated security checks.',
    },
    {
      id: 'DOC-03',
      titlePt: 'Relatório Final do Consulado dos EUA em Salvador: "The Aircraft That Wasn\'t There"',
      titleEn: 'US Consulate Salvador Final Report: "The Aircraft That Wasn\'t There"',
      dateStr: '1963-11-20',
      authorAgency: 'U.S. Consulate Salvador, Bahia',
      classification: 'DOCUMENTO_PRIMARIO_VERIFICADO',
      summaryPt: 'Investigação local e relatório formal do cônsul americano após averiguações com o Ministério da Aeronáutica e autoridades policiais baianas.',
      summaryEn: 'Local investigation and formal report by US Consul after inquiries with Brazilian Air Force and Bahia police.',
      transcriptExcerpt: 'Investigation conducted with local authorities, reporters, and Ministry of Aeronautics confirms story is entirely groundless. No crater, no sphere, no witnesses found in Conde. Story originated as irresponsible sensationalism in Rio press.',
      epistemicAnalysisPt: 'Documento primário verificado. Registra que as inspeções locais coordenadas com o Ministério da Aeronáutica e autoridades policiais baianas nos dias subsequentes não encontraram cratera, destroços ou testemunhas presenciais em Conde, indicando ausência de suporte empírico para o relato material.',
      epistemicAnalysisEn: 'Verified primary document. Records that local inspections conducted with the Brazilian Air Force and Bahia police found no crater, debris, or eyewitnesses in Conde, indicating lack of empirical support for the material event.',
    },
    {
      id: 'DOC-04',
      titlePt: 'Transcrição FBIS: Transmissão da Rádio Tupi (Rio de Janeiro)',
      titleEn: 'FBIS Transcript: Radio Tupi Broadcast (Rio de Janeiro)',
      dateStr: '1963-11-08',
      authorAgency: 'Foreign Broadcast Information Service (FBIS / CIA)',
      classification: 'DOCUMENTO_PRIMARIO_VERIFICADO',
      summaryPt: 'Interceptação e transcrição oficial pelo serviço de monitoramento do governo dos EUA da transmissão radiofônica contemporânea.',
      summaryEn: 'Official intercept and transcript by US government monitoring service of the contemporary radio broadcast.',
      transcriptExcerpt: 'Radio Tupi reports: Large metallic sphere landed in central Conde, Bahia, creating 4-meter crater. Heavy glass windows, unrecognizable writing, and dead human-like body in heavy pressurized suit alleged inside.',
      epistemicAnalysisPt: 'A interceptação é um documento primário genuíno; no entanto, o seu CONTEÚDO representa um relato jornalístico preliminar que não contou com verificação astronômica ou física independente.',
      epistemicAnalysisEn: 'The intercept is a genuine primary record; however, its CONTENT represents a preliminary journalistic report lacking independent astronomical or physical verification.',
    },
    {
      id: 'DOC-05',
      titlePt: 'Catálogo de Elementos Orbitais NORAD 528 (Registro S00528)',
      titleEn: 'NORAD 528 Orbital Element Catalog (Record S00528)',
      dateStr: '1963-10-27',
      authorAgency: 'US Air Force Space Command / Space-Track',
      classification: 'FONTE_SECUNDARIA',
      summaryPt: 'Conjunto de elementos orbitais históricos para 1963-003B com época em 27/10/1963 e data catalogada de reentrada em 08/11/1963.',
      summaryEn: 'Historical orbital element set for 1963-003B with epoch 27/10/1963 and cataloged reentry date 08/11/1963.',
      transcriptExcerpt: 'Epoch: 63300.61111111 (1963 Oct 27 14:40:00 UTC). Inc: 81.8615 deg, MM: 15.7490 rev/day, BSTAR: 0.00000. Decay: 1963-11-08.',
      epistemicAnalysisPt: 'Catálogo retrospectivo derivado. O BSTAR = 0 reflete convenção manual de catálogo não-ajustado, e não ausência de arrasto físico.',
      epistemicAnalysisEn: 'Retrospective derived catalog. BSTAR = 0 represents an uncalibrated placeholder convention in manual tracking, not zero physical drag.',
    },
    {
      id: 'DOC-06',
      titlePt: 'Dossiê Desclassificado da NRO: Missão 7153 (Veículo 2313)',
      titleEn: 'NRO Declassified Mission Log: Mission 7153 (Vehicle 2313)',
      dateStr: '1963-01-16',
      authorAgency: 'National Reconnaissance Office (NRO) / SAFSP',
      classification: 'DOCUMENTO_PRIMARIO_VERIFICADO',
      summaryPt: 'Registro do lançamento Thor-Agena D carregando o satélite militar Ferret 3 (OPS 0180) para inteligência eletrônica.',
      summaryEn: 'Flight record of Thor-Agena D carrying secret military Ferret 3 (OPS 0180) ELINT payload.',
      transcriptExcerpt: 'Vehicle 2313 successfully launched into polar orbit 16 Jan 1963 from SLC-2W. Orbit achieved: 81.85 deg. Primary payload battery depletion observed after short mission.',
      epistemicAnalysisPt: 'Comprova a identidade militar secreta do lançamento e a natureza do satélite principal (527) e dos componentes descartados no estágio (528 e 529).',
      epistemicAnalysisEn: 'Proves the classified military nature of the launch and establishes the identities of main payload (527) and discarded stage hardware (528, 529).',
    },
  ];

  const filteredDocs = documents.filter((doc) => {
    const matchesClass = filterClass === 'ALL' || doc.classification === filterClass;
    const matchesSearch =
      doc.titlePt.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.titleEn.toLowerCase().includes(searchTerm.toLowerCase()) ||
      doc.authorAgency.toLowerCase().includes(searchTerm.toLowerCase());
    return matchesClass && matchesSearch;
  });

  return (
    <div className="space-y-6">
      {/* Intro Header */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-6">
        <div className="space-y-1 max-w-3xl">
          <div className="inline-flex items-center gap-1.5 px-2.5 py-0.5 rounded-full bg-cyan-950/80 border border-cyan-800 text-cyan-300 text-xs font-mono">
            <FileText className="w-3.5 h-3.5 text-cyan-400" />
            <span>{isPt ? 'ARQUIVO DOCUMENTAL & CRÍTICA DE FONTES' : 'DOCUMENT ARCHIVE & SOURCE CRITICISM'}</span>
          </div>
          <h2 className="text-lg font-bold text-zinc-100">
            {isPt
              ? 'Dossiê Histórico e Auditoria Epistemológica'
              : 'Historical Dossier & Epistemological Audit'}
          </h2>
          <p className="text-xs text-zinc-300 leading-relaxed">
            {isPt
              ? 'Todo fato científico exige classificação explícita de proveniência. Não tratamos catálogos derivados como observações primárias nem notícias de rádio como dados astronômicos. Examine abaixo os documentos desclassificados e relatórios oficiais que fundamentam a reconstrução.'
              : 'Every scientific fact demands explicit provenance classification. We treat neither derived catalogs as primary observations nor commercial radio broadcasts as astronomical data. Inspect declassified records and official reports below.'}
          </p>
        </div>
      </div>

      {/* Curated documentary context is independent of the legacy illustrative dossier cards. */}
      <SourceCitationFeed lang={lang} />

      {/* Epistemological Badges Legend */}
      <div className="grid grid-cols-2 md:grid-cols-4 gap-3 text-xs">
        <div className="p-3 rounded-lg bg-zinc-900 border border-emerald-800/60">
          <div className="text-emerald-400 font-bold font-mono text-[11px]">
            DOCUMENTO PRIMÁRIO VERIFICADO
          </div>
          <p className="text-zinc-400 text-[11px] mt-1">
            Registro original de época (NASA SSR, telegrama consular, NRO log) consultado diretamente.
          </p>
        </div>

        <div className="p-3 rounded-lg bg-zinc-900 border border-cyan-800/60">
          <div className="text-cyan-400 font-bold font-mono text-[11px]">
            FONTE SECUNDÁRIA
          </div>
          <p className="text-zinc-400 text-[11px] mt-1">
            Catálogos orbitais derivados, transcrições posteriores e compilações históricas.
          </p>
        </div>

        <div className="p-3 rounded-lg bg-zinc-900 border border-amber-800/60">
          <div className="text-amber-400 font-bold font-mono text-[11px]">
            INFERÊNCIA DINÂMICA
          </div>
          <p className="text-zinc-400 text-[11px] mt-1">
            Propagações matemáticas calculadas (SGP4, J2, arrasto, teste inverso, Monte Carlo).
          </p>
        </div>

        <div className="p-3 rounded-lg bg-zinc-900 border border-rose-800/60">
          <div className="text-rose-400 font-bold font-mono text-[11px]">
            HIPÓTESE
          </div>
          <p className="text-zinc-400 text-[11px] mt-1">
            Proposição teórica a ser submetida a teste de falsificação e verificação física.
          </p>
        </div>
      </div>

      {/* Filter Bar */}
      <div className="bg-zinc-900 border border-zinc-800 rounded-xl p-4 flex flex-col sm:flex-row items-center justify-between gap-3 text-xs">
        <div className="relative w-full sm:w-80">
          <Search className="w-4 h-4 text-zinc-500 absolute left-3 top-2.5" />
          <input
            type="text"
            placeholder={isPt ? 'Filtrar documentos por título ou órgão...' : 'Search by title or agency...'}
            value={searchTerm}
            onChange={(e) => setSearchTerm(e.target.value)}
            className="w-full bg-zinc-950 border border-zinc-800 rounded-lg pl-9 pr-3 py-2 text-zinc-200 placeholder-zinc-500 focus:outline-none focus:border-cyan-500"
          />
        </div>

        <div className="flex items-center gap-1.5 w-full sm:w-auto overflow-x-auto pb-1 sm:pb-0 font-mono text-[11px]">
          <button
            onClick={() => setFilterClass('ALL')}
            className={`px-3 py-1.5 rounded transition-colors cursor-pointer whitespace-nowrap ${
              filterClass === 'ALL'
                ? 'bg-zinc-800 text-white font-bold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Todos ({documents.length})
          </button>
          <button
            onClick={() => setFilterClass('DOCUMENTO_PRIMARIO_VERIFICADO')}
            className={`px-3 py-1.5 rounded transition-colors cursor-pointer whitespace-nowrap ${
              filterClass === 'DOCUMENTO_PRIMARIO_VERIFICADO'
                ? 'bg-emerald-950 border border-emerald-800 text-emerald-300 font-bold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Primários
          </button>
          <button
            onClick={() => setFilterClass('FONTE_SECUNDARIA')}
            className={`px-3 py-1.5 rounded transition-colors cursor-pointer whitespace-nowrap ${
              filterClass === 'FONTE_SECUNDARIA'
                ? 'bg-cyan-950 border border-cyan-800 text-cyan-300 font-bold'
                : 'text-zinc-400 hover:text-zinc-200'
            }`}
          >
            Secundários
          </button>
        </div>
      </div>

      {/* Document Cards List */}
      <div className="space-y-4">
        {filteredDocs.map((doc) => (
          <div
            key={doc.id}
            className="bg-zinc-900 border border-zinc-800 rounded-xl p-5 space-y-4 hover:border-zinc-700 transition-colors"
          >
            <div className="flex flex-col sm:flex-row sm:items-center justify-between gap-2 border-b border-zinc-800/80 pb-3">
              <div className="space-y-0.5">
                <div className="flex items-center gap-2">
                  <span className="font-mono text-xs font-bold text-cyan-400">{doc.id}</span>
                  <span className="text-zinc-500 font-mono">|</span>
                  <span className="text-xs font-mono text-zinc-400 flex items-center gap-1">
                    <Calendar className="w-3.5 h-3.5" />
                    {doc.dateStr}
                  </span>
                  <span className="text-zinc-500 font-mono">|</span>
                  <span className="text-xs text-zinc-400 font-medium flex items-center gap-1">
                    <Building className="w-3.5 h-3.5 text-zinc-500" />
                    {doc.authorAgency}
                  </span>
                </div>
                <h3 className="text-base font-bold text-zinc-100">
                  {isPt ? doc.titlePt : doc.titleEn}
                </h3>
              </div>

              <span
                className={`text-[10px] px-2.5 py-1 rounded font-mono font-bold border self-start sm:self-auto ${
                  doc.classification === 'DOCUMENTO_PRIMARIO_VERIFICADO'
                    ? 'text-emerald-400 bg-emerald-950/60 border-emerald-800'
                    : doc.classification === 'FONTE_SECUNDARIA'
                    ? 'text-cyan-400 bg-cyan-950/60 border-cyan-800'
                    : 'text-amber-400 bg-amber-950/60 border-amber-800'
                }`}
              >
                {doc.classification}
              </span>
            </div>

            <p className="text-xs text-zinc-300 leading-relaxed">
              {isPt ? doc.summaryPt : doc.summaryEn}
            </p>

            {/* Transcript Quote */}
            <div className="p-3 rounded-lg bg-zinc-950 border border-zinc-800/80 text-xs font-mono text-zinc-300 border-l-4 border-l-cyan-500">
              <div className="text-[10px] text-zinc-500 uppercase tracking-wider mb-1">
                {isPt ? 'Trecho Documental Original' : 'Original Document Excerpt'}
              </div>
              <p className="italic">{doc.transcriptExcerpt}</p>
            </div>

            {/* Epistemic Evaluation */}
            <div className="p-3 rounded-lg bg-zinc-950/60 border border-zinc-800/60 text-xs text-zinc-400 space-y-1">
              <strong className="text-zinc-300 font-semibold text-[11px] flex items-center gap-1.5">
                <ShieldCheck className="w-3.5 h-3.5 text-cyan-400" />
                <span>{isPt ? 'Avaliação Epistemológica' : 'Epistemological Assessment'}</span>
              </strong>
              <p className="leading-relaxed text-[11px]">
                {isPt ? doc.epistemicAnalysisPt : doc.epistemicAnalysisEn}
              </p>
            </div>
          </div>
        ))}
      </div>

      {/* Missing Information Wishlist (Section 7 and 11 of Handoff) */}
      <div className="p-5 rounded-xl bg-zinc-900 border border-cyan-900/60 space-y-3">
        <h4 className="text-sm font-bold text-cyan-200 flex items-center gap-2">
          <HelpCircle className="w-4 h-4 text-cyan-400" />
          <span>{isPt ? 'Documentos Pendentes Capazes de Sanar a Incerteza Restante' : 'Missing Documents Capable of Resolving Remaining Uncertainty'}</span>
        </h4>
        <div className="text-xs text-zinc-300 space-y-2 leading-relaxed">
          <p>
            Para converter o veredito atual (<strong>Critério B: Compatibilidade Restrita / Não-Identificabilidade de Fase Final</strong>) em uma localização orbital irrefutável, seriam necessários:
          </p>
          <ul className="list-disc list-inside space-y-1 pl-2 text-zinc-400 font-mono text-[11px]">
            <li>
              <strong className="text-zinc-200">1. Boletins Diários de Rastreamento SPADATS / AFSPC</strong> entre 01/11 e 08/11/1963 com registros de passagens por radar de Shepard AFB, BMEWS ou Eglin AFB.
            </li>
            <li>
              <strong className="text-zinc-200">2. Registros da Rede de Câmeras Baker-Nunn (SAO)</strong> das estações do hemisfério sul (especialmente Natal-RN, Villa Dolores na Argentina ou Arequipa no Peru).
            </li>
            <li>
              <strong className="text-zinc-200">3. Relatório de Desaparecimento de Catálogo da Força Aérea dos EUA (USAF TIP - Tracking and Impact Prediction)</strong> de novembro de 1963.
            </li>
          </ul>
        </div>
      </div>
    </div>
  );
};

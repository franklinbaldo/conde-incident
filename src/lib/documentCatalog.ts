// Editorial inventory derived from the cumulative matrix in PR #1.
// A primary document about a report is NOT a primary observation of an impact.
// Links are fixed to reviewed snapshots rather than silently following another branch.
export type Locale = 'pt' | 'en';
export type Localized = Record<Locale, string>;
export type ArchiveKind = 'contemporary' | 'derived' | 'locator';
export interface ArchiveEntry {
  id: string;
  date: string;
  title: Localized;
  agency: string;
  kind: ArchiveKind;
  matrixIds: string;
  matrixUrl: string;
  originalUrl: string;
  evidenceHref: string;
  finding: Localized;
  provenance: Localized;
  limitation: Localized;
}

export const matrixSnapshot = 'https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md';

export const archiveEntries: readonly ArchiveEntry[] = [
  {
    id: 'doc-01', date: '1963-11-15', kind: 'contemporary',
    title: { pt: 'NASA: Satellite Situation Report, vol. 3, nº 22', en: 'NASA: Satellite Situation Report, vol. 3, no. 22' },
    agency: 'NASA / Goddard Space Flight Center', matrixIds: 'C197–C202',
    matrixUrl: matrixSnapshot + '#L901-L912',
    originalUrl: 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf',
    evidenceHref: '#/research/c197',
    finding: {
      pt: 'Na lista DECAYED OBJECTS, o boletim de 15/11/1963 registra 1963-003B com dia de decaimento em 8/11/1963.',
      en: 'In DECAYED OBJECTS, the November 15, 1963 bulletin records a November 8 decay date for 1963-003B.',
    },
    provenance: {
      pt: 'Fac-símile da NASA identificado e inspecionado na matriz C197; ficha NTRS C198 refere-se ao mesmo documento, não a outra medição.',
      en: 'NASA facsimile identified and inspected in matrix C197; NTRS metadata C198 describes the same record, not another measurement.',
    },
    limitation: {
      pt: 'Data registrada, sem hora, coordenadas, trajetória terminal ou vínculo físico com Conde. NASA/NORAD podem compartilhar rastreamento (C201).',
      en: 'Recorded day only: no time, coordinates, terminal trajectory or physical link to Conde. NASA/NORAD may share tracking sources (C201).',
    },
  },
  {
    id: 'doc-02', date: '1963-11-14', kind: 'contemporary',
    title: { pt: 'DOS-UAP-D001: comunicação diplomática de 14/11', en: 'DOS-UAP-D001: November 14 diplomatic cable' },
    agency: 'U.S. Department of State', matrixIds: 'C08, C15',
    matrixUrl: matrixSnapshot + '#L26-L33',
    originalUrl: 'https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf',
    evidenceHref: '#/research',
    finding: {
      pt: 'O telegrama documenta uma consulta diplomática e relata informação recebida por ligação telefônica de qualidade ruim.',
      en: 'The cable documents a diplomatic inquiry and information received during a poor-quality telephone call.',
    },
    provenance: {
      pt: 'Fac-símile diplomático citado como diretamente inspecionado na matriz. Informação telefônica é mediada, não observação in loco.',
      en: 'Diplomatic facsimile reported as directly inspected in the matrix. The telephone account is mediated, not an on-site observation.',
    },
    limitation: {
      pt: 'Não confirma objeto no solo, observação independente ou contato direto com testemunha identificada.',
      en: 'Does not confirm a ground object, independent sighting or direct contact with an identified witness.',
    },
  },
  {
    id: 'doc-03', date: '1963-11-20', kind: 'contemporary',
    title: { pt: 'DOS-UAP-D002: despacho consular A-628', en: 'DOS-UAP-D002: consular dispatch A-628' },
    agency: 'U.S. Consulate, Salvador', matrixIds: 'C05–C06, C09–C10',
    matrixUrl: matrixSnapshot + '#L23-L28',
    originalUrl: 'https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf',
    evidenceHref: '#/research',
    finding: {
      pt: 'O despacho relata respostas de autoridades e menciona dois recortes de jornais baianos encaminhados por malote.',
      en: 'The dispatch reports official responses and mentions two Bahia newspaper clippings forwarded by diplomatic pouch.',
    },
    provenance: {
      pt: 'Fac-símile diplomático de duas páginas citado na matriz; os recortes originais e depoimentos locais não estão anexados à cópia disponível.',
      en: 'Two-page diplomatic facsimile cited in the matrix; the source clippings and local interviews are not attached to the accessible copy.',
    },
    limitation: {
      pt: 'Uma avaliação consular ou negativa relatada não equivale a inspeção física independente demonstrada por documentação primária.',
      en: 'A reported consular assessment or denial is not independently documented physical inspection.',
    },
  },
  {
    id: 'doc-04', date: '1963-11-08/09', kind: 'contemporary',
    title: { pt: 'Tupi → FBIS: registro de uma notícia', en: 'Tupi → FBIS: record of a broadcast report' },
    agency: 'Rádio Tupi / Foreign Broadcast Information Service', matrixIds: 'C01–C03',
    matrixUrl: matrixSnapshot + '#L19-L21',
    originalUrl: 'https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf',
    evidenceHref: '#/research/c01',
    finding: {
      pt: 'O fac-símile preserva a notícia de esfera, cratera, inscrições e corpo como elementos do mesmo relato de rádio.',
      en: 'The facsimile preserves sphere, crater, inscriptions and body as claims in the same radio report.',
    },
    provenance: {
      pt: 'Tupi → transcrição FBIS → reprodução documental: uma cadeia jornalística, não três testemunhas independentes.',
      en: 'Tupi → FBIS transcript → documentary reproduction: one reporting chain, not three independent witnesses.',
    },
    limitation: {
      pt: 'A gravação original e uma observação material em Conde não foram verificadas; o carimbo 2330 não identifica a hora da queda.',
      en: 'The original audio and physical observation at Conde remain unverified; the 2330 timestamp does not date an impact.',
    },
  },
  {
    id: 'doc-05', date: '1963-10-27 (época atribuída)', kind: 'derived',
    title: { pt: 'NORAD 528: elementos orbitais sob auditoria', en: 'NORAD 528: orbital elements under audit' },
    agency: 'Dados de aplicativo / investigação de custódia', matrixIds: 'C191, C194 e conflito RAAN',
    matrixUrl: matrixSnapshot + '#L872-L875',
    originalUrl: 'https://github.com/franklinbaldo/conde-incident/pull/14',
    evidenceHref: '#/research/raan',
    finding: {
      pt: 'O laboratório contém linhas TLE não autenticadas e duas referências de RAAN incompatíveis sem conciliação de épocas.',
      en: 'The laboratory contains unauthenticated TLE lines and conflicting RAAN references with unreconciled epochs.',
    },
    provenance: {
      pt: 'Valores de aplicação e espelhos derivados; PR #14 audita origem e checksums. Nenhum TLE primário é certificado por esta ficha.',
      en: 'Application values and derivative mirrors; PR #14 audits custody and checksums. This entry certifies no primary TLE.',
    },
    limitation: {
      pt: 'Checksum válido não autentica observação, arrasto, posição terminal ou impacto. Sem domínio físico admissível validado.',
      en: 'Valid checksum does not authenticate observation, drag, terminal position or impact. No validated physical admissible domain.',
    },
  },
  {
    id: 'doc-06', date: '1994 (compilação retrospectiva)', kind: 'derived',
    title: { pt: 'NRO: The SIGINT Satellite Story', en: 'NRO: The SIGINT Satellite Story' },
    agency: 'National Reconnaissance Office', matrixIds: 'C54–C55',
    matrixUrl: matrixSnapshot + '#L194-L195',
    originalUrl: 'https://www.nro.gov/Portals/65/documents/foia/declass/HISTORICALLY%20SIGNIFICANT%20DOCs/NRO%2060th%20Anniversary%20Docs/SC-2021-00003_C05134315.pdf',
    evidenceHref: '#/research',
    finding: {
      pt: 'Compilação institucional posterior relaciona o lançamento 1963-003A à missão 7153 e ao programa Ferret.',
      en: 'A later institutional history relates the 1963-003A launch to mission 7153 and the Ferret programme.',
    },
    provenance: {
      pt: 'História institucional retrospectiva de 1994, não um diário operacional de janeiro de 1963.',
      en: 'A retrospective institutional history from 1994, not a January 1963 operational log.',
    },
    limitation: {
      pt: 'Não identifica com documentação primária a natureza de cada componente 528/529 nem qualquer evento em Conde.',
      en: 'Does not identify every 528/529 component through primary records or establish any event at Conde.',
    },
  },
  {
    id: 'doc-07', date: '1963-11-09 (edição citada)', kind: 'locator',
    title: { pt: 'Diário de Notícias (Salvador): recorte pendente', en: 'Diário de Notícias (Salvador): missing clipping' },
    agency: 'Diário de Notícias / acervo IGHB', matrixIds: 'C05, C209',
    matrixUrl: matrixSnapshot + '#L23-L23',
    originalUrl: 'https://www.ighb.org.br/biblioteca',
    evidenceHref: '#/research',
    finding: {
      pt: 'O despacho A-628 cita um recorte com negativa de autoridades; o jornal dessa data não foi lido diretamente.',
      en: 'Dispatch A-628 cites a clipping reporting an official denial; the original issue has not been read directly.',
    },
    provenance: {
      pt: 'Localizador de acervo por título, não fac-símile do fascículo nem leitura da página de 9/11.',
      en: 'Collection-level locator, not a facsimile or reading of the November 9 issue.',
    },
    limitation: {
      pt: 'Não se pode atribuir conteúdo literal ao recorte ausente nem contá-lo como testemunha independente sem leitura.',
      en: 'No verbatim content can be assigned to the missing clipping or counted as independent testimony.',
    },
  },
  {
    id: 'doc-08', date: '1963-11-11 (edição citada)', kind: 'locator',
    title: { pt: 'Jornal da Bahia: recorte pendente', en: 'Jornal da Bahia: missing clipping' },
    agency: 'Jornal da Bahia / acervo IGHB', matrixIds: 'C06, C205, C209',
    matrixUrl: matrixSnapshot + '#L24-L24',
    originalUrl: 'https://www.ighb.org.br/biblioteca',
    evidenceHref: '#/research',
    finding: {
      pt: 'O A-628 menciona uma reportagem local; seu texto e suas fontes ainda não foram inspecionados.',
      en: 'A-628 mentions local reporting; its text and sources have not been inspected.',
    },
    provenance: {
      pt: 'Inventário de coleção e citação diplomática, não exemplar original da edição de 11/11.',
      en: 'Collection inventory and diplomatic reference, not an original copy of the November 11 issue.',
    },
    limitation: {
      pt: 'Independência empresarial não é observação independente. Não afirmar o que a página original dizia.',
      en: 'Separate ownership does not mean independent observation. The original page content is not established.',
    },
  },
];

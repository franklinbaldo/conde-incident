/** Reviewed editorial readings of canonical documentary statuses.
 * The canonical code is never rewritten; an unknown code must be reviewed.
 * These labels describe sources, not independent physical observations.
 */
const readings = Object.freeze({
  '1963_DOCUMENT_DATE_ONLY_NO_TERMINAL_PLACE': [
    'Data catalogada, sem local de queda',
    'Documento de catálogo registra uma data de decaimento para o objeto.',
    'Não localiza a reentrada, sua hora nem um fragmento em Conde.'
  ],
  'CATALOGUE_ENTRY_SAME_WORK': [
    'Ficha da mesma obra documental',
    'Metadados de acervo remetem à mesma publicação já citada.',
    'Não representam uma segunda medição independente.'
  ],
  'DERIVED_AGGREGATOR': [
    'Agregação derivada',
    'Série reunida por terceiro, útil para contexto e conferência.',
    'Não acrescenta uma terceira fonte primária independente.'
  ],
  'EXTERNAL_METADATA_NOT_ORIGINAL_AND_NOT_CROSSWALKED': [
    'Metadado externo sem equivalência confirmada',
    'Registro de plataforma externa ainda sem ligação documental demonstrada.',
    'Não identifica por si só o mesmo processo do acervo original.'
  ],
  'HISTORICAL_WIND_MEASUREMENT_RECIFE_NOT_CONDE': [
    'Medição histórica de vento em Recife',
    'Registro instrumental meteorológico situado em Recife.',
    'Não mede o vento em Conde nem comprova transporte de fragmentos.'
  ],
  'HISTORIC_INSTRUMENTAL_INDEX': [
    'Índice geofísico instrumental',
    'Série instrumental de contexto físico histórico.',
    'Não é uma medição da órbita nem identifica objeto ou queda.'
  ],
  'NARA_ORIGINAL_DIGITAL_OBJECT_VISUALLY_INSPECTED_BY_LONTRA_NOT_FIELD_OBSERVATION': [
    'Peça digital original examinada',
    'Ficha de acervo conferida visualmente, com conteúdo documental próprio.',
    'Não equivale a observação de campo ou constatação física do relato.'
  ],
  'OFFICIAL_GENERAL_ARCHIVAL_GUIDE': [
    'Guia geral de acervo',
    'Orientação oficial sobre séries e organização documental.',
    'Não comprova a existência ou conteúdo da peça específica.'
  ],
  'ORIGINAL_DIPLOMATIC_SUMMARY_CLIPPINGS_NOT_INSPECTED': [
    'Resumo diplomático, recortes não examinados',
    'Documento primário resume notícias e correspondência de sua época.',
    'Não autentica os recortes ausentes nem verifica o evento relatado.'
  ],
  'ORIGINAL_DOCUMENT_NEW_EDITION_SHARED_TRACKING': [
    'Nova edição de série de rastreamento',
    'Edição posterior do mesmo conjunto documental de catálogo.',
    'Não constitui nova observação instrumental independente.'
  ],
  'ORIGINAL_DOCUMENT_REPORTS_BROADCAST_NOT_OBSERVATION': [
    'Registro original de notícia retransmitida',
    'Documento histórico registra uma afirmação transmitida por emissora.',
    'Não confirma observação física independente nem o conteúdo da notícia.'
  ],
  'SECONDARY_HOSTED_INDEX_TEXT_ONLY': [
    'Índice secundário em texto',
    'Resumo hospedado por terceiro permite localizar referências de arquivo.',
    'Não substitui a peça original nem a verificação material do caso.'
  ],
  'SECONDARY_MIRROR_DIFFERENT_OBJECT_EPOCH': [
    'Espelho orbital de época diferente',
    'Elementos orbitais secundários identificam outro objeto e outra época.',
    'Não servem como observação coépoca para triangulação direta.'
  ],
  'SECONDARY_MIRROR_ORIGINAL_TRACKING_UNVERIFIED': [
    'Espelho de elementos orbitais não autenticado',
    'Elementos médios reproduzidos em fonte secundária.',
    'Não demonstram custódia da observação instrumental original.'
  ],
});

export function interpretArchiveStatus(code) {
  if (!Object.hasOwn(readings, code)) {
    throw new Error('Estado documental sem leitura editorial revisada: ' + code);
  }
  const [label, support, limit] = readings[code];
  return Object.freeze({ label, support, limit });
}

export function archiveStatusGuide(records) {
  const counts = new Map();
  for (const row of records) {
    interpretArchiveStatus(row.source_status);
    counts.set(row.source_status, (counts.get(row.source_status) || 0) + 1);
  }
  const lines = [
    '## Como interpretar os estados documentais',
    '',
    'Os rótulos abaixo explicam **tipos de referência**, não graus de probabilidade de queda. ' +
    'A contagem é de vínculos curados neste arquivo, nunca de observações físicas independentes.',
    ''
  ];
  for (const [code, count] of [...counts].sort(([a], [b]) => a.localeCompare(b, 'en'))) {
    const {label, support, limit} = interpretArchiveStatus(code);
    lines.push('- **' + label + '** (' + count + ' vínculo(s); código \`' + code + '\`): ' +
      support + ' **Não permite concluir:** ' + limit);
  }
  return lines;
}


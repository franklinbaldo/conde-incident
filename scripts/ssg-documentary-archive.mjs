/** Static, traceable edition of the curated archive; not an orbital observation. */
import assert from 'node:assert/strict';
import {mkdirSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {archiveKey,verifiedArchiveLinks} from './ssg-wayback-links.mjs';
import {interpretArchiveStatus,archiveStatusGuide} from './archive-source-status.mjs';
import {renderArchiveStatusIndex,ARCHIVE_ROOT,MATRIX_ROW_ROOT} from './archive-status-index.mjs';

const ROOT=ARCHIVE_ROOT;
const MATRIX=MATRIX_ROW_ROOT;
export const matrixRowUrl = line => MATRIX + line;
const safe = value => String(value).replaceAll('\\', '\\\\').replace(/([\[\]_*`<>|])/g, '\\$1').replace(/\r?\n/g, ' ');
const scalar = value => JSON.stringify(String(value));
const page = (title, description, body, type='Page', fields={}) => [
  '---', 'type: '+type, 'title: '+scalar(title), 'description: '+scalar(description),
  'layout: page', 'language: pt-BR',
  'date: '+scalar('2026-11-13'),
  'author: '+scalar('Projeto Conde (índice documental gerado)'),
  ...Object.entries(fields).map(([key,value]) => key+': '+scalar(value)),
  '---', '', body, '',
].join('\n');
const https = url => /^https:\/\/[^\s<>"'()]+$/u.test(url);
const familySlug = family => {
  assert.match(family, /^[A-Z][A-Z0-9_]{1,79}$/, 'Identificador de família inválido');
  return family.toLowerCase().replaceAll('_', '-');
};
// Source identifiers are stable documentary keys, not physical witnesses.
const sourceSlug = source => {
  assert.match(source, /^[A-Z][A-Z0-9_]{1,95}$/, 'Identificador de fonte inválido');
  return source.toLowerCase().replaceAll('_', '-');
};
// Work identifiers are documentary keys, never filesystem paths supplied by users.
const workSlug = work => {
  assert.match(work, /^[A-Z][A-Z0-9_]{1,95}$/, 'Identificador de obra inválido');
  return work.toLowerCase().replaceAll('_', '-');
};

export function archivePages(citations, lineage, wayback=null) {
  assert.equal(citations.schema, 'conde.source-citations/v1');
  assert.equal(lineage.schema, 'conde.declared-documentary-dependence/v1');
  assert.match(citations.matrix_git_blob_sha1, /^[a-f0-9]{40}$/);
  assert.equal(lineage.matrix_git_blob_sha1, citations.matrix_git_blob_sha1,
    'A genealogia deve utilizar a mesma matriz imutável');
  assert.equal(lineage.epistemic_limits?.absence_of_edge_does_not_prove_independence, true);
  assert.equal(lineage.epistemic_limits?.independent_physical_observation_count, null);
  assert.ok(Array.isArray(citations.records) && Array.isArray(lineage.citation_lineages));
  const archived = wayback ? verifiedArchiveLinks(wayback, citations) : new Map();
  const grouped = new Map();
  for (const record of citations.records) {
    assert.match(record.occurrence, /^C[0-9]{1,3}#[1-9][0-9]*$/);
    assert.equal(record.snapshot_ref, `matrix:${citations.matrix_git_blob_sha1}:${record.occurrence}`);
    assert.equal(record.not_a_verified_conde_physical_event, true);
    assert.ok(Number.isSafeInteger(record.matrix_line) && record.matrix_line > 0);
    assert.match(record.row_sha256, /^[a-f0-9]{64}$/);
    assert.match(record.source_status, /^[A-Z0-9][A-Z0-9_]{0,159}$/,
      'Estado documental canônico inválido');
    assert.ok(https(record.citation_url), 'URL documental deve ser HTTPS');
    for (const key of ['source_id', 'source_family', 'work_id', 'claim_text', 'locator', 'relation', 'scope'])
      assert.ok(typeof record[key] === 'string' && record[key].trim(), `Campo ${key} ausente`);
    const lineageEntries = lineage.citation_lineages.filter(item =>
      item.snapshot_ref === record.snapshot_ref && item.source_id === record.source_id);
    assert.equal(lineageEntries.length, 1, 'Genealogia ausente/duplicada para fonte e ocorrência');
    const ancestry = lineageEntries[0];
    assert.equal(ancestry.family_id, record.source_family, 'Família divergente');
    assert.equal(ancestry.row_sha256, record.row_sha256, 'Linha de matriz divergente');
    assert.equal(ancestry.independent_physical_observation_count, null);
    assert.ok(Array.isArray(ancestry.declared_upstream_paths));
    if (!grouped.has(record.occurrence)) grouped.set(record.occurrence, []);
    assert.ok(!grouped.get(record.occurrence).some(x=>x.record.source_id === record.source_id), 'Fonte duplicada');
    grouped.get(record.occurrence).push({record, ancestry});
  }
  assert.equal(grouped.size, citations.curated_occurrences, 'Cobertura curada divergente');
  assert.equal(citations.curated_occurrences + citations.unmapped_occurrences, citations.total_matrix_occurrences);
  // Every declared ancestry must have a corresponding curated citation. Otherwise
  // unrendered, potentially misleading dependencies silently survive validation.
  const citationKeys = new Set(citations.records.map(r =>
    JSON.stringify([r.snapshot_ref, r.source_id])));
  for (const entry of lineage.citation_lineages) {
    assert.ok(citationKeys.has(JSON.stringify([entry.snapshot_ref, entry.source_id])),
      'Genealogia órfã: não corresponde a uma citação curada');
  }
  const files = new Map();
  const sorted = [...grouped].sort(([a],[b])=> {
    const [ia,na] = a.slice(1).split('#').map(Number), [ib,nb] = b.slice(1).split('#').map(Number);
    return ia-ib || na-nb;
  });
  const links = sorted.map(([id, entries]) => {
    const slug = id.toLowerCase().replace('#','-');
    const record = entries[0].record;
    const parts = [`## ${id}: fontes e limites`, '',
      `**Resumo curado da ocorrência (não é transcrição literal do documento):** ${safe(record.claim_text)}`, '',
      '**Registro documental, não verificação de ocorrência física.** Nenhuma hora, local ou probabilidade de queda foi determinada.', '',
      `Esta ocorrência possui **${entries.length} referência(s) curada(s)**. Referências documentais não devem ser contadas como testemunhos físicos independentes.`, '',
      `[Abrir ocorrência na matriz imutável](${MATRIX}${record.matrix_line})`, ''];
    for (const [i, {record:r, ancestry}] of entries.entries()) {
      const reading=interpretArchiveStatus(r.source_status);
      parts.push(`## Referência ${i+1}: ${safe(r.source_id)}`, '',
        `- **Obra:** [${safe(r.work_id)}](${ROOT}obras/${workSlug(r.work_id)}/)`,
        `- **Fonte:** [${safe(r.source_id)}](${ROOT}fontes/${sourceSlug(r.source_id)}/)`,
        `- **Família:** [${safe(r.source_family)}](${ROOT}familias/${familySlug(r.source_family)}/)`,
        `- **Leitura do estado da fonte:** ${safe(reading.label)}. ${safe(reading.support)}`,
        `- **Não permite concluir:** ${safe(reading.limit)}`,
        `- **Estado documental (código canônico, não veredito):** \`${r.source_status}\``,
        `- **Relação:** ${safe(r.relation)}`, `- **Limite:** ${safe(r.scope)}`,
        `- **Localizador:** ${safe(r.locator)}`,
        `- **SHA-256 da linha na matriz:** \`${r.row_sha256}\``, '',
        `[Abrir linha desta referência na matriz imutável](${MATRIX}${r.matrix_line}) · [Abrir documento original](${r.citation_url})`, '',
        ...(archived.has(archiveKey(r.snapshot_ref,r.source_id)) ? (() => {
          const copy=archived.get(archiveKey(r.snapshot_ref,r.source_id));
          return [
            `[PDF preservado no Wayback (${copy.utc.replace('T',' ').replace('Z',' UTC')})](${copy.url})`, '',
            `**Custódia digital:** SHA-256 ${copy.sha256}; ${copy.count} captura(s) do mesmo PDF. Uma captura moderna não equivale a nova observação de 1963.`, '',
          ];
        })() : []),

        `[Outras ocorrências da família ${safe(r.source_family)}](${ROOT}familias/${familySlug(r.source_family)}/) · [Outras referências da obra ${safe(r.work_id)}](${ROOT}obras/${workSlug(r.work_id)}/)`, '',
        '**Genealogia declarada:**', '');
      if (!ancestry.declared_upstream_paths.length) {
        parts.push('Nenhuma cadeia ancestral declarada neste snapshot. **Independência desconhecida.**', '');
      } else {
        for (const path of ancestry.declared_upstream_paths) {
          assert.ok(path.edges.length > 0 && path.upstream_source_id);
          let cursor = r.source_id;
          const visited = new Set([cursor]);
          for (const edge of path.edges) {
            assert.equal(edge.from, cursor, 'Cadeia de proveniência descontínua');
            assert.ok(edge.to && edge.kind && edge.to !== cursor);
            assert.ok(!visited.has(edge.to), 'Ciclo de proveniência documental');
            visited.add(edge.to);
            parts.push(`- ${safe(edge.from)} → ${safe(edge.to)} (${safe(edge.kind)})`);
            cursor=edge.to;
          }
          assert.equal(cursor, path.upstream_source_id, 'Origem declarada divergente');
        }
        parts.push('');
      }
    }
    parts.push('[Voltar ao índice curado]('+ROOT+') · [Índice de famílias documentais]('+ROOT+'familias/) · [Abrir laboratório antigo](/conde-incident/lab/#/documents)');
    files.set(slug+'/index.md', page(`${id}: referências documentais`,
      `Proveniência curada da ocorrência ${id}`, parts.join('\n'), 'Evidence', {
        occurrence:id,matrix_snapshot:citations.matrix_git_blob_sha1,
        verification_status:'documentary_record_only'
      }));
    return `- [${id}: ${safe(record.source_family)}](${ROOT}${slug}/) (${entries.length} referência(s))`;
  });
  // A source family groups documentary references, not physical witnesses. One
  // occurrence may belong to multiple families, without merging their custody.
  const byFamily = new Map();
  for (const [id, entries] of sorted) {
    for (const {record} of entries) {
      const key = record.source_family;
      const slug = familySlug(key);
      if (!byFamily.has(key)) byFamily.set(key, {slug, links: []});
      byFamily.get(key).links.push({id, record});
    }
  }
  const families = [...byFamily].sort(([a], [b]) => a.localeCompare(b, 'en'));
  const familyLinks = [];
  for (const [name, {slug, links: rows}] of families) {
    const occurrences = new Set(rows.map(({id}) => id));
    const works = new Set(rows.map(({record}) => record.work_id));
    const sources = new Set(rows.map(({record}) => record.source_id));
    const familyBody = [
      `## Família documental: ${safe(name)}`, '',
      '**Agrupamento de referências, não conjunto de testemunhas independentes.** A classificação não atesta observação física, nem independência instrumental. Ausência de dependência declarada não prova independência.', '',
      `**No recorte curado:** ${occurrences.size} ocorrência(s), ${rows.length} vínculo(s), ${sources.size} identificador(es) de fonte, ${works.size} obra(s). Um documento pode sustentar mais de uma ocorrência.`, '',
      ...rows.flatMap(({id, record}) => [
        `### ${safe(id)} · ${safe(record.source_id)}`, '',
        `- **Obra:** ${safe(record.work_id)}`,
        `- **Localizador:** ${safe(record.locator)}`,
        `- [Ver ocorrência e genealogia](${ROOT}${id.toLowerCase().replace('#','-')}/)`,
        `- [Ficha da fonte](${ROOT}fontes/${sourceSlug(record.source_id)}/)`,
        `- [Linha da matriz imutável](${MATRIX}${record.matrix_line})`,
        `- [Consultar fonte documental](${record.citation_url})`, '',
      ]),
      '[Todas as famílias documentais]('+ROOT+'familias/) · [Arquivo curado]('+ROOT+')',
    ].join('\n');
    files.set(`familias/${slug}/index.md`, page(`Família ${name}: referências`,
      `Índice documental da família ${name}, sem presumir independência.`, familyBody));
    familyLinks.push(`- [${safe(name)}](${ROOT}familias/${slug}/) · ${occurrences.size} ocorrência(s), ${works.size} obra(s)`);
  }
  // Reverse index per WORK, not per source and not per physical witness. A
  // single publication may be cited in many occurrences, as can a single source.
  const byWork = new Map();
  for (const [id, entries] of sorted) {
    for (const {record} of entries) {
      if (!byWork.has(record.work_id)) byWork.set(record.work_id, []);
      byWork.get(record.work_id).push({id, record});
    }
  }
  const workLinks = [];
  for (const [work, rows] of [...byWork].sort(([a],[b])=>a.localeCompare(b,'en'))) {
    const slug = workSlug(work);
    const occurrences = new Set(rows.map(({id})=>id));
    const sources = new Set(rows.map(({record})=>record.source_id));
    const familiesOfWork = new Set(rows.map(({record})=>record.source_family));
    const body = [
      `## Obra documental: ${safe(work)}`, '',
      '**Índice reverso de referências, não contagem de observações independentes.** Reutilizações da mesma obra não produzem novos testemunhos. As relações de genealogia e as incertezas permanecem nas páginas das ocorrências.', '',
      `**No recorte curado:** ${occurrences.size} ocorrência(s), ${rows.length} vínculo(s), ${sources.size} fonte(s) identificada(s), ${familiesOfWork.size} família(s).`, '',
      ...rows.flatMap(({id,record})=>[
        `### ${safe(id)} · ${safe(record.source_id)}`, '',
        `- **Família:** ${safe(record.source_family)}`,
        `- **Localizador:** ${safe(record.locator)}`,
        `- **Relação:** ${safe(record.relation)}`,
        `- **Limite:** ${safe(record.scope)}`,
        `- **SHA-256 da linha na matriz:** \`${record.row_sha256}\``, '',
        `- [Abrir ocorrência e genealogia](${ROOT}${id.toLowerCase().replace('#','-')}/)`,
        `- [Ficha da fonte](${ROOT}fontes/${sourceSlug(record.source_id)}/)`,
        `- [Linha da matriz imutável](${MATRIX}${record.matrix_line})`,
        `- [Consultar documento](${record.citation_url})`,
        `- [Ver família](${ROOT}familias/${familySlug(record.source_family)}/)`, '',
      ]),
      `[Índice de obras](${ROOT}obras/) · [Famílias documentais](${ROOT}familias/) · [Arquivo curado](${ROOT})`,
    ].join('\n');
    files.set(`obras/${slug}/index.md`, page(`Obra ${work}: referências`,
      `Índice reverso da obra ${work}; não prova de observação independente.`, body));
    workLinks.push(`- [${safe(work)}](${ROOT}obras/${slug}/) · ${occurrences.size} ocorrência(s), ${sources.size} fonte(s)`);
  }
  // A source identifier may be reused across many matrix occurrences. This
  // reverse index makes those reuses inspectable without counting witnesses.
  const bySource = new Map();
  for (const [id, entries] of sorted) {
    for (const {record} of entries) {
      const slug = sourceSlug(record.source_id);
      if (!bySource.has(record.source_id)) bySource.set(record.source_id, {slug, rows: []});
      bySource.get(record.source_id).rows.push({id, record});
    }
  }
  const sourceLinks = [];
  for (const [source, {slug, rows}] of [...bySource].sort(([a],[b])=>a.localeCompare(b,'en'))) {
    const occurrences = new Set(rows.map(({id})=>id));
    const works = new Set(rows.map(({record})=>record.work_id));
    const families = new Set(rows.map(({record})=>record.source_family));
    const body = [
      `## Identificador de fonte: ${safe(source)}`, '',
      '**Identificador documental, não testemunha física independente.** Cada ocorrência referencia sua linha imutável; múltiplas citações do mesmo identificador não validam um sobrevoo, uma hora ou uma queda.', '',
      `**No recorte curado:** ${occurrences.size} ocorrência(s), ${rows.length} vínculo(s), ${works.size} obra(s), ${families.size} família(s).`, '',
      ...rows.flatMap(({id,record})=>[
        `### ${safe(id)} · ${safe(record.work_id)}`, '',
        `- **Família:** ${safe(record.source_family)}`,
        `- **Localizador:** ${safe(record.locator)}`,
        `- **Relação:** ${safe(record.relation)}`,
        `- **Limite:** ${safe(record.scope)}`,
        `- **SHA-256 da linha:** \`${record.row_sha256}\``,
        `- [Linha da matriz imutável](${MATRIX}${record.matrix_line})`,
        `- [Ocorrência e genealogia](${ROOT}${id.toLowerCase().replace('#','-')}/)`,
        `- [Obra relacionada](${ROOT}obras/${workSlug(record.work_id)}/)`,
        `- [Documento original](${record.citation_url})`, '',
      ]),
      `[Índice de identificadores](${ROOT}fontes/) · [Arquivo curado](${ROOT})`,
    ].join('\n');
    files.set(`fontes/${slug}/index.md`, page(`Fonte ${source}: vínculos`,
      `Referências da fonte documental ${source} na matriz curada.`, body));
    sourceLinks.push(`- [${safe(source)}](${ROOT}fontes/${slug}/) · ${occurrences.size} ocorrência(s), ${works.size} obra(s)`);
  }
  files.set('fontes/index.md', page('Identificadores documentais: índice',
    'Fontes citadas e reutilizações, sem presumir testemunhos independentes.', [
      '## Identificadores de fontes', '',
      '**Uma fonte pode aparecer em várias ocorrências.** O índice distingue referências documentais de observações instrumentais e conserva cada ligação à matriz.', '',
      ...sourceLinks, '', `[Voltar ao arquivo curado](${ROOT})`,
    ].join('\n')));
  files.set('obras/index.md', page('Obras documentais: índice',
    'Obras citadas no arquivo curado, com ocorrências e dependências rastreáveis.', [
      '## Obras documentais', '',
      '**Obra citada não equivale a medição independente.** Os vínculos são derivados do mesmo feed curado e de uma matriz imutável, sem preenchimento de fontes ausentes.', '',
      ...workLinks, '', `[Voltar ao arquivo curado](${ROOT})`,
    ].join('\n')));

  files.set('familias/index.md', page('Famílias documentais: índice',
    'Agrupamentos das referências curadas por família e obra documental.', [
      '## Famílias de fontes', '',
      '**Família documental não equivale a testemunho físico independente.** Este é apenas o recorte curado dos feeds versionados. Uma ocorrência pode aparecer em mais de uma família.', '',
      ...familyLinks, '',
      '[Voltar ao arquivo curado]('+ROOT+')',
    ].join('\n')));
  // Indexed reference categories, never independent witnesses.
  files.set('estados/index.md', page('Estados documentais: índice de vínculos',
    'Referências curadas agrupadas por estado, sem inferir observação física.',
    renderArchiveStatusIndex(citations.records)));
  const index = [
    '## Arquivo de fontes documentais', '',
    '**Leitura estática gerada pelo SSG Rust a partir dos feeds curados do laboratório.** Sem React ou JavaScript. O laboratório anterior permanece disponível durante a migração. A data editorial deste índice não é a data de uma observação em 1963.', '',
    `**Cobertura:** ${citations.curated_occurrences} ocorrências curadas de ${citations.total_matrix_occurrences}. ${citations.unmapped_occurrences} ocorrências não mapeadas no feed parcial **não significam fonte inexistente**.`, '',
    'Uma mesma obra pode originar múltiplos vínculos documentais, sem criar novas testemunhas físicas. Ausência de genealogia declarada não significa independência. Datas NASA são entradas de catálogo, não posições ou horários observados de queda.', '',
    '[Consultar famílias documentais e ocorrências relacionadas]('+ROOT+'familias/) · [Consultar obras e suas reutilizações]('+ROOT+'obras/) · [Consultar identificadores de fontes]('+ROOT+'fontes/) · [Explorar por estado documental]('+ROOT+'estados/)', '',
    '## Ocorrências curadas', '',
    ...links, '',
    ...archiveStatusGuide(citations.records), '',
    `**Matriz imutável (Git blob):** ${citations.matrix_git_blob_sha1}.`, '',
    '[Consultar documentos no laboratório interativo](/conde-incident/lab/#/documents) · [Evidências editoriais](/conde-incident/evidencias/)',
  ].join('\n');
  files.set('index.md', page('Arquivo documental: ocorrências curadas', 'Proveniência e genealogia documental sem alegar queda física.', index));
  return files;
}

export function writeArchivePages(outputDir, citations, lineage, wayback=null) {
  const pages = archivePages(citations, lineage, wayback);
  for (const [name, data] of pages) {
    const file=join(outputDir,name);
    mkdirSync(file.slice(0, file.lastIndexOf('/')), {recursive: true});
    writeFileSync(file, data, 'utf8');
  }
  return pages.size;
}

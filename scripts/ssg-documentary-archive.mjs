/** Static, traceable edition of the curated archive; not an orbital observation. */
import assert from 'node:assert/strict';
import {mkdirSync, writeFileSync} from 'node:fs';
import {join} from 'node:path';

const ROOT = '/conde-incident/evidencias/arquivo/';
const MATRIX = 'https://github.com/franklinbaldo/conde-incident/blob/faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df/research/evidence_matrix_C001-C238_2026-11-11.md#L';
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

export function archivePages(citations, lineage) {
  assert.equal(citations.schema, 'conde.source-citations/v1');
  assert.equal(lineage.schema, 'conde.declared-documentary-dependence/v1');
  assert.match(citations.matrix_git_blob_sha1, /^[a-f0-9]{40}$/);
  assert.equal(lineage.matrix_git_blob_sha1, citations.matrix_git_blob_sha1,
    'A genealogia deve utilizar a mesma matriz imutável');
  assert.equal(lineage.epistemic_limits?.absence_of_edge_does_not_prove_independence, true);
  assert.equal(lineage.epistemic_limits?.independent_physical_observation_count, null);
  assert.ok(Array.isArray(citations.records) && Array.isArray(lineage.citation_lineages));
  const grouped = new Map();
  for (const record of citations.records) {
    assert.match(record.occurrence, /^C[0-9]{1,3}#[1-9][0-9]*$/);
    assert.equal(record.snapshot_ref, `matrix:${citations.matrix_git_blob_sha1}:${record.occurrence}`);
    assert.equal(record.not_a_verified_conde_physical_event, true);
    assert.ok(Number.isSafeInteger(record.matrix_line) && record.matrix_line > 0);
    assert.match(record.row_sha256, /^[a-f0-9]{64}$/);
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
      parts.push(`## Referência ${i+1}: ${safe(r.source_id)}`, '',
        `- **Obra:** ${safe(r.work_id)}`, `- **Família da fonte:** ${safe(r.source_family)}`,
        `- **Relação:** ${safe(r.relation)}`, `- **Limite:** ${safe(r.scope)}`,
        `- **Localizador:** ${safe(r.locator)}`, '',
        `[Abrir documento original](${r.citation_url})`, '',
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
    parts.push('[Voltar ao índice curado]('+ROOT+') · [Abrir laboratório antigo](/conde-incident/lab/#/documents)');
    files.set(slug+'/index.md', page(`${id}: referências documentais`,
      `Proveniência curada da ocorrência ${id}`, parts.join('\n'), 'Evidence', {
        occurrence:id,matrix_snapshot:citations.matrix_git_blob_sha1,
        verification_status:'documentary_record_only'
      }));
    return `- [${id}: ${safe(record.source_family)}](${ROOT}${slug}/) (${entries.length} referência(s))`;
  });
  const index = [
    '## Arquivo de fontes documentais', '',
    '**Leitura estática gerada pelo SSG Rust a partir dos feeds curados do laboratório.** Sem React ou JavaScript. O laboratório anterior permanece disponível durante a migração. A data editorial deste índice não é a data de uma observação em 1963.', '',
    `**Cobertura:** ${citations.curated_occurrences} ocorrências curadas de ${citations.total_matrix_occurrences}. ${citations.unmapped_occurrences} ocorrências não mapeadas no feed parcial **não significam fonte inexistente**.`, '',
    'Uma mesma obra pode originar múltiplos vínculos documentais, sem criar novas testemunhas físicas. Ausência de genealogia declarada não significa independência. Datas NASA são entradas de catálogo, não posições ou horários observados de queda.', '',
    ...links, '',
    `**Matriz imutável (Git blob):** ${citations.matrix_git_blob_sha1}.`, '',
    '[Consultar documentos no laboratório interativo](/conde-incident/lab/#/documents) · [Evidências editoriais](/conde-incident/evidencias/)',
  ].join('\n');
  files.set('index.md', page('Arquivo documental: ocorrências curadas', 'Proveniência e genealogia documental sem alegar queda física.', index));
  return files;
}

export function writeArchivePages(outputDir, citations, lineage) {
  const pages = archivePages(citations, lineage);
  for (const [name, data] of pages) {
    const file=join(outputDir,name);
    mkdirSync(file.slice(0, file.lastIndexOf('/')), {recursive: true});
    writeFileSync(file, data, 'utf8');
  }
  return pages.size;
}

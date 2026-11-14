/** Post-matrix documents are archival leads, never new rows in the frozen matrix. */
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {join} from 'node:path';
import {readBundle,audit,visibleDocument} from './verify-ssg-evidence-index.mjs';
import {matrixCatalogPages} from './ssg-matrix-catalog.mjs';

const esc=s=>String(s).replaceAll('&','&amp;').replaceAll('<','&lt;').replaceAll('>','&gt;').replaceAll('\\','\\\\').replaceAll('_','\\_').replaceAll('*','\\*').replaceAll('`','\\`').replaceAll('[','\\[').replaceAll(']','\\]').replaceAll('|','\\|').replace(/\r?\n/g,' ');
const identifier=s=>typeof s==='string'&&/^[A-Z0-9][A-Z0-9_-]{2,99}$/.test(s);
const https=s=>typeof s==='string'&&/^https:\/\/[^\s<>"'()]+$/.test(s);
const report=s=>typeof s==='string'&&/^research\/archives\/[a-z0-9_/-]+\.md$/.test(s)&&!s.includes('..');
const sha=s=>typeof s==='string'&&/^[0-9a-f]{64}$/.test(s);
const matrixId=s=>typeof s==='string'&&/^C[0-9]{1,3}#[1-9][0-9]*$/.test(s);

/** Cross-check the digital object against the separately versioned custodial report.
 * Recalculating coordinated JSON digests alone must not forge an NARA object. */
export function auditedReportDigest(item) {
  assert.ok(report(item.report_path),'Pós-matriz: caminho de pesquisa inválido');
  const bytes=readFileSync(item.report_path);
  const body=bytes.toString('utf8');
  const unit=body.match(/unidade documental \x60naId: (\d+)\x60/);
  assert.equal(unit?.[1],String(item.nara_fileunit_naid),
    'Pós-matriz: NAID da unidade diverge do relatório original');
  assert.equal(item.report_file_unit_id,'NARA_BB_UNIT_'+item.nara_fileunit_naid,
    'Pós-matriz: identificador da unidade divergente');
  const rows=[...body.matchAll(/^\|\s*(\d+)\s*\|\s*(\d+)\s*\|\s*\[([a-z0-9_.-]+)\]\((https:\/\/[^)\s]+)\)\s*\|\s*[\d.]+\s*\|\s*\x60([0-9a-f]{64})\x60\s*\|$/gm)];
  const matches=rows.filter(row=>row[2]===String(item.nara_object_id));
  assert.equal(matches.length,1,'Pós-matriz: objeto NARA ausente ou duplicado no relatório');
  const [,page,,filename,url,digest]=matches[0];
  assert.equal(item.image_filename,filename,'Pós-matriz: nome do objeto diverge do relatório');
  assert.equal(item.report_citation_url,url,'Pós-matriz: URL diverge do relatório');
  assert.equal(item.image_sha256,digest,'Pós-matriz: SHA-256 diverge do relatório');
  if(item.source_id==='NARA_AIRA_TELEGRAM_19631114') {
    const backtick=String.fromCharCode(96);
    const marker='**Imagem '+page+', '+backtick+filename+backtick+':**';
    const description=body.split('\n').find(line=>line.startsWith(marker));
    assert.ok(description?.includes('mensagem')&&description.includes('14 NOV 1963'),
      'Pós-matriz: telegrama não corresponde à imagem documental indicada');
  }
  return createHash('sha256').update(bytes).digest('hex');
}


/** Bind every supplemental reference to the audited, frozen 241-row index.
 * A syntactically valid Cnn#N and a matching string ref are not enough. */
export function postMatrixLinks(citations,bundle=readBundle()) {
  audit(bundle);
  assert.equal(bundle.manifest.matrix_git_blob_sha1,citations.matrix_git_blob_sha1,
    'Pós-matriz: snapshot diferente do índice canônico auditado');
  const {entries}=matrixCatalogPages(bundle);
  const locations=new Map();
  for(const [index,{pointer}] of entries.entries()) {
    assert.ok(!locations.has(pointer.occurrence),'Pós-matriz: ID duplicado no índice');
    const number=String(Math.floor(index/20)+1).padStart(2,'0');
    locations.set(pointer.occurrence,
      '/conde-incident/evidencias/matriz/paginas/'+number+'/#'+pointer.occurrence.replace('#','-'));
  }
  return locations;
}

/** Check actual, visible built HTML, not a matching href inside scripts or templates. */
export function auditBuiltPostMatrix(html,citations,bundle=readBundle()) {
  const locations=postMatrixLinks(citations,bundle);
  const main=/<main\b[^>]*>([\s\S]*?)<\/main>/i.exec(html)?.[1];
  assert.ok(main,'Pós-matriz: HTML sem região principal');
  const doc=visibleDocument(html);
  assert.ok(doc.links.has('/conde-incident/evidencias/matriz/'),
    'Pós-matriz: falta retorno visível à matriz');

  // A valid link or digest elsewhere on the page cannot authenticate a record.
  // Audit each rendered record separately against its canonical source and
  // source-locked custody report, including the epistemic qualifications.
  const items=[...citations.post_matrix_occurrences].sort((a,b)=>
    a.id.localeCompare(b.id,'en'));
  const headings=[...main.matchAll(/<h3\b[^>]*>([^<>]*)<\/h3>/gi)];
  assert.deepEqual(headings.map(match=>match[1]),items.map(item=>item.id),
    'Pós-matriz: cabeçalhos ausentes, duplicados ou fora da ordem canônica');
  let checked=0;
  for(let i=0;i<items.length;i++) {
    const item=items[i];
    const heading=headings[i];
    const headingDoc=visibleDocument('<main>'+heading[0]+'</main>');
    assert.ok(headingDoc.visibleText.includes(item.id),
      'Pós-matriz: cabeçalho não visível: '+item.id);
    const section=main.slice(heading.index+heading[0].length,
      headings[i+1]?.index??main.length);
    const visible=visibleDocument('<main>'+section+'</main>');
    const field=(label,value)=>{
      const expression=new RegExp('<strong>'+label+':<\/strong>\\s*<code>'+value+'<\/code>');
      assert.match(section,expression,
        'Pós-matriz: campo vinculado ao registro ausente: '+item.id+' / '+label);
      assert.ok(visible.visibleText.includes(value),
        'Pós-matriz: valor visível ausente: '+item.id+' / '+label);
    };
    field('Estado canônico',item.status);
    field('Independência jornalística',item.journalistic_source_independence);
    field('SHA-256 da imagem arquivística',item.image_sha256);
    field('SHA-256 do relatório de custódia versionado',auditedReportDigest(item));
    assert.ok(visible.links.has(item.report_citation_url),
      'Pós-matriz: link NARA ausente na ficha: '+item.id);
    assert.ok(visible.links.has('https://github.com/franklinbaldo/conde-incident/blob/main/'+item.report_path),
      'Pós-matriz: relatório de custódia não navegável: '+item.id);
    for(const id of item.related_matrix_occurrences) {
      assert.ok(locations.has(id),'Pós-matriz: ID ausente da matriz: '+id);
      assert.ok(visible.links.has(locations.get(id)),
        'Pós-matriz: link visível na ficha para a ocorrência ausente: '+id);
      checked++;
    }
  }
  return checked;
}

export function postMatrixPage(citations,lineage,bundle=readBundle()) {
  const locations=postMatrixLinks(citations,bundle);
  assert.equal(citations.schema,'conde.source-citations/v1');
  assert.equal(lineage.schema,'conde.declared-documentary-dependence/v1');
  assert.equal(citations.matrix_git_blob_sha1,lineage.matrix_git_blob_sha1,
    'Pós-matriz: snapshot da genealogia divergente');
  assert.match(citations.matrix_git_blob_sha1,/^[a-f0-9]{40}$/);
  assert.ok(Array.isArray(citations.post_matrix_occurrences));
  assert.ok(Array.isArray(lineage.post_matrix_lineages));
  const items=citations.post_matrix_occurrences;
  const deps=lineage.post_matrix_lineages;
  const byId=new Map(deps.map(d=>[d.id,d]));
  assert.equal(new Set(items.map(x=>x.id)).size,items.length,'Pós-matriz: ID duplicado');
  assert.equal(byId.size,deps.length,'Pós-matriz: genealogia duplicada');
  assert.deepEqual([...byId.keys()].sort(),items.map(x=>x.id).sort(),
    'Pós-matriz: identidade sem genealogia ou órfã');

  const lines=[
    '## Registros posteriores ao congelamento da matriz', '',
    '**Este suplemento não altera a matriz histórica.** Cada registro é uma pista documental posterior à curadoria, não uma ocorrência física ou nova medição. A ausência de uma ficha na matriz não demonstra ausência de documentação.', '',
    `**Registros pós-matriz:** ${items.length}. **Referências curadas da matriz:** ${citations.records.length}; as duas contagens não são intercambiáveis.`, '',
  ];
  for(const item of [...items].sort((a,b)=>a.id.localeCompare(b.id,'en'))) {
    const dep=byId.get(item.id);
    assert.ok(identifier(item.id)&&identifier(item.source_id)&&identifier(item.quoted_source_id),
      'Pós-matriz: identificador inválido');
    assert.ok(identifier(dep.source_id)&&identifier(dep.source_family),
      'Pós-matriz: fonte/família inválida');
    assert.equal(item.source_id,dep.source_id,'Pós-matriz: fonte da genealogia divergente');
    assert.equal(item.not_a_verified_conde_physical_event,true,
      'Pós-matriz: evento físico não verificado');
    assert.equal(item.physical_constraint,null,'Pós-matriz: restrição física inventada');
    assert.equal(dep.independent_physical_observation_count,null,
      'Pós-matriz: independência física não demonstrada');
    assert.equal(item.observation_type,'DOCUMENTARY_CITATION_NOT_PHYSICAL_OBSERVATION');
    assert.equal(item.journalistic_source_independence,'UNRESOLVED',
      'Pós-matriz: independência jornalística não validada');
    assert.ok(identifier(item.status),'Pós-matriz: código de estado inválido');
    assert.ok(https(item.report_citation_url),'Pós-matriz: URL externa deve ser HTTPS');
    assert.ok(report(item.report_path),'Pós-matriz: caminho de pesquisa inválido');
    assert.ok(sha(item.image_sha256)&&item.image_sha256===item.report_object_sha256,
      'Pós-matriz: digest de objeto inconsistente');
    const reportDigest=auditedReportDigest(item);
    assert.ok(Array.isArray(item.related_matrix_occurrences)&&
      Array.isArray(item.related_matrix_snapshot_refs)&&
      item.related_matrix_occurrences.length===item.related_matrix_snapshot_refs.length,
      'Pós-matriz: refs relacionadas divergentes');
    assert.equal(new Set(item.related_matrix_occurrences).size,
      item.related_matrix_occurrences.length,'Pós-matriz: ocorrência relacionada duplicada');
    for(let i=0;i<item.related_matrix_occurrences.length;i++){
      const id=item.related_matrix_occurrences[i];
      assert.ok(matrixId(id),'Pós-matriz: ID de matriz inválido');
      assert.ok(locations.has(id),'Pós-matriz: ocorrência não existe no snapshot da matriz: '+id);
      assert.equal(item.related_matrix_snapshot_refs[i],
        `matrix:${citations.matrix_git_blob_sha1}:${id}`,
        'Pós-matriz: relação sem snapshot imutável');
    }
    assert.ok(Array.isArray(dep.declared_upstream_paths));
    const edges=[];
    for(const path of dep.declared_upstream_paths){
      assert.ok(Array.isArray(path.edges)&&path.edges.length>0,'Pós-matriz: caminho vazio');
      const visited=new Set([item.source_id]);
      let current=item.source_id;
      for(const edge of path.edges){
        assert.equal(edge.from,current,'Pós-matriz: aresta desconectada');
        assert.ok(identifier(edge.to)&&typeof edge.kind==='string'&&
          /^[a-z_]{2,80}$/.test(edge.kind)&&!visited.has(edge.to),
          'Pós-matriz: aresta inválida ou cíclica');
        visited.add(edge.to);
        edges.push(`- ${esc(edge.from)} → ${esc(edge.to)} (${esc(edge.kind)})`);
        current=edge.to;
      }
      assert.equal(current,path.upstream_source_id,'Pós-matriz: origem declarada divergente');
    }
    lines.push(`### ${esc(item.id)}`,'',
      `**Fonte:** ${esc(item.source_id)} · **Família:** ${esc(dep.source_family)}`,'',
      `**Estado canônico:** \`${item.status}\` · **Independência jornalística:** \`${item.journalistic_source_independence}\`.`,'',
      `**O que o documento afirma:** ${esc(item.proposition)}`,'',
      `**Verificação e limite:** ${esc(item.verification)}`,'',
      `**Localizador:** ${esc(item.report_locator)}`,'',
      `**SHA-256 da imagem arquivística:** \`${item.image_sha256}\``,'',
      '**SHA-256 do relatório de custódia versionado:** `'+reportDigest+'`','',
      `[Abrir objeto no catálogo NARA](${item.report_citation_url}) · [Ler relatório de custódia no repositório](https://github.com/franklinbaldo/conde-incident/blob/main/${item.report_path})`,'',
      '**Relações de proveniência declaradas, não testemunhas independentes:**','',
      ...(edges.length?edges:['- Nenhuma relação adicional declarada.']),'',
      '**IDs da matriz relacionados, sem atribuir um novo número histórico:**',
      item.related_matrix_occurrences.map(id=>'['+id+']('+locations.get(id)+')').join(' · '),'',
      `**Próxima fonte necessária:** ${esc(item.next_dependency)}`,'');
  }
  lines.push('[Voltar ao arquivo documental](/conde-incident/evidencias/arquivo/) · [Consultar a matriz histórica](/conde-incident/evidencias/matriz/)');
  return ['---','type: Page','title: "Suplemento pós-matriz: documentos e pendências"',
    'description: "Pistas documentais posteriores à matriz, com custódia e incerteza explícitas."',
    'layout: page','language: pt-BR','date: "2026-11-14"',
    'author: "Projeto Conde (catálogo documental gerado)"','---','',
    lines.join('\n'),''].join('\n');
}

export function writePostMatrixPage(outputDir,citations,lineage){
  const file=join(outputDir,'pos-matriz','index.md');
  mkdirSync(join(outputDir,'pos-matriz'),{recursive:true});
  writeFileSync(file,postMatrixPage(citations,lineage),'utf8');
  return file;
}

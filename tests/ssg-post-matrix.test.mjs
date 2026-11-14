import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {postMatrixPage,postMatrixLinks,auditBuiltPostMatrix} from '../scripts/ssg-post-matrix.mjs';
import {postMatrixAnchor} from '../scripts/ssg-post-matrix-backlinks.mjs';

const citations=JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
const lineage=JSON.parse(readFileSync('public/data/conde-declared-dependence.json','utf8'));
const clone=o=>structuredClone(o);

test('post-matrix SSG preserves archived source, frozen IDs and epistemic limit',()=>{
  const page=postMatrixPage(citations,lineage);
  assert.match(page,/type: Page/);
  assert.match(page,/pós-matriz/i);
  assert.match(page,/NARA-BB-CONDE-20261112-01/);
  assert.match(page,/NARA\\_AIRA\\_TELEGRAM\\_19631114/);
  assert.match(page,/136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9/);
  assert.match(page,/catalog.archives.gov/);
  assert.match(page,/reports?|relatório de custódia/i);
  assert.match(page,/`CONNECTED_PENDING_DOCUMENTARY_VERIFICATION`/);
  assert.doesNotMatch(page,/CONNECTED\\\\_PENDING/);
  assert.match(page,/C232#1/);
  assert.match(page,/C01#1/);
  assert.match(page,/Independência jornalística/);
  assert.match(page,/Próxima fonte necessária/);
  assert.doesNotMatch(page,/<script|onclick=|onload=/i);
  assert.doesNotMatch(page,/C999#1/);
});
test('post-matrix refuses physical promotion and invented independence',()=>{
  const forged=clone(citations);
  forged.post_matrix_occurrences[0].physical_constraint={altitude_km:5};
  assert.throws(()=>postMatrixPage(forged,lineage),/restrição física inventada/);
  const claim=clone(citations);
  claim.post_matrix_occurrences[0].not_a_verified_conde_physical_event=false;
  assert.throws(()=>postMatrixPage(claim,lineage),/evento físico não verificado/);
  const falseIndependence=clone(lineage);
  falseIndependence.post_matrix_lineages[0].independent_physical_observation_count=1;
  assert.throws(()=>postMatrixPage(citations,falseIndependence),/independência física não demonstrada/);
  const news=clone(citations);
  news.post_matrix_occurrences[0].journalistic_source_independence='CONFIRMED';
  assert.throws(()=>postMatrixPage(news,lineage),/independência jornalística/);
});
test('post-matrix fails on retargeting frozen snapshots and orphan genealogy',()=>{
  const moved=clone(citations);
  moved.post_matrix_occurrences[0].related_matrix_occurrences[0]='C999#1';
  assert.throws(()=>postMatrixPage(moved,lineage),/ocorrência não existe no snapshot da matriz/);
  const duplicate=clone(citations);
  duplicate.post_matrix_occurrences.push(clone(duplicate.post_matrix_occurrences[0]));
  assert.throws(()=>postMatrixPage(duplicate,lineage),/ID duplicado/);
  const missing=clone(lineage);
  missing.post_matrix_lineages=[];
  assert.throws(()=>postMatrixPage(citations,missing),/identidade sem genealogia/);
  const wrong=clone(lineage);
  wrong.post_matrix_lineages[0].declared_upstream_paths[0].edges[0].from='OTHER';
  assert.throws(()=>postMatrixPage(citations,wrong),/aresta desconectada/);
});
test('post-matrix rejects links, paths and digests that fail custody',()=>{
  const url=clone(citations);
  url.post_matrix_occurrences[0].report_citation_url='javascript:alert(1)';
  assert.throws(()=>postMatrixPage(url,lineage),/HTTPS/);
  const path=clone(citations);
  path.post_matrix_occurrences[0].report_path='../outside.md';
  assert.throws(()=>postMatrixPage(path,lineage),/caminho de pesquisa inválido/);
  const hash=clone(citations);
  hash.post_matrix_occurrences[0].report_object_sha256='0'.repeat(64);
  assert.throws(()=>postMatrixPage(hash,lineage),/digest de objeto inconsistente/);
  const xss=clone(citations);
  xss.post_matrix_occurrences[0].proposition='<script>alert(1)</script>';
  const rendered=postMatrixPage(xss,lineage);
  assert.doesNotMatch(rendered,/<script>/);
  assert.match(rendered,/&lt;script&gt;/);
});

test('post-matrix cross-checks digital object against the actual archived report',()=>{
  const file=citations.post_matrix_occurrences[0].report_path;
  const expected=createHash('sha256').update(readFileSync(file)).digest('hex');
  assert.match(postMatrixPage(citations,lineage),new RegExp(expected));
  const changed=clone(citations);
  changed.post_matrix_occurrences[0].image_sha256='0'.repeat(64);
  changed.post_matrix_occurrences[0].report_object_sha256='0'.repeat(64);
  assert.throws(()=>postMatrixPage(changed,lineage),/SHA-256 diverge do relatório/);
  const other=clone(citations);
  other.post_matrix_occurrences[0].nara_object_id=302531015;
  assert.throws(()=>postMatrixPage(other,lineage),/nome do objeto diverge do relatório/);
  const url=clone(citations);
  url.post_matrix_occurrences[0].report_citation_url='https://example.org/0810.jp2';
  assert.throws(()=>postMatrixPage(url,lineage),/URL diverge do relatório/);
  const unit=clone(citations);
  unit.post_matrix_occurrences[0].report_file_unit_id='NARA_BB_UNIT_000000000';
  assert.throws(()=>postMatrixPage(unit,lineage),/identificador da unidade divergente/);
  const fileName=clone(citations);
  fileName.post_matrix_occurrences[0].image_filename='0811.jp2';
  assert.throws(()=>postMatrixPage(fileName,lineage),/nome do objeto diverge do relatório/);
});

test('post-matrix references open real no-JS matrix anchors and reject coordinated fake IDs',()=>{
  const page=postMatrixPage(citations,lineage);
  const locations=postMatrixLinks(citations);
  for(const id of citations.post_matrix_occurrences[0].related_matrix_occurrences)
    assert.ok(page.includes('['+id+']('+locations.get(id)+')'),id);
  const counterfeit=clone(citations);
  counterfeit.post_matrix_occurrences[0].related_matrix_occurrences[0]='C999#1';
  counterfeit.post_matrix_occurrences[0].related_matrix_snapshot_refs[0]=
    'matrix:'+citations.matrix_git_blob_sha1+':C999#1';
  assert.throws(()=>postMatrixPage(counterfeit,lineage),
    /ocorrência não existe no snapshot da matriz/);
  const wrongSnapshot=clone(citations);
  wrongSnapshot.matrix_git_blob_sha1='0'.repeat(40);
  assert.throws(()=>postMatrixPage(wrongSnapshot,lineage),
    /snapshot diferente do índice canônico auditado/);
});

test('post-matrix built HTML binds navigation, source identity and custody in each visible record',()=>{
  const item=citations.post_matrix_occurrences[0];
  const reportDigest=createHash('sha256').update(readFileSync(item.report_path)).digest('hex');
  const locations=postMatrixLinks(citations);
  const expected=item.related_matrix_occurrences.map(id=>locations.get(id));
  const links=item.related_matrix_occurrences.map((id,i)=>
    '<a href="'+expected[i]+'">'+id+'</a>').join('');
  const field=(label,value)=>'<p><strong>'+label+':</strong> <code>'+value+'</code></p>';
  const source='<a href="'+item.report_citation_url+'">NARA</a>';
  const custody='<a href="https://github.com/franklinbaldo/conde-incident/blob/main/'+
    item.report_path+'">Relatório</a>';
  const state=field('Estado canônico',item.status);
  const independence=field('Independência jornalística',item.journalistic_source_independence);
  const imageDigest=field('SHA-256 da imagem arquivística',item.image_sha256);
  const report=field('SHA-256 do relatório de custódia versionado',reportDigest);
  const heading='<h3 id="'+postMatrixAnchor(item.id)+'" tabindex="-1">'+item.id+'</h3>';
  const base='<main><a href="/conde-incident/evidencias/matriz/">Matriz</a>'+
    heading+state+independence+imageDigest+report+source+custody+links+'</main>';
  assert.equal(auditBuiltPostMatrix(base,citations),expected.length);

  // A raw <h3> cannot authenticate a record when an ancestor hides it.
  // Earlier auditing detached the heading from its hidden parent.
  for(const hidden of [
    '<div hidden>'+heading+'</div>',
    '<section aria-hidden="true">'+heading+'</section>',
    '<template>'+heading+'</template>',
    '<div style="display:none">'+heading+'</div>',
  ]) {
    assert.throws(()=>auditBuiltPostMatrix(base.replace(heading,hidden),citations),
      /cabeçalhos ausentes|cabeçalho não visível/,
      'hidden headings must not be accepted as visible record headings');
  }

  assert.throws(()=>auditBuiltPostMatrix(base.replace(' tabindex="-1"',''),citations),
    /âncora documental ativa e única ausente/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(' id="'+postMatrixAnchor(item.id)+'"',''),citations),
    /âncora documental ativa e única ausente/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(heading,heading+heading),citations),
    /cabeçalhos ausentes|âncora documental ativa e única ausente/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(heading,'<template>'+heading+'</template>'),citations),
    /cabeçalhos ausentes|âncora documental ativa e única ausente/);

  const target='<a href="'+expected[0]+'">'+item.related_matrix_occurrences[0]+'</a>';
  assert.throws(()=>auditBuiltPostMatrix(base.replace(target,
    '<template>'+target+'</template>'),citations),/link visível na ficha/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(target,
    '<div aria-hidden="true">'+target+'</div>'),citations),/link visível na ficha/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(target,
    '<a href="/conde-incident/evidencias/matriz/">linha errada</a>'),citations),
    /link visível na ficha/);

  // A valid href with a counterfeit label or a duplicated visible link is not a valid citation.
  assert.throws(()=>auditBuiltPostMatrix(base.replace(target,
    '<a href="'+expected[0]+'">queda física confirmada</a>'),citations),
    /rótulo diverge do identificador canônico/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(target,target+target),citations),
    /link visível ausente ou duplicado/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(target,
    '<a href="'+expected[1]+'">'+item.related_matrix_occurrences[0]+'</a>'),citations),
    /rótulo diverge do identificador canônico|link visível na ficha/);


  assert.throws(()=>auditBuiltPostMatrix(base.replace(heading,'<h3>OTHER</h3>'),citations),
    /cabeçalhos ausentes/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(state,
    '<div hidden>'+state+'</div>'),citations),/campo visível vinculado/);
  // G74 adversarial: hidden field plus a visible, unbound echo.
  // Text somewhere in a record does not make the authentic field visible.
  for(const [original,value] of [
    [state,item.status],[independence,item.journalistic_source_independence],
    [imageDigest,item.image_sha256],[report,reportDigest],
  ]) {
    const decoy=base.replace(original,
      '<div hidden>'+original+'</div><span>'+value+'</span>');
    assert.throws(()=>auditBuiltPostMatrix(decoy,citations),/campo visível vinculado/);
  }

  assert.throws(()=>auditBuiltPostMatrix(base.replace(independence,
    field('Independência jornalística','CONFIRMED')),citations),/campo visível vinculado/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(imageDigest,
    field('SHA-256 da imagem arquivística','0'.repeat(64))),citations),/campo visível vinculado/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(report,
    field('SHA-256 do relatório de custódia versionado','0'.repeat(64))),citations),
    /campo visível vinculado/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(source,
    '<a href="https://example.org/not-nara">NARA</a>'),citations),/link NARA ausente/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(custody,''),citations),
    /relatório de custódia não navegável/);
  assert.throws(()=>auditBuiltPostMatrix(base.replace(report,'')+report,citations),
    /campo visível vinculado/);
});

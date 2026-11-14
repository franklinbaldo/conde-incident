import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {postMatrixPage} from '../scripts/ssg-post-matrix.mjs';

const citations=JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
const lineage=JSON.parse(readFileSync('public/data/conde-declared-dependence.json','utf8'));
const clone=o=>structuredClone(o);

test('post-matrix SSG preserves archived source, frozen IDs and epistemic limit',()=>{
  const page=postMatrixPage(citations,lineage);
  assert.match(page,/type: Page/);
  assert.match(page,/Pós-matriz/);
  assert.match(page,/NARA-BB-CONDE-20261112-01/);
  assert.match(page,/NARA\\_AIRA\\_TELEGRAM\\_19631114/);
  assert.match(page,/136be026e23acdd5e7ff0a5307e04bef799249b48346072a43cae1506be37ce9/);
  assert.match(page,/catalog.archives.gov/);
  assert.match(page,/reports?|relatório de custódia/i);
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
  assert.throws(()=>postMatrixPage(moved,lineage),/relação sem snapshot imutável/);
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
  assert.match(rendered,/\\<script\\>/);
});

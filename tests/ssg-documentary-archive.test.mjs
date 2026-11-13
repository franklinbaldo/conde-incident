import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {archivePages} from '../scripts/ssg-documentary-archive.mjs';

const feed = JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
const ancestry = JSON.parse(readFileSync('public/data/conde-declared-dependence.json','utf8'));
const clone = obj=>JSON.parse(JSON.stringify(obj));

test('SSG publishes one stable, no-JS page per curated occurrence', () => {
  const pages=archivePages(feed, ancestry);
  assert.equal(pages.size, feed.curated_occurrences+11);
  const index=pages.get('index.md');
  assert.match(index,/28 ocorrências curadas de 241/);
  assert.match(index,/213 ocorrências não mapeadas/);
  assert.match(index,/independência/);
  assert.match(index,/\/conde-incident\/lab\/#\/documents/);
  assert.doesNotMatch(index, /<script|onclick=|onload=/i);
  for(const key of ['c01-1/index.md','c197-1/index.md','c232-1/index.md']) {
    const contents=pages.get(key);
    assert.ok(contents, `Ocorrência ausente: ${key}`);
    assert.match(contents,/Abrir ocorrência na matriz imutável/);
    assert.match(contents,/não verificação de ocorrência física/);
    assert.match(contents,/layout: page/);
  }
  assert.match(pages.get('c232-1/index.md'),/Referência 2:/);
  assert.match(pages.get('c232-1/index.md'),/2 referência\(s\) curada\(s\)/);
  assert.match(pages.get('c01-1/index.md'),/RADIO\\_TUPI\\_19631108/);
  assert.match(pages.get('c197-1/index.md'),/C197#1/);
  assert.match(index,/famílias documentais e ocorrências relacionadas/);
  assert.match(pages.get('c232-1/index.md'),/familias\/usaf-aira-bluebook\//);
  assert.match(pages.get('c232-1/index.md'),/familias\/bluebook-derivative-catalogues\//);
  assert.match(pages.get('familias/index.md'),/Famílias de fontes/);
  assert.match(pages.get('familias/radio-tupi-fbis/index.md'),/C01#1/);
  assert.match(pages.get('familias/radio-tupi-fbis/index.md'),/C03#1/);
  assert.match(pages.get('familias/norad-nasa-tracking/index.md'),/12 ocorrência\(s\)/);
  assert.match(pages.get('familias/usaf-aira-bluebook/index.md'),/C232#1/);
  assert.match(pages.get('familias/bluebook-derivative-catalogues/index.md'),/C232#1/);
  for (const [path, html] of pages) {
    assert.doesNotMatch(html, /<script|onclick=|onload=/i, `Página não estática: ${path}`);
  }
});

test('SSG fails closed on lineage and snapshot errors', () => {
  const wrong=clone(ancestry);
  wrong.matrix_git_blob_sha1='a'.repeat(40);
  assert.throws(()=>archivePages(feed,wrong), /matriz imutável/);
  const missing=clone(ancestry);
  missing.citation_lineages.pop();
  assert.throws(()=>archivePages(feed,missing), /Genealogia ausente/);
  // Adversary: a new dependency for a non-curated source must not be ignored.
  const orphan=clone(ancestry);
  orphan.citation_lineages.push({
    ...clone(ancestry.citation_lineages[0]),
    source_id:'SYNTHETIC_SOURCE_NOT_IN_CURATED_CITATIONS',
    declared_upstream_paths:[],
  });
  assert.throws(()=>archivePages(feed,orphan), /Genealogia órfã/);
  // Positive control: the unmodified one-to-one corpus is accepted.
  assert.doesNotThrow(()=>archivePages(feed,ancestry));
  const confused=clone(ancestry);
  confused.citation_lineages[0].family_id='OTHER';
  assert.throws(()=>archivePages(feed,confused), /Família divergente/);
  const fakeEvent=clone(feed);
  fakeEvent.records[0].not_a_verified_conde_physical_event=false;
  assert.throws(()=>archivePages(fakeEvent,ancestry), /true/);
});

test('SSG rejects source URL injection and unintended omissions',()=>{
  const malicious=clone(feed);
  malicious.records[0].citation_url='javascript:alert(1)';
  assert.throws(()=>archivePages(malicious,ancestry), /HTTPS/);
  const omitted=clone(feed);
  omitted.records=omitted.records.slice(1);
  assert.throws(()=>archivePages(omitted,ancestry), /Cobertura curada divergente/);
});

test('SSG rejects circular genealogy, including non-adjacent ancestry loops', () => {
  const cyclic=clone(ancestry);
  const item=cyclic.citation_lineages.find(x=>x.declared_upstream_paths.length);
  assert.ok(item, 'Corpus requires a declared source dependency');
  const origin=item.source_id;
  item.declared_upstream_paths[0]={
    upstream_source_id:origin,
    edges:[
      {from:origin,to:'SYNTHETIC_INTERMEDIARY',kind:'transcribes'},
      {from:'SYNTHETIC_INTERMEDIARY',to:origin,kind:'reprints'},
    ],
  };
  assert.throws(()=>archivePages(feed,cyclic), /Ciclo de proveniência documental/);

  // Positive control: a new two-hop dependency with distinct nodes is permitted.
  const acyclic=clone(ancestry);
  const valid=acyclic.citation_lineages.find(x=>x.declared_upstream_paths.length);
  const start=valid.source_id;
  valid.declared_upstream_paths[0]={
    upstream_source_id:'SYNTHETIC_UPSTREAM',
    edges:[
      {from:start,to:'SYNTHETIC_INTERMEDIARY',kind:'transcribes'},
      {from:'SYNTHETIC_INTERMEDIARY',to:'SYNTHETIC_UPSTREAM',kind:'reprints'},
    ],
  };
  assert.doesNotThrow(()=>archivePages(feed,acyclic));
});

test('SSG rejects unsafe or ambiguous family identifiers', () => {
  const changed=clone(feed);
  changed.records[0].source_family='RADIO_TUPI_FBIS/../../escape';
  const linked=clone(ancestry);
  linked.citation_lineages.find(x=>x.snapshot_ref===changed.records[0].snapshot_ref
    && x.source_id===changed.records[0].source_id).family_id=changed.records[0].source_family;
  assert.throws(()=>archivePages(changed,linked), /Identificador de família inválido/);
});

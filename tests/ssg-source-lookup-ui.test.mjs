import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {referenceView,sourceFromUrl,sourceLookupUrl,sourceArchiveUrl} from '../static/js/ssg-source-lookup-ui.mjs';

const page=readFileSync('pages/evidencias/fontes/page.md','utf8');
const loader=readFileSync('static/js/ssg-source-lookup-loader.mjs','utf8');
const ui=readFileSync('static/js/ssg-source-lookup-ui.mjs','utf8');
const pointer=JSON.parse(readFileSync('public/data/conde-source-lookup-manifest.json'));
const index=JSON.parse(readFileSync(pointer.source_index.path));
test('every actual curated source points only to archival pages with pinned matrix bytes',()=>{
  assert.equal(index.sources.length,15);
  const refs=index.sources.flatMap(referenceView);
  assert.equal(refs.length,index.curated_reference_count);
  for(const ref of refs){
    assert.equal(ref.archive_path,'/conde-incident/evidencias/arquivo/'+
      ref.occurrence.toLowerCase().replace('#','-')+'/');
    assert.equal(ref.row_sha256.length,64);
    assert.ok(Array.isArray(ref.upstream_edges));
  }
});
test('reject wrong occurrence, path escape, and tampered row SHA before rendering',()=>{
  const source=index.sources[0];
  for(const [key,value] of [['archive_path','https://evil.invalid/x'],
    ['archive_path','/conde-incident/evidencias/matriz/'],
    ['occurrence','<img onerror=alert(1)>'],['row_sha256','0']]){
    const mutated=structuredClone(source);mutated.references[0][key]=value;
    assert.throws(()=>referenceView(mutated));
  }
});
test('page is progressive, CSP-local and explicitly limits inference',()=>{
  assert.match(page,/type: Page/);
  assert.match(page,/source-lookup-form" hidden/);
  assert.match(page,/source-lookup-status" role="status" aria-live="polite"/);
  assert.match(page,/\/conde-incident\/evidencias\/arquivo\//);
  assert.match(page,/sem JavaScript/i);
  assert.match(page,/não significa múltiplas observações físicas independentes/);
  assert.match(page,/src="\/conde-incident\/js\/ssg-source-lookup-ui.mjs"/);
  assert.match(ui,/replaceChildren/);
  assert.doesNotMatch(ui,/\.innerHTML\s*=/);
  assert.match(loader,/shard-digest/);
  assert.match(loader,/mixed-snapshot/);
});

test('source lookup announces concise status without replaying the full SHA-256 result list',()=>{
  const region=page.match(/<section id="source-lookup-results"[^>]*>/)?.[0]??'';
  assert.match(region,/aria-label="Referências da fonte selecionada"/);
  assert.doesNotMatch(region,/aria-live=|aria-atomic=/);
  assert.match(page,/id="source-lookup-status" role="status" aria-live="polite"/);
  assert.match(ui,/status\.textContent=source[\s\S]*?vínculo\(s\) curado\(s\)/);
});

test('shareable reverse-source selection trusts only verified IDs, preserves unrelated URL state',()=>{
  const known=new Map(index.sources.map(s=>[s.source_id,s]));
  const id=index.sources[0].source_id;
  const base='https://example.org/conde-incident/evidencias/fontes/?lang=pt#consultar';
  const link=sourceLookupUrl(base,id);
  assert.equal(link,'/conde-incident/evidencias/fontes/?lang=pt&source='+encodeURIComponent(id)+'#consultar');
  assert.deepEqual(sourceFromUrl('https://example.org'+link,known),{id,invalid:false});
  assert.deepEqual(sourceFromUrl(base,known),{id:'',invalid:false});
  assert.deepEqual(sourceFromUrl(base.replace('?lang=pt','?source=NAO-EXISTE&lang=pt'),known),
    {id:'',invalid:true});
  assert.deepEqual(sourceFromUrl(base.replace('?lang=pt','?source=%3Cscript%3E&lang=pt'),known),
    {id:'',invalid:true});
  assert.equal(sourceLookupUrl('https://example.org'+link,''),
    '/conde-incident/evidencias/fontes/?lang=pt#consultar');
});

test('documentary upstream links expose declared citations, not independent witnesses',()=>{
  const refs=index.sources.flatMap(referenceView);
  const edges=refs.flatMap(ref=>ref.upstream_edges);
  assert.equal(edges.length,13);
  assert.equal(new Set(edges.map(edge=>JSON.stringify(edge))).size,8);
  const indexed=new Set(index.sources.map(s=>s.source_id));
  assert.ok(edges.some(edge=>!indexed.has(edge[2])));
  assert.match(ui,/Relações documentais declaradas \(não são observações independentes\)/);
  assert.match(ui,/sources\.has\(target\)/);
  assert.match(ui,/sourceLookupUrl\(doc\.location\.href,target\)/);
  assert.match(ui,/fora deste índice curado/);
  assert.match(ui,/EDGE_LABELS\[kind\]/);
  assert.doesNotMatch(ui,/\.innerHTML\s*=/);
});

test('reject plausible but swapped archival page and alien upstream source before rendering',()=>{
  const withEdges=index.sources.find(s=>s.references.some(r=>r.upstream_edges.length));
  const wrongPage=structuredClone(withEdges);
  wrongPage.references[0].archive_path='/conde-incident/evidencias/arquivo/c999-1/';
  assert.throws(()=>referenceView(wrongPage),/Referência inválida/);
  const spoofed=structuredClone(withEdges);
  spoofed.references[0].upstream_edges[0][0]='OUTRO_DOCUMENTO';
  assert.throws(()=>referenceView(spoofed),/Referência inválida/);
});

// The UI must not require JS to reach the full status, original document
// locator and epistemic qualification already published by the SSG archive.
test('all curated source IDs have deterministic, guarded static profile routes',()=>{
  const routes=new Set();
  for(const source of index.sources){
    const route=sourceArchiveUrl(source.source_id);
    assert.match(route,/^\/conde-incident\/evidencias\/arquivo\/fontes\/[a-z0-9-]+\/$/);
    assert.equal(route,'/conde-incident/evidencias/arquivo/fontes/'+
      source.source_id.toLowerCase().replaceAll('_','-')+'/');
    assert.ok(!routes.has(route),'duplicate static source route');
    routes.add(route);
  }
  assert.equal(routes.size,index.sources.length);
  for(const forged of ['', '../forged', 'SOURCE%2FOTHER', '<script>',
    'https://example.org/other', 'lowercase', null]){
    assert.throws(()=>sourceArchiveUrl(forged),/Identificador de fonte inválido/);
  }
  assert.match(ui,/profileLink\.href=sourceArchiveUrl\(source\.source_id\)/);
  assert.match(ui,/Abrir ficha documental estática de/);
  assert.match(page,/\/conde-incident\/evidencias\/arquivo\/fontes\//);
});

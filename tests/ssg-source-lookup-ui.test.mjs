import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {referenceView} from '../static/js/ssg-source-lookup-ui.mjs';

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
    assert.ok(ref.archive_path.startsWith('/conde-incident/evidencias/arquivo/'));
    assert.equal(ref.row_sha256.length,64);
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

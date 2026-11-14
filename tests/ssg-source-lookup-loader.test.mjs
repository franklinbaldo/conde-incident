import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {createHash} from 'node:crypto';
import {loadCondeSourceLookup,SourceLookupIntegrityError} from '../scripts/ssg-source-lookup-loader.mjs';

const BASE='https://example.org/conde-incident/';
const P='data/conde-source-lookup-manifest.json';
const E='data/conde-evidence-index-manifest.json';
const bytes = item => Buffer.from(JSON.stringify(item));
const hashBytes = item => createHash('sha256').update(item).digest('hex');
const stockPointer=JSON.parse(readFileSync('public/'+P));
const shardPath=stockPointer.source_index.path.replace(/^public\//,'');
const stock=new Map([[P,readFileSync('public/'+P)],[E,readFileSync('public/'+E)],
  [shardPath,readFileSync(stockPointer.source_index.path)]]);

function fixture(overrides=new Map()) {
  const m=new Map([...stock,...overrides]);
  const calls=[];
  const fetcher=async (url,opts)=>{
    const path=new URL(url).pathname.replace('/conde-incident/','');
    calls.push([path,opts.cache]);
    const b=m.get(path);
    if(!b) return {ok:false};
    return {ok:true,arrayBuffer:async()=>b.buffer.slice(b.byteOffset,b.byteOffset+b.byteLength)};
  };
  const read=()=>loadCondeSourceLookup({baseUrl:BASE,fetcher,hashBytes});
  return {read,calls};
}
const fails=async (fixture,code)=>assert.rejects(fixture.read(),err=>
  err instanceof SourceLookupIntegrityError&&err.code===code);

test('verified source lookup binds pointer, immutable shard, evidence generation and coverage',async()=>{
  const f=fixture();
  const value=await f.read();
  assert.equal(value.sources.length,15);
  assert.equal(value.families.length,9);
  assert.equal(value.curated_reference_count,29);
  assert.equal(value.curated_occurrence_count,28);
  assert.equal(value.unmapped_occurrence_count,213);
  assert.equal(value.independent_physical_observation_count,null);
  assert.deepEqual(f.calls.sort(),[[E,'no-store'],[P,'no-store'],[shardPath,'force-cache']].sort());
});

test('digest-named shard from stale cache fails closed',async()=>{
  const corrupted=Buffer.from(stock.get(shardPath));
  corrupted[100]^=1;
  await fails(fixture(new Map([[shardPath,corrupted]])),'shard-digest');
});

test('old source pointer and a new evidence index cannot be mixed',async()=>{
  const changed=Buffer.from(stock.get(E));changed[100]^=1;
  await fails(fixture(new Map([[E,changed]])),'mixed-snapshot');
});

test('source pointer cannot redirect to another path even with plausible digest',async()=>{
  const pointer=structuredClone(stockPointer);
  pointer.source_index.path='public/data/../private/part-'+pointer.source_index.sha256+'.json';
  await fails(fixture(new Map([[P,bytes(pointer)]])),'shard-contract');
});

test('source index metadata cannot lie about byte length',async()=>{
  const pointer=structuredClone(stockPointer);pointer.source_index.bytes+=1;
  await fails(fixture(new Map([[P,bytes(pointer)]])),'shard-digest');
});

test('source index metadata cannot add epistemic claim without a schema change',async()=>{
  const pointer=structuredClone(stockPointer);pointer.independent_physical_observation_count=5;
  await fails(fixture(new Map([[P,bytes(pointer)]])),'pointer-schema');
});

test('missing shard is not silently replaced by an old or unverified copy',async()=>{
  await fails(fixture(new Map([[shardPath,null]])),'http-failure');
});

test('same SHA with source graph mutation is not accepted even if pointer and shard are re-signed',async()=>{
  const index=JSON.parse(stock.get(shardPath));
  index.source_files_sha256['public/data/conde-source-citations.json']='f'.repeat(64);
  const changed=bytes(index),digest=hashBytes(changed);
  const pointer=structuredClone(stockPointer);
  const newPath=`data/conde-source-lookup/part-${digest}.json`;
  pointer.source_index={path:'public/'+newPath,sha256:digest,bytes:changed.length};
  await fails(fixture(new Map([[P,bytes(pointer)],[newPath,changed]])),'source-snapshot');
});

test('post-matrix document cannot become a claimed physical observation after pointer reseal',async()=>{
  const index=JSON.parse(stock.get(shardPath));
  index.post_matrix_only[0].independent_physical_observation_count=1;
  const changed=bytes(index),digest=hashBytes(changed);
  const pointer=structuredClone(stockPointer);
  const newPath=`data/conde-source-lookup/part-${digest}.json`;
  pointer.source_index={path:'public/'+newPath,sha256:digest,bytes:changed.length};
  await fails(fixture(new Map([[P,bytes(pointer)],[newPath,changed]])),'post-matrix-promotion');
});

test('wrong origin is rejected before any fetch',async()=>{
  const f=fixture();
  await assert.rejects(loadCondeSourceLookup({baseUrl:'http://example.org/conde-incident/',
    fetcher:()=>assert.fail('should not fetch'),hashBytes}),
  e=>e.code==='unsafe-origin');
});

test('loopback Chromium server is safe while HTTP outside loopback remains rejected',async()=>{
  const f=fixture();
  const fetcher=async (url,opts)=>{
    assert.equal(new URL(url).hostname,'127.0.0.1');
    const path=new URL(url).pathname.replace('/conde-incident/','');
    const source=stock.get(path);
    return {ok:Boolean(source),arrayBuffer:async()=>source.buffer.slice(source.byteOffset,source.byteOffset+source.byteLength)};
  };
  const verified=await loadCondeSourceLookup({baseUrl:'http://127.0.0.1:4173/conde-incident/',fetcher,hashBytes});
  assert.equal(verified.sources.length,15);
  await assert.rejects(loadCondeSourceLookup({baseUrl:'http://example.org/conde-incident/',
    fetcher,hashBytes}),e=>e.code==='unsafe-origin');
});


// These checks protect consumers even if the pointer and shard digest are
// rewritten together. A digest is a checksum, not a semantic authorization.
function resealed(index) {
  const changed=bytes(index), digest=hashBytes(changed);
  const pointer=structuredClone(stockPointer);
  const newPath=`data/conde-source-lookup/part-${digest}.json`;
  pointer.source_index={path:'public/'+newPath,sha256:digest,bytes:changed.length};
  return fixture(new Map([[P,bytes(pointer)],[newPath,changed]]));
}

test('duplicate source ID cannot silently overwrite a browser Map entry',async()=>{
  const index=JSON.parse(stock.get(shardPath));
  index.sources[1].source_id=index.sources[0].source_id;
  await fails(resealed(index),'index-shape');
});

test('orphan and duplicate family membership cannot pass by re-signing shard',async()=>{
  const index=JSON.parse(stock.get(shardPath));
  index.families[0].source_ids.push(index.families[0].source_ids[0]);
  await fails(resealed(index),'index-shape');
});

test('reverse catalog coverage must equal the independent evidence manifest',async()=>{
  const index=JSON.parse(stock.get(shardPath));
  index.unmapped_occurrence_count+=1;
  await fails(resealed(index),'coverage-mismatch');
});

test('malformed base URL returns a typed integrity failure, not a raw URL exception',async()=>{
  await assert.rejects(loadCondeSourceLookup({baseUrl:'https://[bad]/',
    fetcher:()=>assert.fail('should not fetch'),hashBytes}),
  e=>e instanceof SourceLookupIntegrityError && e.code==='invalid-base-url');
});

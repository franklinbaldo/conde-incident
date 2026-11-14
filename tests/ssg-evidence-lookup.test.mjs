/** Adversarial tests for the complete 241-occurrence search crosswalk. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readBundle,audit} from '../scripts/verify-ssg-evidence-index.mjs';

const digest=raw=>createHash('sha256').update(raw).digest('hex');
const forge=(bundle,mutate)=>{
  const part=bundle.lookupShards.at(-1);
  const copy=JSON.parse(part.raw);
  mutate(copy.records);
  part.raw=Buffer.from(JSON.stringify(copy));
  const meta=bundle.manifest.lookup_shards.at(-1);
  meta.sha256=digest(part.raw);
  meta.bytes=part.raw.length;
  meta.path=meta.path.replace(/-[a-f0-9]{64}\.json$/,'-'+meta.sha256+'.json');
  part.path=meta.path;
};

test('every original occurrence resolves exactly to a curated or unmapped shard',()=>{
  const bundle=readBundle();
  const count=bundle.lookupShards.reduce((sum,part)=>sum+JSON.parse(part.raw).records.length,0);
  assert.equal(count,bundle.manifest.total_matrix_occurrences);
  const entries=bundle.lookupShards.flatMap(part=>JSON.parse(part.raw).records);
  for (const label of ['C44','C45','C46']) {
    assert.ok(entries.some(item=>item.occurrence===label+'#1'));
    assert.ok(entries.some(item=>item.occurrence===label+'#2'));
  }
  assert.ok(entries.some(item=>item.kind==='curated'));
  assert.ok(entries.some(item=>item.kind==='unmapped'));
  audit(bundle);
});

test('retargeted pointer rejected despite recomputed digest',()=>{
  const bundle=readBundle();
  forge(bundle,items=>{items[0].positions[0][1]++;});
  assert.throws(()=>audit(bundle),/Lookup pointers differ/);
});

test('forged epistemological promotion rejected despite recomputed digest',()=>{
  const bundle=readBundle();
  forge(bundle,items=>{items[0].kind='curated';});
  assert.throws(()=>audit(bundle),/Lookup pointers differ/);
});

test('omitted occurrence rejected despite recomputed digest and count',()=>{
  const bundle=readBundle();
  forge(bundle,items=>{items.pop();});
  bundle.manifest.lookup_shards.at(-1).record_count--;
  assert.throws(()=>audit(bundle),/Lookup pointers differ/);
});

test('unreviewed metadata field rejected despite recomputed digest',()=>{
  const bundle=readBundle();
  forge(bundle,items=>{items[0].physical_observation=true;});
  assert.throws(()=>audit(bundle),/Unexpected lookup record fields/);
});

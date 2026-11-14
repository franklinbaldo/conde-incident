/** Independent, exact occurrence -> shard/offset verification for the SSG feed. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {exactKeys,shardMetaKeys} from './ssg-evidence-index-schema.mjs';

const digest=raw=>createHash('sha256').update(raw).digest('hex');
const schema='conde.evidence-lookup-shard/v1';

export function auditLookup(manifest,shards,gapShards,lookupShards,matrixInventory) {
  const locations=new Map();
  for (const [kind,groups] of [['curated',shards],['unmapped',gapShards]]) {
    for (const [shardIndex,part] of groups.entries()) {
      for (const [rowIndex,row] of JSON.parse(part.raw).records.entries()) {
        const item=locations.get(row.occurrence) ?? {
          occurrence:row.occurrence,kind,positions:[],
        };
        assert.equal(item.kind,kind,'Contradictory curation for '+row.occurrence);
        item.positions.push([shardIndex,rowIndex]);
        locations.set(row.occurrence,item);
      }
    }
  }
  assert.equal(locations.size,matrixInventory.size,
    'Lookup misses a frozen matrix occurrence');
  const expected=[...matrixInventory.keys()].map(id=>{
    assert.ok(locations.has(id),'Missing lookup occurrence '+id);
    return locations.get(id);
  });
  assert.equal(lookupShards.length,manifest.lookup_shards.length);
  const actual=[];
  for (const [i,meta] of manifest.lookup_shards.entries()) {
    exactKeys(meta,shardMetaKeys,'lookup metadata');
    assert.equal(meta.path,
      'public/data/conde-evidence-lookup/part-'+String(i+1).padStart(3,'0')+'.json',
      'Unexpected lookup path/order');
    const part=lookupShards[i];
    assert.equal(part.path,meta.path);
    assert.equal(meta.sha256,digest(part.raw),'Lookup SHA mismatch');
    assert.equal(meta.bytes,part.raw.length,'Lookup size mismatch');
    assert.ok(meta.bytes<=12000,'Lookup shard exceeds 12kB');
    const data=JSON.parse(part.raw);
    exactKeys(data,['schema','records'],'lookup shard');
    assert.equal(data.schema,schema);
    assert.equal(meta.record_count,data.records.length);
    for (const item of data.records) {
      exactKeys(item,['occurrence','kind','positions'],'lookup record');
      assert.ok(['curated','unmapped'].includes(item.kind),'Invalid lookup kind');
      assert.ok(Array.isArray(item.positions) && item.positions.length>0);
      for (const position of item.positions)
        assert.ok(Array.isArray(position) && position.length===2 &&
          position.every(n=>Number.isSafeInteger(n) && n>=0),
        'Invalid lookup offset');
      actual.push(item);
    }
  }
  assert.deepEqual(actual,expected,
    'Lookup pointers differ from original shards and immutable matrix');
  return {occurrences:actual.length,lookupShards:lookupShards.length};
}

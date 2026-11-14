/** Verify immutable digest shards AND exact pre-migration aliases for cached v1 manifests. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync,readdirSync} from 'node:fs';
import {join} from 'node:path';

const sha=raw=>createHash('sha256').update(raw).digest('hex');
const digestName=/^part-[0-9]{3}-([0-9a-f]{64})\.json$/;
const legacyName=/^part-[0-9]{3}\.json$/;
const folders=['conde-evidence-index','conde-evidence-gaps','conde-evidence-lookup'];
const fields=['shards','unmapped_shards','lookup_shards'];
const sourceSha='35a4d1a0853fe71e95d155fb6117c386f6dde849fa0e1f68588018396f11e740';

export function auditPublishedHistory(root,manifest) {
  const ledger=JSON.parse(readFileSync(join(root,'tools/ssg-legacy-shards.json')));
  const old=readFileSync(join(root,'tests/fixtures/ssg-legacy-manifest-v1.json'));
  assert.equal(sha(old),sourceSha,'Original pre-migration manifest changed');
  assert.equal(ledger.schema,'conde.ssg-legacy-shards/v1');
  assert.equal(ledger.source_commit,'b905dd5b3d197d340261e395b19079642e3ae99f');
  assert.equal(ledger.source_manifest_sha256,sourceSha);
  const previous=JSON.parse(old);
  const oldRefs=fields.flatMap(field=>previous[field]);
  assert.equal(ledger.shards.length,oldRefs.length,'Legacy ledger truncated');
  const pinned=new Map();
  for(const entry of ledger.shards) {
    assert.deepEqual(Object.keys(entry).sort(),['bytes','path','sha256']);
    assert.ok(folders.some(folder=>entry.path.startsWith('public/data/'+folder+'/')));
    assert.ok(legacyName.test(entry.path.split('/').at(-1)),'Invalid legacy alias');
    assert.ok(!pinned.has(entry.path),'Duplicate legacy alias');
    pinned.set(entry.path,entry);
    assert.ok(oldRefs.some(ref=>ref.path===entry.path&&ref.bytes===entry.bytes&&ref.sha256===entry.sha256),
      'Legacy alias differs from cached manifest');
  }
  for(const [folder,refField] of folders.map((name,i)=>[name,fields[i]])) {
    const location=join(root,'public/data',folder);
    const names=readdirSync(location).filter(name=>/^part-.*\.json$/.test(name));
    const present=new Set(names);
    for(const meta of manifest[refField])
      assert.ok(present.has(meta.path.split('/').at(-1)),'Missing '+folder+' shard: '+meta.path);
    for(const ref of oldRefs.filter(row=>row.path.startsWith('public/data/'+folder+'/')))
      assert.ok(present.has(ref.path.split('/').at(-1)),'Missing legacy cached shard: '+ref.path);
    for(const name of names) {
      const relative='public/data/'+folder+'/'+name;
      const match=digestName.exec(name);
      if(match) assert.equal(sha(readFileSync(join(location,name))),match[1],
        'Historical digest shard mismatch: '+relative);
      else {
        assert.ok(pinned.has(relative),'Unpinned/orphan legacy shard: '+relative);
        const entry=pinned.get(relative);
        const raw=readFileSync(join(location,name));
        assert.equal(raw.length,entry.bytes,'Legacy shard size mismatch: '+relative);
        assert.equal(sha(raw),entry.sha256,'Legacy shard hash mismatch: '+relative);
      }
    }
  }
}

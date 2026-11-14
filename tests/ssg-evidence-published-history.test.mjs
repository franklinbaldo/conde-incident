/** Regression: a cached v1 manifest can still fetch its eleven numbered shards. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {copyFileSync,cpSync,mkdirSync,mkdtempSync,readFileSync,writeFileSync,rmSync,unlinkSync} from 'node:fs';
import {join,resolve} from 'node:path';
import {tmpdir} from 'node:os';
import {auditPublishedHistory} from '../scripts/ssg-evidence-published-history.mjs';

const root=resolve(import.meta.dirname,'..');
const groups=['conde-evidence-index','conde-evidence-gaps','conde-evidence-lookup'];
const manifest=JSON.parse(readFileSync(join(root,'public/data/conde-evidence-index-manifest.json')));
const legacy=JSON.parse(readFileSync(join(root,'tools/ssg-legacy-shards.json')));

function fixture(fn) {
  const testRoot=mkdtempSync(join(tmpdir(),'conde-legacy-cache-'));
  try {
    mkdirSync(join(testRoot,'tools'),{recursive:true});
    mkdirSync(join(testRoot,'tests/fixtures'),{recursive:true});
    copyFileSync(join(root,'tools/ssg-legacy-shards.json'),join(testRoot,'tools/ssg-legacy-shards.json'));
    copyFileSync(join(root,'tests/fixtures/ssg-legacy-manifest-v1.json'),
      join(testRoot,'tests/fixtures/ssg-legacy-manifest-v1.json'));
    for(const folder of groups)
      cpSync(join(root,'public/data',folder),join(testRoot,'public/data',folder),{recursive:true});
    fn(testRoot);
  } finally { rmSync(testRoot,{recursive:true,force:true}); }
}

test('all cached v1 references coexist with the current digest release',()=> {
  fixture(tmp=>auditPublishedHistory(tmp,manifest));
});

test('legacy alias byte substitution fails even when current manifest is valid',()=> {
  fixture(tmp=>{
    const path=join(tmp,legacy.shards[0].path);
    const raw=readFileSync(path);raw[0]^=1;writeFileSync(path,raw);
    assert.throws(()=>auditPublishedHistory(tmp,manifest),/Legacy shard hash mismatch/);
  });
});

test('missing cached v1 alias fails',()=>{
  fixture(tmp=>{
    unlinkSync(join(tmp,legacy.shards[0].path));
    assert.throws(()=>auditPublishedHistory(tmp,manifest),/Missing legacy cached shard/);
  });
});

test('unlisted numbered shard fails',()=>{
  fixture(tmp=>{
    writeFileSync(join(tmp,'public/data/conde-evidence-index/part-999.json'),'{}');
    assert.throws(()=>auditPublishedHistory(tmp,manifest),/Unpinned\/orphan legacy shard/);
  });
});

test('tampering with old manifest fixture fails independently of ledger',()=>{
  fixture(tmp=>{
    const file=join(tmp,'tests/fixtures/ssg-legacy-manifest-v1.json');
    writeFileSync(file,readFileSync(file).toString().replace('curated','forged'));
    assert.throws(()=>auditPublishedHistory(tmp,manifest),/Original pre-migration manifest changed/);
  });
});

test('corrupt immutable historical digest-named shard fails',()=>{
  fixture(tmp=>{
    const path=join(tmp,manifest.shards[0].path);
    writeFileSync(path,'{}\n');
    assert.throws(()=>auditPublishedHistory(tmp,manifest),/Historical digest shard mismatch/);
  });
});

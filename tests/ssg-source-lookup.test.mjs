import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {auditSourceLookup} from '../scripts/verify-ssg-source-lookup.mjs';

const sha=raw=>createHash('sha256').update(raw).digest('hex');
const manifest='public/data/conde-source-lookup-manifest.json';
test('source reverse lookup independently reconstructs all citations and post-matrix lineage',()=>{
  const result=auditSourceLookup();
  assert.equal(result.citations,29);
  assert.equal(result.sources,15);
  assert.equal(result.families,9);
  assert.equal(result.postMatrix,1);
});
test('forged epistemic count fails even when JSON SHA and pointer are resealed',()=>{
  const pointer=JSON.parse(readFileSync(manifest));
  const path=pointer.source_index.path;
  const forged=JSON.parse(readFileSync(path));
  forged.independent_physical_observation_count=1;
  const bytes=Buffer.from(JSON.stringify(forged));
  const newSha=sha(bytes);
  const newPath=path.replace(/[a-f0-9]{64}\.json$/g,newSha+'.json');
  pointer.source_index={path:newPath,bytes:bytes.length,sha256:newSha};
  const overrides=new Map([[manifest,Buffer.from(JSON.stringify(pointer))],
    [newPath,bytes]]);
  assert.throws(()=>auditSourceLookup('.',overrides),/Reverse lookup differs/);
});
test('retargeted source or false edge fails with matching digest',()=>{
  const pointer=JSON.parse(readFileSync(manifest));
  const path=pointer.source_index.path;
  const forged=JSON.parse(readFileSync(path));
  forged.sources[0].references[0].upstream_edges=[['A','invented_independence','B']];
  const bytes=Buffer.from(JSON.stringify(forged));
  const newSha=sha(bytes);
  const newPath=path.replace(/[a-f0-9]{64}\.json$/g,newSha+'.json');
  pointer.source_index={path:newPath,bytes:bytes.length,sha256:newSha};
  assert.throws(()=>auditSourceLookup('.',new Map([
    [manifest,Buffer.from(JSON.stringify(pointer))],[newPath,bytes]])),
  /Reverse lookup differs/);
});

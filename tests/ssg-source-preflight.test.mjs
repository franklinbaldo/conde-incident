import test from 'node:test';
import assert from 'node:assert/strict';
import {cpSync,existsSync,mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {join,resolve,dirname} from 'node:path';
import {spawnSync} from 'node:child_process';

const project=resolve(import.meta.dirname,'..');
const script=join(project,'scripts/prepare-ssg.mjs');
function fixture(fn){
  const tmp=mkdtempSync(join(tmpdir(),'conde-ssg-preflight-'));
  const sources=[
    'stories','pages','public/data','research/archives',
    'research/evidence_matrix_C001-C238_2026-11-11.md',
    'research/tle_custody/mirror_528_1963-10-27.tle',
    'tools/ssg-legacy-shards.json','tests/fixtures/ssg-legacy-manifest-v1.json',
  ];
  try {
    for(const source of sources){
      const output=join(tmp,source);
      mkdirSync(dirname(output),{recursive:true});
      cpSync(join(project,source),output,{recursive:true});
    }
    const run=()=>spawnSync(process.execPath,[script,'--check'],{
      cwd:tmp,encoding:'utf8',timeout:90_000});
    fn({tmp,run});
  } finally {rmSync(tmp,{force:true,recursive:true});}
}
const edit=(tmp,file,replace)=>{
  const path=join(tmp,file),original=readFileSync(path,'utf8');
  const changed=replace(original);
  assert.notEqual(changed,original,'Test mutant failed to change the canonical source');
  writeFileSync(path,changed);
};

test('SSG --check validates all canonical sources without creating content',()=>{
  fixture(({tmp,run})=>{
    const before=readFileSync(join(tmp,'public/data/conde-source-citations.json'));
    const result=run();
    assert.equal(result.status,0,result.stderr);
    assert.match(result.stdout,/Preflight de fontes SSG \(sem escrita\)/);
    assert.match(result.stdout,/"totalOccurrences":241/);
    assert.ok(!existsSync(join(tmp,'content')),'--check must not create SSG output');
    assert.deepEqual(readFileSync(join(tmp,'public/data/conde-source-citations.json')),before);
  });
});
test('SSG --check rejects forged newspaper metadata before generating files',()=>{
  fixture(({tmp,run})=>{
    edit(tmp,'public/data/conde-source-citations.json',source=>
      source.replace('"newspaper_page": null','"newspaper_page": "inventada"'));
    const result=run();
    assert.notEqual(result.status,0);
    assert.match(result.stderr,/Source SHA mismatch|metadado jornalístico não verificado/);
    assert.ok(!existsSync(join(tmp,'content')));
  });
});
test('SSG --check rejects damaged custody report with unchanged JSON',()=>{
  fixture(({tmp,run})=>{
    const file='research/archives/nara_bluebook_conde_naid_302531012_2026-11-12.md';
    edit(tmp,file,source=>source.replace('**14 NOV 1963**','**15 NOV 1963**'));
    const result=run();
    assert.notEqual(result.status,0);
    assert.match(result.stderr,/Cronologia: data do telegrama diverge|telegrama não corresponde/);
    assert.ok(!existsSync(join(tmp,'content')));
  });
});
test('SSG --check rejects an authored page claiming a different route',()=>{
  fixture(({tmp,run})=>{
    edit(tmp,'pages/metodo/page.md',source=>
      source.replace('/conde-incident/metodo/','/conde-incident/hipoteses/'));
    const result=run();
    assert.notEqual(result.status,0);
    assert.match(result.stderr,/URL declarada não coincide|Page/);
    assert.ok(!existsSync(join(tmp,'content')));
  });
});
test('SSG --check detects tampered pinned TLE bytes',()=>{
  fixture(({tmp,run})=>{
    edit(tmp,'research/tle_custody/mirror_528_1963-10-27.tle',source=>
      source.replace('1 00528','1 00529'));
    const result=run();
    assert.notEqual(result.status,0);
    assert.match(result.stderr,/Bytes de custódia TLE diferentes/);
    assert.ok(!existsSync(join(tmp,'content')));
  });
});

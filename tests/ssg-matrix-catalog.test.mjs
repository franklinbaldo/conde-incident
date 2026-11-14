/** Source-locked, accessible without JS, 241-row matrix catalog. */
import test from 'node:test';
import {readFileSync,writeFileSync,mkdirSync,mkdtempSync,rmSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join} from 'node:path';
import assert from 'node:assert/strict';
import {readBundle,audit} from '../scripts/verify-ssg-evidence-index.mjs';
import {matrixCatalogPages,auditBuiltMatrixCatalog} from '../scripts/ssg-matrix-catalog.mjs';
import {matrixRowUrl} from '../scripts/ssg-documentary-archive.mjs';

const clone=o=>JSON.parse(JSON.stringify(o));

test('241 frozen occurrences have stable paginated HTML source links, including uncurated gaps',()=>{
  const bundle=readBundle();
  audit(bundle);
  const {files,entries,pages}=matrixCatalogPages(bundle);
  assert.equal(files.size,14);
  assert.equal(pages.length,13);
  assert.equal(entries.length,241);
  assert.equal(entries.filter(({pointer})=>pointer.kind==='curated').length,28);
  assert.equal(entries.filter(({pointer})=>pointer.kind==='unmapped').length,213);
  assert.match(files.get('index.md'),/241 ocorrências/);
  assert.match(files.get('index.md'),/213 ainda sem ficha/);
  assert.match(files.get('index.md'),/Localizador rápido por identificador/);
  assert.ok(Buffer.byteLength(files.get('index.md'),'utf8')<=20000);
  for(const [n,{pointer,record}] of entries.entries()){
    const destination='/conde-incident/evidencias/matriz/paginas/'+String(Math.floor(n/20)+1).padStart(2,'0')+'/';
    const anchor=pointer.occurrence.replace('#','-');
    assert.ok(files.get('index.md').includes('['+pointer.occurrence+']('+destination+'#'+anchor+')'),
      'Missing direct ID locator for '+pointer.occurrence);
    const page=files.get('paginas/'+String(Math.floor(n/20)+1).padStart(2,'0')+'/index.md');
    assert.ok(page.includes('<span id="'+anchor+'" tabindex="-1"></span>'),
      'Missing fragment target for '+pointer.occurrence);
    assert.ok(page.includes('## '+pointer.occurrence+' · '),pointer.occurrence);
    assert.ok(page.includes(matrixRowUrl(record.matrix_line)),pointer.occurrence);
    assert.ok(page.includes(record.row_sha256),pointer.occurrence);
    if(pointer.kind==='curated')assert.ok(page.includes(record.archive_path));
    else assert.ok(page.includes('ainda sem ficha documental curada'));
  }
  for(const slug of ['paginas/01/index.md','paginas/13/index.md']){
    const page=files.get(slug);
    assert.match(page,/^---\ntype: Page\n/);
    assert.match(page,/Índice da matriz/);
    assert.ok(Buffer.byteLength(page,'utf8')<=20000);
  }
  const pagesText=[...files.values()].join('\n');
  for(const id of ['C44#1','C44#2','C45#1','C45#2','C46#1','C46#2'])
    assert.ok(pagesText.includes('## '+id+' · '),'Duplicate matrix label lost: '+id);
  assert.doesNotMatch(pagesText,/<script|onclick=|onload=/i);
  assert.doesNotMatch(pagesText,/independent_physical_observation_count: [0-9]/);
});

test('altering a lookup offset never silently sends a reader to another row',()=>{
  const bundle=readBundle();
  const pointer=JSON.parse(bundle.lookupShards[0].raw);
  const saved=clone(pointer.records[0]);
  pointer.records[0].positions[0][1]++;
  bundle.lookupShards[0].raw=Buffer.from(JSON.stringify(pointer));
  assert.throws(()=>matrixCatalogPages(bundle),/Expected values to be strictly equal/);
  assert.notDeepEqual(pointer.records[0],saved);
});

test('title display remains inert Markdown, not injected HTML',()=>{
  const bundle=readBundle();
  const part=JSON.parse(bundle.gapShards[0].raw);
  part.records[0].claim_text='<script>alert(1)</script> [false](javascript:alert(1))';
  bundle.gapShards[0].raw=Buffer.from(JSON.stringify(part));
  const {files}=matrixCatalogPages(bundle);
  const page=files.get('paginas/01/index.md');
  assert.ok(page.includes('\\<script\\>'));
  assert.ok(page.includes('\\[false\\]'));
  assert.ok(!page.includes('<script>'));
});

// Reproduce the published-HTML gate, not only the Markdown generator: a fragment
// found in a comment or inert element cannot be a browser navigation target.
test('built matrix audit rejects inert and duplicated fragment targets',()=>{
  const bundle=readBundle();
  const {entries,pages}=matrixCatalogPages(bundle);
  const root=mkdtempSync(join(tmpdir(),'conde-g59-'));
  const write=(relative,html)=>{
    const path=join(root,relative);
    mkdirSync(dirname(path),{recursive:true});
    writeFileSync(path,html);
  };
  const link=href=>`<a href="${href}">abrir</a>`;
  try{
    write('evidencias/matriz/index.html','<html><main>'+[
      ...pages.map(p=>link(p.url)),
      ...entries.map(({pointer},i)=>link(pages[Math.floor(i/20)].url+'#'+pointer.occurrence.replace('#','-'))),
    ].join('')+'</main></html>');
    for(let i=0;i<pages.length;i++){
      const parts=entries.slice(i*20,(i+1)*20).map(({pointer,record})=>[
        `<span id="${pointer.occurrence.replace('#','-')}" tabindex="-1"></span>`,
        `<h2>${pointer.occurrence}</h2><p>${record.row_sha256}</p>`,
        link(matrixRowUrl(record.matrix_line)),
        ...(pointer.kind==='curated'?[link(record.archive_path)]:[]),
      ].join(''));
      write('evidencias/matriz/paginas/'+String(i+1).padStart(2,'0')+'/index.html',
        '<html><main>'+link('/conde-incident/evidencias/matriz/')+parts.join('')+'</main></html>');
    }
    for(const path of ['evidencias/index.html','evidencias/arquivo/index.html'])
      write(path,'<html><main>'+link('/conde-incident/evidencias/matriz/')+'</main></html>');
    assert.deepEqual(auditBuiltMatrixCatalog(bundle,root),{pages:14,occurrences:241});
    const path=join(root,'evidencias/matriz/paginas/01/index.html');
    const original=readFileSync(path,'utf8');
    const marker='<span id="'+entries[0].pointer.occurrence.replace('#','-')+'" tabindex="-1"></span>';
    assert.ok(original.includes(marker));
    for(const [scenario,replacement] of [
      ['comment','<!-- '+marker+' -->'],
      ['script','<script>'+marker+'</script>'],
      ['template','<template>'+marker+'</template>'],
      ['hidden','<section aria-hidden="true">'+marker+'</section>'],
      ['outside main','</main>'+marker+'<main>'],
      ['duplicate',marker+marker],
    ]){
      writeFileSync(path,original.replace(marker,replacement));
      assert.throws(()=>auditBuiltMatrixCatalog(bundle,root),
        /Missing unique active target anchor/,scenario);
    }
  }finally{rmSync(root,{recursive:true,force:true});}
});

/** Regression tests: static SSG routes and immutable documentary JSON stay joined. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,mkdirSync,readFileSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join} from 'node:path';
import {audit,auditBuiltSite,readBundle,visibleDocument} from '../scripts/verify-ssg-evidence-index.mjs';

const clean=()=>readBundle(); // Fresh, independent on-disk fixture each time.
const mutateRow=(bundle,change)=>{
  const shard=bundle.shards[0];
  const data=JSON.parse(shard.raw);
  change(data.records[0]);
  shard.raw=Buffer.from(JSON.stringify(data));
  bundle.manifest.shards[0].sha256=createHash('sha256').update(shard.raw).digest('hex');
  bundle.manifest.shards[0].bytes=shard.raw.length;
};

test('every published JSON record links to a generated, navigable SSG occurrence',()=>{
  const summary=audit(readBundle());
  assert.ok(summary.references>=summary.occurrences);
  assert.ok(summary.ssgPages>summary.occurrences);
  assert.ok(summary.shards>0);
});

test('modified historical matrix is rejected even with unchanged feeds',()=>{
  const bundle=clean();
  bundle.matrixBytes=Buffer.concat([bundle.matrixBytes,Buffer.from('\n<!-- changed -->\n')]);
  assert.throws(()=>audit(bundle),/Frozen matrix Git blob mismatch/);
});

test('consistent forged hash across citation, lineage and shard is rejected',()=>{
  const bundle=clean();
  const record=bundle.citations.records[0];
  record.row_sha256='0'.repeat(64);
  const lineage=bundle.lineage.citation_lineages.find(item=>
    item.snapshot_ref===record.snapshot_ref && item.source_id===record.source_id);
  lineage.row_sha256=record.row_sha256;
  mutateRow(bundle,row=>{row.row_sha256=record.row_sha256;});
  assert.throws(()=>audit(bundle),/Matrix row SHA-256 mismatch/);
});

test('tampered shard bytes fail digest validation',()=>{
  const bundle=clean();
  bundle.shards[0].raw=Buffer.from('{}');
  assert.throws(()=>audit(bundle),/Shard SHA mismatch/);
});

test('forged link fails even with recomputed shard SHA',()=>{
  const bundle=clean();
  mutateRow(bundle,row=>{row.archive_path='/conde-incident/evidencias/arquivo/c999-1/';});
  assert.throws(()=>audit(bundle),/Broken archive route/);
});

// A source-feed SHA and shard SHA can both be recomputed after a forged edit.
// Node must inspect the provenance graph itself, not simply compare two copies.
function mutateSynchronizedLineage(bundle,change) {
  const entry=bundle.lineage.citation_lineages.find(row=>row.declared_upstream_paths.length);
  assert.ok(entry,'Expected at least one documented dependency chain');
  change(entry.declared_upstream_paths[0],entry);
  const raw=Buffer.from(JSON.stringify(bundle.lineage));
  bundle.sourceBytes.set('public/data/conde-declared-dependence.json',raw);
  bundle.manifest.source_files[1].sha256=createHash('sha256').update(raw).digest('hex');
  const shard=bundle.shards.find(part=>JSON.parse(part.raw).records.some(row=>
    row.snapshot_ref===entry.snapshot_ref && row.source_id===entry.source_id));
  assert.ok(shard);
  const data=JSON.parse(shard.raw);
  const indexed=data.records.find(row=>row.snapshot_ref===entry.snapshot_ref &&
    row.source_id===entry.source_id);
  indexed.declared_upstream_paths=structuredClone(entry.declared_upstream_paths);
  shard.raw=Buffer.from(JSON.stringify(data));
  const meta=bundle.manifest.shards.find(item=>item.path===shard.path);
  meta.sha256=createHash('sha256').update(shard.raw).digest('hex');
  meta.bytes=shard.raw.length;
}

test('synchronized source and shard cannot smuggle an unvalidated terminal claim',()=>{
  const bundle=clean();
  mutateSynchronizedLineage(bundle,path=>{
    path.norad_528_terminal_epoch_utc='1963-11-08T08:15:00Z';
  });
  assert.throws(()=>audit(bundle),/Unvalidated dependency path fields/);
});

test('synchronized source and shard cannot introduce a dependency cycle',()=>{
  const bundle=clean();
  mutateSynchronizedLineage(bundle,(path,entry)=>{
    path.edges.push({from:path.upstream_source_id,to:entry.source_id,kind:'claims'});
    path.upstream_source_id=entry.source_id;
  });
  assert.throws(()=>audit(bundle),/Cyclic dependency chain/);
});

test('synchronized source and shard cannot jump between dependency nodes',()=>{
  const bundle=clean();
  mutateSynchronizedLineage(bundle,path=>{
    path.edges[0].from='UNKNOWN_INTERMEDIATE';
  });
  assert.throws(()=>audit(bundle),/Discontinuous dependency chain/);
});

test('synchronized source and shard cannot insert unvalidated edge fields',()=>{
  const bundle=clean();
  mutateSynchronizedLineage(bundle,path=>{
    path.edges[0].terminal_latitude=-11.85;
  });
  assert.throws(()=>audit(bundle),/Unvalidated dependency edge fields/);
});

test('status reinterpretation fails even with recomputed shard SHA',()=>{
  const bundle=clean();
  mutateRow(bundle,row=>{row.source_status='PHYSICAL_IMPACT_CONFIRMED';});
  assert.throws(()=>audit(bundle),/Citation data changed/);
});

test('a disappeared no-JS occurrence page fails',()=>{
  const bundle=clean();
  bundle.pages.delete('c01-1/index.md');
  assert.throws(()=>audit(bundle),/SSG route missing/);
});

test('a missing family reverse link fails without changing JSON',()=>{
  const bundle=clean();
  const name='c01-1/index.md';
  bundle.pages.set(name,bundle.pages.get(name).replaceAll('/conde-incident/evidencias/arquivo/familias/radio-tupi-fbis/', '/absent/'));
  assert.throws(()=>audit(bundle),/SSG reverse link missing/);
});

test('actual generated HTML must exist: feed and Markdown alone are insufficient',()=>{
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-bridge-'));
  try {
    mkdirSync(join(directory,'evidencias/arquivo'),{recursive:true});
    writeFileSync(join(directory,'evidencias/arquivo/index.html'),'');
    assert.throws(()=>auditBuiltSite(readBundle(),directory),/SSG HTML missing/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

// G44 adversarial fixture: fake HTML contains the expected route text and
// digests, but not a single navigable anchor. A rendered-site audit must
// reject it even when the source Markdown, JSON and all paths are valid.
test('built HTML index must expose navigable href anchors, not inert path text',()=>{
  const bundle=clean();
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-inert-'));
  try {
    const shards=bundle.shards.flatMap(part=>JSON.parse(part.raw).records);
    const digests=shards.map(row=>row.row_sha256).join(' ');
    for (const [name] of bundle.pages) {
      const dest=join(directory,'evidencias/arquivo',name.replace(/index\.md$/,'index.html'));
      mkdirSync(dirname(dest),{recursive:true});
      writeFileSync(dest,`<!doctype html><html><body><p>${digests}</p></body></html>`);
    }
    // The index prints every route string, but gives readers zero links.
    writeFileSync(join(directory,'evidencias/arquivo/index.html'),
      `<!doctype html><p>${shards.map(row=>row.archive_path).join(' ')}</p>`);
    assert.throws(()=>auditBuiltSite(bundle,directory),/Built index missing navigable anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

test('built occurrence pages must expose live family, source and work reverse links',()=>{
  const bundle=clean();
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-reverse-'));
  try {
    mockBuiltSite(bundle,directory);
    const row=bundle.shards.flatMap(part=>JSON.parse(part.raw).records)[0];
    const page=join(directory,'evidencias/arquivo/c01-1/index.html');
    const html=readFileSync(page,'utf8');
    const target='/conde-incident/evidencias/arquivo/familias/'+
      row.source_family.toLowerCase().replaceAll('_','-')+'/';
    assert.ok(html.includes('href="'+target+'"'));
    writeFileSync(page,html.replaceAll('href="'+target+'"',
      'data-inert-family="'+target+'"'));
    assert.throws(()=>auditBuiltSite(bundle,directory),
      /Built occurrence missing reverse anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

// Synthetic HTML projection of generator Markdown. This tests the verifier,
// not SSG itself (which is exercised by the Pages build on the exact SHA).
function mockBuiltSite(bundle,directory) {
  for (const [name,markdown] of bundle.pages) {
    const dest=join(directory,'evidencias/arquivo',name.replace(/index\.md$/,'index.html'));
    mkdirSync(dirname(dest),{recursive:true});
    const html=markdown.replace(/\[([^\]]+)\]\(([^)]+)\)/g,(_match,label,url)=>
      '<a href="'+url.replaceAll('&','&amp;')+'">'+label+'</a>');
    writeFileSync(dest,'<!doctype html><html><body><main>'+html+'</main></body></html>');
  }
}

test('synthetic complete navigation passes the verifier before live SSG CI',()=>{
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-complete-'));
  try {
    const bundle=clean();
    mockBuiltSite(bundle,directory);
    assert.equal(auditBuiltSite(bundle,directory).references,bundle.citations.records.length);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

test('printed source URL is not a valid outbound documentary link',()=>{
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-source-'));
  try {
    const bundle=clean();
    mockBuiltSite(bundle,directory);
    const row=bundle.citations.records[0];
    const page=join(directory,'evidencias/arquivo/c01-1/index.html');
    const html=readFileSync(page,'utf8');
    assert.ok(html.includes('href="'+row.citation_url+'"'));
    writeFileSync(page,html.replace('href="'+row.citation_url+'"',
      'data-inert-source="'+row.citation_url+'"'));
    assert.throws(()=>auditBuiltSite(bundle,directory),
      /Built occurrence missing source\/matrix\/index anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

test('status code must be rendered in evidence, not just stored in JSON',()=>{
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-status-'));
  try {
    const bundle=clean();
    mockBuiltSite(bundle,directory);
    const row=bundle.citations.records[0];
    const page=join(directory,'evidencias/arquivo/c01-1/index.html');
    writeFileSync(page,readFileSync(page,'utf8').replaceAll(row.source_status,'STATUS_HIDDEN'));
    assert.throws(()=>auditBuiltSite(bundle,directory),
      /Built HTML missing canonical epistemic status/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

test('reverse source index must link back to the cited occurrence',()=>{
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-backlink-'));
  try {
    const bundle=clean();
    mockBuiltSite(bundle,directory);
    const row=bundle.shards.flatMap(part=>JSON.parse(part.raw).records)[0];
    const page=join(directory,'evidencias/arquivo/fontes',
      row.source_id.toLowerCase().replaceAll('_','-'),'index.html');
    const html=readFileSync(page,'utf8');
    assert.ok(html.includes('href="'+row.archive_path+'"'));
    writeFileSync(page,html.replaceAll('href="'+row.archive_path+'"',
      'data-inert-route="'+row.archive_path+'"'));
    assert.throws(()=>auditBuiltSite(bundle,directory),
      /Built reverse page missing occurrence anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

test('immutable matrix row must be a link, not printed text',()=>{
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-matrix-'));
  try {
    const bundle=clean();
    mockBuiltSite(bundle,directory);
    const page=join(directory,'evidencias/arquivo/c01-1/index.html');
    const html=readFileSync(page,'utf8');
    const matrix='https://github.com/franklinbaldo/conde-incident/blob/';
    assert.ok(html.includes('href="'+matrix));
    writeFileSync(page,html.replaceAll('href="'+matrix,'data-inert-matrix="'+matrix));
    assert.throws(()=>auditBuiltSite(bundle,directory),
      /Built occurrence missing source\/matrix\/index anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

// A green CI must mean a reader can reach the actual source, not that a
// string containing href survived in an inert or hidden fragment.
test('static HTML navigation excludes inert, hidden and non-content anchors',()=>{
  const target='/conde-incident/evidencias/arquivo/c01-1/';
  const deceptive=[
    `<script>"<a href="${target}">source</a>"</script>`,
    `<style>/* <a href="${target}">source</a> */</style>`,
    `<template><a href="${target}">source</a></template>`,
    `<noscript><a href="${target}">source</a></noscript>`,
    `<div hidden><a href="${target}">source</a></div>`,
    `<div inert><a href="${target}">source</a></div>`,
    `<div aria-hidden="true"><a href="${target}">source</a></div>`,
    `<div style="display:none"><a href="${target}">source</a></div>`,
    `<div style="visibility:hidden"><a href="${target}">source</a></div>`,
    `<a tabindex="-1" href="${target}">source</a>`,
    `<a aria-disabled="true" href="${target}">source</a>`,
  ];
  for (const fragment of deceptive) {
    const {links}=visibleDocument(`<main>${fragment}</main>`);
    assert.ok(!links.has(target),'Inert anchor was counted: '+fragment);
  }
  assert.ok(!visibleDocument(`<nav><a href="${target}">source</a></nav>`).links.has(target),
    'Link outside main must not satisfy documentary evidence navigation');
  assert.ok(visibleDocument(`<main><a title="a > b" href="${target}">source</a></main>`)
    .links.has(target),'Quoted > must not terminate a real anchor');
});

test('hidden and metadata-only epistemic states do not count as rendered text',()=>{
  const code='DOC_STATUS_TEST';
  for (const fragment of [
    `<script>"${code}"</script>`, `<template>${code}</template>`,
    `<p hidden>${code}</p>`, `<p aria-hidden="true">${code}</p>`,
    `<p style="display:none">${code}</p>`,
    `<meta name="status" content="${code}">`,
  ]) {
    assert.ok(!visibleDocument(`<main>${fragment}</main>`).visibleText.includes(code),
      'Inert status counted: '+fragment);
  }
  assert.ok(visibleDocument(`<main><code>${code}</code></main>`).visibleText.includes(code));
});

test('built archive rejects a source URL hidden in script after its live link disappears',()=>{
  const bundle=clean();
  const directory=mkdtempSync(join(tmpdir(),'conde-ssg-script-decoy-'));
  try {
    mockBuiltSite(bundle,directory);
    const row=bundle.citations.records[0];
    const page=join(directory,'evidencias/arquivo/c01-1/index.html');
    const html=readFileSync(page,'utf8').replace('href="'+row.citation_url+'"',
      'data-inert-source="'+row.citation_url+'"');
    writeFileSync(page,html.replace('</main>',
      `<script>"<a href="${row.citation_url}">not a link</a>"</script></main>`));
    assert.throws(()=>auditBuiltSite(bundle,directory),
      /Built occurrence missing source\/matrix\/index anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

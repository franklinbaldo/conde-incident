/** Verify the exact JSON-to-SSG documentary route contract; no physical inference. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {existsSync, readFileSync, readdirSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {archivePages} from './ssg-documentary-archive.mjs';

const PREFIX='/conde-incident/evidencias/arquivo/';
const DATA='public/data/';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const slug=value=>value.toLowerCase().replaceAll('_','-');
const link=(kind,id)=>PREFIX+kind+'/'+slug(id)+'/';
const idPath=id=>PREFIX+id.toLowerCase().replace('#','-')+'/';
const key=row=>JSON.stringify([row.snapshot_ref,row.source_id]);
const tracked=['occurrence','snapshot_ref','source_id','source_family','work_id',
  'source_status','relation','scope','locator','claim_text','citation_url',
  'row_sha256','matrix_line'];
const take=(row,fields)=>Object.fromEntries(fields.map(name=>[name,row[name]]));
// Inspect actual anchor attributes in the generated HTML, not inert text in
// paragraphs, metadata, comments or pre-rendered Markdown source.
const anchors=html=>new Set([...html.replace(/<!--[\s\S]*?-->/g,'')
  .matchAll(/<a\b[^>]*\bhref\s*=\s*(['"])([^'"]+)\1/gi)]
  .map(match=>match[2].replaceAll('&amp;','&')));

export function readBundle(root='.') {
  const read=path=>readFileSync(join(root,path));
  const citationsRaw=read(DATA+'conde-source-citations.json');
  const lineageRaw=read(DATA+'conde-declared-dependence.json');
  const citations=JSON.parse(citationsRaw);
  const lineage=JSON.parse(lineageRaw);
  const manifest=JSON.parse(read(DATA+'conde-evidence-index-manifest.json'));
  const shards=manifest.shards.map(meta=>({path:meta.path, raw:read(meta.path)}));
  return {citations,lineage,manifest,shards,sourceBytes:new Map([
    [DATA+'conde-source-citations.json',citationsRaw],
    [DATA+'conde-declared-dependence.json',lineageRaw],
  ]),pages:archivePages(citations,lineage)};
}

export function audit(bundle) {
  const {citations,lineage,manifest,shards,sourceBytes,pages}=bundle;
  assert.equal(manifest.schema,'conde.evidence-index/v1');
  assert.equal(manifest.matrix_git_blob_sha1,citations.matrix_git_blob_sha1);
  assert.equal(lineage.matrix_git_blob_sha1,citations.matrix_git_blob_sha1);
  assert.equal(manifest.no_js_index,PREFIX);
  assert.equal(manifest.independent_physical_observation_count,null);
  assert.equal(manifest.absence_of_declared_dependency_proves_independence,false);
  assert.equal(manifest.curated_occurrences,citations.curated_occurrences);
  assert.equal(manifest.curated_reference_count,citations.records.length);
  assert.equal(manifest.unmapped_matrix_occurrences,citations.unmapped_occurrences);
  assert.equal(manifest.total_matrix_occurrences,citations.total_matrix_occurrences);
  assert.deepEqual(manifest.post_matrix_ids_not_in_curated_index,
    citations.post_matrix_occurrences.map(item=>item.id));
  const sourcePaths=[DATA+'conde-source-citations.json',DATA+'conde-declared-dependence.json'];
  assert.deepEqual(manifest.source_files.map(file=>file.path),sourcePaths);
  for (const file of manifest.source_files)
    assert.equal(file.sha256,hash(sourceBytes.get(file.path)), 'Source SHA mismatch: '+file.path);
  assert.equal(shards.length,manifest.shards.length);
  const actual=new Map();
  for (const [i,meta] of manifest.shards.entries()) {
    assert.equal(meta.path,`public/data/conde-evidence-index/part-${String(i+1).padStart(3,'0')}.json`,
      'Unexpected shard path/order');
    const part=shards[i];
    assert.equal(part.path,meta.path);
    assert.equal(meta.sha256,hash(part.raw),'Shard SHA mismatch: '+meta.path);
    assert.equal(meta.bytes,part.raw.length,'Shard size mismatch: '+meta.path);
    assert.ok(meta.bytes<=12_000,'Shard exceeds 12kB');
    const parsed=JSON.parse(part.raw);
    assert.equal(parsed.schema,'conde.evidence-index-shard/v1');
    assert.equal(parsed.records.length,meta.record_count);
    for (const row of parsed.records) {
      assert.ok(!actual.has(key(row)),'Duplicate JSON key: '+key(row));
      actual.set(key(row),row);
    }
  }
  assert.equal(actual.size,citations.records.length,'Missing or surplus indexed references');
  const lineageByKey=new Map(lineage.citation_lineages.map(item=>[key(item),item]));
  assert.equal(lineageByKey.size,lineage.citation_lineages.length,'Duplicate lineage entries');
  const occurrences=new Set();
  const families=new Set(),works=new Set(),sources=new Set();
  const archiveIndex=pages.get('index.md');
  assert.ok(archiveIndex?.includes(PREFIX+'familias/'),'No-JS root absent');
  for (const record of citations.records) {
    const row=actual.get(key(record));
    assert.ok(row,'Citation missing from JSON: '+key(record));
    assert.deepEqual(take(row,tracked),take(record,tracked),'Citation data changed: '+key(record));
    assert.equal(row.archive_path,idPath(record.occurrence),'Broken archive route: '+key(record));
    assert.equal(row.not_a_verified_conde_physical_event,true);
    assert.equal(row.independent_physical_observation_count,null);
    assert.deepEqual(row.declared_upstream_paths,
      lineageByKey.get(key(record))?.declared_upstream_paths,'Lineage changed: '+key(record));
    occurrences.add(record.occurrence);
    families.add(record.source_family);
    works.add(record.work_id);
    sources.add(record.source_id);
    const route=row.archive_path.slice(PREFIX.length)+'index.md';
    const rendered=pages.get(route);
    assert.ok(rendered,'SSG route missing: '+row.archive_path);
    assert.ok(archiveIndex.includes(row.archive_path),'No-JS index missing: '+row.archive_path);
    assert.ok(rendered.includes(row.row_sha256),'SSG row checksum missing: '+row.archive_path);
    for (const target of [link('familias',row.source_family),
      link('obras',row.work_id),link('fontes',row.source_id)]) {
      assert.ok(rendered.includes(target),'SSG reverse link missing: '+target);
      assert.ok(pages.has(target.slice(PREFIX.length)+'index.md'),'SSG reverse route missing: '+target);
    }
  }
  assert.equal(occurrences.size,manifest.curated_occurrences);
  assert.equal(pages.size,occurrences.size+4+families.size+works.size+sources.size,
    'SSG page inventory no longer matches JSON IDs');
  for (const id of occurrences)
    assert.ok(pages.has(idPath(id).slice(PREFIX.length)+'index.md'));
  return {references:actual.size,occurrences:occurrences.size,ssgPages:pages.size,shards:shards.length};
}

// Check the real build output, not merely expected Markdown pages. Called after SSG build.
export function auditBuiltSite(bundle,siteRoot='public') {
  const counts=audit(bundle);
  for (const [name] of bundle.pages) {
    const path=join(siteRoot,'evidencias/arquivo',name.replace(/index\.md$/,'index.html'));
    assert.ok(existsSync(path),'SSG HTML missing: '+path);
  }
  const allRows=bundle.shards.flatMap(part=>JSON.parse(part.raw).records);
  const index=readFileSync(join(siteRoot,'evidencias/arquivo/index.html'),'utf8');
  const indexAnchors=anchors(index);
  for (const row of allRows) {
    assert.ok(indexAnchors.has(row.archive_path),
      'Built index missing navigable anchor: '+row.archive_path);
    const page=join(siteRoot,row.archive_path.slice(PREFIX.length)
      ? 'evidencias/arquivo/'+row.archive_path.slice(PREFIX.length)+'index.html'
      : 'evidencias/arquivo/index.html');
    const html=readFileSync(page,'utf8');
    assert.ok(html.includes(row.row_sha256),'Built HTML missing row digest: '+row.archive_path);
    const reverseAnchors=anchors(html);
    for (const target of [link('familias',row.source_family),
      link('obras',row.work_id),link('fontes',row.source_id)])
      assert.ok(reverseAnchors.has(target),
        'Built occurrence missing reverse anchor: '+row.archive_path+' -> '+target);
  }
  return counts;
}

if (process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  const root=resolve(import.meta.dirname,'..');
  const bundle=readBundle(root);
  // Do not run a stale-shard audit if the directory holds extra unmapped parts.
  const actual=readdirSync(join(root,'public/data/conde-evidence-index'))
    .filter(name=>/^part-.*\.json$/.test(name)).sort();
  assert.deepEqual(actual,bundle.manifest.shards.map(m=>m.path.split('/').at(-1)));
  const result=process.argv.includes('--built-site')
    ? auditBuiltSite(bundle,join(root,'public')):audit(bundle);
  console.log('SSG ↔ JSON:',JSON.stringify(result));
}

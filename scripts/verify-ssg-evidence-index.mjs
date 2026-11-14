/** Verify the exact JSON-to-SSG documentary route contract; no physical inference. */
import assert from 'node:assert/strict';
import {tracked,exactKeys,manifestKeys,curatedKeys,shardMetaKeys,gapKeys}
  from './ssg-evidence-index-schema.mjs';
import {createHash} from 'node:crypto';
import {existsSync, readFileSync, readdirSync} from 'node:fs';
import {join, resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {archivePages,matrixRowUrl} from './ssg-documentary-archive.mjs';
import {auditLookup} from './verify-ssg-evidence-lookup.mjs';

const PREFIX='/conde-incident/evidencias/arquivo/';
const DATA='public/data/';
const MATRIX='research/evidence_matrix_C001-C238_2026-11-11.md';
const hash=bytes=>createHash('sha256').update(bytes).digest('hex');
const gitBlob=bytes=>createHash('sha1')
  .update(Buffer.from('blob '+bytes.length+'\0')).update(bytes).digest('hex');
const slug=value=>value.toLowerCase().replaceAll('_','-');
const link=(kind,id)=>PREFIX+kind+'/'+slug(id)+'/';
const idPath=id=>PREFIX+id.toLowerCase().replace('#','-')+'/';
const key=row=>JSON.stringify([row.snapshot_ref,row.source_id]);
const take=(row,fields)=>Object.fromEntries(fields.map(name=>[name,row[name]]));
// Revalidate the dependency paths in the independent JS publication gate.
// Comparing shard equality alone accepts two consistently forged feeds.
function validateDeclaredPaths(sourceId, paths) {
  assert.ok(Array.isArray(paths), 'Declared upstream paths are not an array');
  for (const path of paths) {
    assert.ok(path && typeof path==='object' && !Array.isArray(path),
      'Invalid declared upstream path');
    assert.deepEqual(Object.keys(path).sort(),['edges','upstream_source_id'],
      'Unvalidated dependency path fields');
    assert.ok(Array.isArray(path.edges) && path.edges.length>0,
      'Empty declared dependency path');
    let cursor=sourceId;
    const seen=new Set([cursor]);
    for (const edge of path.edges) {
      assert.ok(edge && typeof edge==='object' && !Array.isArray(edge),
        'Invalid dependency edge');
      assert.deepEqual(Object.keys(edge).sort(),['from','kind','to'],
        'Unvalidated dependency edge fields');
      assert.equal(edge.from,cursor,'Discontinuous dependency chain');
      assert.ok(typeof edge.to==='string' && edge.to.trim(),
        'Missing dependency target');
      assert.ok(typeof edge.kind==='string' && edge.kind.trim(),
        'Missing dependency kind');
      assert.ok(!seen.has(edge.to),'Cyclic dependency chain');
      seen.add(edge.to);
      cursor=edge.to;
    }
    assert.equal(path.upstream_source_id,cursor,'Dependency terminal ID mismatch');
  }
}
// Audit the content readers can actually navigate, not strings in scripts,
// comments, templates, metadata or a hidden clone of the link inventory.
// This intentionally checks only the static DOM contract; an external CSS rule
// or a runtime JS mutation still requires the browser/UX audit.
const voidTags=new Set(['area','base','br','col','embed','hr','img','input','link',
  'meta','param','source','track','wbr']);
const rawTags=new Set(['script','style','template','noscript','svg']);
const attribute=(source,name)=>{
  const match=new RegExp('(?:^|\\s)'+name+
    '(?:\\s*=\\s*(?:"([^"]*)"|\'([^\']*)\'|([^\\s>]+)))?(?=\\s|$)','i').exec(source);
  return match ? (match[1] ?? match[2] ?? match[3] ?? '') : null;
};
const suppressed=(tag,attrs)=>rawTags.has(tag) ||
  ['hidden','inert'].some(name=>attribute(attrs,name)!==null) ||
  attribute(attrs,'aria-hidden')?.toLowerCase()==='true' ||
  attribute(attrs,'aria-disabled')?.toLowerCase()==='true' ||
  /(?:^|;)\s*(?:display\s*:\s*none|visibility\s*:\s*hidden)(?:\s*[;!]|$)/i
    .test(attribute(attrs,'style') ?? '');

export function visibleDocument(html) {
  const links=new Set(),content=[],activeAnchors=new Map(),idCounts=new Map();
  const stack=[];
  let last=0;
  // Quote-aware tags: a '>' inside an attribute must not terminate a tag.
  const tokens=/<!--[\s\S]*?-->|<(?:[^>"']|"[^"]*"|'[^']*')*>/g;
  for (const match of html.matchAll(tokens)) {
    const parent=stack.at(-1);
    if (parent?.main && !parent.hidden && match.index>last)
      content.push(html.slice(last,match.index));
    last=match.index+match[0].length;
    const token=match[0];
    if (token.startsWith('<!--') || /^<!/.test(token)) continue;
    const closing=/^<\s*\/\s*([\w:-]+)/.exec(token);
    if (closing) {
      const i=stack.findLastIndex(item=>item.tag===closing[1].toLowerCase());
      if (i!==-1) stack.length=i;
      continue;
    }
    const opening=/^<\s*([\w:-]+)\b/.exec(token);
    if (!opening) continue;
    const tag=opening[1].toLowerCase();
    const attrs=token.slice(opening[0].length,-1);
    const hidden=Boolean(parent?.hidden || suppressed(tag,attrs));
    const main=Boolean(parent?.main || tag==='main');
    // Fragment resolution uses the first DOM ID, including hidden elements.
    // Count IDs across the document; require exactly one active target inside main.
    const id=attribute(attrs,'id');
    if(id) idCounts.set(id,(idCounts.get(id)??0)+1);
    if(tag==='span' && main && !hidden && attribute(attrs,'tabindex')==='-1' && id)
      activeAnchors.set(id,(activeAnchors.get(id)??0)+1);
    if (tag==='a' && main && !hidden && attribute(attrs,'tabindex')!=='-1') {
      const href=attribute(attrs,'href');
      if (href) links.add(href.replaceAll('&amp;','&'));
    }
    if (!voidTags.has(tag) && !/\/\s*>$/.test(token)) stack.push({tag,hidden,main});
  }
  return {links,visibleText:content.join(' '),activeAnchors,idCounts};
}

export function readBundle(root='.') {
  const read=path=>readFileSync(join(root,path));
  const matrixBytes=read(MATRIX);
  const citationsRaw=read(DATA+'conde-source-citations.json');
  const lineageRaw=read(DATA+'conde-declared-dependence.json');
  const citations=JSON.parse(citationsRaw);
  const lineage=JSON.parse(lineageRaw);
  const manifest=JSON.parse(read(DATA+'conde-evidence-index-manifest.json'));
  const shards=manifest.shards.map(meta=>({path:meta.path, raw:read(meta.path)}));
  const gapShards=manifest.unmapped_shards.map(meta=>({path:meta.path, raw:read(meta.path)}));
  const lookupShards=manifest.lookup_shards.map(meta=>({path:meta.path, raw:read(meta.path)}));
  return {citations,lineage,manifest,shards,gapShards,lookupShards,matrixBytes,sourceBytes:new Map([
    [DATA+'conde-source-citations.json',citationsRaw],
    [DATA+'conde-declared-dependence.json',lineageRaw],
  ]),pages:archivePages(citations,lineage)};
}

export function audit(bundle) {
  const {citations,lineage,manifest,shards,gapShards,lookupShards,matrixBytes,sourceBytes,pages}=bundle;
  exactKeys(manifest,manifestKeys,'manifest');
  assert.equal(manifest.schema,'conde.evidence-index/v1');
  assert.equal(manifest.matrix_git_blob_sha1,citations.matrix_git_blob_sha1);
  assert.equal(gitBlob(matrixBytes),manifest.matrix_git_blob_sha1,
    'Frozen matrix Git blob mismatch');
  exactKeys(manifest.matrix_source,['path','bytes','sha256'],'matrix_source');
  assert.deepEqual(manifest.matrix_source,{
    path:MATRIX,bytes:matrixBytes.length,sha256:hash(matrixBytes),
  },'Frozen matrix SHA-256/size/path mismatch');
  const matrixLines=matrixBytes.toString('utf8').split('\n');
  const matrixInventory=new Map(),labelCounts=new Map();
  for (const [index,line] of matrixLines.entries()) {
    const label=/^\|\s*\*{0,2}(C[0-9]+)\*{0,2}\s*\|/.exec(line)?.[1];
    if (!label) continue;
    const number=(labelCounts.get(label)??0)+1;
    labelCounts.set(label,number);
    matrixInventory.set(label+'#'+number,index+1);
  }
  assert.equal(matrixInventory.size,citations.total_matrix_occurrences,
    'Matrix row inventory differs from declared coverage');
  const curatedIds=new Set(citations.records.map(row=>row.occurrence));
  const gaps=[...matrixInventory].filter(([id])=>!curatedIds.has(id))
    .map(([occurrence,matrix_line])=>({occurrence,matrix_line}));
  assert.equal(gaps.length,citations.unmapped_occurrences,
    'Matrix gap count does not match curated coverage');
  assert.deepEqual(manifest.unmapped_matrix_refs,gaps,
    'Unmapped matrix ledger differs from frozen source rows');
  // Independently reconstruct the searchable *uncurated* texts from the blob.
  // Two consistent counterfeit JSONs with recalculated SHA must still fail.
  const expectedGaps=gaps.map(({occurrence,matrix_line})=>{
    const line=matrixLines[matrix_line-1];
    return {occurrence,matrix_line,row_sha256:hash(Buffer.from(line)),
      claim_text:line.split('|')[2].trim()};
  });
  assert.equal(gapShards.length,manifest.unmapped_shards.length);
  const publishedGaps=[];
  for (const [i,meta] of manifest.unmapped_shards.entries()) {
    exactKeys(meta,shardMetaKeys,'gap shard metadata');
    const expectedPath=`public/data/conde-evidence-gaps/part-${String(i+1).padStart(3,'0')}.json`;
    assert.equal(meta.path,expectedPath,'Unexpected gap shard path/order');
    const part=gapShards[i];
    assert.equal(part.path,meta.path);
    assert.equal(meta.sha256,hash(part.raw),'Gap shard SHA mismatch: '+meta.path);
    assert.equal(meta.bytes,part.raw.length,'Gap shard size mismatch: '+meta.path);
    assert.ok(meta.bytes<=12_000,'Gap shard exceeds 12kB');
    const parsed=JSON.parse(part.raw);
    assert.equal(parsed.schema,'conde.evidence-gap-shard/v1');
    assert.deepEqual(Object.keys(parsed).sort(),['records','schema']);
    assert.equal(parsed.records.length,meta.record_count);
    for (const row of parsed.records) exactKeys(row,gapKeys,'gap record');
    publishedGaps.push(...parsed.records);
  }
  assert.deepEqual(publishedGaps,expectedGaps,
    'Uncurated claim text/hash differs from frozen matrix');
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
  for (const file of manifest.source_files) exactKeys(file,['path','sha256'],'source file metadata');
  for (const file of manifest.source_files)
    assert.equal(file.sha256,hash(sourceBytes.get(file.path)), 'Source SHA mismatch: '+file.path);
  assert.equal(shards.length,manifest.shards.length);
  const actual=new Map();
  for (const [i,meta] of manifest.shards.entries()) {
    exactKeys(meta,shardMetaKeys,'curated shard metadata');
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
      exactKeys(row,curatedKeys,'curated record');
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
  assert.ok(archiveIndex.includes(PREFIX+'estados/'),'No-JS state index absent');
  const stateIndex=pages.get('estados/index.md');
  assert.ok(stateIndex,'Missing SSG state index');
  for (const record of citations.records) {
    const originalLine=matrixLines[record.matrix_line-1];
    assert.equal(matrixInventory.get(record.occurrence),record.matrix_line,
      'Matrix occurrence ordinal/line mismatch: '+record.occurrence);
    assert.ok(originalLine,'Matrix line missing: '+record.occurrence);
    assert.equal(hash(Buffer.from(originalLine)),record.row_sha256,
      'Matrix row SHA-256 mismatch: '+record.occurrence);
    assert.equal(/^\|\s*\*{0,2}(C[0-9]+)\*{0,2}\s*\|/.exec(originalLine)?.[1],
      record.occurrence.split('#')[0],'Matrix row ID mismatch: '+record.occurrence);
    assert.equal(record.claim_text,originalLine.split('|')[2]?.trim(),
      'Matrix claim text mismatch: '+record.occurrence);
    const row=actual.get(key(record));
    assert.ok(row,'Citation missing from JSON: '+key(record));
    assert.deepEqual(take(row,tracked),take(record,tracked),'Citation data changed: '+key(record));
    assert.equal(row.archive_path,idPath(record.occurrence),'Broken archive route: '+key(record));
    assert.equal(row.not_a_verified_conde_physical_event,true);
    assert.equal(row.independent_physical_observation_count,null);
    assert.deepEqual(row.declared_upstream_paths,
      lineageByKey.get(key(record))?.declared_upstream_paths,'Lineage changed: '+key(record));
    validateDeclaredPaths(record.source_id,row.declared_upstream_paths);
    occurrences.add(record.occurrence);
    families.add(record.source_family);
    works.add(record.work_id);
    sources.add(record.source_id);
    const route=row.archive_path.slice(PREFIX.length)+'index.md';
    const rendered=pages.get(route);
    assert.ok(rendered,'SSG route missing: '+row.archive_path);
    assert.ok(archiveIndex.includes(row.archive_path),'No-JS index missing: '+row.archive_path);
    assert.ok(stateIndex.includes(row.archive_path),'State index missing: '+row.archive_path);
    assert.ok(stateIndex.includes(matrixRowUrl(row.matrix_line)),
      'State index missing immutable row: '+row.archive_path);
    assert.ok(rendered.includes(row.row_sha256),'SSG row checksum missing: '+row.archive_path);
    assert.ok(rendered.includes(row.source_status),'SSG canonical status absent: '+row.archive_path);
    for (const target of [link('familias',row.source_family),
      link('obras',row.work_id),link('fontes',row.source_id)]) {
      assert.ok(rendered.includes(target),'SSG reverse link missing: '+target);
      assert.ok(pages.has(target.slice(PREFIX.length)+'index.md'),'SSG reverse route missing: '+target);
    }
  }
  auditLookup(manifest,shards,gapShards,lookupShards,matrixInventory);
  assert.equal(occurrences.size,manifest.curated_occurrences);
  assert.equal(pages.size,occurrences.size+5+families.size+works.size+sources.size,
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
  const indexAnchors=visibleDocument(index).links;
  const stateHtml=readFileSync(join(siteRoot,'evidencias/arquivo/estados/index.html'),'utf8');
  const stateAnchors=visibleDocument(stateHtml).links;
  assert.ok(indexAnchors.has(PREFIX+'estados/'),'Built archive missing state browser link');
  // Cache reverse-link targets; each source/obra/família may cover many records.
  const reverseCache=new Map();
  const reversePage=path=>{
    if (!reverseCache.has(path)) {
      const filename=join(siteRoot,'evidencias/arquivo',path.slice(PREFIX.length),'index.html');
      reverseCache.set(path,visibleDocument(readFileSync(filename,'utf8')).links);
    }
    return reverseCache.get(path);
  };
  for (const row of allRows) {
    assert.ok(indexAnchors.has(row.archive_path),
      'Built index missing navigable anchor: '+row.archive_path);
    assert.ok(stateAnchors.has(row.archive_path),
      'Built state browser missing occurrence: '+row.archive_path);
    assert.ok(stateAnchors.has(matrixRowUrl(row.matrix_line)),
      'Built state browser missing matrix row: '+row.archive_path);
    const page=join(siteRoot,row.archive_path.slice(PREFIX.length)
      ? 'evidencias/arquivo/'+row.archive_path.slice(PREFIX.length)+'index.html'
      : 'evidencias/arquivo/index.html');
    const html=readFileSync(page,'utf8');
    const {links:reverseAnchors,visibleText}=visibleDocument(html);
    assert.ok(visibleText.includes(row.row_sha256),
      'Built HTML missing visible row digest: '+row.archive_path);
    assert.ok(visibleText.includes(row.source_status),
      'Built HTML missing canonical epistemic status: '+row.archive_path);
    // This is a navigable citation, not a PDF URL printed as inert text.
    for (const target of [row.citation_url,matrixRowUrl(row.matrix_line),PREFIX])
      assert.ok(reverseAnchors.has(target),
        'Built occurrence missing source/matrix/index anchor: '+row.archive_path+' -> '+target);
    for (const target of [link('familias',row.source_family),
      link('obras',row.work_id),link('fontes',row.source_id)])
      assert.ok(reverseAnchors.has(target),
        'Built occurrence missing reverse anchor: '+row.archive_path+' -> '+target);
    for (const target of [link('familias',row.source_family),
      link('obras',row.work_id),link('fontes',row.source_id)])
      assert.ok(reversePage(target).has(row.archive_path),
        'Built reverse page missing occurrence anchor: '+target+' -> '+row.archive_path);
  }
  return counts;
}

if (process.argv[1] && import.meta.url===pathToFileURL(resolve(process.argv[1])).href) {
  const root=resolve(import.meta.dirname,'..');
  const bundle=readBundle(root);
  // Do not run a stale-shard audit if the directory holds extra unmapped parts.
  for (const [folder,refs] of [
    ['conde-evidence-index',bundle.manifest.shards],
    ['conde-evidence-gaps',bundle.manifest.unmapped_shards],
    ['conde-evidence-lookup',bundle.manifest.lookup_shards],
  ]) {
    const actual=readdirSync(join(root,'public/data',folder))
      .filter(name=>/^part-.*\.json$/.test(name)).sort();
    assert.deepEqual(actual,refs.map(m=>m.path.split('/').at(-1)),
      'Orphan/missing '+folder+' shard');
  }
  const result=process.argv.includes('--built-site')
    ? auditBuiltSite(bundle,join(root,'public')):audit(bundle);
  console.log('SSG ↔ JSON:',JSON.stringify(result));
}

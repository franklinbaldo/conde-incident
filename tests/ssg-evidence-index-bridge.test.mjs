/** Regression tests: static SSG routes and immutable documentary JSON stay joined. */
import test from 'node:test';
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdtempSync,mkdirSync,rmSync,writeFileSync} from 'node:fs';
import {tmpdir} from 'node:os';
import {dirname,join} from 'node:path';
import {audit,auditBuiltSite,readBundle} from '../scripts/verify-ssg-evidence-index.mjs';

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
    const rows=bundle.shards.flatMap(part=>JSON.parse(part.raw).records);
    const digests=rows.map(row=>row.row_sha256).join(' ');
    for (const [name] of bundle.pages) {
      const dest=join(directory,'evidencias/arquivo',name.replace(/index\.md$/,'index.html'));
      mkdirSync(dirname(dest),{recursive:true});
      writeFileSync(dest,`<!doctype html><html><body><p>${digests}</p></body></html>`);
    }
    // Index is truly clickable; occurrence pages are not.
    writeFileSync(join(directory,'evidencias/arquivo/index.html'),
      `<!doctype html><main>${[...new Set(rows.map(row=>row.archive_path))]
        .map(path=>`<a href="${path}">go</a>`).join('')}</main>`);
    assert.throws(()=>auditBuiltSite(bundle,directory),/Built occurrence missing reverse anchor/);
  } finally {rmSync(directory,{recursive:true,force:true});}
});

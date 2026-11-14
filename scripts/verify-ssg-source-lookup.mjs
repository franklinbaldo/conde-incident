/** Independent byte-level and semantic audit of the derived source lookup. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {join} from 'node:path';
import {pathToFileURL} from 'node:url';

const sha=raw=>createHash('sha256').update(raw).digest('hex');
const C='public/data/conde-source-citations.json';
const L='public/data/conde-declared-dependence.json';
const E='public/data/conde-evidence-index-manifest.json';
const M='research/evidence_matrix_C001-C238_2026-11-11.md';
const P='public/data/conde-source-lookup-manifest.json';
const sortTuple=(a,b)=>a.join('\0')<b.join('\0')?-1:a.join('\0')>b.join('\0')?1:0;
const requireKeys=(obj,keys)=>assert.deepEqual(Object.keys(obj).sort(),keys.sort());
const sourceKey=x=>JSON.stringify([x.snapshot_ref,x.source_id]);

export function auditSourceLookup(root='.',overrides=new Map()) {
  const read=name=>overrides.get(name)??readFileSync(join(root,name));
  const inputs=new Map([C,L,E,M].map(name=>[name,read(name)]));
  const citations=JSON.parse(inputs.get(C));
  const lineage=JSON.parse(inputs.get(L));
  const evidence=JSON.parse(inputs.get(E));
  const matrix=inputs.get(M).toString('utf8').split(/\r?\n/);
  const pointer=JSON.parse(read(P));
  requireKeys(pointer,['schema','source_index','inputs_sha256']);
  assert.equal(pointer.schema,'conde.source-reverse-lookup-manifest/v1');
  assert.deepEqual(pointer.inputs_sha256,Object.fromEntries(
    [...inputs].map(([p,raw])=>[p,sha(raw)])));
  requireKeys(pointer.source_index,['path','bytes','sha256']);
  const {path,bytes,sha256}=pointer.source_index;
  assert.equal(path,'public/data/conde-source-lookup/part-'+sha256+'.json');
  assert.match(sha256,/^[a-f0-9]{64}$/);
  const published=read(path);
  assert.equal(published.length,bytes,'Index size mismatch');
  assert.equal(sha(published),sha256,'Index digest mismatch');
  const actual=JSON.parse(published);
  requireKeys(actual,[
    'schema','description','matrix_git_blob_sha1','source_files_sha256',
    'independent_physical_observation_count',
    'absence_of_declared_edge_proves_independence',
    'curated_reference_count','curated_occurrence_count','unmapped_occurrence_count',
    'sources','families','post_matrix_only',
  ]);
  const files={'public/data/conde-source-citations.json':sha(inputs.get(C)),
    'public/data/conde-declared-dependence.json':sha(inputs.get(L))};
  assert.deepEqual(evidence.source_files.map(x=>[x.path,x.sha256]).sort(),
    Object.entries(files).sort());
  assert.equal(evidence.matrix_source.sha256,sha(inputs.get(M)));
  assert.equal(citations.matrix_git_blob_sha1,lineage.matrix_git_blob_sha1);
  const referenceKeys=new Set(citations.records.map(sourceKey));
  const lineages=new Map(lineage.citation_lineages.map(x=>[sourceKey(x),x]));
  assert.equal(lineages.size,lineage.citation_lineages.length);
  assert.deepEqual([...lineages.keys()].sort(),[...referenceKeys].sort());
  const grouped=new Map();
  for(const row of citations.records){
    const dep=lineages.get(sourceKey(row));
    assert.equal(dep.family_id,row.source_family);
    assert.equal(dep.row_sha256,row.row_sha256);
    assert.equal(dep.matrix_line,row.matrix_line);
    assert.equal(sha(Buffer.from(matrix[row.matrix_line-1])),row.row_sha256);
    assert.equal(dep.independent_physical_observation_count,null);
    assert.equal(row.not_a_verified_conde_physical_event,true);
    const edges=dep.declared_upstream_paths.flatMap(p=>p.edges.map(edge=>{
      assert.equal(edge.from,row.source_id);
      assert.ok(edge.to&&edge.kind);
      return [edge.from,edge.kind,edge.to];
    }));
    const upstream_edges=[...new Map(edges.map(x=>[JSON.stringify(x),x])).values()]
      .sort(sortTuple);
    const ref={
      occurrence:row.occurrence,snapshot_ref:row.snapshot_ref,
      matrix_line:row.matrix_line,row_sha256:row.row_sha256,work_id:row.work_id,
      archive_path:'/conde-incident/evidencias/arquivo/'+
        row.occurrence.toLowerCase().replace('#','-')+'/',
      upstream_edges,
    };
    const group=grouped.get(row.source_id)??[];
    group.push({family:row.source_family,reference:ref});
    grouped.set(row.source_id,group);
  }
  const families=new Map();
  const sources=[...grouped].sort(([a],[b])=>a<b?-1:a>b?1:0)
    .map(([source_id,rows])=>{
      assert.equal(new Set(rows.map(x=>x.family)).size,1);
      const source_family=rows[0].family;
      families.set(source_family,[...(families.get(source_family)??[]),source_id]);
      return {source_id,source_family,references:rows.map(x=>x.reference)
        .sort((a,b)=>a.matrix_line-b.matrix_line||
             (a.work_id<b.work_id?-1:a.work_id>b.work_id?1:0))};
    });
  const familyList=[...families].sort(([a],[b])=>a<b?-1:a>b?1:0)
    .map(([family_id,source_ids])=>({family_id,source_ids}));
  const postById=new Map(lineage.post_matrix_lineages.map(x=>[x.id,x]));
  assert.equal(postById.size,lineage.post_matrix_lineages.length);
  assert.deepEqual([...postById.keys()].sort(),
    citations.post_matrix_occurrences.map(x=>x.id).sort());
  const post_matrix_only=[...citations.post_matrix_occurrences].sort((a,b)=>
    a.id<b.id?-1:a.id>b.id?1:0).map(x=>{
      const dep=postById.get(x.id);
      assert.equal(dep.source_id,x.source_id);
      assert.equal(dep.independent_physical_observation_count,null);
      assert.equal(x.physical_constraint,null);
      const edges=dep.declared_upstream_paths.flatMap(p=>p.edges.map(e=>{
        assert.equal(e.from,x.source_id);
        return [e.from,e.kind,e.to];
      }));
      const upstream_edges=[...new Map(edges.map(z=>[JSON.stringify(z),z])).values()]
        .sort(sortTuple);
      return {id:x.id,source_id:x.source_id,source_family:dep.source_family,
        source_status:x.status,upstream_edges,matrix_line:null,
        independent_physical_observation_count:null};
    });
  const expected={
    schema:'conde.source-reverse-lookup/v1',
    description:'Índice derivado de citações documentais, não observações físicas',
    matrix_git_blob_sha1:citations.matrix_git_blob_sha1,
    source_files_sha256:files,
    independent_physical_observation_count:null,
    absence_of_declared_edge_proves_independence:false,
    curated_reference_count:citations.records.length,
    curated_occurrence_count:citations.curated_occurrences,
    unmapped_occurrence_count:citations.unmapped_occurrences,
    sources,families:familyList,post_matrix_only,
  };
  assert.deepEqual(actual,expected,'Reverse lookup differs from canonical source graph');
  return {sources:sources.length,families:familyList.length,
    citations:citations.records.length,postMatrix:post_matrix_only.length};
}

if(process.argv[1]&&import.meta.url===pathToFileURL(process.argv[1]).href){
  console.log('PASS source reverse lookup',auditSourceLookup());
}

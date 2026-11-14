/** Reciprocal navigation is a reference to a later document, never a curated observation. */
import assert from 'node:assert/strict';

export const POST_MATRIX_URL='/conde-incident/evidencias/arquivo/pos-matriz/';
export function postMatrixAnchor(id) {
  assert.match(id,/^[A-Z][A-Z0-9_-]{2,99}$/,'Pós-matriz: ID de backlink inválido');
  return 'postmatrix-'+id.toLowerCase();
}

/** Only connect supplemental documents to existing, source-locked matrix IDs. */
export function relatedDocumentBacklinks(citations,occurrences,matrixSha) {
  assert.equal(citations.schema,'conde.source-citations/v1','Pós-matriz: schema divergente');
  assert.equal(citations.matrix_git_blob_sha1,matrixSha,
    'Pós-matriz: snapshot diferente do índice canônico');
  assert.ok(Array.isArray(citations.post_matrix_occurrences));
  const valid=new Set(occurrences);
  assert.equal(valid.size,occurrences.length,'Pós-matriz: IDs de matriz duplicados');
  const seen=new Set();
  const backlinks=new Map();
  for(const item of citations.post_matrix_occurrences) {
    const anchor=postMatrixAnchor(item.id);
    assert.ok(!seen.has(item.id),'Pós-matriz: documento repetido');
    seen.add(item.id);
    assert.equal(item.not_a_verified_conde_physical_event,true,
      'Pós-matriz: backlink não pode verificar evento físico');
    assert.equal(item.physical_constraint,null,
      'Pós-matriz: backlink não pode acrescentar restrição física');
    assert.equal(item.observation_type,'DOCUMENTARY_CITATION_NOT_PHYSICAL_OBSERVATION',
      'Pós-matriz: backlink não é observação independente');
    assert.equal(item.journalistic_source_independence,'UNRESOLVED',
      'Pós-matriz: independência não demonstrada');
    assert.ok(Array.isArray(item.related_matrix_occurrences)&&
      Array.isArray(item.related_matrix_snapshot_refs)&&
      item.related_matrix_occurrences.length===item.related_matrix_snapshot_refs.length,
      'Pós-matriz: refs do snapshot desalinhadas');
    const local=new Set();
    for(let i=0;i<item.related_matrix_occurrences.length;i++) {
      const occurrence=item.related_matrix_occurrences[i];
      assert.ok(valid.has(occurrence),'Pós-matriz: ID não pertence à matriz: '+occurrence);
      assert.ok(!local.has(occurrence),'Pós-matriz: relação duplicada: '+occurrence);
      local.add(occurrence);
      assert.equal(item.related_matrix_snapshot_refs[i],
        'matrix:'+matrixSha+':'+occurrence,'Pós-matriz: snapshot da relação adulterado');
      if(!backlinks.has(occurrence))backlinks.set(occurrence,[]);
      backlinks.get(occurrence).push({id:item.id,url:POST_MATRIX_URL+'#'+anchor});
    }
  }
  for(const refs of backlinks.values())refs.sort((a,b)=>a.id.localeCompare(b.id,'en'));
  return backlinks;
}


/** Audit rendered link *identities*, not only href presence in a Set.
 * visibleMarkup must come from visibleDocument(), which removes inert content.
 * A correct URL with a false label can misrepresent archival provenance. */
export function auditVisibleIdentityLinks(visibleMarkup,expected,prefix,context) {
  const byUrl=new Map();
  for(const {id,url} of expected) {
    assert.ok(url.startsWith(prefix),context+': prefixo inesperado');
    assert.ok(!byUrl.has(url),context+': destino canônico repetido');
    byUrl.set(url,id);
  }
  const counts=new Map();
  for(const match of visibleMarkup.matchAll(/<a\b([^>]*)>([\s\S]*?)<\/a\s*>/gi)) {
    const href=/(?:^|\s)href\s*=\s*(?:"([^"]*)"|'([^']*)')(?=\s|$)/i.exec(match[1]);
    if(!href)continue;
    const url=(href[1]??href[2]).replaceAll('&amp;','&');
    if(!url.startsWith(prefix))continue;
    assert.ok(byUrl.has(url),context+': destino documental não declarado');
    const label=match[2].replace(/<[^>]*>/g,'').trim();
    assert.equal(label,byUrl.get(url),context+': rótulo diverge do identificador canônico');
    counts.set(url,(counts.get(url)??0)+1);
  }
  assert.deepEqual([...counts].sort(),[...byUrl.keys()].map(url=>[url,1]).sort(),
    context+': link visível ausente ou duplicado');
}

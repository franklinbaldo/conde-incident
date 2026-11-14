/** Deterministic entry to archival leads outside the frozen historical matrix. */
import assert from 'node:assert/strict';
import {POST_MATRIX_URL,postMatrixAnchor} from './ssg-post-matrix-backlinks.mjs';
const safe=value=>String(value).replaceAll('_',String.fromCharCode(92)+'_');
const sourceId=value=>assert.match(value,/^[A-Z][A-Z0-9_]{1,95}$/,
  'Pós-matriz: identificador de fonte inválido');

export function sourceIndexBody(sourceLinks,root,citations) {
  assert.ok(Array.isArray(citations.post_matrix_occurrences),
    'Pós-matriz: lista de pistas ausente');
  const seen=new Set();
  const links=[...citations.post_matrix_occurrences]
    .sort((a,b)=>a.id.localeCompare(b.id,'en')).map(item=>{
      const anchor=postMatrixAnchor(item.id);
      assert.ok(!seen.has(item.id),'Pós-matriz: ID duplicado');
      seen.add(item.id);
      sourceId(item.source_id);
      assert.match(item.status,/^[A-Z][A-Z0-9_]{2,159}$/,
        'Pós-matriz: estado inválido');
      assert.equal(item.not_a_verified_conde_physical_event,true,
        'Pós-matriz: não é evento físico verificado');
      assert.equal(item.physical_constraint,null,
        'Pós-matriz: não é restrição física');
      assert.equal(item.observation_type,'DOCUMENTARY_CITATION_NOT_PHYSICAL_OBSERVATION',
        'Pós-matriz: não é observação física');
      assert.equal(item.journalistic_source_independence,'UNRESOLVED',
        'Pós-matriz: independência não demonstrada');
      const tick=String.fromCharCode(96);
      return '- ['+safe(item.id)+']('+POST_MATRIX_URL+'#'+anchor+
        ') · Fonte documental: '+safe(item.source_id)+
        ' · Estado: '+tick+item.status+tick+' (fora do recorte curado)';
    });
  return [
    '## Identificadores de fontes', '',
    '**Uma fonte pode aparecer em várias ocorrências.** O índice distingue referências documentais de observações instrumentais e conserva cada ligação à matriz.', '',
    ...sourceLinks, '',
    '## Pistas documentais posteriores à matriz', '',
    '**Catálogo separado do recorte curado.** Estas pistas não acrescentam linhas à matriz, fontes curadas ou observações físicas independentes. A verificação e as pendências estão no suplemento documental.', '',
    ...(links.length?links:['Nenhuma pista posterior registrada neste feed.']), '',
    '[Voltar ao arquivo curado]('+root+')',
  ].join('\n');
}

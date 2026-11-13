import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync,existsSync} from 'node:fs';
import {archivePages} from '../scripts/ssg-documentary-archive.mjs';
test('sete contratos OKF possuem specs versionadas',()=>{
 for(const name of ['page','story','source','evidence','hypothesis','constraint','experiment']){
  const path='.okf/specs/'+name+'.md';
  assert.ok(existsSync(path),'Spec ausente: '+name);
  assert.match(readFileSync(path,'utf8'),/^---\ntype: Spec\n/);
 }
});
test('arquivo SSG distingue índice Page e ocorrência Evidence',()=>{
 const citations=JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
 const lineage=JSON.parse(readFileSync('public/data/conde-declared-dependence.json','utf8'));
 const pages=archivePages(citations,lineage);
 assert.equal(pages.size,citations.curated_occurrences+2+new Set(citations.records.map(r=>r.source_family)).size);
 assert.match(pages.get('familias/index.md'),/^---\ntype: Page\n/);
 assert.match(pages.get('index.md'),/^---\ntype: Page\n/);
 const record=pages.get('c197-1/index.md');
 assert.match(record,/^---\ntype: Evidence\n/);
 assert.match(record,/occurrence: "C197#1"/);
 assert.ok(record.includes(citations.matrix_git_blob_sha1));
 assert.match(record,/verification_status: "documentary_record_only"/);
 assert.match(record,/Registro documental, não verificação de ocorrência física/);
});
test('gerador tipa Story na fonte e Page nos índices sem editar capítulos',()=>{
 const generator=readFileSync('scripts/prepare-ssg.mjs','utf8');
 assert.match(generator,/fm\.type,'Story'/);
 assert.match(generator,/'type: Story'/);
 assert.match(generator,/'type: Page'/);
});

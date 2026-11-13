import assert from 'node:assert/strict';
import {readdirSync,readFileSync,statSync,existsSync} from 'node:fs';
import {join} from 'node:path';
import {AUTHORED_ROUTES,checkPage} from './ssg-authored-pages.mjs';
const root='content', files=[];
function walk(dir){
 for(const entry of readdirSync(dir)){
  const path=join(dir,entry);
  if(statSync(path).isDirectory())walk(path);
  else if(path.endsWith('.md'))files.push(path);
 }
}
walk(root);
assert.ok(files.length>0,'Nenhum Markdown gerado pelo SSG');
const permitted=new Set(['Page','Story','Source','Evidence','Hypothesis','Constraint','Experiment']);
for(const path of files){
 const body=readFileSync(path,'utf8');
 const match=/^---\r?\n([\s\S]*?)\r?\n---\r?\n/.exec(body);
 assert.ok(match,'Frontmatter ausente: '+path);
 const attributes=new Map;
 for(const line of match[1].split(/\r?\n/)){
  const found=/^([a-z_]+):\s*(.*)$/.exec(line);
  assert.ok(found,'Campo frontmatter inválido: '+path);
  assert.ok(!attributes.has(found[1]),'Campo duplicado '+found[1]+' em '+path);
  attributes.set(found[1],found[2]);
 }
 const type=attributes.get('type');
 assert.ok(permitted.has(type),'Tipo OKF não autorizado: '+path);
 assert.ok(existsSync('.okf/specs/'+type.toLowerCase()+'.md'),'Spec não encontrada: '+type);
 for(const key of ['title','description'])
  assert.ok(attributes.get(key)&&attributes.get(key)!=='""','Metadado ausente: '+key+' '+path);
 if(path.startsWith('content/stories/')&&!path.endsWith('/index.md')){
  assert.equal(type,'Story','Capítulo não é Story: '+path);
  for(const key of ['summary','chapter','date','author','status','source_path'])
   assert.ok(attributes.get(key),'Metadado Story ausente: '+key+' '+path);
 }
 if(path.startsWith('content/evidencias/arquivo/')&&!path.endsWith('/index.md')){
  assert.equal(type,'Evidence','Ocorrência não é Evidence: '+path);
  assert.match(attributes.get('occurrence')||'',/^"C[0-9]{1,3}#[1-9][0-9]*"$/);
  assert.match(attributes.get('matrix_snapshot')||'',/^"[a-f0-9]{40}"$/);
  assert.equal(attributes.get('verification_status'),'"documentary_record_only"');
 }
}
for(const path of ['content/index.md','content/stories/index.md','content/evidencias/arquivo/index.md'])
 assert.match(readFileSync(path,'utf8'),/^---\ntype: Page\n/);
for(const slug of AUTHORED_ROUTES){
 const path='pages/'+slug+'/page.md';
 const source=checkPage(slug,readFileSync(path,'utf8'));
 assert.equal(readFileSync('content/'+slug+'/index.md','utf8'),source,
   'Saída SSG diverge da página OKF canônica: '+slug);
}
console.log('OKF SSG: '+files.length+' páginas tipadas, '+AUTHORED_ROUTES.length+' páginas canônicas.');

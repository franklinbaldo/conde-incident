import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
const root='public';
const read=path=>readFileSync(join(root,path),'utf8');
const index=read('index.html'), listing=read('stories/index.html'), lab=read('lab/index.html');
for(const [name,html] of [['home',index],['stories',listing]]) {
  assert.match(html,/\/conde-incident\/stories\//,name+' sem rota Caderno');
  assert.match(html,/\/conde-incident\/lab\//,name+' sem rota laboratório');
  assert.match(html,/<html[^>]+lang=["']?pt-BR/i,name+' sem idioma pt-BR');
}
assert.match(lab,/\/conde-incident\/lab\/assets\//,'Assets Vite fora de /lab/');
assert.doesNotMatch(lab,/(?:src|href)=["']\/assets\//,'Assets relativos à raiz, 404 no Pages');
assert.ok(existsSync('public/lab/assets'),'Assets de laboratório ausentes');
assert.ok(existsSync('public/css/site.css'),'CSS do Caderno ausente');
let chapters=0;
for(const name of readdirSync('stories').filter(s=>/^\d{4}-\d{2}-\d{2}-.+\.md$/.test(s))){
  const slug=name.slice(0,-3);
  const source=readFileSync(join('stories',name),'utf8');
  const article=read(join('stories',slug,'index.html'));
  assert.ok(listing.includes('/conde-incident/stories/'+slug+'/'),'Capítulo omitido: '+slug);
  assert.match(article,/<article\b/i,'Sem artigo HTML: '+slug);
  assert.ok(article.includes('/conde-incident/lab/'),'Artigo sem retorno ao laboratório: '+slug);
  assert.ok(article.includes('https://github.com/franklinbaldo/conde-incident/blob/main/stories/'+name),'Fonte canônica ausente: '+slug);
  assert.ok(article.includes('https://') && source.includes('https://'),'Sem referência externa: '+slug);
  chapters++;
}
assert.ok(chapters>0,'Nenhuma reportagem renderizada');
console.log('PASS: '+chapters+' capítulos, índice, CSS, laboratório e rotas GitHub Pages.');

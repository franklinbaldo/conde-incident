import assert from 'node:assert/strict';
import {readFileSync,readdirSync,mkdirSync,rmSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';
import {writeArchivePages} from './ssg-documentary-archive.mjs';
import {writeMatrixCatalogPages} from './ssg-matrix-catalog.mjs';
import {writeTleCustodyPage} from './ssg-tle-custody.mjs';
import {writeAuthoredPages} from './ssg-authored-pages.mjs';
import {editorialChronology} from './ssg-chronology.mjs';

// stories/*.md is the sole human-authored content; content/ is regenerated.
const names=readdirSync('stories').filter(n=>/^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$/.test(n)).sort();
assert.ok(names.length, 'Caderno vazio: não publicar um índice oco');
function scalar(value, file) {
  if (value.startsWith('"')) return JSON.parse(value);
  if (value.startsWith("'") && value.endsWith("'")) return value.slice(1,-1).replaceAll("''","'");
  if (/[:#]|^\[/.test(value)) throw Error('Valor YAML não literal; cite-o em '+file+': '+value);
  return value;
}
const stories=names.map(filename=>{
  const source=readFileSync(join('stories',filename),'utf8');
  const found=/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(source);
  assert.ok(found,'Frontmatter YAML ausente em '+filename);
  const fm={};
  for(const line of found[1].split(/\r?\n/)) {
    if(!line.trim() || line.trim().startsWith('#')) continue;
    const match=/^([a-z_]+):\s*(.*?)\s*$/.exec(line);
    assert.ok(match,'Frontmatter incompatível em '+filename+': '+line);
    assert.ok(!Object.hasOwn(fm,match[1]),'Campo duplicado '+match[1]+' em '+filename);
    fm[match[1]]=scalar(match[2],filename);
  }
  assert.equal(fm.type,'Story','Capítulo não OKF Story: '+filename);
  for(const field of ['title','description','date','summary','chapter','author','status']) {
    assert.ok(typeof fm[field]==='string'&&fm[field].trim(),field+' ausente em '+filename);
  }
  assert.match(fm.date,/^\d{4}-\d{2}-\d{2}$/);
  assert.ok(filename.startsWith(fm.date+'-'),'Data incompatível em '+filename);
  assert.match(fm.chapter,/^\d+$/);
  const slug=filename.slice(0,-3);
  // The original body stays verbatim, except the duplicated first H1.
  const body=found[2].replace(/^\s*# [^\r\n]*\r?\n(?:\r?\n)?/,'');
  return {filename,slug,...fm,body};
}).sort((a,b)=>Number(a.chapter)-Number(b.chapter));
stories.forEach((s,i)=>{
  assert.equal(Number(s.chapter),i+1,'Capítulos não consecutivos');
  if(i) assert.ok(stories[i-1].date<=s.date,'Cronologia retrocedeu');
});
if(process.argv.includes('--check')) {
  console.log('Validados '+stories.length+' capítulos canônicos; nenhuma cópia escrita.');
  process.exit(0);
}
rmSync('content',{recursive:true,force:true});
mkdirSync('content/stories',{recursive:true});
const quote=s=>JSON.stringify(String(s));
function page(title,summary,layout,body) {
  return ['---','type: Page','title: '+quote(title),'description: '+quote(summary),
    'layout: '+layout,'language: pt-BR','---','',body,''].join('\n');
}
const intro='Os documentos não demonstram que a notícia de Conde e o decaimento do NORAD 528 tenham a mesma causa. Cada capítulo distingue registro, relato e hipótese.';
const listing=stories.map(s=>'- [Capítulo '+s.chapter+': '+s.title+'](/conde-incident/stories/'+s.slug+'/) — '+s.summary).join('\n');
const indexBody='# Conde, 1963: investigação documentada\n\n'+intro+'\n\n## Caderno de histórias\n\n'+listing+'\n\n[Laboratório científico](/conde-incident/lab/)';
const storiesBody='# Caderno de histórias\n\n'+intro+'\n\n'+listing+'\n\n[Laboratório científico](/conde-incident/lab/)';
writeFileSync('content/index.md',page('Conde, 1963: Caderno','Investigar não é confirmar uma queda.', 'index',indexBody));
writeFileSync('content/stories/index.md',page('Caderno de histórias','Capítulos com fontes e hipóteses distinguíveis.', 'index',storiesBody));
for(const s of stories){
  const fm=['---','type: Story','title: '+quote(s.title),'description: '+quote(s.summary),
    'date: '+quote(s.date),'layout: page','language: pt-BR',
    'summary: '+quote(s.summary),'chapter: '+quote(s.chapter),'author: '+quote(s.author),
    'status: '+quote(s.status),
    'source_path: '+quote('stories/'+s.filename),'---',''];
  // Source custody is derived from the canonical filename, not optional SSG page metadata.
  // Keep the real Markdown link in the rendered article even if the theme changes.
  const provenance = '\n\n---\n\n[Consultar Markdown-fonte e histórico](https://github.com/franklinbaldo/conde-incident/blob/main/stories/' + s.filename + ')\n';
  writeFileSync(join('content/stories',s.filename),fm.join('\n')+s.body+provenance);
}
console.log('Gerado conteúdo SSG de '+stories.length+' capítulos sem alterar stories/.');


const links=[
 ['cronologia','Cronologia'],['evidencias','Evidências'],
 ['hipoteses','Hipóteses'],['mapa','Mapa'],['simulacoes','Simulações'],['metodo','Método']
];
const newNav=links.map(([slug,title])=>'- ['+title+'](/conde-incident/'+slug+'/)').join('\n');
function landing(slug,title,description,content){
 mkdirSync('content/'+slug,{recursive:true});
 writeFileSync('content/'+slug+'/index.md',page(title,description,'index',content+'\n\n[Início](/conde-incident/) · [Caderno](/conde-incident/stories/)'));
}
landing('cronologia','Cronologia da investigação','Datas editoriais da investigação do Conde.',
 '# Cronologia da investigação\n\n**Estas datas são de publicação dos capítulos, não datas de observação, passagem ou queda.**\n\n'+editorialChronology(stories));
landing('evidencias','Evidências e fontes','Índice de textos, fontes e proveniência.',
 '# Evidências e fontes\n\nEste índice cobre os capítulos editoriais, **não toda a matriz científica**. Verifique as fontes originais e a dependência entre relatos.\n\n'+stories.map(s=>
 '- [Capítulo '+s.chapter+': '+s.title+'](/conde-incident/stories/'+s.slug+'/) · [Markdown canônico](https://github.com/franklinbaldo/conde-incident/blob/main/stories/'+s.filename+')'
 ).join('\n')+'\n\n[Arquivo documental estático: proveniência e genealogia](/conde-incident/evidencias/arquivo/)\n\n[Matriz integral: alegações curadas e ainda sem ficha](/conde-incident/evidencias/matriz/)\n\n[Índice documental JSON auditável](/conde-incident/data/conde-evidence-index-manifest.json)\n\n[Pesquisa e evidências completas](https://github.com/franklinbaldo/conde-incident/tree/main/research)');
const archiveCount = writeArchivePages('content/evidencias/arquivo',
  JSON.parse(readFileSync('public/data/conde-source-citations.json', 'utf8')),
  JSON.parse(readFileSync('public/data/conde-declared-dependence.json', 'utf8')), 
  JSON.parse(readFileSync('public/data/conde-wayback-citation-links.json', 'utf8')));
const archiveHome='content/evidencias/arquivo/index.md';
const archiveIndex=readFileSync(archiveHome,'utf8');
const archiveMarker='## Ocorrências curadas';
assert.ok(archiveIndex.includes(archiveMarker),'Arquivo curado sem âncora de matriz');
writeFileSync(archiveHome,archiveIndex.replace(archiveMarker,
  '[Percorrer toda a matriz, inclusive ocorrências ainda sem ficha](/conde-incident/evidencias/matriz/)\n\n'+archiveMarker));
console.log('Arquivo SSG: '+archiveCount+' páginas Markdown para SSG sem JS.');
const matrixCount=writeMatrixCatalogPages('content/evidencias/matriz');
console.log('Matriz SSG integral: '+matrixCount+' páginas geradas sem JS.');
const authoredCount=writeAuthoredPages();
writeTleCustodyPage();
console.log('SSG: custódia do TLE secundário 528 publicada sem React.');
console.log('Páginas Page canônicas validadas e copiadas: '+authoredCount);
const homePath='content/index.md';
const home=readFileSync(homePath,'utf8');
const heading='## Caderno de histórias';
assert.ok(home.includes(heading),'Secção Caderno ausente do índice SSG');
writeFileSync(homePath,home.replace(heading,'## Explore a investigação\n\n'+newNav+'\n\n'+heading));

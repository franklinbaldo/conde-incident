import assert from 'node:assert/strict';
import {readFileSync,readdirSync,mkdirSync,rmSync,writeFileSync} from 'node:fs';
import {join} from 'node:path';

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
  for(const field of ['title','date','summary','chapter','author','status']) {
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
  return ['---','title: '+quote(title),'description: '+quote(summary),
    'layout: '+layout,'language: pt-BR','---','',body,''].join('\n');
}
const intro='Os documentos não demonstram que a notícia de Conde e o decaimento do NORAD 528 tenham a mesma causa. Cada capítulo distingue registro, relato e hipótese.';
const listing=stories.map(s=>'- [Capítulo '+s.chapter+': '+s.title+'](/conde-incident/stories/'+s.slug+'/) — '+s.summary).join('\n');
const indexBody='# Conde, 1963: investigação documentada\n\n'+intro+'\n\n## Caderno de histórias\n\n'+listing+'\n\n[Laboratório científico](/conde-incident/lab/)';
const storiesBody='# Caderno de histórias\n\n'+intro+'\n\n'+listing+'\n\n[Laboratório científico](/conde-incident/lab/)';
writeFileSync('content/index.md',page('Conde, 1963: Caderno','Investigar não é confirmar uma queda.', 'index',indexBody));
writeFileSync('content/stories/index.md',page('Caderno de histórias','Capítulos com fontes e hipóteses distinguíveis.', 'index',storiesBody));
for(const s of stories){
  const fm=['---','title: '+quote(s.title),'description: '+quote(s.summary),
    'date: '+quote(s.date),'layout: page','language: pt-BR',
    'chapter: '+quote(s.chapter),'author: '+quote(s.author),
    'status: '+quote(s.status),
    'source_path: '+quote('stories/'+s.filename),'---',''];
  // Source custody is derived from the canonical filename, not optional SSG page metadata.
  // Keep the real Markdown link in the rendered article even if the theme changes.
  const provenance = '\n\n---\n\n[Consultar Markdown-fonte e histórico](https://github.com/franklinbaldo/conde-incident/blob/main/stories/' + s.filename + ')\n';
  writeFileSync(join('content/stories',s.filename),fm.join('\n')+s.body+provenance);
}
console.log('Gerado conteúdo SSG de '+stories.length+' capítulos sem alterar stories/.');

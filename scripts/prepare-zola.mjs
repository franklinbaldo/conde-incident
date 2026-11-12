import { readFileSync, readdirSync, mkdirSync, rmSync, writeFileSync } from 'node:fs';
import { join } from 'node:path';

// stories/*.md is canonical; content/stories is generated, never edited.
const output = 'content/stories';
const required = ['title','date','summary','chapter','author','status'];
const files = readdirSync('stories').filter(name => /^\d{4}-\d{2}-\d{2}-[a-z0-9-]+\.md$/.test(name)).sort();
if (files.length === 0) throw Error('Nenhum capítulo em stories/');

const stories = files.map(filename => {
  const original = readFileSync(join('stories',filename),'utf8');
  const match = /^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(original);
  if (!match) throw Error('Front matter ausente: '+filename);
  const info = {};
  for (const line of match[1].split(/\r?\n/)) {
    if (!line.trim()) continue;
    const kv = /^([a-z]+):\s*(.+)$/.exec(line);
    if (!kv || !required.includes(kv[1]) || Object.hasOwn(info,kv[1])) {
      throw Error('Campo inesperado/repetido em '+filename+': '+line);
    }
    const value = kv[2].trim();
    info[kv[1]] = value.startsWith('"') ? JSON.parse(value) :
      value.startsWith("'") && value.endsWith("'") ? value.slice(1,-1) : value;
  }
  for (const field of required) if (!info[field]) throw Error('Campo obrigatório: '+filename+' / '+field);
  if (!/^\d{4}-\d{2}-\d{2}$/.test(info.date) || !filename.startsWith(info.date+'-')) {
    throw Error('Data inconsistente: '+filename);
  }
  if (!/^\d+$/.test(info.chapter)) throw Error('Número de capítulo inválido: '+filename);
  return {filename, ...info, body:match[2]};
}).sort((a,b) => Number(a.chapter)-Number(b.chapter));

for(let i=0;i<stories.length;i++) {
  if(Number(stories[i].chapter)!==i+1) throw Error('Capítulos não consecutivos em stories/');
  if(i && stories[i].date < stories[i-1].date) throw Error('Capítulo em data anterior à sequência');
}

if (!process.argv.includes('--check')) {
  rmSync(output, {recursive:true,force:true});
  mkdirSync(output,{recursive:true});
  writeFileSync(join(output,'_index.md'),'+++\ntitle = "Reportagens"\nsort_by = "weight"\npage_template = "story.html"\n+++\n');
  for(const s of stories) {
    const q = x => JSON.stringify(x);
    const lines = [
      '+++',
      'title = '+q(s.title),
      'date = '+s.date,
      'description = '+q(s.summary),
      'slug = '+q(s.filename.slice(0,-3)),
      'weight = '+Number(s.chapter),
      '[extra]',
      'chapter = '+q(s.chapter),
      'author = '+q(s.author),
      'status = '+q(s.status),
      'source_path = '+q('stories/'+s.filename),
      '+++',''
    ];
    // The canonical Markdown starts after a YAML newline; remove a repeated first H1
    // even if the author separates it from front matter with blank lines.
    const body = s.body.replace(/^(?:\r?\n)*# [^\r\n]*\r?\n(?:\r?\n)*/, '');
    writeFileSync(join(output,s.filename),lines.join('\n')+body);
  }
}
console.log('Validated '+stories.length+' chronological chapter(s); Zola content '+(process.argv.includes('--check')?'not written':'generated')+'.');

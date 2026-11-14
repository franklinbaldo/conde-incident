import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,readdirSync,writeFileSync,lstatSync} from 'node:fs';
import {dirname,join,relative} from 'node:path';

// Explicit paths make the source-to-public-URL mapping reviewable.
export const AUTHORED_ROUTES=Object.freeze([
  'dossie','o-que-sabemos','hipoteses','metodo','simulacoes','mapa',
  'simulacoes/inverso','simulacoes/triangulacao',
  'simulacoes/sensibilidade','simulacoes/montecarlo',
  'simulacoes/tles','evidencias/fontes',
]);

export function checkPage(slug,source){
  assert.ok(AUTHORED_ROUTES.includes(slug),'Rota Page não cadastrada: '+slug);
  const found=/^---\r?\n([\s\S]*?)\r?\n---\r?\n([\s\S]*)$/.exec(source);
  assert.ok(found,'Frontmatter Page não encontrado: '+slug);
  const fields=new Map();
  for(const line of found[1].split(/\r?\n/)){
    const match=/^([a-z][a-z_]*)\s*:\s*(.*)$/.exec(line);
    assert.ok(match,'Metadado Page inválido: '+slug);
    assert.ok(!fields.has(match[1]),'Metadado Page duplicado: '+match[1]);
    const value=match[2].startsWith('"')?JSON.parse(match[2]):match[2];
    fields.set(match[1],value);
  }
  assert.equal(fields.get('type'),'Page','Somente Page canônica em pages/');
  assert.equal(fields.get('layout'),'index');
  assert.equal(fields.get('language'),'pt-BR');
  for(const field of ['title','description','page_kind']){
    assert.ok(typeof fields.get(field)==='string'&&fields.get(field).trim(),
      'Campo Page obrigatório ausente: '+field);
  }
  assert.equal(fields.get('canonical_route'),'/conde-incident/'+slug+'/',
    'URL declarada não coincide com o caminho OKF: '+slug);
  assert.match(found[2],/^\s*# [^\r\n]+\r?\n/,'Página sem H1');
  if(slug==='mapa'||slug.startsWith('simulacoes/')){
    assert.ok(found[2].includes('/conde-incident/lab/#/'),
      'Página de ferramenta sem link de preservação do laboratório: '+slug);
  }
  return source;
}

function collect(dir,root,found){
  for(const name of readdirSync(dir)){
    const file=join(dir,name);
    const stat=lstatSync(file);
    assert.ok(!stat.isSymbolicLink(),'Não incluir symlink em pages/');
    if(stat.isDirectory())collect(file,root,found);
    else {
      assert.ok(file.endsWith('/page.md'),'Arquivo de Page sem rota: '+file);
      found.push(relative(root,dirname(file)).replaceAll('\\','/'));
    }
  }
}

export function writeAuthoredPages(sourceDir='pages',targetDir='content'){
  const actual=[];
  collect(sourceDir,sourceDir,actual);
  assert.deepEqual(actual.sort(),[...AUTHORED_ROUTES].sort(),
    'Fontes Page devem coincidir com rotas registradas; sem omissão nem URL órfã');
  for(const slug of AUTHORED_ROUTES){
    const source=checkPage(slug,readFileSync(join(sourceDir,slug,'page.md'),'utf8'));
    const target=join(targetDir,slug,'index.md');
    mkdirSync(dirname(target),{recursive:true});
    writeFileSync(target,source,'utf8');
  }
  return actual.length;
}

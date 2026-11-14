/** No-JS, paginated reading path for all occurrences in the frozen C001-C238 matrix.
 * This is a coverage index, not independent historical testimony. */
import assert from 'node:assert/strict';
import {mkdirSync,readFileSync,writeFileSync} from 'node:fs';
import {dirname,join,resolve} from 'node:path';
import {pathToFileURL} from 'node:url';
import {readBundle,audit,visibleDocument} from './verify-ssg-evidence-index.mjs';
import {matrixRowUrl} from './ssg-documentary-archive.mjs';

const ROOT='/conde-incident/evidencias/matriz/';
const PER_PAGE=20;
const safe=value=>String(value).replaceAll('\\','\\\\')
  .replace(/([\[\]_*`<>|])/g,'\\$1').replace(/[\r\n\t]/g,' ');
const page=(title,description,body)=>[
  '---','type: Page','title: '+JSON.stringify(title),
  'description: '+JSON.stringify(description),'layout: page','language: pt-BR',
  'date: '+JSON.stringify('2026-11-13'),
  'author: '+JSON.stringify('Projeto Conde (índice documental gerado)'),
  '---','',body,'',
].join('\n');
const url=index=>ROOT+'paginas/'+String(index+1).padStart(2,'0')+'/';
const data=bundle=>bundle.lookupShards.flatMap(part=>JSON.parse(part.raw).records)
  .map(pointer=>{
    const meta=pointer.kind==='curated'?bundle.shards:bundle.gapShards;
    const [shard,row]=pointer.positions[0];
    const record=JSON.parse(meta[shard].raw).records[row];
    assert.equal(pointer.occurrence,record.occurrence);
    for(const [otherShard,otherRow] of pointer.positions){
      const other=JSON.parse(meta[otherShard].raw).records[otherRow];
      assert.equal(other.occurrence,record.occurrence);
      assert.equal(other.row_sha256,record.row_sha256);
      assert.equal(other.claim_text,record.claim_text);
    }
    return {pointer,record};
  });

export function matrixCatalogPages(bundle) {
  const entries=data(bundle);
  const {manifest}=bundle;
  assert.equal(entries.length,manifest.total_matrix_occurrences);
  assert.equal(entries.filter(x=>x.pointer.kind==='curated').length,manifest.curated_occurrences);
  assert.equal(entries.filter(x=>x.pointer.kind==='unmapped').length,manifest.unmapped_matrix_occurrences);
  const files=new Map();
  const pages=[];
  for(let start=0;start<entries.length;start+=PER_PAGE){
    const current=pages.length;
    const slice=entries.slice(start,start+PER_PAGE);
    const items=slice.flatMap(({pointer,record})=>{
      const curated=pointer.kind==='curated';
      const target=curated?record.archive_path:null;
      if(curated) assert.match(target,/^\/conde-incident\/evidencias\/arquivo\/c\d+-\d+\/$/);
      return [
        '## '+safe(pointer.occurrence)+' · '+safe(record.claim_text),'',
        curated
          ? '**Cobertura do índice:** ficha documental curada, com '+pointer.positions.length+
            ' referência(s). [Abrir fonte, estado e genealogia]('+target+')'
          : '**Cobertura do índice:** ainda sem ficha documental curada. Isso não significa que a alegação seja falsa, que falte uma fonte ou que tenha ocorrido um evento físico.',
        '',
        '[Consultar linha '+record.matrix_line+' da matriz]('+matrixRowUrl(record.matrix_line)+') · '+
          '**SHA-256 da linha:** `'+record.row_sha256+'`','',
      ];
    });
    const before=current>0?'[Página anterior]('+url(current-1)+') · ':'';
    const after=start+PER_PAGE<entries.length?' · [Página seguinte]('+url(current+1)+')':'';
    const body=[
      '**Este é um inventário editorial de alegações, não um catálogo de observações físicas confirmadas.** Títulos e hashes vêm da matriz congelada. Só as fichas curadas possuem vínculo documental e genealogia no recorte publicado.','',
      '**Recorte '+(start+1)+'–'+(start+slice.length)+' de '+entries.length+' ocorrências.**', '',
      before+'[Índice da matriz]('+ROOT+')'+after,'',...items,
      before+'[Índice da matriz]('+ROOT+')'+after,
    ].join('\n');
    const name='paginas/'+String(current+1).padStart(2,'0')+'/index.md';
    const content=page('Matriz histórica · página '+(current+1),
      'Alegações da matriz, com links para linhas originais e fichas curadas.',body);
    assert.ok(Buffer.byteLength(content,'utf8')<=20000,'Página gerada acima do teto de 20 KB');
    files.set(name,content);
    pages.push({first:slice[0].pointer.occurrence,last:slice.at(-1).pointer.occurrence,
      start:start+1,end:start+slice.length,url:url(current)});
  }
  const index=page('Matriz histórica: 241 ocorrências',
    'Cobertura integral da matriz editorial congelada, com lacunas de curadoria visíveis.',[
      '**Este catálogo reúne alegações registradas na matriz, não fatos físicos demonstrados.**', '',
      '**'+manifest.total_matrix_occurrences+' ocorrências:** '+manifest.curated_occurrences+
        ' com fichas documentais curadas e '+manifest.unmapped_matrix_occurrences+
        ' ainda sem ficha no índice. Ausência de curadoria não equivale a ausência de fonte.', '',
      '**Custódia da matriz:** Git blob `'+manifest.matrix_git_blob_sha1+'`; SHA-256 `'+
        manifest.matrix_source.sha256+'` ('+manifest.matrix_source.bytes+' bytes).', '',
      '## Percorrer as ocorrências', '',
      ...pages.map(p=>'- [Registros '+p.start+'–'+p.end+' ('+p.first+' até '+p.last+')]('+p.url+')'),
      '', '## Localizador rápido por identificador', '',
      'Use a busca do navegador pelo identificador `Cnn#N`. Cada atalho abre a página estática que contém a ocorrência; nenhum JavaScript é necessário.', '',
      ...pages.flatMap((p,i)=>[
        '**Registros '+p.start+'–'+p.end+':** '+entries.slice(i*PER_PAGE,(i+1)*PER_PAGE)
          .map(({pointer})=>'['+pointer.occurrence+']('+p.url+')').join(' · '),
        '',
      ]),
      '[Arquivo de fichas curadas](/conde-incident/evidencias/arquivo/) · '+
        '[Evidências editoriais](/conde-incident/evidencias/)',
    ].join('\n'));
  assert.ok(Buffer.byteLength(index,'utf8')<=20000,'Índice de IDs acima do teto de 20 KB');
  files.set('index.md',index);
  return {files,entries,pages};
}

export function writeMatrixCatalogPages(outputDir,bundle=readBundle()) {
  audit(bundle); // The generator refuses a coherent but forged lookup+shard pair.
  const {files}=matrixCatalogPages(bundle);
  for(const [name,content] of files){
    const path=join(outputDir,name);
    mkdirSync(dirname(path),{recursive:true});
    writeFileSync(path,content,'utf8');
  }
  return files.size;
}

export function auditBuiltMatrixCatalog(bundle,siteRoot='public') {
  audit(bundle);
  const {entries,pages}=matrixCatalogPages(bundle);
  const index=visibleDocument(readFileSync(join(siteRoot,'evidencias/matriz/index.html'),'utf8'));
  for(const item of pages) assert.ok(index.links.has(item.url),'Index missing page '+item.url);
  for(let i=0;i<pages.length;i++){
    const name=String(i+1).padStart(2,'0');
    const html=readFileSync(join(siteRoot,'evidencias/matriz/paginas',name,'index.html'),'utf8');
    const doc=visibleDocument(html);
    assert.ok(doc.links.has(ROOT),'Page missing return to matrix index: '+name);
    for(const {pointer,record} of entries.slice(i*PER_PAGE,(i+1)*PER_PAGE)){
      assert.ok(doc.visibleText.includes(pointer.occurrence),'Missing occurrence '+pointer.occurrence);
      assert.ok(doc.visibleText.includes(record.row_sha256),'Missing row digest '+pointer.occurrence);
      assert.ok(doc.links.has(matrixRowUrl(record.matrix_line)),
        'Missing original matrix link '+pointer.occurrence);
      if(pointer.kind==='curated')assert.ok(doc.links.has(record.archive_path),
        'Missing curated evidence link '+pointer.occurrence);
    }
  }
  for(const path of ['evidencias/index.html','evidencias/arquivo/index.html']){
    const doc=visibleDocument(readFileSync(join(siteRoot,path),'utf8'));
    assert.ok(doc.links.has(ROOT),'Missing matrix navigation from '+path);
  }
  return {pages:pages.length+1,occurrences:entries.length};
}

if(process.argv[1]&&import.meta.url===pathToFileURL(resolve(process.argv[1])).href){
  const bundle=readBundle();
  const outcome=process.argv.includes('--built-site')
    ? auditBuiltMatrixCatalog(bundle):writeMatrixCatalogPages('content/evidencias/matriz',bundle);
  console.log('Matriz SSG sem JS:',JSON.stringify(outcome));
}

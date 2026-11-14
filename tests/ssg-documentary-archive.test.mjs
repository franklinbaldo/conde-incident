import test from 'node:test';
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {archivePages} from '../scripts/ssg-documentary-archive.mjs';
import {interpretArchiveStatus} from '../scripts/archive-source-status.mjs';
import {archiveStatusAnchor,archiveStatusLink} from '../scripts/archive-status-index.mjs';

const feed = JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
const ancestry = JSON.parse(readFileSync('public/data/conde-declared-dependence.json','utf8'));
const clone = obj=>JSON.parse(JSON.stringify(obj));

test('SSG publishes one stable, no-JS page per curated occurrence', () => {
  const pages=archivePages(feed, ancestry);
  const families=new Set(feed.records.map(r=>r.source_family));
  const works=new Set(feed.records.map(r=>r.work_id));
  const sources=new Set(feed.records.map(r=>r.source_id));
  assert.equal(pages.size, feed.curated_occurrences+5+families.size+works.size+sources.size);
  const index=pages.get('index.md');
  assert.match(index,/28 ocorrências curadas de 241/);
  assert.match(index,/213 ocorrências não mapeadas/);
  assert.match(index,/independência/);
  assert.match(index,/\/conde-incident\/lab\/#\/documents/);
  assert.doesNotMatch(index, /<script|onclick=|onload=/i);
  for(const key of ['c01-1/index.md','c197-1/index.md','c232-1/index.md']) {
    const contents=pages.get(key);
    assert.ok(contents, `Ocorrência ausente: ${key}`);
    assert.match(contents,/Abrir ocorrência na matriz imutável/);
    assert.match(contents,/não verificação de ocorrência física/);
    assert.match(contents,/layout: page/);
  }
  assert.match(pages.get('c232-1/index.md'),/Referência 2:/);
  assert.match(pages.get('c232-1/index.md'),/2 referência\(s\) curada\(s\)/);
  assert.match(pages.get('c01-1/index.md'),/RADIO\\_TUPI\\_19631108/);
  assert.match(pages.get('c197-1/index.md'),/C197#1/);
  assert.match(index,/famílias documentais e ocorrências relacionadas/);
  assert.match(pages.get('c232-1/index.md'),/familias\/usaf-aira-bluebook\//);
  assert.match(pages.get('c232-1/index.md'),/familias\/bluebook-derivative-catalogues\//);
  assert.match(pages.get('familias/index.md'),/Famílias de fontes/);
  assert.match(pages.get('familias/radio-tupi-fbis/index.md'),/C01#1/);
  assert.match(pages.get('familias/radio-tupi-fbis/index.md'),/C03#1/);
  assert.match(pages.get('familias/norad-nasa-tracking/index.md'),/12 ocorrência\(s\)/);
  assert.match(pages.get('familias/usaf-aira-bluebook/index.md'),/C232#1/);
  assert.match(pages.get('familias/bluebook-derivative-catalogues/index.md'),/C232#1/);
  assert.match(index,/Consultar obras e suas reutilizações/);
  assert.match(pages.get('obras/index.md'),/Obras documentais/);
  assert.ok(pages.get('obras/index.md').includes('/obras/nasa-ssr-vol3-22/'));
  assert.match(pages.get('obras/nasa-ssr-vol3-22/index.md'),/8 ocorrência\(s\), 8 vínculo\(s\)/);
  assert.match(pages.get('obras/nasa-ssr-vol3-22/index.md'),/C197#1/);
  assert.match(pages.get('obras/nasa-ssr-vol3-22/index.md'),/SHA-256 da linha na matriz/);
  assert.match(pages.get('c232-1/index.md'),/obras\/nara-bb-card-302531013\//);
  assert.match(index,/Explorar por estado documental/);
  assert.match(index,/\/conde-incident\/evidencias\/arquivo\/estados\//);
  const byState=pages.get('estados/index.md');
  assert.ok(byState,'SSG state browser missing');
  assert.match(byState,/vínculos de fontes, não observações físicas independentes/);
  assert.doesNotMatch(byState,/<script|onclick=|onload=/i);
  for (const record of feed.records) {
    const reading=interpretArchiveStatus(record.source_status);
    const id=record.occurrence.toLowerCase().replace('#','-');
    const source=record.source_id.toLowerCase().replaceAll('_','-');
    assert.ok(byState.includes(reading.label), 'Estado não indexado: '+record.source_status);
    assert.ok(byState.includes('['+record.occurrence+' · '+record.source_id+']('+
      '/conde-incident/evidencias/arquivo/'+id+'/)'),
      'Vínculo documental perdido no índice: '+record.occurrence);
    assert.ok(byState.includes('/fontes/'+source+'/)'),'Ficha da fonte perdida: '+source);
    assert.ok(byState.includes('#L'+record.matrix_line+')'), 'Linha da matriz perdida');
  }
  // Each status is a stable, shareable, keyboard-usable in-page destination.
  const codes=[...new Set(feed.records.map(r=>r.source_status))];
  assert.equal(codes.length,14);
  for (const code of codes) {
    const fragment=archiveStatusAnchor(code);
    const {label}=interpretArchiveStatus(code);
    assert.match(fragment,/^estado-[a-z0-9-]+$/);
    assert.ok(byState.includes('<a id="'+fragment+'"></a>'), 'Sem âncora: '+code);
    assert.ok(byState.includes('](#'+fragment+')'), 'Sem sumário navegável: '+code);
    assert.ok(byState.includes(label), 'Rótulo de estado ausente: '+code);
  }
  for (const record of feed.records) {
    const slug=record.occurrence.toLowerCase().replace('#','-');
    const link=archiveStatusLink(record.source_status);
    assert.ok(pages.get(slug+'/index.md').includes(link), 'Sem volta ao estado na ocorrência');
    assert.ok(pages.get('fontes/'+record.source_id.toLowerCase().replaceAll('_','-')+'/index.md').includes(link),
      'Sem volta ao estado na ficha da fonte');
    assert.ok(pages.get('obras/'+record.work_id.toLowerCase().replaceAll('_','-')+'/index.md').includes(link),
      'Sem volta ao estado na obra');
  }
  assert.throws(()=>archiveStatusAnchor('NOT_A_REAL_STATUS'),/sem leitura editorial revisada/);
  assert.throws(()=>archiveStatusAnchor('<script>'),/Código documental inválido/);
  assert.match(index,/Consultar identificadores de fontes/);
  assert.match(pages.get('fontes/index.md'),/Identificadores de fontes/);
  const repeated=pages.get('fontes/nasa-ssr-19631115/index.md');
  assert.match(repeated,/7 ocorrência\(s\), 7 vínculo\(s\)/);
  assert.match(repeated,/matriz imutável/);
  assert.match(repeated,/C197#1/);
  assert.match(repeated,/Documento original/);
  for(const source of sources){
    assert.ok(pages.has('fontes/'+source.toLowerCase().replaceAll('_','-')+'/index.md'),
      'Fonte sem índice: '+source);
  }
  for(const work of works){
    const slug=work.toLowerCase().replaceAll('_','-');
    assert.ok(pages.has('obras/'+slug+'/index.md'), 'Obra ausente: '+work);
  }
  for (const [path, html] of pages) {
    assert.doesNotMatch(html, /<script|onclick=|onload=/i, `Página não estática: ${path}`);
  }
});

test('SSG fails closed on lineage and snapshot errors', () => {
  const wrong=clone(ancestry);
  wrong.matrix_git_blob_sha1='a'.repeat(40);
  assert.throws(()=>archivePages(feed,wrong), /matriz imutável/);
  const missing=clone(ancestry);
  missing.citation_lineages.pop();
  assert.throws(()=>archivePages(feed,missing), /Genealogia ausente/);
  // Adversary: a new dependency for a non-curated source must not be ignored.
  const orphan=clone(ancestry);
  orphan.citation_lineages.push({
    ...clone(ancestry.citation_lineages[0]),
    source_id:'SYNTHETIC_SOURCE_NOT_IN_CURATED_CITATIONS',
    declared_upstream_paths:[],
  });
  assert.throws(()=>archivePages(feed,orphan), /Genealogia órfã/);
  // Positive control: the unmodified one-to-one corpus is accepted.
  assert.doesNotThrow(()=>archivePages(feed,ancestry));
  const confused=clone(ancestry);
  confused.citation_lineages[0].family_id='OTHER';
  assert.throws(()=>archivePages(feed,confused), /Família divergente/);
  const fakeEvent=clone(feed);
  fakeEvent.records[0].not_a_verified_conde_physical_event=false;
  assert.throws(()=>archivePages(fakeEvent,ancestry), /true/);
});

test('SSG rejects source URL injection and unintended omissions',()=>{
  const malicious=clone(feed);
  malicious.records[0].citation_url='javascript:alert(1)';
  assert.throws(()=>archivePages(malicious,ancestry), /HTTPS/);
  const omitted=clone(feed);
  omitted.records=omitted.records.slice(1);
  assert.throws(()=>archivePages(omitted,ancestry), /Cobertura curada divergente/);
});

test('SSG rejects circular genealogy, including non-adjacent ancestry loops', () => {
  const cyclic=clone(ancestry);
  const item=cyclic.citation_lineages.find(x=>x.declared_upstream_paths.length);
  assert.ok(item, 'Corpus requires a declared source dependency');
  const origin=item.source_id;
  item.declared_upstream_paths[0]={
    upstream_source_id:origin,
    edges:[
      {from:origin,to:'SYNTHETIC_INTERMEDIARY',kind:'transcribes'},
      {from:'SYNTHETIC_INTERMEDIARY',to:origin,kind:'reprints'},
    ],
  };
  assert.throws(()=>archivePages(feed,cyclic), /Ciclo de proveniência documental/);

  // Positive control: a new two-hop dependency with distinct nodes is permitted.
  const acyclic=clone(ancestry);
  const valid=acyclic.citation_lineages.find(x=>x.declared_upstream_paths.length);
  const start=valid.source_id;
  valid.declared_upstream_paths[0]={
    upstream_source_id:'SYNTHETIC_UPSTREAM',
    edges:[
      {from:start,to:'SYNTHETIC_INTERMEDIARY',kind:'transcribes'},
      {from:'SYNTHETIC_INTERMEDIARY',to:'SYNTHETIC_UPSTREAM',kind:'reprints'},
    ],
  };
  assert.doesNotThrow(()=>archivePages(feed,acyclic));
});

test('SSG rejects unsafe or ambiguous family identifiers', () => {
  const changed=clone(feed);
  changed.records[0].source_family='RADIO_TUPI_FBIS/../../escape';
  const linked=clone(ancestry);
  linked.citation_lineages.find(x=>x.snapshot_ref===changed.records[0].snapshot_ref
    && x.source_id===changed.records[0].source_id).family_id=changed.records[0].source_family;
  assert.throws(()=>archivePages(changed,linked), /Identificador de família inválido/);
});

test('SSG exposes a verified Wayback PDF only via an exact frozen citation join', () => {
  const graph=JSON.parse(readFileSync('public/data/conde-wayback-citation-links.json','utf8'));
  const pages=archivePages(feed,ancestry,graph);
  for (const id of ['c197-1/index.md','c198-1/index.md']) {
    const page=pages.get(id);
    assert.match(page,/PDF preservado no Wayback \(2015-02-17 13:30:01 UTC\)/);
    assert.match(page,/0f27ed20f8428e44e8dd1f5d4e932661b01a0f8188aaddcae1360ea128336674/);
    assert.match(page,/3 captura\(s\) do mesmo PDF/);
    assert.match(page,/não equivale a nova observação de 1963/);
  }
  assert.doesNotMatch(pages.get('c01-1/index.md'),/PDF preservado no Wayback/);
  assert.match(pages.get('c197-1/index.md'),/Abrir documento original/);
  const corrupt=clone(graph);
  corrupt.nodes.find(n=>n.kind==='VERIFIED_ARCHIVAL_COPY'
    && n.id.includes('LEGACY-CAPTURE')).retrieved_bytes_sha256='0'.repeat(64);
  assert.throws(()=>archivePages(feed,ancestry,corrupt),/Bytes Wayback divergentes/);
  const wrong=clone(graph);
  wrong.matrix_git_blob_sha1='f'.repeat(40);
  assert.throws(()=>archivePages(feed,ancestry,wrong),/snapshot exato/);
  const rogue=clone(graph);
  rogue.edges=rogue.edges.filter(e=>!e.kind.includes('SAME_SSR_WORK'));
  assert.throws(()=>archivePages(feed,ancestry,rogue),/único payload/);
  const tampered=clone(graph);
  tampered.nodes.find(n=>n.kind==='VERIFIED_ARCHIVAL_COPY'
    && n.id.includes('LEGACY-CAPTURE')).archived_url='javascript:alert(1)';
  assert.throws(()=>archivePages(feed,ancestry,tampered),/Somente URL Wayback/);
});

test('SSG rejects forged or path-like work IDs before creating links',()=>{
  const changed=clone(feed);
  changed.records[0].work_id='NASA/../../outside';
  assert.throws(()=>archivePages(changed,ancestry),/Identificador de obra inválido/);
  const alternate=clone(feed);
  alternate.records[0].work_id='NASA <script>';
  assert.throws(()=>archivePages(alternate,ancestry),/Identificador de obra inválido/);
});

test('SSG rejects unsafe source identifiers before generating source URLs',()=>{
  const mutated=clone(feed);
  mutated.records[0].source_id='NASA/../../escape';
  assert.throws(()=>archivePages(mutated,ancestry),/Genealogia ausente|Identificador de fonte inválido/);
});

test('UX-04: every citation has a round-trip path to its matrix row and original', () => {
  const pages=archivePages(feed, ancestry);
  const used=new Set();
  for(const r of feed.records){
    const occurrence=r.occurrence.toLowerCase().replace('#','-');
    const slug=value=>value.toLowerCase().replaceAll('_','-');
    const routes={
      occurrence:occurrence+'/index.md',
      source:'fontes/'+slug(r.source_id)+'/index.md',
      work:'obras/'+slug(r.work_id)+'/index.md',
      family:'familias/'+slug(r.source_family)+'/index.md',
    };
    const detail=pages.get(routes.occurrence);
    assert.ok(detail.includes('/fontes/'+slug(r.source_id)+'/'), 'Fonte sem ida: '+r.occurrence);
    assert.ok(detail.includes('/obras/'+slug(r.work_id)+'/'), 'Obra sem ida: '+r.occurrence);
    assert.ok(detail.includes('/familias/'+slug(r.source_family)+'/'), 'Família sem ida: '+r.occurrence);
    assert.ok(detail.includes(r.row_sha256), 'SHA da linha não visível: '+r.occurrence);
    assert.ok(detail.includes('#L'+r.matrix_line+')'), 'Referência não aponta para sua linha: '+r.occurrence);
    assert.ok(detail.includes(r.citation_url), 'Original não alcançável: '+r.occurrence);
    for(const [type,path] of Object.entries(routes)){
      assert.ok(pages.has(path), 'Destino inexistente: '+path);
      if(type!=='occurrence'){
        const reverse=pages.get(path);
        assert.ok(reverse.includes('/'+occurrence+'/'), 'Sem retorno da '+type+': '+r.occurrence);
      }
    }
    used.add(r.occurrence);
  }
  const multiple=[...used].filter(id=>feed.records.filter(r=>r.occurrence===id).length>1);
  assert.ok(multiple.length>0, 'Corpus sem controle positivo de múltiplas referências');
  for(const id of multiple){
    const page=pages.get(id.toLowerCase().replace('#','-')+'/index.md');
    for(const r of feed.records.filter(r=>r.occurrence===id))
      assert.ok(page.includes('/fontes/'+r.source_id.toLowerCase().replaceAll('_','-')+'/'),
        'Fonte de referência múltipla perdida: '+id);
  }
});

test('UX-04: every curated canonical state has legible, non-probabilistic reading', () => {
  const pages=archivePages(feed, ancestry);
  const index=pages.get('index.md');
  assert.match(index,/Como interpretar os estados documentais/);
  assert.match(index,/nunca de observações físicas independentes/);
  for (const record of feed.records) {
    const {label,support,limit}=interpretArchiveStatus(record.source_status);
    const route=record.occurrence.toLowerCase().replace('#','-')+'/index.md';
    const detail=pages.get(route);
    for (const piece of [label,support,limit]) {
      assert.ok(detail.includes(piece), 'Leitura ausente na ocorrência: '+route+' '+piece);
      assert.ok(index.includes(piece), 'Leitura ausente no índice: '+piece);
    }
    assert.ok(detail.includes(record.source_status), 'Código canônico removido');
  }
  assert.match(pages.get('c197-1/index.md'),/Data catalogada, sem local de queda/);
  assert.match(pages.get('c179-1/index.md'),/Espelho de elementos orbitais não autenticado/);
  const unknown=clone(feed);
  unknown.records[0].source_status='UNREVIEWED_INSTRUMENTAL_OBSERVATION';
  assert.throws(()=>archivePages(unknown,ancestry),/sem leitura editorial revisada/);
  assert.throws(()=>interpretArchiveStatus('__proto__'),/sem leitura editorial revisada/);
});


test('chapter 03 keeps FBIS and NASA as separate, reversible documentary journeys', () => {
  const chapter=readFileSync('stories/2026-11-12-a-resposta-que-veio-de-salvador.md','utf8');
  const pages=archivePages(feed,ancestry);
  for (const [occurrence,anchor,label] of [
    ['C01#1','contexto-fbis','a transmissão FBIS'],
    ['C197#1','contexto-nasa','a data no catálogo NASA'],
  ]) {
    const record=feed.records.find(r=>r.occurrence===occurrence);
    assert.ok(record, 'Ocorrência científica ausente: '+occurrence);
    const file=occurrence.toLowerCase().replace('#','-')+'/index.md';
    const toArchive='/conde-incident/evidencias/arquivo/'+file.replace('index.md','');
    const back='/conde-incident/stories/2026-11-12-a-resposta-que-veio-de-salvador/#'+anchor;
    assert.ok(chapter.includes('id="'+anchor+'"'), 'Âncora editorial ausente');
    assert.ok(chapter.includes(']('+toArchive+')'), 'Sem entrada para ocorrência');
    for (const target of [file,
      'fontes/'+record.source_id.toLowerCase().replaceAll('_','-')+'/index.md',
      'obras/'+record.work_id.toLowerCase().replaceAll('_','-')+'/index.md']) {
      const data=pages.get(target);
      assert.ok(data?.includes(']('+back+')'), 'Retorno editorial ausente: '+target);
      assert.ok(data.includes(record.citation_url), 'Original custodiado perdeu link: '+target);
    }
    assert.ok(pages.get(file).includes('SHA-256 da linha na matriz'));
    assert.ok(pages.get(file).includes('Não permite concluir'));
    assert.ok(pages.get(file).includes('Voltar à reportagem: '+label));
  }
  // No unrelated occurrence may acquire a spurious link to this article.
  assert.doesNotMatch(pages.get('c232-1/index.md'),/Voltar à reportagem/);
});

import {loadCondeSourceLookup} from './ssg-source-lookup-loader.mjs';

const PREFIX='/conde-incident/';
const KNOWN_PATH=/^\/conde-incident\/evidencias\/arquivo\/[a-z0-9-]+\/$/;
const EDGE_LABELS=Object.freeze({
  aggregates_from:'agrega dados de',
  catalogue_of_same_work:'cataloga a mesma obra que',
  later_issue_same_series:'é edição posterior da série de',
  part_of_archival_unit:'integra a unidade arquivística',
  quotes_uninspected_source:'cita fonte ainda não inspecionada',
  transcribes:'transcreve',
});

// A link is actionable only if its source ID belongs to the verified index.
export function sourceFromUrl(href,verifiedSources){
  const requested=new URL(href).searchParams.get('source');
  if(requested===null) return {id:'',invalid:false};
  return verifiedSources.has(requested)
    ? {id:requested,invalid:false} : {id:'',invalid:true};
}

export function sourceLookupUrl(href,id){
  const url=new URL(href);
  if(id) url.searchParams.set('source',id);
  else url.searchParams.delete('source');
  return url.pathname+url.search+url.hash;
}

// Mirror the SSG archive's sourceSlug, without trusting an arbitrary URL or ID.
// Every destination is already materialized by the static archive generator.
export function sourceArchiveUrl(id){
  if(typeof id!=='string' || !/^[A-Z][A-Z0-9_]{1,95}$/.test(id))
    throw Error('Identificador de fonte inválido');
  return PREFIX+'evidencias/arquivo/fontes/'+id.toLowerCase().replaceAll('_','-')+'/';
}

export function referenceView(source){
  if(!source || typeof source.source_family!=='string' ||
     !Array.isArray(source.references)) throw Error('Fonte incompatível');
  sourceArchiveUrl(source.source_id);
  return source.references.map(ref=>{
    const expected='/conde-incident/evidencias/arquivo/'+
      String(ref.occurrence).toLowerCase().replace('#','-')+'/';
    if(!KNOWN_PATH.test(ref.archive_path) || !/^C\d+#[1-9]\d*$/.test(ref.occurrence) ||
       ref.archive_path!==expected || !Number.isSafeInteger(ref.matrix_line) ||
       ref.matrix_line<1 || !/^[a-f0-9]{64}$/.test(ref.row_sha256) ||
       !Array.isArray(ref.upstream_edges) || ref.upstream_edges.some(edge=>
         !Array.isArray(edge) || edge.length!==3 || edge[0]!==source.source_id ||
         !/^[a-z][a-z0-9_]*$/.test(edge[1]) ||
         typeof edge[2]!=='string' || !edge[2]))
      throw Error('Referência inválida');
    return {occurrence:ref.occurrence,archive_path:ref.archive_path,
      matrix_line:ref.matrix_line,row_sha256:ref.row_sha256,
      work_id:ref.work_id,snapshot_ref:ref.snapshot_ref,
      upstream_edges:ref.upstream_edges};
  });
}

export async function mountSourceLookup(doc=document, loader=loadCondeSourceLookup){
  const form=doc.getElementById('source-lookup-form');
  const select=doc.getElementById('source-lookup-id');
  const status=doc.getElementById('source-lookup-status');
  const results=doc.getElementById('source-lookup-results');
  const retry=doc.getElementById('source-lookup-retry');
  if(!form || !select || !status || !results || !retry) return;
  let sources=new Map();
  const clear=()=>results.replaceChildren();
  const textElement=(tag,content)=>{
    const element=doc.createElement(tag);
    element.textContent=content;
    return element;
  };
  const render=()=>{
    clear();
    const source=sources.get(select.value);
    if(!source) return;
    const refs=referenceView(source);
    results.append(textElement('h2','Fonte '+source.source_id));
    results.append(textElement('p','Família documental: '+source.source_family+'. '+
      refs.length+' vínculo(s) curado(s), não contagem de observações físicas independentes.'));
    // The static profile carries document URLs, statuses and locators that the
    // compact reverse-index deliberately does not duplicate in its shard.
    const profile=doc.createElement('p');
    const profileLink=doc.createElement('a');
    profileLink.href=sourceArchiveUrl(source.source_id);
    profileLink.textContent='Abrir ficha documental estática de '+source.source_id;
    profile.append(profileLink);
    results.append(profile);
    const list=doc.createElement('ol');
    for(const ref of refs){
      const li=doc.createElement('li');
      const link=doc.createElement('a');
      link.href=ref.archive_path;
      link.textContent='Abrir ocorrência '+ref.occurrence;
      li.append(link,textElement('p','Obra '+ref.work_id+' · Linha da matriz '+ref.matrix_line+
        ' · Snapshot '+ref.snapshot_ref+' · SHA-256 '+ref.row_sha256));
      if(ref.upstream_edges.length){
        li.append(textElement('p','Relações documentais declaradas (não são observações independentes):'));
        const edges=doc.createElement('ul');
        for(const [,kind,target] of ref.upstream_edges){
          const node=doc.createElement('li');
          node.append(textElement('span',(EDGE_LABELS[kind]??'relação '+kind)+': '));
          if(sources.has(target)){
            const a=doc.createElement('a');
            a.href=sourceLookupUrl(doc.location.href,target);
            a.textContent=target;
            node.append(a);
          } else node.append(textElement('span',target+' (fora deste índice curado)'));
          edges.append(node);
        }
        li.append(edges);
      }
      list.append(li);
    }
    results.append(list);
  };
  const updateSelection=()=>{
    render();
    const source=sources.get(select.value);
    status.textContent=source
      ? 'Fonte '+source.source_id+' selecionada: '+source.references.length+' vínculo(s) curado(s).'
      : 'Índice verificado: '+sources.size+' fonte(s) curada(s). Escolha uma fonte.';
  };
  const restoreSelection=()=>{
    const selected=sourceFromUrl(doc.location.href,sources);
    select.value=selected.id;
    updateSelection();
    if(selected.invalid)
      status.textContent='A fonte indicada no link não consta do índice verificado. Escolha uma fonte disponível.';
  };
  select.addEventListener('change',()=>{
    const id=sources.has(select.value)?select.value:'';
    doc.defaultView?.history?.pushState(null,'',sourceLookupUrl(doc.location.href,id));
    updateSelection();
  });
  doc.defaultView?.addEventListener('popstate',restoreSelection);
  async function refresh(){
    form.hidden=true;retry.hidden=true;clear();
    status.textContent='Verificando manifesto, versão da matriz e SHA-256 das fontes…';
    try {
      const data=await loader({baseUrl:new URL(PREFIX,doc.location.origin).href});
      const next=new Map(data.sources.map(s=>[s.source_id,s]));
      // Validate every link before showing any result; partial results are not trustworthy.
      for(const source of next.values()) referenceView(source);
      sources=next;
      select.replaceChildren(textElement('option','Escolha uma fonte'));
      select.options[0].value='';
      for(const source of next.values()){
        const option=textElement('option',source.source_id+' · '+source.source_family);
        option.value=source.source_id;
        select.append(option);
      }
      form.hidden=false;
      restoreSelection();
    } catch {
      sources=new Map();
      status.textContent='Não foi possível verificar a integridade do índice ou a rede. Nenhum resultado foi exibido. Use o arquivo documental estático.';
      retry.hidden=false;
    }
  }
  retry.addEventListener('click',refresh);
  await refresh();
}
if(typeof document!=='undefined') void mountSourceLookup();

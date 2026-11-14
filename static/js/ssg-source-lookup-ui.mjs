import {loadCondeSourceLookup} from './ssg-source-lookup-loader.mjs';

const PREFIX='/conde-incident/';
const KNOWN_PATH=/^\/conde-incident\/evidencias\/arquivo\/[a-z0-9-]+\/$/;

export function referenceView(source){
  if(!source || typeof source.source_id!=='string' ||
     typeof source.source_family!=='string' || !Array.isArray(source.references))
    throw Error('Fonte incompatível');
  return source.references.map(ref=>{
    if(!KNOWN_PATH.test(ref.archive_path) || !/^C\d+#\d+$/.test(ref.occurrence) ||
       !Number.isInteger(ref.matrix_line) || !/^[a-f0-9]{64}$/.test(ref.row_sha256))
      throw Error('Referência inválida');
    return {occurrence:ref.occurrence,archive_path:ref.archive_path,
      matrix_line:ref.matrix_line,row_sha256:ref.row_sha256,
      work_id:ref.work_id,snapshot_ref:ref.snapshot_ref};
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
    const list=doc.createElement('ol');
    for(const ref of refs){
      const li=doc.createElement('li');
      const link=doc.createElement('a');
      link.href=ref.archive_path;
      link.textContent='Abrir ocorrência '+ref.occurrence;
      li.append(link,textElement('p','Obra '+ref.work_id+' · Linha da matriz '+ref.matrix_line+
        ' · Snapshot '+ref.snapshot_ref+' · SHA-256 '+ref.row_sha256));
      list.append(li);
    }
    results.append(list);
  };
  select.addEventListener('change',render);
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
      status.textContent='Índice verificado: '+next.size+' fonte(s) curada(s). Escolha uma fonte.';
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

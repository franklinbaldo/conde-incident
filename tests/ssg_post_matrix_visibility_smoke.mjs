// G75: test CSS-computed custody fields on the actual SSG page, not HTML alone.
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {readFileSync} from 'node:fs';
import {chromium} from 'playwright';

const citations=JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
const rows=citations.post_matrix_occurrences;
assert.ok(Array.isArray(rows)&&rows.length>0,'post-matrix rows were not discovered');
const records=[...rows].sort((a,b)=>a.id.localeCompare(b.id,'en')).map(item=>({
  id:item.id,
  fields:[
    ['Estado canônico',item.status],
    ['Independência jornalística',item.journalistic_source_independence],
    ['SHA-256 da imagem arquivística',item.image_sha256],
    ['SHA-256 do relatório de custódia versionado',
      createHash('sha256').update(readFileSync(item.report_path)).digest('hex')],
  ],
  sources:[
    item.report_citation_url,
    'https://github.com/franklinbaldo/conde-incident/blob/main/'+item.report_path,
  ],
}));
const root=(process.env.UI_AUDIT_SSG_URL||'http://127.0.0.1:4173/conde-incident/').replace(/\/?$/,'/');
const url=new URL('evidencias/arquivo/pos-matriz/',root).href;

async function verifyVisible(page){
  return page.evaluate(({records})=>{
    const main=document.querySelector('main');
    if(!main) throw new Error('main não presente');
    const headings=[...main.querySelectorAll('h3')];
    if(headings.length!==records.length)
      throw new Error('cabeçalhos pós-matriz divergentes: '+headings.length+' / '+records.length);
    const text=el=>el?.textContent?.replace(/\s+/g,' ').trim()??'';
    const follows=(a,b)=>Boolean(a.compareDocumentPosition(b)&Node.DOCUMENT_POSITION_FOLLOWING);
    const visible=(el,context)=>{
      if(!el||!el.checkVisibility({checkOpacity:true,checkVisibilityCSS:true}))
        throw new Error(context+': invisível no CSS/DOM calculado');
      const box=el.getBoundingClientRect();
      if(box.width<1||box.height<1||box.right<=0||box.left>=innerWidth)
        throw new Error(context+': invisível fora da área horizontal');
    };
    let fields=0,links=0;
    for(let i=0;i<records.length;i++){
      const item=records[i],h=headings[i],next=headings[i+1];
      if(text(h)!==item.id) throw new Error('identidade do cabeçalho divergente: '+item.id);
      visible(h,'cabeçalho '+item.id);
      const between=el=>follows(h,el)&&(!next||follows(el,next));
      const strongs=[...main.querySelectorAll('strong')].filter(between);
      for(const [label,value] of item.fields){
        const matches=strongs.filter(el=>text(el)===label+':');
        if(matches.length!==1)throw new Error('cardinalidade de rótulo: '+item.id+' / '+label);
        const strong=matches[0],code=strong.nextElementSibling;
        if(!code||code.tagName!=='CODE'||code.parentElement!==strong.parentElement||
           text(code)!==value||!between(code))
          throw new Error('par rótulo/valor divergente: '+item.id+' / '+label);
        visible(strong,'rótulo '+item.id+' / '+label);
        visible(code,'valor '+item.id+' / '+label);
        fields++;
      }
      const anchors=[...main.querySelectorAll('a[href]')].filter(between);
      for(const href of item.sources){
        const matches=anchors.filter(el=>el.getAttribute('href')===href);
        if(matches.length!==1)throw new Error('cardinalidade do link '+item.id+' / '+href);
        visible(matches[0],'link '+item.id+' / '+href);
        links++;
      }
    }
    if(document.styleSheets.length<1)throw new Error('nenhuma folha de estilo carregada');
    if(document.documentElement.scrollWidth>innerWidth+1)
      throw new Error('overflow horizontal: '+document.documentElement.scrollWidth+' > '+innerWidth);
    return {rows:records.length,fields,links,styleSheets:document.styleSheets.length};
  },{records});
}
const browser=await chromium.launch({headless:true});
try{
  for(const width of [320,375,1440]){
    const page=await browser.newPage({viewport:{width,height:850},reducedMotion:'reduce'});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    const response=await page.goto(url,{waitUntil:'networkidle',timeout:30000});
    assert.ok(response?.ok(),'post-matrix HTTP '+response?.status());
    const before=await verifyVisible(page);
    assert.deepEqual(errors,[],'browser JS errors');

    // The historical HTML-only auditor does not evaluate computed styles.
    // Each synthetic mutation MUST fail this browser gate.
    for(const css of [
      'main strong{display:none!important}',
      'main code{opacity:0!important}',
      'main strong{visibility:hidden!important}',
      'main code{position:absolute!important;left:-99999px!important}',
    ]){
      await page.evaluate(css=>{const sheet=new CSSStyleSheet();sheet.replaceSync(css);document.adoptedStyleSheets=[...document.adoptedStyleSheets,sheet];},css);
      await assert.rejects(()=>verifyVisible(page),/invisível/,'CSS mutation survived: '+css);
      await page.evaluate(()=>{document.adoptedStyleSheets=document.adoptedStyleSheets.slice(0,-1)});
      await verifyVisible(page);
    }
    console.log(JSON.stringify({width,url,...before,cssMutantsRejected:4,errors:errors.length}));
    await page.close();
  }
}finally{
  await browser.close();
}

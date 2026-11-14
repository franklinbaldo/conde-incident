import assert from 'node:assert/strict';
import {chromium} from 'playwright';

const base=process.env.SSG_SEARCH_AUDIT_URL||'http://127.0.0.1:4173/conde-incident/';
const url=new URL('evidencias/fontes/',base).href;
const browser=await chromium.launch({headless:true});
try {
  for(const width of [320,390,1440]){
    const page=await browser.newPage({viewport:{width,height:720}});
    const errors=[];
    page.on('pageerror',error=>errors.push(error.message));
    try {
      const response=await page.goto(url,{waitUntil:'networkidle'});
      assert(response?.ok(),'Reverse source page must be generated on this HEAD');
      const form=page.locator('#source-lookup-form');
      await page.waitForFunction(()=>{const s=document.querySelector('#source-lookup-status')?.textContent||''; return s.includes('Índice verificado')||s.includes('Não foi possível verificar');});
      assert.equal(await form.isVisible(),true,'O formulário não abriu: '+await page.locator('#source-lookup-status').innerText());
      assert.match(await page.locator('#source-lookup-status').innerText(),/Índice verificado/);
      const selector=page.getByLabel('Fonte documental');
      // A reverse-lookup page should expose its primary control without scrolling on mobile.
      const rect=await selector.boundingBox();
      assert(rect && rect.y>=0 && rect.y+rect.height<=720,
        'Fonte documental control below first 720px viewport at '+width+'px: '+JSON.stringify(rect));
      assert.equal(await selector.locator('option').count(),16,'15 curated sources plus prompt');
      await selector.selectOption({index:1});
      const selected=await selector.inputValue();
      assert.equal(new URL(page.url()).searchParams.get('source'),selected,
        'source selection must be shareable');
      await page.reload({waitUntil:'networkidle'});
      assert.equal(await selector.inputValue(),selected,
        'verified deep link must restore the selection');
      await page.goBack({waitUntil:'networkidle'});
      assert.equal(await selector.inputValue(),'',
        'browser Back must restore the previous selection');
      await page.goForward({waitUntil:'networkidle'});
      assert.equal(await selector.inputValue(),selected,
        'browser Forward must restore the verified selection');
      const entries=page.locator('#source-lookup-results li');
      assert((await entries.count())>0,'no occurrence rendered');
      const link=entries.first().getByRole('link',{name:/Abrir ocorrência/});
      const href=await link.getAttribute('href');
      assert.match(href,/^\/conde-incident\/evidencias\/arquivo\/c\d+-\d+\/$/);
      const details=await entries.first().innerText();
      assert.match(details,/SHA-256 [a-f0-9]{64}/);
      assert.match(details,/Linha da matriz/);
      await link.click();
      await page.waitForURL(new RegExp(href.replaceAll('/','\\/')));
      assert.match(await page.locator('main').innerText(),/ocorrência|evidência|arquivo/i);
      await page.goBack({waitUntil:'networkidle'});
      await page.locator('#source-lookup-form').waitFor({state:'visible'});
      assert.equal(await page.evaluate(()=>document.documentElement.scrollWidth<=innerWidth+1),true,
        'source lookup has horizontal overflow at '+width+'px');
      assert.deepEqual(errors,[],'script errors');
    } finally {await page.close();}
  }
  const invalid=await browser.newPage();
  try {
    await invalid.goto(url+'?source=%3Cscript%3E',{waitUntil:'networkidle'});
    assert.equal(await invalid.locator('#source-lookup-form').isVisible(),true);
    assert.equal(await invalid.locator('#source-lookup-id').inputValue(),'');
    assert.match(await invalid.locator('#source-lookup-status').innerText(),/não consta do índice verificado/);
    assert.equal(await invalid.locator('#source-lookup-results a').count(),0);
  } finally {await invalid.close();}
  const broken=await browser.newPage();
  try{
    await broken.route('**/data/conde-source-lookup-manifest.json',route=>route.fulfill({status:200,
      contentType:'application/json',body:'{"schema":"tampered"}'}));
    await broken.goto(url,{waitUntil:'networkidle'});
    assert.equal(await broken.locator('#source-lookup-form').isVisible(),false,
      'tampered pointer must not enable unverified UI');
    assert.match(await broken.locator('#source-lookup-status').innerText(),/Não foi possível verificar/);
    assert.equal(await broken.locator('#source-lookup-results a').count(),0);
    assert.equal(await broken.getByRole('link',{name:/arquivo documental estático/i}).count(),1);
  } finally {await broken.close();}
  const noJs=await browser.newContext({javaScriptEnabled:false});
  try {
    const page=await noJs.newPage();
    await page.goto(url,{waitUntil:'domcontentloaded'});
    assert.equal(await page.locator('#source-lookup-form').isVisible(),false);
    assert.equal(await page.getByRole('link',{name:/arquivo documental estático/i}).count(),1);
  } finally {await noJs.close();}
} finally {await browser.close();}

import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';

// SSG 0.0.75 emits its own CSP for page layouts. The Markdown article contains
// two tightly scoped external document/map iframes. Amend only this generated
// article; do not weaken script-src or the site-wide policy.
const file='public/stories/2026-11-12-a-resposta-que-veio-de-salvador/index.html';
let html=readFileSync(file,'utf8');
for(const required of [
  'https://www.openstreetmap.org/export/embed.html',
  'https://media.ondisclosure.org/web/official-uap/pursue/release-05/'
]) assert.ok(html.includes(required),'Iframe nao encontrado: '+required);
const csp=/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/;
const match=csp.exec(html);
assert.ok(match,'CSP original do SSG ausente');
assert.ok(!match[1].includes('frame-src'),'CSP do SSG mudou: reavaliar integracao');
const allow='frame-src https://www.openstreetmap.org https://media.ondisclosure.org';
const replacement=match[0].replace(match[1],match[1].replace(/;?\s*$/, '; ')+allow+';');
html=html.replace(match[0],replacement);
assert.ok(html.includes(allow));
writeFileSync(file,html);
console.log('PASS: CSP restrita do capitulo 03 autoriza mapa e fac-simile embutidos.');

 
// A primary 1963 newspaper page is embedded in chapter 05. This exception
// applies to that page only; the original document also remains a direct link.
const newspaper='public/stories/2026-11-12-o-humorista-que-encontrou-um-satelite-na-redacao/index.html';
let paperHtml=readFileSync(newspaper,'utf8');
const requiredPaper='https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00477.pdf';
assert.ok(paperHtml.includes(requiredPaper),'Hemeroteca original ausente do capitulo 05');
const paperMatch=csp.exec(paperHtml);
assert.ok(paperMatch,'CSP original da pagina 05 ausente');
assert.ok(!paperMatch[1].includes('frame-src'),'CSP de pagina 05 mudou: auditar regra');
const paperAllow='frame-src https://hemeroteca-pdf.bn.gov.br';
paperHtml=paperHtml.replace(paperMatch[0],paperMatch[0].replace(paperMatch[1],paperMatch[1].replace(/;?\s*$/, '; ')+paperAllow+';'));
assert.ok(paperHtml.includes(paperAllow));
writeFileSync(newspaper,paperHtml);
console.log('PASS: CSP restrita do capitulo 05 autoriza apenas a Hemeroteca em iframe.');

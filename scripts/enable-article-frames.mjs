import { localizeGeneratedPages } from './localize-ssg-search.mjs';
import { localizeRuntime } from './localize-ssg-search-runtime.mjs';
import { markGeneratedNavigation } from './mark-editorial-nav.mjs';
import assert from 'node:assert/strict';
import {readFileSync,writeFileSync} from 'node:fs';

// SSG 0.0.75 emits its own CSP for page layouts. The Markdown article contains
// one tightly scoped external documentary PDF iframe. Amend only this generated
// article; do not weaken script-src or the site-wide policy.
const file='public/stories/2026-11-12-a-resposta-que-veio-de-salvador/index.html';
let html=readFileSync(file,'utf8');
for(const required of [
  'https://media.ondisclosure.org/web/official-uap/pursue/release-05/'
]) assert.ok(html.includes(required),'Iframe nao encontrado: '+required);
const csp=/<meta http-equiv="Content-Security-Policy" content="([^"]+)">/;
const match=csp.exec(html);
assert.ok(match,'CSP original do SSG ausente');
assert.ok(!match[1].includes('frame-src'),'CSP do SSG mudou: reavaliar integracao');
const allow='frame-src https://media.ondisclosure.org';
const replacement=match[0].replace(match[1],match[1].replace(/;?\s*$/, '; ')+allow+';');
html=html.replace(match[0],replacement);
assert.ok(html.includes(allow));
writeFileSync(file,html);
console.log('PASS: CSP restrita do capitulo 03 autoriza somente fac-simile PDF embutido.');

 
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


// Chapter 07 embeds only the official NORAD 1963 fac-simile. No wildcard host.
const camerasFile='public/stories/2026-11-12-as-cameras-que-o-norad-nao-ganhou/index.html';
let camerasHtml=readFileSync(camerasFile,'utf8');
const camerasUrl='https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/11.pdf#page=3';
assert.ok(camerasHtml.includes(camerasUrl),'Fac-simile NORAD 1963 ausente do capitulo 07');
const camerasCsp=csp.exec(camerasHtml);
assert.ok(camerasCsp,'CSP da pagina 07 ausente');
assert.ok(!camerasCsp[1].includes('frame-src'),'Nova frame-src de pagina 07 requer reavaliacao');
const camerasAllow='frame-src https://nsarchive.gwu.edu';
camerasHtml=camerasHtml.replace(camerasCsp[0],
  camerasCsp[0].replace(camerasCsp[1],camerasCsp[1].replace(/;?\s*$/, '; ')+camerasAllow+';'));
assert.ok(camerasHtml.includes(camerasAllow));
writeFileSync(camerasFile,camerasHtml);
console.log('PASS: CSP restrita do capitulo 07 permite so o fac-simile NORAD.');

// The same post-SSG integration step localizes its built-in search UI.
// Static labels and the generated client search use the same pt-BR locale.
// The runtime is versioned afresh and all HTML integrity attributes updated.
localizeGeneratedPages();
localizeRuntime();

// Identify the active editorial section on every generated SSG page.
markGeneratedNavigation();

import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
const html = path => readFileSync(join('public',path),'utf8');
const home=html('index.html'), listing=html('stories/index.html'), lab=html('lab/index.html');
assert.match(home,/\/conde-incident\/lab\//,'missing lab URL');
assert.match(home,/\/conde-incident\/lab\/#\/map/,'missing copyable map URL');
assert.match(home,/href="#conteudo"/,'missing keyboard skip link');
assert.match(home,/rel="canonical"/,'missing canonical URL');
assert.match(home,/\/conde-incident\/stories\//,'missing journal URL');
assert.match(lab,/\/conde-incident\/lab\/assets\//,'Vite base must be /lab/');
assert.doesNotMatch(lab,/(?:src|href)="\/assets\//,'root asset path is wrong');
assert.ok(existsSync('public/lab/assets'),'no lab bundles copied');
for(const name of readdirSync('stories').filter(s => /^\d{4}-\d{2}-\d{2}-.+\.md$/.test(s))) {
  const slug=name.slice(0,-3);
  const article=html(join('stories',slug,'index.html'));
  assert.ok(listing.includes(slug),'chapter missing in listing: '+name);
  assert.ok(article.includes('<article'),'chapter did not render: '+name);
  assert.ok(article.includes('id="conteudo"'),'chapter missing main landmark: '+name);
  assert.ok(article.includes('evidence_matrix_C001-C238_2026-11-11.md'),'chapter missing matrix snapshot: '+name);
  assert.ok(article.includes('/lab/#/map'),'chapter missing deep link to map: '+name);
  assert.ok(article.includes('/lab/#/research'),'chapter missing functional Evidence link: '+name);
  assert.ok(article.includes('sem hora ou coordenadas') || article.includes('não há hora ou coordenadas'),'chapter must not present an unsupported terminal point: '+name);
  assert.ok(article.includes('og:type" content="article"'),'chapter missing article social metadata: '+name);
  assert.ok(article.includes('rel="canonical" href="'+ 'https://franklinbaldo.github.io/conde-incident/stories/'+slug+'/'),'chapter canonical missing or points elsewhere: '+name);
}
console.log('Zola stories, lab and /conde-incident/ paths verified.');

import assert from 'node:assert/strict';
import {readFileSync,readdirSync,existsSync} from 'node:fs';
import {join} from 'node:path';
const html = path => readFileSync(join('public',path),'utf8');
const home=html('index.html'), listing=html('stories/index.html'), lab=html('lab/index.html');
assert.match(home,/\/conde-incident\/lab\//,'missing lab URL');
assert.match(home,/\/conde-incident\/stories\//,'missing journal URL');
assert.match(lab,/\/conde-incident\/lab\/assets\//,'Vite base must be /lab/');
assert.doesNotMatch(lab,/(?:src|href)="\/assets\//,'root asset path is wrong');
assert.ok(existsSync('public/lab/assets'),'no lab bundles copied');
for(const name of readdirSync('stories').filter(s => /^\d{4}-\d{2}-\d{2}-.+\.md$/.test(s))) {
  const slug=name.slice(0,-3);
  const article=html(join('stories',slug,'index.html'));
  assert.ok(listing.includes(slug),'chapter missing in listing: '+name);
  assert.ok(article.includes('<article'),'chapter did not render: '+name);
}
console.log('Zola stories, lab and /conde-incident/ paths verified.');

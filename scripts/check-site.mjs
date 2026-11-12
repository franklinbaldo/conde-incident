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
const chapters = readdirSync('stories')
  .filter(s => /^\d{4}-\d{2}-\d{2}-.+\.md$/.test(s))
  .map(name => {
    const source = readFileSync(join('stories', name), 'utf8');
    const chapter = /(?:^|\n)chapter:\s*["']?(\d+)/.exec(source);
    assert.ok(chapter, 'missing chapter number in ' + name);
    return {name, slug: name.slice(0, -3), number: Number(chapter[1])};
  }).sort((a, b) => a.number - b.number);
const publicStories = 'https://franklinbaldo.github.io/conde-incident/stories/';
for (const [index, {name, slug}] of chapters.entries()) {
  const article=html(join('stories',slug,'index.html'));
  assert.ok(listing.includes(slug),'chapter missing in listing: '+name);
  assert.ok(article.includes('<article'),'chapter did not render: '+name);
  assert.ok(article.includes('id="conteudo"'),'chapter missing main landmark: '+name);
  assert.ok(article.includes('evidence_matrix_C001-C238_2026-11-11.md'),'chapter missing matrix snapshot: '+name);
  assert.ok(article.includes('/lab/#/map'),'chapter missing deep link to map: '+name);
  assert.ok(article.includes('/lab/#/research'),'chapter missing functional Evidence link: '+name);
  assert.ok(article.includes('/lab/#/research/c01'),'chapter missing evidence occurrence permalink C01: '+name);
  assert.ok(article.includes('/lab/#/research/c197'),'chapter missing evidence occurrence permalink C197: '+name);
  assert.ok(article.includes('sem hora ou coordenadas') || article.includes('não há hora ou coordenadas'),'chapter must not present an unsupported terminal point: '+name);
  assert.ok(article.includes('og:type" content="article"'),'chapter missing article social metadata: '+name);
  assert.ok(article.includes('property="article:published_time" content="'+name.slice(0,10)+'"'),
    'chapter missing publication date metadata: '+name);
  assert.ok(article.includes('<nav class="story-toc" aria-label="Índice da reportagem">'),
    'chapter missing native keyboard-accessible table of contents: '+name);
  const toc = article.split('<nav class="story-toc"')[1]?.split('</nav>')[0] ?? '';
  assert.ok(toc.includes('<details>') && toc.includes('<summary>'),
    'chapter TOC must use native disclosure controls: '+name);
  const renderedBody = article.split('<div class="story-body">')[1] ?? '';
  assert.doesNotMatch(renderedBody, /^\s*<h1\b/,
    'Markdown repeated the page title as a second H1: '+name);
  const targetIds = new Set([...article.matchAll(/<h[2-6]\b[^>]*\bid="([^"]+)"/g)].map(m => m[1]));
  const tocIds = [...toc.matchAll(/href="[^"]*#([^"]+)"/g)].map(m => decodeURIComponent(m[1]));
  assert.ok(tocIds.length > 0, 'chapter TOC missing Markdown heading links: '+name);
  for(const id of tocIds) {
    assert.ok(targetIds.has(id), 'chapter TOC fragment without heading target: '+name+'#'+id);
  }
  assert.ok(article.includes('<nav class="story-chapter-nav" aria-label="Continuar lendo o Caderno">'),
    'chapter missing sequential reading landmark: '+name);
  const previous = chapters[index-1], next = chapters[index+1];
  const previousLink = previous ? 'rel="prev" href="'+publicStories+previous.slug+'/"' : 'rel="prev"';
  const nextLink = next ? 'rel="next" href="'+publicStories+next.slug+'/"' : 'rel="next"';
  assert.equal(article.includes(previousLink), !!previous,
    'wrong or missing previous chapter link: '+name);
  assert.equal(article.includes(nextLink), !!next,
    'wrong or missing next chapter link: '+name);

  assert.ok(article.includes('rel="canonical" href="'+ 'https://franklinbaldo.github.io/conde-incident/stories/'+slug+'/'),'chapter canonical missing or points elsewhere: '+name);
}
console.log('Zola stories, lab and /conde-incident/ paths verified.');

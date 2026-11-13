import test from 'node:test';
import assert from 'node:assert/strict';
import { mkdtempSync, mkdirSync, readFileSync, writeFileSync, rmSync, existsSync } from 'node:fs';
import { tmpdir } from 'node:os';
import { join } from 'node:path';
import { createHash } from 'node:crypto';
import { localizeRuntime, localizeRuntimeSource } from '../scripts/localize-ssg-search-runtime.mjs';

// The four dynamic strings are copied from the pinned SSG runtime. The
// fixture also exercises path rewrites, exact SRI and a second idempotent run.
const source = "var results=document.getElementById('ssg-search-results');\n" +
  "results.innerHTML='<div class=\"ssg-no-results\" role=\"status\">No results for “&ldquo;'+esc(q)+'&rdquo;”</div>';\n" +
  "sr.textContent='No results found';\n" +
  "sr.textContent=hits.length+' result'+(hits.length===1?'':'s')+' found';\n" +
  "function close(){overlay.classList.remove('active');active=-1}\n" +
  "btn.addEventListener('click',function(){open()});\n" +
  "if(e.key==='Escape')close();\n" +
  "if(e.key==='Enter'){e.preventDefault();var items=results.querySelectorAll('.ssg-result');}\n";
const sha384 = text => 'sha384-' + createHash('sha384').update(text).digest('base64');
test('Full dynamic locale: visible empty state, announcements for zero and N results', () => {
  const result = localizeRuntimeSource(source);
  assert.equal(result.changed, true);
  assert.match(result.code, /Nenhum resultado para &ldquo;/);
  assert.match(result.code, /Nenhum resultado encontrado/);
  assert.match(result.code, /resultado.*encontrado/);
  assert.doesNotMatch(result.code, /No results| result'| found/);
  assert.match(result.code, /ssg-search-close/);
  assert.match(result.code, /btn\.focus\(\)/);
  assert.match(result.code, /e\.key==='Tab'/);
  assert.match(result.code, /document\.activeElement/);
  assert.match(result.code, /e\.target!==closeBtn/);
  assert.deepEqual(localizeRuntimeSource(result.code), { ...result, changed: false });
  assert.throws(() => localizeRuntimeSource(source.replace('No results found', 'No matches')),
    /runtime drift/);
});
test('Real HTML links and SHA384 remain valid after versioned asset rewrite', () => {
  const root = mkdtempSync(join(tmpdir(), 'conde-search-'));
  try {
    mkdirSync(join(root, '_csp'));
    const oldName = '123456789abcdef0.js';
    writeFileSync(join(root, '_csp', oldName), source);
    for (const path of ['index.html', 'stories.html', 'arquivo.html']) {
      const html = '<html lang="pt-BR"><div id="ssg-search-widget"></div>' +
        '<script src="/conde-incident/_csp/' + oldName + '" integrity="' +
        sha384(source) + '" crossorigin="anonymous"></script></html>';
      writeFileSync(join(root, path), html);
    }
    const result = localizeRuntime({ root });
    assert.equal(result.pages, 3);
    assert.equal(result.changed, true);
    assert.ok(!existsSync(join(root, '_csp', oldName)));
    const asset = readFileSync(join(root, '_csp', result.asset), 'utf8');
    assert.match(asset, /Nenhum resultado encontrado/);
    for (const page of ['index.html', 'stories.html', 'arquivo.html']) {
      const html = readFileSync(join(root, page), 'utf8');
      assert.ok(html.includes(result.asset));
      assert.ok(html.includes('integrity="' + sha384(asset) + '"'));
      assert.ok(!html.includes(oldName));
    }
    const repeated = localizeRuntime({ root, check: true });
    assert.equal(repeated.changed, false);
    assert.equal(repeated.asset, result.asset);
  } finally { rmSync(root, { recursive: true, force: true }); }
});

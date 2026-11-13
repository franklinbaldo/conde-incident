import assert from 'node:assert/strict';
import { createHash } from 'node:crypto';
import { existsSync, readFileSync, readdirSync, writeFileSync, unlinkSync } from 'node:fs';
import { join, relative, resolve } from 'node:path';
import { fileURLToPath } from 'node:url';

// The pinned SSG 0.0.75 ships an English-only client-side search runtime.
// Translate its visible empty state and screen-reader announcements as one
// reproducible post-build asset, without weakening CSP or invalidating SRI.
const changes = [
  ['No results for “&ldquo;', 'Nenhum resultado para &ldquo;'],
  ['&rdquo;”</div>', '&rdquo;</div>'],
  ['No results found', 'Nenhum resultado encontrado'],
  ["hits.length+' result'+(hits.length===1?'':'s')+' found'",
   "hits.length+' resultado'+(hits.length===1?'':'s')+' encontrado'+(hits.length===1?'':'s')"],
  // The stock SSG dialog has no close control, focus restoration or Tab boundary.
  // Scope these edits to exact upstream tokens and fail closed on runtime drift.
  ["function close(){overlay.classList.remove('active');active=-1}",
   "function close(){overlay.classList.remove('active');active=-1;btn.focus()}"],
  ["btn.addEventListener('click',function(){open()});",
   "var closeBtn=document.getElementById('ssg-search-close');if(!closeBtn)throw Error('SSG search close button missing');closeBtn.addEventListener('click',close);btn.addEventListener('click',open);"],
  ["if(e.key==='Escape')close();",
   "if(e.key==='Escape'){e.preventDefault();close()}if(e.key==='Tab'){var stops=Array.from(overlay.querySelectorAll('input:not([disabled]),button:not([disabled]),a[href],[tabindex]:not([tabindex=\"-1\"])'));if(stops.length){var first=stops[0],last=stops[stops.length-1];if(e.shiftKey&&(document.activeElement===first||!overlay.contains(document.activeElement))){e.preventDefault();last.focus()}else if(!e.shiftKey&&(document.activeElement===last||!overlay.contains(document.activeElement))){e.preventDefault();first.focus()}}}"],
  ["if(e.key==='Enter'){e.preventDefault();var items=",
   "if(e.key==='Enter'&&e.target!==closeBtn){e.preventDefault();var items="],
];
const digest = (algorithm, body, encoding) => createHash(algorithm).update(body).digest(encoding);

export function localizeRuntimeSource(input) {
  assert.ok(input.includes("getElementById('ssg-search-results')"),
    'SSG search runtime marker changed; audit upstream integration');
  let output = input;
  let translated = 0;
  for (const [english, portuguese] of changes) {
    const originalCount = output.split(english).length - 1;
    const localizedCount = output.split(portuguese).length - 1;
    assert.ok((originalCount === 1 && localizedCount === 0) ||
              (originalCount === 0 && localizedCount === 1),
      'SSG search runtime drift: ' + english);
    if (originalCount) {
      output = output.replace(english, portuguese);
      translated++;
    }
  }
  // SSG 0.0.75 can emit escaped quote characters around the empty-state
  // query interpolation. Those turn +esc(q)+ into *visible literal text*.
  // Repair only the exact upstream pattern, then check the result in CI.
  const brokenQuery = String.raw`\'+esc(q)+\'`;
  const liveQuery = "'+esc(q)+'";
  const brokenCount = output.split(brokenQuery).length - 1;
  assert.ok(brokenCount <= 1, 'Duplicate SSG empty-state interpolation');
  if (brokenCount) output = output.replace(brokenQuery, liveQuery);
  assert.ok(translated === 0 || translated === changes.length,
    'Partially localized runtime is not safe to publish');
  return { code: output, changed: translated > 0 || brokenCount === 1 };
}

function* htmlFiles(folder) {
  for (const entry of readdirSync(folder, { withFileTypes: true })) {
    const path = join(folder, entry.name);
    if (entry.isDirectory()) yield* htmlFiles(path);
    else if (entry.isFile() && entry.name.endsWith('.html')) yield path;
  }
}

export function localizeRuntime({ root = resolve('public'), check = false } = {}) {
  const cspDir = join(root, '_csp');
  assert.ok(existsSync(cspDir), 'SSG CSP assets missing');
  const runtimeNames = readdirSync(cspDir).filter(name => {
    if (!name.endsWith('.js')) return false;
    return readFileSync(join(cspDir, name), 'utf8')
      .includes("getElementById('ssg-search-results')");
  });
  assert.equal(runtimeNames.length, 1, 'Expected exactly one SSG search runtime');
  const originalName = runtimeNames[0];
  const original = readFileSync(join(cspDir, originalName), 'utf8');
  const result = localizeRuntimeSource(original);
  assert.ok(!check || !result.changed, 'SSG search runtime not localized');
  const localizedName = 'ssg-search-ptbr-' +
    digest('sha256', result.code, 'hex').slice(0, 16) + '.js';
  const oldUri = '/conde-incident/_csp/' + originalName;
  const newUri = '/conde-incident/_csp/' + localizedName;
  const oldSRI = 'sha384-' + digest('sha384', original, 'base64');
  const newSRI = 'sha384-' + digest('sha384', result.code, 'base64');
  const oldTag = 'src="' + oldUri + '" integrity="' + oldSRI + '"';
  const newTag = 'src="' + newUri + '" integrity="' + newSRI + '"';
  let pages = 0;
  for (const path of htmlFiles(root)) {
    const html = readFileSync(path, 'utf8');
    if (!html.includes('id="ssg-search-widget"')) continue;
    const oldCount = html.split(oldTag).length - 1;
    const newCount = html.split(newTag).length - 1;
    assert.ok((result.changed && oldCount === 1 && newCount === 0) ||
      (!result.changed && newCount === 1 && oldCount === 1),
      'Unexpected SSG search script/SRI on ' + relative(root, path));
    pages++;
    if (result.changed && !check)
      writeFileSync(path, html.replace(oldTag, newTag));
  }
  assert.ok(pages >= 3, 'Search runtime not linked by generated pages');
  if (result.changed && !check) {
    writeFileSync(join(cspDir, localizedName), result.code, 'utf8');
    unlinkSync(join(cspDir, originalName));
  }
  assert.ok(check || existsSync(join(cspDir, localizedName)),
    'Translated runtime asset missing');
  console.log('SSG search runtime PT-BR: ' + pages +
    ' pages with verified script and SRI; changed=' + result.changed);
  return { pages, asset: localizedName, changed: result.changed };
}

if (process.argv[1] && resolve(process.argv[1]) === fileURLToPath(import.meta.url))
  localizeRuntime({ check: process.argv.includes('--check') });

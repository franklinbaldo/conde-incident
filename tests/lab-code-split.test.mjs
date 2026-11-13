// Regression on the built, published Vite asset graph, not only TS source.
// UX-08: keep first-visit laboratory overhead separate from scientific tools.
import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync, mkdirSync, writeFileSync } from 'node:fs';
import { gzipSync } from 'node:zlib';

const dist = 'dist';
const manifest = JSON.parse(readFileSync(`${dist}/.vite/manifest.json`, 'utf8'));
const pagesIndex = readFileSync(`${dist}/index.html`, 'utf8');
const instruments = [
  'OrbitalMap', 'InversePassInspector', 'TriangulationDashboard',
  'AtmosphereSensitivity', 'MonteCarloVisualizer', 'DocumentArchive',
  'TleAuditViewer', 'PythonScriptModal',
];
const initial = manifest['index.html'];

function eagerDependencies(key, seen = new Set()) {
  if (seen.has(key)) return seen;
  seen.add(key);
  for (const dep of manifest[key]?.imports || []) eagerDependencies(dep, seen);
  return seen;
}
function byteSizes(file) {
  const js = readFileSync(`${dist}/${file}`);
  return { raw: js.byteLength, gzip: gzipSync(js, { level: 9 }).byteLength };
}

test('first visit does not eagerly download the seven tools or the modal', () => {
  assert(initial?.isEntry && initial.file?.endsWith('.js'), 'Vite entry missing');
  const eager = eagerDependencies('index.html');
  for (const name of instruments) {
    const key = `src/components/${name}.tsx`;
    const entry = manifest[key];
    assert(entry?.isDynamicEntry && entry.file?.endsWith('.js'), `${name} must be a separate dynamic JS entry`);
    assert(!eager.has(key), `${name} was pulled into the first navigation payload`);
  }
});

test('initial route is bounded and audit metrics are persisted', () => {
  assert(initial?.file, 'missing compiled index');
  const files = [...eagerDependencies('index.html')]
    .map(key => manifest[key]?.file).filter(Boolean);
  const metrics = {
    source: 'vite-production-manifest',
    caveat: 'gzip byte counts are transfer estimates, not network timings, CWV, real-device or browser cache measurements',
    entry: initial.file,
    eagerFiles: files.map(file => ({ file, ...byteSizes(file) })),
    dynamicTools: Object.fromEntries(instruments.map(name => {
      const file = manifest[`src/components/${name}.tsx`].file;
      return [name, { file, ...byteSizes(file) }];
    })),
  };
  const gzipBytes = metrics.eagerFiles.reduce((n, file) => n + file.gzip, 0);
  console.log(`UX-08 initial compressed JS modules: ${gzipBytes} bytes across ${files.length} files`);
  assert(gzipBytes < 256 * 1024, 'first page exceeds the provisional 256 KiB gzipped JS budget');
  mkdirSync('test-results/ui', { recursive: true });
  writeFileSync('test-results/ui/lab-bundle-metrics.json', JSON.stringify(metrics, null, 2) + '\n');
});

test('offline laboratory CSP does not allow obsolete Google Maps scripts', () => {
  assert.match(pagesIndex, /script-src 'self';/);
  assert.doesNotMatch(pagesIndex, /maps\.googleapis\.com|\*\.googleapis\.com|\*\.gstatic\.com/);
});

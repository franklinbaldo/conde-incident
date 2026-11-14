import { test } from 'node:test';
import assert from 'node:assert/strict';
import { addBreadcrumbs } from '../scripts/ssg-breadcrumbs.mjs';

const main = '<main id="main" class="wrap" tabindex="-1">';
const page = title => '<html><head><title>' + title + '</title></head><body>' +
  '<header class="masthead"><nav aria-label="Navegação principal"></nav></header>' +
  main + '<h1>Conteúdo</h1></main></body></html>';
test('navegação do capítulo preserva pai, título, H1 e volta sem JS', () => {
  const path = 'stories/2026-11-13-um-capitulo/index.html';
  const before = page('Uma fonte &amp; uma hipótese');
  const after = addBreadcrumbs(before, path, ancestor => ancestor === 'stories');
  assert.equal(after.eligible, true);
  assert.match(after.html, /href="\/conde-incident\/stories\/">Histórias<\/a>/);
  assert.match(after.html, /<span aria-current="page">Uma fonte &amp; uma hipótese<\/span>/);
  assert.equal((after.html.match(/<h1>/g) || []).length, 1);
  assert.ok(after.html.indexOf('Trilha de navegação') > after.html.indexOf(main));
  assert.equal(addBreadcrumbs(after.html, path).changed, false);
});
test('ocorrência oferece índice e arquivo somente quando existem', () => {
  const path = 'evidencias/arquivo/c197-1/index.html';
  const all = addBreadcrumbs(page('C197#1: registro NASA'), path,
    ancestor => ['evidencias', 'evidencias/arquivo'].includes(ancestor));
  assert.match(all.html, /href="\/conde-incident\/evidencias\/">Evidências<\/a>/);
  assert.match(all.html, /href="\/conde-incident\/evidencias\/arquivo\/">Arquivo documental<\/a>/);
  const missing = addBreadcrumbs(page('C197#1'), path,
    ancestor => ancestor === 'evidencias');
  assert.doesNotMatch(missing.html, /href="\/conde-incident\/evidencias\/arquivo\/"/);
});
test('não cria rota intermediária órfã nem altera a home ou SPA', () => {
  const path = 'simulacoes/tles/custodia/index.html';
  const result = addBreadcrumbs(page('Custódia de TLE'), path,
    ancestor => ancestor === 'simulacoes');
  assert.match(result.html, /href="\/conde-incident\/simulacoes\/">Simulações<\/a>/);
  assert.doesNotMatch(result.html, /href="\/conde-incident\/simulacoes\/tles\/"/);
  for (const other of ['index.html','evidencias/index.html','lab/index.html']) {
    const original = page('Início');
    assert.equal(addBreadcrumbs(original, other).html, original);
  }
});
test('falha fechado com HTML sem main, title inválido ou rota insegura', () => {
  assert.throws(() => addBreadcrumbs('<title>Teste</title>', 'stories/teste/index.html'), /Main/);
  assert.throws(() => addBreadcrumbs('<title><script>não</script></title>' + main,
    'stories/teste/index.html'), /Título/);
  assert.throws(() => addBreadcrumbs(page('Título'), 'stories/../invalida/index.html'),
    /insegura/);
});

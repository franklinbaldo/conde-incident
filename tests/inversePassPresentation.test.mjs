import assert from 'node:assert/strict';
import { test } from 'node:test';
import { inverseBahiaClock, inverseHeuristicText, inverseLegacyNote } from '../src/lib/inversePassPresentation.mjs';

test('heuristic codes are readable in either language without changing the underlying codes', () => {
  const cases = [['ALTA', 'HIGH'], ['MODERADA', 'MODERATE'],
    ['EXTREMA', 'EXTREME'], ['INCOMPATIVEL', 'INCOMPATIBLE']];
  for (const [source, translated] of cases) {
    assert.equal(inverseHeuristicText(source, 'pt'), source);
    assert.equal(inverseHeuristicText(source, 'en'), translated);
  }
  assert.match(inverseHeuristicText('UNKNOWN_CODE', 'en'), /Untranslated legacy code.*UNKNOWN_CODE/);
  assert.equal(inverseHeuristicText('toString', 'en'), 'Untranslated legacy code (PT): toString');
});

test('four solver notes and both altitude suffixes are translated, without rewriting PT evidence', () => {
  const sources = [
    'Geometria nominal quase direta sobre o litoral norte baiano. Requer ajuste de fase mínimo (<0,5°).',
    'Passagem dentro do horizonte visual de alta altitude (>150 km). Fase sintonizável com pequena variação de arrasto.',
    'Passagem regional distante (Atlântico ou interior do Brasil). Exigiria desvio balístico acumulado de 3° a 10°.',
    'Fora de qualquer raio de observação ou reentrada terminal local (>1500 km de Conde).',
  ];
  const suffixes = [
    '',
    ' Altura orbital ainda em vácuo (>200 km); não é ponto de queda.',
    ' CORREDOR DE REENTRADA TÉRMICA (120-70 km).',
  ];
  for (const source of sources) {
    for (const suffix of suffixes) {
      const note = source + suffix;
      assert.equal(inverseLegacyNote(note, 'pt'), note);
      const en = inverseLegacyNote(note, 'en');
      assert(!en.includes('Untranslated'), 'known legacy note must be translated');
      assert(!en.includes('Passagem') && !en.includes('Geometria') && !en.includes('reentrada'),
        'English note must not leak Portuguese clauses');
    }
  }
});

test('changed, unsafe or unknown notes fail closed and are never silently discarded', () => {
  const unknown = 'Texto novo (nova alegação do motor)';
  assert.equal(inverseLegacyNote(unknown, 'en'), 'Untranslated legacy note (PT): ' + unknown);
  const altered = 'Passagem regional distante (Atlântico ou interior do Brasil). Exigiria desvio balístico acumulado de 3° a 10°. Nova hipótese.';
  assert.match(inverseLegacyNote(altered, 'en'), /^Untranslated legacy note \(PT\):/);
});

test('Bahia clock translates only the known suffix, preserving the exact clock bytes', () => {
  const clock = '13:45:12 (Horário da Bahia / UTC-3)';
  assert.equal(inverseBahiaClock(clock, 'pt'), clock);
  assert.equal(inverseBahiaClock(clock, 'en'), '13:45:12 (Bahia time / UTC-3)');
  assert.match(inverseBahiaClock('unknown-format', 'en'), /Untranslated legacy time label.*unknown-format/);
});

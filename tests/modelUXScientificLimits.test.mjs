import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = path => readFileSync(new URL(path, import.meta.url), 'utf8');
const inverse = source('../src/components/InversePassInspector.tsx');
const monteCarlo = source('../src/components/MonteCarloVisualizer.tsx');
const monteModel = source('../src/lib/monteCarlo.ts');

test('inverse inspector does not preselect a fabricated historical encounter', () => {
  assert.match(inverse, /useState<CandidatePass \| null>\(null\)/);
  assert.match(inverse, /const chooseDate =/);
  assert.match(inverse, /setSelectedPass\(null\)/);
  assert.doesNotMatch(inverse, /setSelectedPass\(closest\)|Regra de Falsificação|Viabilidade Física:/);
  assert.match(inverse, /aria-pressed=\{isSelected\}/);
  assert.match(inverse, /focus-visible:outline-cyan-300/);
});

test('inverse times and parameters are disclosed as scenarios with traceable evidence', () => {
  assert.match(inverse, /Hora UTC modelada:/);
  assert.match(inverse, /Parâmetros hipotéticos \(sem validação física\)/);
  assert.match(inverse, /Resultado indeterminado/);
  assert.doesNotMatch(inverse, /physicalFeasibility|selectedPass\.notes|fisicamente necessários/);
  for (const id of ['c197', 'c44-orbital', 'raan']) {
    assert.ok(inverse.includes('#/research/' + id), id);
  }
});

test('Monte Carlo displays fractions of synthetic samples, never empirical impact probabilities', () => {
  assert.match(monteCarlo, /Amostras sintéticas: não são probabilidades de impacto/);
  assert.match(monteCarlo, /Fração das amostras/);
  assert.match(monteCarlo, /role="img"/);
  assert.match(monteCarlo, /sem seed de reprodução/);
  assert.match(monteCarlo, /Resultado: indeterminado/);
  assert.doesNotMatch(monteCarlo, /Veredito Final|Probabilidade empírica|Falsificação Bayesiana|0,0062%/);
  for (const id of ['c197', 'raan', 'holdout529']) {
    assert.ok(monteCarlo.includes('#/research/' + id), id);
  }
});

test('Monte Carlo source samples random orbital phase and has no historical holdout calibration', () => {
  assert.match(monteModel, /entryArgLatitudeRad = Math\.random\(\) \* 2 \* Math\.PI/);
  assert.match(monteModel, /raanAtDecayDeg = \(284\.152/);
  assert.doesNotMatch(monteModel, /fitPreCutoffOrbit|scoreFutureOrbit/);
});

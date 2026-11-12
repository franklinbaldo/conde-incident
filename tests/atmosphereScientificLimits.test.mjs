import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';

const source = readFileSync(new URL('../src/components/AtmosphereSensitivity.tsx', import.meta.url), 'utf8');

test('atmospheric panel cannot present algebraic interpolation as a measured terminal arrival', () => {
  for (const pattern of [
    /simulatedDecayDate/, /simulatedDecayDays/, /Resultado da Integração Numérica/,
    /EXATA CONCORDÂNCIA/, /CONVERGE COM CATÁLOGO/, /real physical decay lands precisely/,
    /arrasto molecular.*governado/, /getTime\(\).*simulatedDecayDays/,
    /Média nov\/1963: 76,5/, /Padrão solar mínimo: 45 km/,
  ]) assert.doesNotMatch(source, pattern);
  assert.match(source, /não integra uma trajetória/);
  assert.match(source, /does not integrate a trajectory/);
  assert.match(source, /Resultado científico para o local e a hora: indeterminado/);
});

test('density visualization shows only dimensionless relative results from existing function', () => {
  assert.match(source, /getThermosphericDensity\(200, scaleHeightKm\)/);
  assert.match(source, /getThermosphericDensity\(altitude, scaleHeightKm\) \/ reference/);
  assert.match(source, /ratio\.toFixed\(3\)/);
  assert.doesNotMatch(source, /kg\/m³|kg\/m3|simulatedDecayEpoch/);
  assert.match(source, /aria-hidden="true"/);
  assert.match(source, /<caption className="sr-only">/);
  assert.match(source, /<th scope="row"/);
});

test('hypothetical H has an accessible named keyboard-native control but not fake solar/Ap controls', () => {
  assert.match(source, /<label htmlFor="atmosphere-height"/);
  assert.match(source, /id="atmosphere-height"/);
  assert.match(source, /aria-describedby="atmosphere-height-help"/);
  assert.match(source, /aria-valuetext=/);
  assert.match(source, /type="range"/);
  assert.equal((source.match(/type="range"/g) ?? []).length, 1);
  assert.doesNotMatch(source, /setGeomagneticAp|setSolarFluxF107|setBallisticCoeff/);
  assert.match(source, /35–65 km.*not a confidence interval/);
});

test('historical matrix IDs, dependent witnesses and scientific limits remain linked in both languages', () => {
  for (const id of ['C191', 'C192', 'C193', 'C194', 'C197–C202']) {
    assert.ok(source.includes(id), id);
  }
  for (const link of ['#/research/c197', '#/research/raan', '#/map', '/pull/37', '/pull/43', '/formal/Conde1963/Core.lean', '19640001198.pdf#page=10']) {
    assert.ok(source.includes(link), link);
  }
  assert.match(source, /BSTAR = 0.*não é medição de arrasto nulo/);
  assert.match(source, /BSTAR = 0.*does not measure zero physical drag/);
  assert.match(source, /não um intervalo físico validado/);
  assert.match(source, /NOT a validated physical interval/);
  assert.match(source, /Não existe nesta interface um conjunto não vazio e reduzido/);
});

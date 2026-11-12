import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { publicMilestones } from '../src/lib/publicMilestones.ts';

test('day-only decay dates and conjectured Conde pass are not plotted as observations', () => {
  const original = [
    { id: 'OBS-06', label: 'last TLE epoch' },
    { id: 'OBS-07', label: 'unsupported Conde encounter' },
    { id: 'OBS-08', label: 'NASA day-only 528' },
    { id: 'OBS-09', label: 'other event' },
    { id: 'OBS-11', label: 'day-only 529' },
  ];
  const displayed = publicMilestones(original);
  assert.deepEqual(displayed.map(e => e.id), ['OBS-06', 'OBS-09']);
  assert.deepEqual(original.map(e => e.id), ['OBS-06','OBS-07','OBS-08','OBS-09','OBS-11']);
  assert.equal(publicMilestones(displayed).length, displayed.length);
});

test('map UX cannot silently restore unsupported terminal precision', () => {
  const map = readFileSync(new URL('../src/components/OrbitalMap.tsx', import.meta.url), 'utf8');
  assert.doesNotMatch(map, /Pausar no Impacto em Conde|MOMENTO DO IMPACTO|0,006%|CONDE_IMPACT_PASS_MS|1963-11-08T19:48:00Z/);
  assert.match(map, /const displayedMilestones = publicMilestones\(NORAD_OBSERVATION_EVENTS\)/);
  assert.match(map, /const \[showObservationMarkers, setShowObservationMarkers\] = useState<boolean>\(false\)/);
  assert.match(map, /const \[showUncertaintyBuffer, setShowUncertaintyBuffer\] = useState<boolean>\(false\)/);
  assert.match(map, /#\/research\/c197/);
  assert.match(map, /#\/research\/raan/);
  assert.match(map, /Visualização exploratória, não reconstrução de queda/);
});

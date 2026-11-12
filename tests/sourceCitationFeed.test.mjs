import test from 'node:test';
import assert from 'node:assert/strict';
import { readFileSync } from 'node:fs';
import { citationContext, declaredLineageContext, isCitationFeed, isDeclaredDependenceFeed, normalizeOccurrence, matrixOccurrenceUrl } from '../src/lib/sourceCitationAudit.ts';

const feed = JSON.parse(readFileSync(new URL('../public/data/conde-source-citations.json', import.meta.url), 'utf8'));
const dependence = JSON.parse(readFileSync(new URL('../public/data/conde-declared-dependence.json', import.meta.url), 'utf8'));
const component = readFileSync(new URL('../src/components/SourceCitationFeed.tsx', import.meta.url), 'utf8');
const archive = readFileSync(new URL('../src/components/DocumentArchive.tsx', import.meta.url), 'utf8');

test('strict occurrence IDs and matrix collision handling', () => {
  assert.equal(normalizeOccurrence(' c197#1 '), 'C197#1');
  assert.equal(normalizeOccurrence('C44'), null);
  assert.equal(normalizeOccurrence('C197'), null);
  assert.equal(normalizeOccurrence('C44#2'), 'C44#2');
  assert.equal(normalizeOccurrence('C197#0'), null);
  assert.equal(citationContext(feed, 'C44#1').state, 'unmapped');
  assert.equal(citationContext(feed, 'C197').state, 'invalid');
});

test('curated feed is current and does not invent additional witnesses', () => {
  assert.equal(isCitationFeed(feed), true);
  assert.equal(feed.curated_occurrences + feed.unmapped_occurrences, feed.total_matrix_occurrences);
  const nasa = citationContext(feed, 'C197#1');
  const ntrs = citationContext(feed, 'C198#1');
  assert.equal(nasa.state, 'mapped');
  assert.equal(ntrs.state, 'mapped');
  assert.equal(nasa.record.work_id, ntrs.record.work_id);
  assert.equal(nasa.record.source_family, ntrs.record.source_family);
  assert.ok(nasa.sameWork.some((x) => x.occurrence === 'C198#1'));
  assert.equal(nasa.record.scope, 'CATALOGUED_DAY_ONLY');
  assert.equal(nasa.record.not_a_verified_conde_physical_event, true);
  const tupi = ['C01#1', 'C02#1', 'C03#1'].map((id) => citationContext(feed, id));
  assert.ok(tupi.every((x) => x.state === 'mapped'));
  assert.equal(new Set(tupi.map((x) => x.record.work_id)).size, 1);
  assert.ok(tupi.every((x) => x.record.not_a_verified_conde_physical_event));
});

test('UI exposes provenance, real source links, accessibility and partial-coverage warning', () => {
  assert.match(component, /aria-live="polite"/);
  assert.match(component, /aria-pressed=\{selected === id\}/);
  assert.match(component, /htmlFor="citation-occurrence"/);
  assert.match(component, /BASE_URL/);
  assert.match(component, /UNMAPPED/);
  assert.match(component, /related\.length/);
  assert.match(component, /rel="noopener noreferrer"/);
  assert.match(component, /not independent witnesses|não são testemunhos independentes/);
  assert.match(archive, /<SourceCitationFeed lang=\{lang\} \/>/);
  assert.ok(matrixOccurrenceUrl(901).endsWith('#L901'));
  assert.equal(matrixOccurrenceUrl(901), 'https://github.com/franklinbaldo/conde-incident/blob/faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df/research/evidence_matrix_C001-C238_2026-11-11.md#L901');
  assert.ok(!matrixOccurrenceUrl(901).includes('/blob/main/'));
  assert.equal(feed.matrix_git_blob_sha1, 'a7978c3a75a153b16ab70118a92c434bba674cb7');
  assert.equal(isCitationFeed({ schema: 'unknown', records: [] }), false);
});


test('companion displays declared Tupi and NASA ancestry without adding witnesses', () => {
  assert.equal(isDeclaredDependenceFeed(dependence), true);
  const tupi = citationContext(feed, 'C01#1');
  const nasa = citationContext(feed, 'C198#1');
  const cel = citationContext(feed, 'C23#1');
  const day = citationContext(feed, 'C197#1');
  assert.equal(tupi.state, 'mapped');
  assert.equal(nasa.state, 'mapped');
  assert.equal(cel.state, 'mapped');
  assert.equal(day.state, 'mapped');
  const tupiLineage = declaredLineageContext(dependence, feed, tupi.record);
  const nasaLineage = declaredLineageContext(dependence, feed, nasa.record);
  const celLineage = declaredLineageContext(dependence, feed, cel.record);
  const dayLineage = declaredLineageContext(dependence, feed, day.record);
  assert.equal(tupiLineage.state, 'declared');
  assert.equal(nasaLineage.state, 'declared');
  assert.equal(celLineage.state, 'declared');
  assert.equal(dayLineage.state, 'declared');
  assert.deepEqual(tupiLineage.paths[0].edges[0], {
    from: 'FBIS_EOP_UAP_D001', to: 'RADIO_TUPI_19631108', kind: 'transcribes',
  });
  assert.deepEqual(nasaLineage.paths[0].edges[0], {
    from: 'NTRS_19640001198', to: 'NASA_SSR_19631115', kind: 'catalogue_of_same_work',
  });
  assert.equal(celLineage.paths.length, 2);
  assert.deepEqual(celLineage.paths.map((path) => path.upstream_source_id),
    ['GFZ_KP_AP_SERIES', 'NRC_F107_SERIES']);
  assert.equal(dayLineage.paths.length, 0); // No edge != independent source.
  assert.equal(dependence.epistemic_limits.independent_physical_observation_count, null);
  assert.equal(dependence.epistemic_limits.absence_of_edge_does_not_prove_independence, true);
});

test('unknown, stale and source-mismatched genealogy never silently attaches to citations', () => {
  const tupi = citationContext(feed, 'C01#1');
  assert.equal(tupi.state, 'mapped');
  const stale = { ...dependence, matrix_git_blob_sha1: 'other-matrix' };
  assert.equal(declaredLineageContext(stale, feed, tupi.record).state, 'snapshot-mismatch');
  const alien = { ...tupi.record, source_id: 'DIFFERENT_SOURCE' };
  assert.equal(declaredLineageContext(dependence, feed, alien).state, 'source-mismatch');
  const uncurated = { ...tupi.record, occurrence: 'C44#1' };
  assert.equal(declaredLineageContext(dependence, feed, uncurated).state, 'unmapped');
  const malformed = { ...dependence, epistemic_limits: { absence_of_edge_does_not_prove_independence: false } };
  assert.equal(isDeclaredDependenceFeed(malformed), false);
});

test('C232#1 binds each curated document to its OWN lineage by (snapshot, source)', () => {
  const context = citationContext(feed, 'C232#1');
  assert.equal(context.state, 'mapped');
  assert.deepEqual(context.records.map((row) => row.source_id), [
    'BLUEBOOK_CASES_INDEX_1963', 'NARA_BB_CARD_302531013',
  ]);
  const index = declaredLineageContext(dependence, feed, context.records[0]);
  const card = declaredLineageContext(dependence, feed, context.records[1]);
  assert.equal(index.state, 'declared');
  assert.deepEqual(index.paths, []);
  assert.equal(card.state, 'declared');
  assert.deepEqual(card.paths.map((p) => p.upstream_source_id), ['NARA_BB_UNIT_302531012']);
  assert.equal(card.paths[0].edges[0].kind, 'part_of_archival_unit');
  assert.notEqual(context.records[0].work_id, context.records[1].work_id);
  assert.ok(context.records.every((r) => r.not_a_verified_conde_physical_event));
  assert.equal(dependence.epistemic_limits.independent_physical_observation_count, null);
});

test('duplicate and swapped multi-source lineage is rejected, not promoted', () => {
  const { records } = citationContext(feed, 'C232#1');
  const index = dependence.citation_lineages.find((r) =>
    r.source_id === 'BLUEBOOK_CASES_INDEX_1963' && r.snapshot_ref.endsWith('C232#1'));
  const card = dependence.citation_lineages.find((r) =>
    r.source_id === 'NARA_BB_CARD_302531013' && r.snapshot_ref.endsWith('C232#1'));
  assert.ok(index && card);
  const duplicated = { ...dependence, citation_lineages: [
    ...dependence.citation_lineages, { ...card },
  ] };
  assert.equal(declaredLineageContext(duplicated, feed, records[1]).state, 'source-mismatch');
  const swapped = { ...dependence, citation_lineages: dependence.citation_lineages.map((r) =>
    r === card ? { ...r, family_id: index.family_id } : r),
  };
  assert.equal(declaredLineageContext(swapped, feed, records[1]).state, 'source-mismatch');
});

test('archive UI loads optional companion with accessible ancestry and unknown state', () => {
  assert.match(component, /conde-declared-dependence\.json/);
  assert.match(component, /isDeclaredDependenceFeed/);
  assert.match(component, /declaredLineageContext/);
  assert.match(component, /citation-lineage-\$\{index\}/);
  assert.match(component, /lineage\.paths\.map/);
  assert.match(component, /path\.edges\.map/);
  assert.match(component, /Independência desconhecida|Independence is unknown/);
  assert.match(component, /independência|independence/i);
  assert.match(component, /dependenceError/);
});

test('C232 UI renders BOTH documentary sources with separate lineage and no independence claim', () => {
  const two = citationContext(feed, 'C232#1');
  assert.equal(two.state, 'mapped');
  assert.equal(two.records.length, 2);
  assert.match(component, /context\.records\.map/);
  assert.match(component, /declaredLineageContext\(dependenceFeed, feed, record\)/);
  assert.match(component, /record\.source_id/);
  assert.match(component, /matrixOccurrenceUrl\(record\.matrix_line\)/);
  assert.match(component, /source-mismatch/);
  assert.match(component, /snapshot-mismatch/);
  assert.ok(two.records.every((item) => declaredLineageContext(dependence, feed, item).state === 'declared'));
  assert.deepEqual(two.records.map((record) =>
    declaredLineageContext(dependence, feed, record).paths.length), [0, 1]);
});

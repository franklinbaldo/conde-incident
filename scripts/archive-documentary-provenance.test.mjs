import { readFileSync } from 'node:fs';
import { strict as assert } from 'node:assert';
import test from 'node:test';

const archive = readFileSync('src/components/DocumentArchive.tsx', 'utf8');
const citations = JSON.parse(readFileSync('public/data/conde-source-citations.json', 'utf8'));

test('archive uses curated citations rather than unattested legacy transcript quotes', () => {
  assert.match(archive, /<SourceCitationFeed lang=\{lang\}/);
  assert.match(archive, /matrixOccurrenceUrl\(item\.line\)/);
  assert.doesNotMatch(archive, /transcriptExcerpt|Original Document Excerpt|Trecho Documental Original/);
  assert.doesNotMatch(archive, /TO SECSTATE WASHDC|entirely groundless|battery depletion observed/);
  assert.doesNotMatch(archive, /Critério B: Compatibilidade Restrita|localização orbital irrefutável/);
});

test('documentary guide references exact occurrence and line in pinned matrix feed', () => {
  for (const [id, line] of [['C01#1', 19], ['C05#1', 23], ['C197#1', 905]]) {
    const record = citations.records.find((r) => r.occurrence === id);
    assert.ok(record, 'Missing curated record ' + id);
    assert.equal(record.matrix_line, line);
    assert.ok(archive.includes("occurrence: '" + id + "'"));
    assert.ok(archive.includes('line: ' + line));
    assert.equal(record.not_a_verified_conde_physical_event, true);
  }
  assert.equal(citations.records.find((r) => r.occurrence === 'C197#1').work_id,
    citations.records.find((r) => r.occurrence === 'C198#1').work_id,
    'NTRS index and NASA PDF are the same documentary work');
});

test('archive labels catalogue date and NARA custody without claiming impact or witnesses', () => {
  assert.match(archive, /DECAYED OBJECTS/);
  assert.match(archive, /sem horário ou localização de reentrada/);
  assert.match(archive, /without a reentry time or location/);
  assert.match(archive, /NAID 302531012/);
  assert.match(archive, /https:\/\/catalog\.archives\.gov\/id\/302531012/);
  assert.match(archive, /não são três testemunhas/);
  assert.match(archive, /three witnesses/);
  assert.match(archive, /indeterminado/);
  assert.match(archive, /undetermined/);
  assert.doesNotMatch(archive, /DOC-0[1-9]/);
});

test('archive retains keyboard accessible and bilingual source links', () => {
  assert.match(archive, /aria-labelledby="archive-heading"/);
  assert.match(archive, /focus-visible:outline-2/);
  assert.match(archive, /rel="noopener noreferrer"/);
  assert.match(archive, /item\.title\[lang\]/);
  assert.match(archive, /item\.finding\[lang\]/);
});

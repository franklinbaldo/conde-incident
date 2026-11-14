/** Non-mutating preflight of every canonical input to the SSG documentary site. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {readBundle,audit} from './verify-ssg-evidence-index.mjs';
import {auditPublishedHistory} from './ssg-evidence-published-history.mjs';
import {archivePages} from './ssg-documentary-archive.mjs';
import {postMatrixPage} from './ssg-post-matrix.mjs';
import {matrixCatalogPages} from './ssg-matrix-catalog.mjs';
import {auditAuthoredPages} from './ssg-authored-pages.mjs';
import {renderTleCustody,TLE_SOURCE} from './ssg-tle-custody.mjs';

const data=file=>JSON.parse(readFileSync('public/data/'+file,'utf8'));

/** Verify what would be rendered, but do not write generated Markdown or HTML.
 * A passing Story-only --check must not mask a broken matrix, archive,
 * post-matrix custody claim, authored Page or pinned secondary TLE. */
export function checkSsgSources() {
  const bundle=readBundle();
  const index=audit(bundle);
  auditPublishedHistory('.',bundle.manifest);
  const citations=data('conde-source-citations.json');
  const lineage=data('conde-declared-dependence.json');
  const wayback=data('conde-wayback-citation-links.json');
  assert.deepEqual(bundle.citations,citations,'Citações lidas de snapshots divergentes');
  assert.deepEqual(bundle.lineage,lineage,'Genealogias lidas de snapshots divergentes');
  const archive=archivePages(citations,lineage,wayback);
  const matrix=matrixCatalogPages(bundle,citations);
  const supplement=postMatrixPage(citations,lineage,bundle);
  const authored=auditAuthoredPages();
  const tle=renderTleCustody(readFileSync(TLE_SOURCE,'utf8'));
  assert.ok(supplement.includes('NARA'),'Suplemento documental não renderizado');
  assert.ok(tle.includes('NORAD 528'),'Custódia TLE não renderizada');
  assert.equal(index.occurrences,bundle.manifest.curated_occurrences);
  assert.equal(matrix.entries.length,bundle.manifest.total_matrix_occurrences);
  return {
    references:index.references,
    curatedOccurrences:index.occurrences,
    totalOccurrences:matrix.entries.length,
    archivePages:archive.size,
    matrixPages:matrix.files.size,
    authoredPages:authored,
    postMatrixRecords:citations.post_matrix_occurrences.length,
  };
}

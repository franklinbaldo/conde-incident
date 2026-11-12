import { readFileSync } from 'node:fs';
import { fileURLToPath } from 'node:url';
import { resolve } from 'node:path';

export function verifyNASAAnchor(matrix, anchor) {
  const errors = [];
  const rows = matrix.split(/\r?\n/);
  const c197 = rows.filter(line => /^\|\s*\*\*C197\*\*\s*\|/.test(line));
  const c198 = rows.filter(line => /^\|\s*\*\*C198\*\*\s*\|/.test(line));
  if (c197.length !== 1) errors.push('C197 must have exactly one occurrence in its registered section');
  if (c198.length !== 1) errors.push('C198 catalogue link must remain visible');
  if (anchor.evidence_id !== 'C197' || anchor.ntrs_id !== '19640001198') errors.push('anchor identity mismatch');
  if (anchor.printed_page !== 8 || anchor.pdf_index_zero_based !== 9 ||
      anchor.viewer_page_one_based !== anchor.pdf_index_zero_based + 1) {
    errors.push('printed/PDF page mapping is incorrect');
  }
  if (anchor.publication_date !== '1963-11-15') errors.push('source publication date mismatch');
  if (!anchor.url?.startsWith('https://ntrs.nasa.gov/api/citations/19640001198/')) {
    errors.push('primary NASA facsimile URL missing');
  }
  const row = c197[0] || '';
  if (!row.includes('p. impressa 8 / PDF índice 9 (página 10 do visor)')) errors.push('C197 page locator regression');
  if (!row.includes(anchor.url)) errors.push('C197 does not link to its primary facsimile');
  if (!row.includes('NASA-TM-X-51205')) errors.push('C197 NASA report identifier missing');
  if (!row.includes('PLEASE ADD THE FOLLOWING TO THE DECAYED OBJECTS LIST') ||
      !row.includes('1963 3B') || !row.includes('8 NOV 63')) errors.push('C197 transcript anchors missing');
  if (!row.includes('Não contém hora nem coordenadas')) errors.push('C197 missing explicit no-time/no-position limitation');
  if (!c198[0]?.includes('mesmo documento') || !c198[0]?.includes('não duas fontes independentes')) {
    errors.push('C198 independence declaration missing');
  }
  if (!anchor.uncertainty?.includes('neither terminal time nor reentry coordinates nor a ground impact')) {
    errors.push('anchor loses geographic/time/impact uncertainty');
  }
  return errors;
}

if (process.argv[1] && fileURLToPath(import.meta.url) === resolve(process.argv[1])) {
  const matrix = readFileSync(new URL('../research/evidence_matrix_C001-C238_2026-11-11.md', import.meta.url), 'utf8');
  const anchor = JSON.parse(readFileSync(new URL('../research/source_anchors/nasa-1963-11-15-decay-3b.json', import.meta.url), 'utf8'));
  const errors = verifyNASAAnchor(matrix, anchor);
  if (errors.length) {
    for (const error of errors) console.error('SOURCE_ANCHOR_FAIL: ' + error);
    process.exitCode = 1;
  } else {
    console.log('SOURCE_ANCHOR_OK C197: NASA primary facsimile, p. 8 print / PDF index 9, no terminal time or position');
  }
}

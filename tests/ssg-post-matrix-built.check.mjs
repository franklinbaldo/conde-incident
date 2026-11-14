/** Built-site contract: every post-matrix row link must be visible and real. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';
import {auditBuiltPostMatrix} from '../scripts/ssg-post-matrix.mjs';

const citations=JSON.parse(readFileSync('public/data/conde-source-citations.json','utf8'));
const html=readFileSync('public/evidencias/arquivo/pos-matriz/index.html','utf8');
const expected=citations.post_matrix_occurrences.reduce(
  (sum,item)=>sum+item.related_matrix_occurrences.length,0);
assert.equal(auditBuiltPostMatrix(html,citations),expected);
console.log('Suplemento pós-matriz: '+expected+' links reais para IDs congelados.');

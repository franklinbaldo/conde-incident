/** No-JavaScript index of documentary states; counts links, not witnesses. */
import assert from 'node:assert/strict';
import {interpretArchiveStatus} from './archive-source-status.mjs';

const ROOT='/conde-incident/evidencias/arquivo/';
const MATRIX='https://github.com/franklinbaldo/conde-incident/blob/faf4dd0fd8dfbdd825e4e934b3b30ebd81bf61df/research/evidence_matrix_C001-C238_2026-11-11.md#L';

export function renderArchiveStatusIndex(records) {
  assert.ok(Array.isArray(records), 'Citações documentais ausentes');
  const groups=new Map();
  for(const record of records) {
    // Fail closed before interpolating values into Markdown links.
    assert.match(record.occurrence, /^C[0-9]{1,3}#[1-9][0-9]*$/);
    assert.match(record.source_id, /^[A-Z][A-Z0-9_]{1,95}$/);
    assert.ok(Number.isSafeInteger(record.matrix_line) && record.matrix_line>0);
    interpretArchiveStatus(record.source_status);
    if(!groups.has(record.source_status))groups.set(record.source_status, []);
    groups.get(record.source_status).push(record);
  }
  const lines=[
    '## Explorar por estado documental', '',
    '**Este índice agrupa vínculos de fontes, não observações físicas independentes.** '+
    'Uma ocorrência pode aparecer em vários estados e o número de vínculos não é uma probabilidade. '+
    'A legenda descreve limites editoriais, não uma classificação de veracidade do acontecimento.', '',
    '[Voltar ao arquivo curado]('+ROOT+')', '',
  ];
  for(const [code,rows] of [...groups].sort(([a],[b])=>a.localeCompare(b,'en'))) {
    const {label,support,limit}=interpretArchiveStatus(code);
    const occurrences=new Set(rows.map(row=>row.occurrence));
    lines.push('### '+label, '',
      '**Código canônico:** \`'+code+'\`. **'+rows.length+' vínculo(s)** em **'+occurrences.size+' ocorrência(s)**.', '',
      support, '', '**Não permite concluir:** '+limit, '',
      ...rows.map(row=>{
        const occurrence=row.occurrence.toLowerCase().replace('#','-');
        const source=row.source_id.toLowerCase().replaceAll('_','-');
        return '- ['+row.occurrence+' · '+row.source_id+']('+ROOT+occurrence+'/)'+
          ' · [Ficha da fonte]('+ROOT+'fontes/'+source+'/)'+
          ' · [Linha da matriz]('+MATRIX+row.matrix_line+')';
      }), '');
  }
  lines.push('[Voltar ao arquivo curado]('+ROOT+')');
  return lines.join('\n');
}

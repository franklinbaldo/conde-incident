/** SSG documentary chronology. Dates describe documents, not the alleged event. */
import assert from 'node:assert/strict';
import {readFileSync} from 'node:fs';

const iso=s=>typeof s==='string'&&/^\d{4}-\d{2}-\d{2}$/.test(s)&&
  Number.isFinite(Date.parse(s+'T00:00:00Z'))&&
  new Date(s+'T00:00:00Z').toISOString().slice(0,10)===s;

/** Lock NARA dates to the independently versioned custody report.
 * The quoted newspaper date is NOT authentication of the newspaper original.
 * Other source types need their own primary-source temporal contract first. */
export function documentDateClaims(item) {
  assert.equal(item.source_id,'NARA_AIRA_TELEGRAM_19631114',
    'Cronologia: fonte ainda sem contrato temporal custodiado');
  assert.match(item.report_path,/^research\/archives\/[a-z0-9_/-]+\.md$/,
    'Cronologia: relatório fora do arquivo permitido');
  assert.ok(!item.report_path.includes('..'),'Cronologia: caminho não seguro');
  const report=readFileSync(item.report_path,'utf8');
  const line=report.split('\n').find(s=>s.startsWith('**Imagem 2, `'+item.image_filename+'`:**'));
  assert.ok(line,'Cronologia: imagem não descrita no relatório');
  const telegram=line.match(/\*\*(\d{1,2}) NOV (\d{4})\*\*/);
  const newspaper=line.match(/`O GLOBO` de (\d{1,2}) de novembro de (\d{4})/);
  assert.ok(telegram&&newspaper,'Cronologia: datas originais não extraídas do relatório');
  const date=(day,year)=>year+'-11-'+day.padStart(2,'0');
  const telegramDate=date(telegram[1],telegram[2]);
  const citedDate=date(newspaper[1],newspaper[2]);
  assert.ok(iso(telegramDate)&&iso(citedDate),'Cronologia: data documental inválida');
  assert.equal(item.telegram_date,telegramDate,
    'Cronologia: data do telegrama diverge do relatório');
  assert.equal(item.reported_newspaper_date,citedDate,
    'Cronologia: data jornalística citada diverge do relatório');
  assert.equal(item.quoted_source_id,'O_GLOBO_19631108_UNINSPECTED',
    'Cronologia: obra jornalística ainda não autenticada');
  for(const key of ['newspaper_page','newspaper_edition','newspaper_publication_time'])
    assert.equal(item[key],null,'Cronologia: metadado jornalístico não verificado: '+key);
  return {telegramDate,citedDate};
}

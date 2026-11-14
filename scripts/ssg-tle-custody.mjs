/** SSG-only readout of a pinned secondary TLE, never a tracking observation. */
import assert from 'node:assert/strict';
import {createHash} from 'node:crypto';
import {mkdirSync, readFileSync, writeFileSync} from 'node:fs';
import {dirname} from 'node:path';

export const TLE_SOURCE = 'research/tle_custody/mirror_528_1963-10-27.tle';
export const TLE_SHA256 = '18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd';
const ROOT = '/conde-incident/simulacoes/tles/';
const SOURCE_URL = 'https://github.com/franklinbaldo/conde-incident/blob/main/'+TLE_SOURCE;
const NASA_URL = 'https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10';

export function checkTleLine(line, number, object=528) {
  const actual = line.length === 69 && /^\d$/.test(line[68]) ? Number(line[68]) : null;
  const computed = line.length === 69 ? [...line.slice(0, 68)].reduce((total, c) =>
    total + (/^\d$/.test(c) ? Number(c) : (c === '-' ? 1 : 0)), 0) % 10 : null;
  const prefix = line.startsWith(number+' '+String(object).padStart(5, '0'));
  return {length:line.length, actual, computed, prefix,
    valid:line.length === 69 && prefix && actual !== null && computed === actual};
}

export function renderTleCustody(raw) {
  const sha = createHash('sha256').update(raw).digest('hex');
  assert.equal(sha, TLE_SHA256, 'Bytes de custódia TLE diferentes do SHA-256 fixado');
  assert.ok(raw.endsWith('\n') && !raw.endsWith('\n\n'), 'Separação de linhas TLE não canônica');
  const lines = raw.trimEnd().split('\n');
  assert.equal(lines.length, 2, 'Par TLE deve ter exatamente duas linhas');
  const [first,second] = lines;
  for (const [i,line] of lines.entries()) {
    const audit = checkTleLine(line, i+1);
    assert.ok(audit.valid, `TLE linha ${i+1}: prefixo/comprimento/checksum divergente`);
  }
  const epoch = first.slice(18,32);
  const raan = second.slice(17,25).trim();
  assert.match(epoch, /^\d{5}\.\d{8}$/);
  assert.match(raan, /^\d{1,3}\.\d{4}$/);
  assert.ok(Number(raan) >= 0 && Number(raan) < 360);
  const body = [
    '## Inspeção estática do TLE secundário do NORAD 528', '',
    '**Tipo de dado: par TLE de espelho secundário, não observação instrumental primária.** Os dois checksums conferem com os bytes custodiados; isso não autentica a estação de rastreamento, precisão ou validade histórica do modelo.', '',
    '## Proveniência e identificador', '',
    '- **Objeto:** NORAD 528 (1963-003B).',
    `- **Arquivo custodiado:** [${TLE_SOURCE}](${SOURCE_URL}).`,
    `- **SHA-256 do arquivo (bytes exatos):** \`${sha}\`.`,
    '- **Ocorrência documental:** C179#1. Origem instrumental primária e covariância não recuperadas.',
    '- **Época inscrita na linha 1:** `'+epoch+'` (ano de 1963, dia ordinal 300 com fração; não é hora de reentrada).',
    '- **RAAN inscrito na linha 2:** `'+raan+'°` (valor do espelho, não medição independente).', '',
    '## Linhas verificadas apenas quanto à sintaxe', '',
    '<pre class="tle-source-lines" tabindex="0" role="region" aria-label="Duas linhas do TLE secundário NORAD 528; rolagem horizontal"><code>'+first+'\n'+second+'</code></pre>','',
    '| Linha | Comprimento | Dígito no arquivo | Dígito recalculado | Inspeção sintática |',
    '|:--|--:|--:|--:|:--|',
    ...lines.map((line,i)=>{
      const check = checkTleLine(line,i+1);
      return `| ${i+1} | ${check.length}/69 | ${check.actual} | ${check.computed} | Confere; autenticidade não verificada |`;
    }), '',
    '## Comparação dos três objetos', '',
    '| NORAD | Material exibido nesta página | Limite |',
    '|:--|:--|:--|',
    '| NORAD 527 | Nenhum par TLE primário exibido | Não substituir com vetor ilustrativo |',
    '| NORAD 528 | Par secundário acima, com checksum consistente | Não autentica observação, propagação ou impacto |',
    '| NORAD 529 | Nenhum par TLE primário exibido | Não extrapolar a partir do 528 |', '',
    `O [boletim NASA de 15/11/1963](${NASA_URL}) registra o **dia 08/11/1963** para o decaimento catalogado de 1963-003B. Isso não fornece a hora, a posição terminal ou a confirmação de queda em Conde. Observações adicionais e sua linhagem são necessárias para qualquer restrição física conclusiva.`, '',
    `[Voltar à auditoria TLE](${ROOT}) · [Comparar 527/528/529](/conde-incident/simulacoes/triangulacao/) · [Arquivo de fontes](/conde-incident/evidencias/arquivo/) · [Ferramenta anterior no laboratório](/conde-incident/lab/#/tles)`, ''
  ].join('\n');
  return [
    '---','type: Page',
    'title: "Custódia do TLE secundário NORAD 528"',
    'description: "Checksum e proveniência do par TLE secundário; sem autenticação instrumental ou reentrada inferida."',
    'layout: page','language: pt-BR',
    'date: "2026-11-13"',
    'author: "Projeto Conde (página gerada de custódia documental)"',
    '---','',body
  ].join('\n');
}

export function writeTleCustodyPage(output='content/simulacoes/tles/custodia/index.md') {
  const content = renderTleCustody(readFileSync(TLE_SOURCE,'utf8'));
  mkdirSync(dirname(output),{recursive:true});
  writeFileSync(output,content,'utf8');
}

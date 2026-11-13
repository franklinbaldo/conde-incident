---
type: Guide
title: "C241-L16: duas edições NASA e os três objetos 1963 3A/B/C"
description: "Comparação contemporânea rastreável de períodos nodais, apogeus e perigeus sem inventar épocas instrumentais."
---

# C241-L16: abril versus outubro, não dois pares TLE

**Ocorrência C241-L16**, ligada à [matriz cumulativa](../evidence_matrix_C001-C238_2026-11-11.md), à [C241-L12](evidence_matrix_C241-L12_2026-11-12.md), à [C241-L11](evidence_matrix_C241-L11_2026-11-12.md) e à [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13).

## Fonte e proveniência

[NASA Satellite Situation Report de 30/04/1963, vol. 3 nº 9, NTRS 19630012128](https://ntrs.nasa.gov/citations/19630012128), [PDF oficial](https://ntrs.nasa.gov/api/citations/19630012128/downloads/19630012128.pdf). Tabela **OBJECTS IN ORBIT**, página PDF **7 (índice 6)**, página impressa **5**, três linhas **1963 3A/B/C** conferidas visualmente no fac-símile rotacionado. A capa menciona dados compilados até **1430Z em 30/04/1963**, não uma medição nessa hora de cada um dos três objetos.

Captura efetiva em 12/11/2026: **592.923 bytes**, SHA-256 **87b8c1be1d074dff4b605b422f6a8836c2ebdf80ca4ac0568373b168cc457a38**. Checksum dos bytes do documento, **não** dos TLEs originais. Transcrição visual humana fixada; CI não faz OCR nem reinspeciona pixels.

Comparação com [NASA 15/10/1963, vol. 3 nº 20, NTRS 19640000428](https://ntrs.nasa.gov/citations/19640000428), página PDF **7 (índice 6)**, impressa **5**, previamente auditada em **C241-L12** com duas variantes de bytes do PDF. Designações 3A/3B/3C dos boletins não exibem IDs NORAD; a associação moderna 527/528/529 é dependente da **C241-L10**.

| Designador | Abril: período min, apogeu/perigeu km | Outubro: período min, apogeu/perigeu km | Δ período min | Δ apogeu/perigeu km |
|---|---|---|---:|---:|
| 1963 3A / 527 | 94,6; 537/460 | 94,6; 531/462 | 0,0 | -6/+2 |
| 1963 3B / 528 | 94,1; 505/435 | 92,4; 401/376 | -1,7 | -104/-59 |
| 1963 3C / 529 | 94,3; 531/437 | 93,3; 458/408 | -1,0 | -73/-29 |

Inclinações impressas abril/outubro (graus): 3A **81,89/81,89**, 3B **81,87/81,87**, 3C **81,88/81,87**. Deltas são **diferenças entre tabelas publicadas**, não derivadas temporais orbitais, pois as épocas de ajuste/observação e instrumentos não aparecem. Altitudes inteiras e períodos com uma decimal não carregam precisão instrumental nem covariâncias.

## Dependências e resultado

NASA abril nº 9 → três linhas catalográficas → NASA outubro nº 20 (**C241-L12**) → NASA novembro nº 22 (**C241-L11**, decaimento catalogado 3B em 08/11/1963). Estas são **edições da mesma compilação institucional**, não três sessões independentes de radar. Edição nº 21 segue **NOT_RECOVERED**. Grafo: **CONNECTED_PENDING_CALIBRATION**. A variação publicada é compatível com evolução da informação catalográfica, mas **não prova arrasto medido ou reentrada prevista**.

RAAN **198,5261°** permanece derivada de espelho secundário; **284,1520°** segue legado sem fonte e inativo. TLEs instrumentais line1/line2, epochs, checksum de linha, frame, sigma, sensores, identidade física S00528 e observação terminal **NOT_RECOVERED**. Nenhuma restrição Lean física promovida, domínio admissível não reduzido, simulador de reentrada não executado. **Conde INDETERMINATE**.

## Reprodução

O [ledger](nasa_ssr_apr_oct_1963_C241-L16.json) fixa os 3 × 2 registros e a integridade do PDF de abril. Rodar:

    python3 -m unittest discover -s tests -p test_tle_nasa_ssr_apr_oct_audit.py -v
    python3 tools/tle_nasa_ssr_apr_oct_audit.py --ledger research/tle_custody/nasa_ssr_apr_oct_1963_C241-L16.json --october research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json --pdf /tmp/19630012128.pdf --output /tmp/c241-l16.json

O CI refaz o download, confere bytes/hash, revalida a transcrição e arquiva relatório JSON; nenhum teste sintético é apresentado como evidência histórica.

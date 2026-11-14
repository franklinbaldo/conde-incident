---
type: Guide
title: "C241-L63: NASA registrou o dia de decaimento de 1963-37A em outubro de 1963"
description: "Releitura da última página da edição SSR C241-L12: data catalográfica de 1963-37A, cruzamento secundário com NORAD 668, sem sensor nem hora."
---

# C241-L63: dia publicado de um controle terminal, sem medição horária

A [Tartaruga #8](https://github.com/franklinbaldo/tartaruga/issues/8) solicita recuperar fontes originais para os candidatos de controle **292, 308, 565 e 668**. C241-L62 encontrou datas contemporâneas para 292 e 565; a presente rodada identifica o **dia de decaimento publicado para 1963-37A**, associado ao NORAD **668** por catálogo retrospectivo, na mesma publicação NASA já custodiada em C241-L12.

## Fac-símile e integridade

O [NASA/Goddard Satellite Situation Report, vol. 3 nº 20 (15/10/1963)](https://ntrs.nasa.gov/citations/19640000428), [PDF oficial, página 9](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf#page=9), página **impressa 7 / índice PDF zero-based 8**, contém a tabela **PLEASE ADD THE FOLLOWING TO THE DECAYED OBJECTS LIST**.

| Coluna original | Valor impresso |
| --- | --- |
| OBJECT | 1963 37 A |
| SOURCE | US |
| LAUNCH | 24 SEP |
| DECAY | **12 OCT 63** |

A página rotacionada foi visualmente conferida. A cópia obtida em 14/11/2026 tem **286.417 bytes, 9 páginas**, SHA-256 **fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2**. Ela coincide com a variante autenticada anteriormente na ocorrência C241-L12; outra entrega da mesma URL (282.624 bytes) **não foi reinspecionada nesta página**. Uma nova variante desconhecida deve causar bloqueio para revisão, não aceitação silenciosa.

A folha contemporânea não imprime 668. A associação 1963 37 A ↔ 1963-037A ↔ NORAD 668 é indicada em [catálogo secundário](https://keeptrack.space/satellite/668); ela não foi comprovada por observação instrumental original.

## Relação com a ONU e limites da inferência

A [ONU INF.55](https://www.unoosa.org/documents/pdf/inf055E.pdf), já registrada em C241-L33, também remove 1963-37A no corte administrativo de 15/10. NASA e o registro governamental dos EUA na ONU podem compartilhar dados NORAD. São **publicações distintas, não dois sensores independentes**. A edição NASA acrescenta um **dia registrado como data de decaimento**, não uma determinação de hora UTC, instante de última observação, estação, precisão ou posição de reentrada. Não imputar meia-noite, desvio-padrão nem probabilidade espacial.

O **NORAD 308 (1962-024A)** permanece **sem data terminal primária recuperada** nesta pesquisa. Foi examinada visualmente a lista incremental na página impressa 8 da edição NASA de [15/11/1963 (NTRS 19640001198)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), onde 1962-024A não aparece. A ausência nessa página não equivale a prova de ausência de rastreio; a edição intermediária nº 21 do SSR continua por recuperar.

**Consequência científica:** melhora da custódia documental do controle 668, **sem** nova publicação independente, sem observações originais, sem instantes terminais calibrados e sem alteração da dinâmica ou das restrições sobre NORAD 528. A queda em Conde permanece não demonstrada.

## Auditoria reproduzível

O [ledger JSON](nasa_ssr_terminal_control_668_C241-L63.json), o auditor em tools/tle_ssr_668_c241_l63.py e os testes adversariais em tests/test_tle_ssr_668_c241_l63.py conferem designação, dia, proveniência, nulos obrigatórios, hash e integridade, inclusive sob Python otimizado. A CI baixa novamente o PDF e compara o SHA da variante **efetivamente inspecionada**, além de exigir nove páginas.

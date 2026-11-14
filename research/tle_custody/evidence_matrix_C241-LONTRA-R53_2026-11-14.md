---
type: EvidenceMatrix
title: 'C241-LONTRA-R53: teste dimensional das altitudes STL B-12'
description: 'Comparação reprodutível de duas hipóteses de unidade com cinco linhas na mesma folha NASA, sem sensor novo.'
---

# C241-LONTRA-R53: controles dimensionais na tabela STL

**Fonte editorial:** NASA TM X-59315, volume 2, Apêndice B, página impressa B-12, folha PDF 105 de 117, [PDF NTRS](https://ntrs.nasa.gov/api/citations/19670008638/downloads/19670008638.pdf). SHA-256 integral da cópia **recuperada e auditada na rodada R51**: f77b0e8998d467dd457d0ab8e8012e6e9d69c60fb6180aa3d68f1e8422b32786. Crédito impresso: STL Space Log, volume 3, número 4. O original do fascículo permanece NÃO RECUPERADO. A folha B-12 foi inspecionada visualmente na auditoria R51; nenhum PDF original do STL foi recuperado nesta rodada.

**Problema:** a linha 1963 3A contém 94,7/94,6 minutos, perigeus 298/286 e apogeus 322/334. Não há legenda de unidade inequívoca certificada na folha crítica. Para não depender de uma única órbita, a mesma tabela traz duas escalas independentes para testar a consistência dimensional: Cosmos 13 (89,8 minutos; 127/209) e Syncom 1 (1426,5 minutos; 21268/22974 e 21242/23004).

**Método:** terceira lei de Kepler com raio terrestre 6371 km, parâmetro gravitacional 398600,4418 km³/s², milha terrestre de 1,609344 km, sem ajustar parâmetros a cada linha nem presumir simultaneidade ou dois sensores distintos. A interpretação como milhas terrestres reproduz muito melhor todos os períodos impressos:

| Linha | Período impresso (min) | Simulação se altitudes em km (min) | Simulação se altitudes em milhas (min) |
| --- | ---: | ---: | ---: |
| 1963 3A primeiro conjunto | 94,7 | 90,578 | 94,446 |
| 1963 3A segundo conjunto | 94,6 | 90,578 | 94,446 |
| Cosmos 13 | 89,8 | 87,705 | 89,773 |
| Syncom 1 primeiro conjunto | 1426,5 | 797,708 | 1426,226 |
| Syncom 1 segundo conjunto | 1426,5 | 797,792 | 1426,390 |

Os resíduos de Syncom 1 (cerca de 628,8 min se km, 0,27 min se milhas) e Cosmos 13 (2,09 vs 0,03 min) são controles de escala que não dependem de 1963 3A. São **evidência quantitativa de consistência interna fortemente favorável a milhas**, não confirmação de que o original imprimiu uma determinada legenda. Não alterar o campo documental nulo de unidade no manifesto R51 sem verificar o original ou uma legenda legível. A identidade de soma 620/620 dos dois conjuntos de 1963 3A e os períodos 94,7/94,6 permanecem sem interpretação física independente; ver análise do 🦌 Cervo em research/statistics/C241_STL_PRINTED_PAIR_COHERENCE.md.

**Limites:** dados republicados, não observação nova. Sem UTC instrumental, estação, incerteza, momento exato da órbita, designação NORAD demonstrada pela fonte independente ou covariância. Sem reforço de inferência sobre 7–9/11/1963, sem localização/hora de queda, sem nova restrição física e sem prova de origem soviética da tabela. Nenhum contato institucional.

**Reprodução:** executar python3 -m unittest discover -s tests -p test_stl_unit_crosscheck_r53.py -v; repetir com python3 -O; executar python3 -m tools.audit_stl_unit_crosscheck_r53. O manifesto JSON referencia a custódia R51 e proíbe por teste promover esta inferência a legenda autenticada ou observação independente.

---
type: Guide
title: 'C241-LONTRA-R53: distinguir milha terrestre de milha náutica na tabela STL B-12'
description: 'Cinco linhas e três hipóteses dimensionais, preservando a legenda miles autenticada na reprodução NASA e o original pendente.'
---

# C241-LONTRA-R53 · O rodapé diz miles; qual milha?

**Fac-símile reutilizado:** NASA TM X-59315, volume 2, Apêndice B, página impressa B-12 (folha PDF 105 de 117), [PDF oficial NTRS](https://ntrs.nasa.gov/api/citations/19670008638/downloads/19670008638.pdf). SHA-256 da cópia integral **recuperada anteriormente na rodada R51**: f77b0e8998d467dd457d0ab8e8012e6e9d69c60fb6180aa3d68f1e8422b32786. A reprodução credita *STL Space Log*, volume 3, número 4. O original do fascículo **não** foi recuperado. A inspeção visual R51 já **confirmou expressamente no rodapé inferior direito da folha B-12**: *Period: minutes; Perigee and Apogee altitudes: miles; Inclination: degrees from the equator*. A legenda também aparece em B-1 (folha PDF 94). Esta rodada **não redescobriu a unidade básica** e não deve desmentir R51.

**Questão residual:** a palavra *miles* da reprodução não explicita **milha terrestre (statute mile)** versus **milha náutica (nautical mile)**. Em vez de testar só o objeto 1963 3A, adotei dois controles de escala na mesma folha: Cosmos 13 em órbita baixa e Syncom 1 quase síncrono, preservando também as duas colunas de 1963 3A.

## Reprodução quantitativa

Usei a terceira lei de Kepler, raio terrestre de 6371 km, parâmetro gravitacional 398600,4418 km³/s², milha terrestre 1,609344 km e náutica 1,852 km. Não ajustei os parâmetros por linha, nem tratei as entradas como medições independentes de estação.

| Linha | Período impresso (min) | Se km | Se milhas terrestres | Se milhas náuticas |
| --- | ---: | ---: | ---: | ---: |
| 1963 3A, primeira | 94,7 | 90,578 | 94,446 | 96,002 |
| 1963 3A, segunda | 94,6 | 90,578 | 94,446 | 96,002 |
| Cosmos 13 | 89,8 | 87,705 | 89,773 | 90,601 |
| Syncom 1, primeira | 1426,5 | 797,708 | 1426,226 | 1708,400 |
| Syncom 1, segunda | 1426,5 | 797,792 | 1426,390 | 1708,601 |

A interpretação em **milhas terrestres** é muito mais coerente com os cinco períodos publicados, sobretudo Syncom 1 (resíduo absoluto próximo de 0,27 min, contra 282 min para milhas náuticas). Isso é uma **inferência quantitativa forte sobre o subtipo**, não certificação textual de *statute mile* no rodapé nem leitura da legenda do STL original. Na reprodução NASA a unidade **miles** está documentalmente confirmada e deve permanecer como tal. O manifesto R51 ainda traz valor nulo para a unidade em seu campo específico de perigeu/apogeu, embora seu guia narrativo registre a legenda: qualquer reconciliação de esquema deve preservar a distinção entre legenda NASA e original STL.

Os pares 298+322 e 286+334 de 1963 3A têm a mesma soma impressa 620, mas os períodos divergem 94,7/94,6. Isso não autoriza derivar arrasto, instante UTC, coeficiente balístico ou novo sensor. A análise do 🦌 Cervo em research/statistics/C241_STL_PRINTED_PAIR_COHERENCE.md é complementar, mas documentalmente dependente da mesma reprodução NASA/STL.

**Estado:** inferência quantitativa sobre subtipo da unidade, baseada em reprodução editorial de uma tabela antiga. Não há nova época instrumental, estação, σ, órbita do NORAD 528 ou observação 527/528/529 nos dias 7–9/11/1963. Não há restrição física, localização de queda, vínculo causal à compilação soviética, nem contato institucional.

**Replay:** python3 -m unittest discover -s tests -p test_stl_unit_crosscheck_r53.py -v; repetir com python3 -O; executar python3 -m tools.audit_stl_unit_crosscheck_r53. Os testes rejeitam confundir legenda NASA com legenda STL, quilômetro com milha, milha terrestre com náutica e linha editorial com observação orbital.

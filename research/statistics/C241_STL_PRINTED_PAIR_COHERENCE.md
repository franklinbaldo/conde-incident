---
type: Experiment
title: 'C241: coerência interna dos dois campos impressos STL 1963-003A'
description: 'Diagnóstico de dois pares editoriais: miles impressas, subtipo desconhecido, sem novas observações.'
experiment_id: C241-CERVO-STL-PAIR-COHERENCE
verification_status: DOCUMENTARY_DIAGNOSTIC_ONLY
---

# Dois pares impressos não são duas órbitas medidas

A reprodução editorial de *STL SPACE LOG*, vol. 3 nº 4, na página impressa B-12 do NASA TM X-59315, está preservada no [ledger R51](../tle_custody/stl_space_log_nasa_r51.json). A fonte NASA em PDF tem SHA-256 `f77b0e8998d467dd457d0ab8e8012e6e9d69c60fb6180aa3d68f1e8422b32786`, com inspeção visual reportada no ledger. O exemplar original do STL ainda **não** foi recuperado. O rodapé da própria página B-12 confirma a unidade impressa **miles** para as alturas, mas **não especifica o subtipo** (milhas terrestres ou náuticas). Também não foram identificados instante instrumental individual, sensor, convenção de elementos ou relação temporal entre as duas colunas. Essa correção de proveniência foi integrada em [#828](https://github.com/franklinbaldo/conde-incident/pull/828).

## Identidade aritmética observável no impresso

| Campo no impresso | Primeira coluna | Segunda coluna |
| --- | ---: | ---: |
| Perigeu (miles, subtipo desconhecido) | 298 | 286 |
| Apogeu (miles, subtipo desconhecido) | 322 | 334 |
| Soma das altitudes | 620 | 620 |
| Altitude média aritmética | 310 | 310 |
| Período impresso (min) | 94,7 | 94,6 |

Os extremos variam simetricamente: perigeu −12, apogeu +12. Assim, **qualquer conversão comum de miles e qualquer modelo Kepleriano com os mesmos parâmetros físicos gerariam o mesmo período a partir dessas duas altitudes médias nominais**. Porém os períodos impressos diferem nominalmente em **6 segundos**. Isso é um diagnóstico de coerência dos campos publicados, não uma medição de arrasto, mudança do semieixo maior, perda de massa ou aceleração.

Sob a hipótese adicional de que ambos os períodos são arredondados à décima de minuto, os valores subjacentes caberiam nos envelopes fechados [94,65; 94,75] e [94,55; 94,65] min, que **tocam em 94,65**. A regra de desempate no arredondamento é desconhecida. **Ponto de fronteira não significa compatibilidade sob uma mesma regra de arredondamento.** Se as duas colunas aplicaram a **mesma função determinística** de arredondamento ao mesmo valor subjacente, é impossível imprimir simultaneamente 94,6 e 94,7. No ponto exato 94,65, *half-even* dá 94,6 e *half-up* dá 94,7: há um testemunho matemático de compatibilidade somente se as convenções puderem ser diferentes. O original STL ainda não permite dizer se foram. O campo do relatório `zero_underlying_difference_excluded=false` se refere **apenas à união conservadora de hipóteses desconhecidas**, não a uma alegação de que uma mesma regra determinística produziria ambos os valores. O desacordo nominal não prova um desacordo físico; tampouco esses envelopes constituem sigma instrumental. As altitudes também são números inteiros em miles, mas seu subtipo, regras de arredondamento e convenção original permanecem desconhecidos. Datas distintas, parâmetros médios versus osculantes, correções orbitais e erros de transcrição são alternativas abertas.

## Evidência capaz de discriminar as alternativas

Priorizar o exemplar original do *STL SPACE LOG*, especialmente cabeçalhos/legenda/unidades das colunas, com edição e página verificáveis. Em seguida, buscar registros instrumentais com UTC, convenção orbital e covariância, e um vínculo independente entre objeto físico e NORAD 528. Um par editorial com mesma soma de altitudes **não** é duas medições independentes para calibrar dinâmica, densidade, massa ou uma posterior.

A ferramenta `python3 -m tools.stl_printed_pair_coherence_C241 --check` reconcilia bytes do manifesto e o auditor R51. O relatório JSON contém as duas identidades e os requisitos de aquisição, com testes sob Python normal e `-O`. Limites: **0 observações novas do 528**, **0 novos sensores**, ganho histórico de posto de massa **0**, `MCMC=NOT_RUN`, `active_constraint=false`, nenhuma redução de domínio geográfico de Conde.


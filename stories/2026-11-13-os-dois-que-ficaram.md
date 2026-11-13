---
type: Story
title: "O satélite saiu da lista. Os outros dois continuaram falando."
description: "Caderno 23: boletins NASA antes e depois do decaimento catalogado do 528, com genealogia documental e leitura de dezembro contestada."
date: "2026-11-13"
summary: "A NASA anotou o decaimento do 528 em novembro, mas continuou a publicar elementos de 527 e 529. O que esses registros posteriores podem dizer sobre 1963?"
chapter: "23"
author: "Coruja · Caderno de investigação"
status: "Documentos históricos inspecionados; elementos compilados, dezembro em revisão, sem reconstrução terminal demonstrada"
---

# O satélite saiu da lista. Os outros dois continuaram falando.

Em **15 de novembro de 1963**, uma folha da NASA mandou acrescentar **1963 3B** à relação de objetos decaídos. Ao lado havia uma data: **8 NOV 63**. Nenhum horário. Nenhuma latitude. Nenhuma menção a Conde, na Bahia. Só o identificador e um dia, na [página impressa 8 do *Satellite Situation Report*, volume 3, nº 22](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10).

A linha poderia parecer o encerramento do arquivo. Não era. Havia outros dois objetos associados ao lançamento, **1963 3A** e **1963 3C**, identificados em catálogos modernos como **527** e **529**. Eles continuaram figurando nas tabelas posteriores. A pergunta agora é diferente: **o que registros feitos depois do desaparecimento catalogado do 528 podem ensinar sobre sua trajetória anterior?**

## Antes: três linhas no mesmo papel

O [boletim de 30 de abril](https://ntrs.nasa.gov/api/citations/19630012128/downloads/19630012128.pdf), o [de 31 de julho, página impressa 5](https://ntrs.nasa.gov/api/citations/19630012290/downloads/19630012290.pdf#page=7), o [de 15 de agosto, página impressa 5](https://ntrs.nasa.gov/api/citations/19630012289/downloads/19630012289.pdf#page=7) e o [de 15 de outubro, página impressa 5](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf#page=7) traziam as três linhas. Seus **períodos nodais impressos**, em minutos:

| Edição NASA | 3A / 527 | 3B / 528 | 3C / 529 |
| --- | ---: | ---: | ---: |
| 30/04/1963 | 94,6 | 94,1 | 94,3 |
| 31/07/1963 | 94,6 | 93,6 | 93,9 |
| 15/08/1963 | 94,6 | 93,3 | 93,8 |
| 15/10/1963 | 94,6 | 92,4 | 93,3 |

O 3A quase não muda **na resolução impressa de décimos de minuto**. Os outros aparecem com períodos progressivamente menores. Isso merece investigação, mas diferenças entre datas editoriais não são taxas físicas diárias: o relatório reúne dados de rastreamento sem informar, para cada célula, **a hora da observação original, estação e covariância instrumental**.

A edição de agosto foi incorporada pela [Tartaruga na PR #377](https://github.com/franklinbaldo/conde-incident/pull/377). O [Polvo, na PR #386](https://github.com/franklinbaldo/conde-incident/pull/386), provou em Lean algumas comparações condicionais sob hipótese explícita de arredondamento decimal. Um verificador pode demonstrar relações entre números publicados; **não transforma tabelas históricas em observações de radar autenticadas**.

## Depois: uma cadeira vazia, duas linhas em órbita

No [boletim nº 23, de 30/11/1963](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7), 3A aparece com **94,6 minutos** e 3C com **92,2 minutos**. O 3B já não aparece entre os *Objects in Orbit*. No [nº 25, de 31/12/1963](https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf#page=7), 3A conserva **94,6 minutos**; 3C continua listado, com inclinação impressa de **81,82°**.

Mas há uma fricção entre duas leituras de uma única linha do boletim de dezembro. Uma anotação anterior da investigação, **C227**, registrou **89,6 minutos** para 3C. A inspeção visual atual do fac-símile aponta **89,2 minutos**. São **24 segundos por volta** de diferença. Não são medições rivais: são **transcrições rivais da mesma página**, a corrigir com segunda leitura independente. Nenhum dos dois números deve entrar sozinho numa simulação histórica calibrada enquanto a divergência continuar aberta.

Mesmo com as duas possibilidades, os valores publicados para 3C mudam de **92,2 para 89,6 ou 89,2 minutos** entre as edições, uma diferença documental de **2,6 ou 3,0 minutos**. Para 3A, o par de boletins mantém 94,6. A diferença persiste apesar do conflito de leitura. **Não sabemos, só por isso, quando exatamente os elementos foram medidos nem que parcela seria de arrasto atmosférico.**

Esses boletins pertencem à mesma família institucional de compilação NASA/Goddard, NORAD e Smithsonian. Mais edições não implicam mais instrumentos independentes. A expressão **“as of 1200Z”** se refere à situação compilada na edição, não necessariamente à época observacional de cada objeto. A presença do 3C numa tabela de 31 de dezembro, dia também associado à sua retirada em catálogos posteriores, não fixa um horário terminal: a latência editorial ainda precisa ser esclarecida.

## Uma observação futura pode restringir uma hipótese passada?

Pode, **condicionalmente**. Posições e períodos de 527 e 529 após 8 de novembro oferecem testes para forças comuns, como a gravidade terrestre e um modelo atmosférico de 1963. Se parâmetros compartilhados forem identificáveis e validados, eles podem ajudar a propagar candidatos ao estado de 528 antes do decaimento. Isso é diferente de observar o 528 depois de desaparecido.

Os três objetos não têm necessariamente a mesma área, massa, atitude ou coeficiente balístico. Tampouco basta comparar linhas registradas em datas diferentes: uma distância entre eles deve ser calculada no **mesmo instante e no mesmo referencial**, propagando as incertezas. Um ajuste que melhora os dois controles e falha no terceiro também é informação. Novas linhas podem revelar uma incompatibilidade de modelo, não apenas diminuir automaticamente a incerteza.

A [custódia C241-L18, integrada pela PR #394](https://github.com/franklinbaldo/conde-incident/pull/394), organiza os boletins de julho, novembro e dezembro e os liga ao [contrato C241-P10 de trajetórias relativas](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/C241-P10_three_object_relative_trajectories.json). Uma checagem editorial sinalizou **possível erro de perigeu na linha de julho de 3C** mesmo após a integração da PR #394; foi aberta [solicitação de segunda leitura à Tartaruga](https://github.com/franklinbaldo/tartaruga/issues/3). A divergência do período de dezembro também permanece aberta. A série científica requer errata rastreável na fonte e no teste, nunca um retoque silencioso na narrativa.

## O próximo papel precisa de relógio e instrumento

O alvo agora é o boletim intermediário de dezembro e, sobretudo, **fichas originais de rastreamento**, com estação, época UTC, observável, referencial, modelo de ajuste e erro. Depois disso será possível validar 527 e 529 contra observações que não foram usadas para ajustá-los, testar modelos atmosféricos compartilhados e avaliar o que eles realmente restringem sobre 528.

Nenhum desses papéis descreve Conde como ponto de impacto. A notícia da esfera e a data de decaimento ainda pertencem a cadeias distintas. Os dois objetos que ficaram não revelaram onde o terceiro terminou. Mas mostram uma direção verificável: **a investigação de um satélite não precisa acabar na última linha dedicada a ele**.

*Proveniência: NASA/Goddard, *Satellite Situation Reports*, edições de 30/04, 31/07, 15/08, 15/10, 15/11, 30/11 e 31/12/1963 (links diretos ao longo do texto). Matriz C197/C227, C241-L12/L16/L17 e C241-L18 integrada com duas leituras ainda contestadas; documentos contemporâneos e cálculos condicionais, não reentrada fisicamente localizada.*

---
type: Story
title: "O minuto que não cabia no erro de edição"
description: "Caderno 13: boletim NASA de 15 de dezembro e contraprova Lean de um viés editorial comum entre 527 e 529."
date: "2026-11-13"
summary: "Um boletim intermediário revelou que a diferença entre dois períodos orbitais impressos aumentava. Uma hipótese simples de erro igual por edição não explica os números."
chapter: "13"
author: "Coruja · Caderno de investigação"
status: "Fac-símiles NASA inspecionados; modelo de viés editorial aditivo falsificado condicionalmente, sem dinâmica terminal"
---

# O minuto que não cabia no erro de edição

O [capítulo 11](https://franklinbaldo.github.io/conde-incident/stories/2026-11-13-os-dois-que-ficaram/) terminou pedindo um documento: o boletim de meados de dezembro de 1963. Em novembro, a NASA já anotara **8 de novembro** como dia do decaimento catalogado do objeto **1963 3B / NORAD 528**, mas seus companheiros **3A / 527** e **3C / 529** continuavam aparecendo nas listas. Um boletim entre novembro e o último dia de dezembro permitiria examinar a sequência sem preencher a lacuna com imaginação.

O documento apareceu. O [*Satellite Situation Report* nº 24, de 15/12/1963](https://ntrs.nasa.gov/citations/19640003479), trouxe um número intermediário e uma pergunta mais precisa: **a mudança das tabelas poderia ser apenas uma correção igual aplicada a todos os objetos de uma edição?** Uma [contraprova formal da PR científica #437](https://github.com/franklinbaldo/conde-incident/pull/437) responde que **não**, para esse modelo restrito e sob premissas explícitas de arredondamento. Não determina, porém, a causa física da diferença.

## Três folhas e dois sobreviventes

Na página impressa **5** (página **7 do PDF**) do [nº 22, de 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=7), o período nodal de 3A aparece como **94,6 minutos**; o de 3C, **92,6**. No [nº 23, de 30/11](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7), as linhas mostram **94,6** e **92,2**. O novo [nº 24, de 15/12](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=7) imprime **94,6** e **91,6**.

| Data da edição NASA | 3A / 527 | 3C / 529 | Diferença 527 − 529 |
| --- | ---: | ---: | ---: |
| 15/11/1963 | 94,6 min | 92,6 min | 2,0 min |
| 30/11/1963 | 94,6 min | 92,2 min | 2,4 min |
| 15/12/1963 | 94,6 min | 91,6 min | 3,0 min |

A linha do **3B / 528** não aparece entre os objetos em órbita nessas edições. Sua ausência acompanha o registro de decaimento na [página impressa 8 do nº 22](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), mas **não constitui observação de reentrada nem fornece hora ou lugar**.

A [custódia C241-L21, integrada pela PR #429](https://github.com/franklinbaldo/conde-incident/pull/429), fixa para o novo documento o identificador **NASA NTRS 19640003479**, **958.927 bytes**, SHA-256 **d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f**. Na linha de 3C, a NASA também imprime **352 km** de apogeu e **347 km** de perigeu. São campos de **tabela compilada**, não o registro bruto de um sensor.

## Uma explicação que se cancela na subtração

Considere uma hipótese editorial simples: cada objeto tem um valor-base constante, mas toda edição acrescenta o mesmo desvio aos dois. Em símbolos, `valor_impresso ≈ base_objeto + desvio_edição`. Quando subtraímos os valores de 527 e 529 **na mesma edição**, o desvio comum desaparece. Portanto a distância entre suas linhas não poderia mudar, além da margem de arredondamento.

Mudou. A diferença impressa cresce de **2,0 para 3,0 minutos** entre 15/11 e 15/12. Se cada número com uma casa decimal representar um arredondamento de **±0,05 minuto**, a variação verdadeira *dessa diferença entre números tabulados* estará em **[0,8; 1,2] minuto**. O zero não pertence ao intervalo. Um deslocamento **aditivo único e comum** às duas linhas não explica as quatro células extremas.

Esse é o resultado estrito formalizado em Lean pela [PR #437, C241-P12](https://github.com/franklinbaldo/conde-incident/pull/437). A [auditoria documental da PR #434](https://github.com/franklinbaldo/conde-incident/pull/434) também decompõe o contraste publicado: a distância 527−529 cresce **0,4 minuto** entre as duas edições de novembro e **0,6 minuto** até 15 de dezembro. A prova vale para a hipótese e os limites de impressão declarados, **não** para qualquer explicação possível. Erros diferentes por objeto, atualizações dos dados de origem, convenções distintas ou evolução física continuam candidatos.

Seria especialmente tentador ler essas diferenças como taxas de arrasto. Mas as datas são **de edição**. A capa do nº 24 informa situação compilada às **1200Z** por NASA/Goddard, NORAD e Smithsonian, não a época de observação de cada objeto. Não há, por célula, estação, referencial, incerteza de sensor ou instante instrumental recuperado. Três boletins dessa mesma linhagem não equivalem a três sensores independentes.

## A conclusão que o Lean não deu

O registro [C241-L21 de observáveis](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/ssr_dec15_1963_observables_C241-L21.json) conecta esses números ao modelo futuro, mantendo como desconhecidas as épocas instrumentais, as convenções e as incertezas. A prova lógica elimina a hipótese **de viés aditivo comum com bases fixas**, não autentica as medições que alimentaram a tabela. O domínio físico admissível da reentrada de 528 **não foi reduzido**.

O [nº 25, de 31/12/1963](https://ntrs.nasa.gov/api/citations/19640005618/downloads/19640005618.pdf#page=7), imprime **89,2 minutos** para 3C. A antiga leitura **89,6** foi corrigida como erro de transcrição na [custódia C241-L18](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/nasa_ssr_jul_dec_1963_C241-L18.json). Esse quarto boletim contextualiza a série, mas **não integra as quatro células extremas** da contraprova de #437. Seu emprego em dinâmica exige reconciliação dos demais campos e da época original.

O próximo teste verificável exige **registros instrumentais históricos**, com época UTC, estação, observável, sistema de referência e erro. Com isso será possível testar forças compartilhadas nos dois objetos que ficaram, respeitando seus parâmetros balísticos distintos, e perguntar se esse ajuste restringe algo sobre a trajetória anterior do 528. Por enquanto, o novo papel fez uma coisa modesta e precisa: **retirou da mesa uma explicação matemática simples, sem fabricar um local de queda em Conde**.

---

**Ficha de verificabilidade.** Fontes primárias: NASA *Satellite Situation Reports* **22** (15/11), **23** (30/11), **24** (15/12), páginas e URLs acima; **25** (31/12) como contexto. Custódia C241-L21 / [#429](https://github.com/franklinbaldo/conde-incident/pull/429), contrastes / [#434](https://github.com/franklinbaldo/conde-incident/pull/434), contraprova Lean condicional C241-P12 / [#437](https://github.com/franklinbaldo/conde-incident/pull/437). Família documental única NASA/NORAD/Smithsonian, épocas instrumentais desconhecidas. Nenhuma reentrada ou queda em Conde demonstrada.

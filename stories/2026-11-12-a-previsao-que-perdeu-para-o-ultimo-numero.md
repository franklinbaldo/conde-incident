---
title: "A previsão que perdeu para o último número"
date: "2026-11-12"
summary: "No agregado de 51 previsões da próxima época do NORAD 529, repetir o valor anterior venceu. Uma contraprova independente revelou a exceção entre 7 e 30 dias: a média dos objetos vizinhos venceu nesse estrato. Nenhum dos placares localiza uma reentrada."
chapter: "11"
author: "Coruja · Caderno de investigação"
status: "C243-T10: contraprova prequential pós-hoc em espelho secundário; sem inferência de reentrada ou impacto"
---

# A previsão que perdeu para o último número

**E se, para prever o próximo registro de um objeto espacial, a melhor estratégia fosse simplesmente repetir o último número conhecido?** A investigação vinha tentando descobrir se os objetos catalogados como **NORAD 527 e 528**, lançados na mesma missão que o **529**, poderiam ajudar a prever sua evolução. No [capítulo 10](https://github.com/franklinbaldo/conde-incident/pull/56), uma recontagem havia preservado uma pequena vantagem da combinação sobre um modelo quadrático. Parecia uma pista promissora. Mas a pergunta ainda era incompleta: **vantagem para prever quanto tempo à frente?**

A resposta chegou de uma contraprova do 🦡 Texugo, na [PR científica #20, ocorrência C243-T10](https://github.com/franklinbaldo/conde-incident/pull/20). Quando o experimento passou a prever **somente a próxima época catalogada** do 529, os três objetos juntos não produziram a melhor previsão. Ganharam alternativas mais simples. A mais simples de todas venceu com folga.

## O que o placar anterior escondia

Os testes anteriores do **C243-T9** cortavam a série de 1963 em quatro momentos e comparavam modelos em futuros que chegavam muitas épocas adiante. Depois de eliminar a dupla contagem, restaram **28 épocas futuras distintas**: o modelo quadrático, ajustado apenas ao 529, teve erro agregado de **0,188775**; a média das curvaturas temporais de 527 e 528, transferida para a série do 529, obteve **0,181910**. Ambos os erros são de *movimento médio* em revoluções por dia, não de posição no espaço. A melhora era descritiva e pequena, mas existia naquele desenho retrospectivo.

O 🦅 Gavião, numa [revisão independente da PR #57](https://github.com/franklinbaldo/conde-incident/pull/57), descobriu o peso desproporcional do último trecho: aproximadamente **99,9% das somas de erros quadráticos** dos dois modelos estavam ali. O capítulo anterior foi [corrigido na própria PR #56](https://github.com/franklinbaldo/conde-incident/pull/56) para incorporar essa distinção e não chamar de “curvatura orbital” uma curvatura ajustada à série de movimento médio.

Era possível que a média conjunta ajudasse na extrapolação mais longa, mas não quando o próximo registro estivesse perto. Para distinguir essas situações, era preciso **mudar o horizonte de previsão**, não procurar uma órbita mais bonita no mapa.

## Uma previsão, depois outra, sem espiar o próximo dado

O novo teste, chamado **prequential** ou *previsão sequencial*, percorreu cronologicamente as épocas disponíveis do NORAD 529. Em cada rodada, treinou os modelos **somente com as épocas já passadas** dos três objetos e pediu que previssem **a próxima época do 529**. Depois da comparação, aquele registro podia integrar o treinamento das rodadas seguintes. Isso impede o uso do futuro na previsão correspondente, mas também explica por que as rodadas **não são experimentos independentes**.

Foram **53 alvos potenciais**: **51 receberam previsão**, enquanto **2 ficaram expressamente como `NOT_RUN`** por histórico insuficiente. O experimento comparou seis alternativas sobre os **mesmos 51 alvos**, sem esconder os modelos derrotados:

| Estratégia | Erro agregado (RMSE, rev/dia) |
| --- | ---: |
| **Persistência: repetir o último valor conhecido do 529** | **0,026904** |
| Quadrático ajustado só ao 529 | 0,074988 |
| Transferência apenas do 528 | 0,079369 |
| Média das curvaturas temporais de 527 e 528 | 0,097122 |
| Transferência apenas do 527 | 0,116989 |
| Linear ajustado só ao 529 | 0,117357 |

No **agregado dos 51 alvos**, a operação mais elementar ficou em primeiro lugar. O modelo conjunto, que havia superado ligeiramente o quadrático na partição do capítulo 10, **agora perdeu para ele no erro agregado**. Nas comparações de erro absoluto individuais entre quadrático e média conjunta, o quadrático foi melhor em **33 das 51 próximas épocas**; a média, em **18**. Essas contagens descrevem resultados correlacionados, não votos de 51 observadores independentes.

O resultado está documentado no [relatório C243-T10](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/texugo_holdout_529.md), na [matriz cumulativa C243-T10](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/evidence_matrix_C001-C238_2026-11-11.md) e no [GitHub Actions #43172444338](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338), que executou o teste numérico sobre o arquivo fixado, com **132 testes Python aprovados**. O [artefato da execução](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338/artifacts/13922149343) permite conferir os resultados. Não se trata de um teste imaginário nem de uma medição de radar nova.

## O intervalo que mudou de vencedor

Uma contraprova independente do 🦅 Gavião, na [PR #60](https://github.com/franklinbaldo/conde-incident/pull/60), reabriu o mesmo arquivo por SHA-256 e recalculou as previsões usando regressão SVD em vez do resolvedor do Texugo. Reproduziu **53/51/2**, os seis erros agregados e o confronto **33 a 18**. A diferença estava na pergunta que faltava: *quantos dias separam um registro do próximo?* O teste de previsão da próxima época não fixa a distância entre as duas datas.

| Intervalo real até a época seguinte | Alvos | Persistência RMSE | Quadrático RMSE | Média 527+528 RMSE |
| --- | ---: | ---: | ---: | ---: |
| Até 1 dia | 2 | **0,039439** | 0,207594 | 0,271683 |
| Mais de 1 até 7 dias | 31 | **0,030682** | 0,078843 | 0,103210 |
| **Mais de 7 até 30 dias** | **18** | 0,016023 | 0,020939 | **0,013378** |
| Mais de 30 dias | 0 | Sem dados | Sem dados | Sem dados |

A virada é real, mas circunscrita: em **18 das 51 próximas épocas**, aquelas separadas por mais de sete e até trinta dias, a **média dos objetos vizinhos venceu ambos os baselines** no RMSE do estrato. Nas outras 33, a persistência venceu. A tabela é uma **estratificação exploratória posterior à escolha do experimento**, não quatro subensaios independentes, não demonstra vantagem generalizável e não converte movimento médio catalogado em posição. O [auditor independente](https://github.com/franklinbaldo/conde-incident/blob/8105fad62bb13e71735f977b34cfed24a85b5c13/tools/gaviao_ch11_prequential.py), o [relatório](https://github.com/franklinbaldo/conde-incident/blob/8105fad62bb13e71735f977b34cfed24a85b5c13/research/gaviao_ch11_review.md) e o [CI verde no SHA da PR #60](https://github.com/franklinbaldo/conde-incident/actions/runs/43178248679) permitem conferir os estratos.

## Uma derrota, duas explicações possíveis

A inversão do placar **não significa que o capítulo 10 estava matematicamente errado**. Naquele capítulo, modelos treinados em quatro cortes eram julgados ao longo de trechos futuros maiores. Aqui, o alvo é sempre o **próximo** registro. A persistência pode funcionar bem em horizontes curtos, sobretudo quando a grandeza não varia muito entre duas observações. Mas os **intervalos entre épocas não são uniformes**, e o desenho foi decidido *depois* de conhecidos os resultados anteriores.

Duas explicações continuam em disputa. Uma diz que informações de outros objetos podem ajudar em determinados horizontes e prejudicar em outros. Outra diz que o pequeno ganho anterior nasceu de peculiaridades do espelho e dos cortes escolhidos, não de forças compartilhadas. **C243-T10 rejeita a alegação de superioridade **universal** da média conjunta no conjunto de próximas épocas; **a estratificação da PR #60 demonstra que a persistência também não vence em todas as faixas**. Nenhum dos dois placares decide qual explicação física é verdadeira.** A vitória da persistência tampouco a torna uma lei orbital.

É especialmente importante não confundir os **três objetos catalogados** com **três instrumentos independentes**. As séries provêm de um único [espelho secundário oxzoid/Space-Track de 1963, revisão `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), de SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. O teste verifica desempenho de estimadores sobre **movimento médio catalogado**, não posição, fase, orientação, força gravitacional conjunta, coeficiente balístico ou ponto de reentrada. Os elementos instrumentais originais com referencial e incerteza continuam ausentes.

## O céu registrado e a notícia contada não se encontraram

Conferi novamente a [página impressa 8, página 10 do PDF, do *Satellite Situation Report* da NASA de 15 de novembro de 1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), documentada na matriz como **C131/C197**: o objeto **1963-003B**, associado ao 528 nos catálogos posteriores, aparece como decaído em **8 de novembro de 1963**. **Não há naquela linha hora, latitude nem longitude.** C131 e C197 não são duas medições independentes: remetem ao mesmo boletim.

O [fac-símile FBIS 03, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), **C01/C02**, registra a notícia atribuída à Rádio Tupi sobre uma esfera em Conde. É evidência de **transmissão de um relato**, não observação de fragmento, corpo ou cratera. NASA e FBIS são duas cadeias documentais com objetos informacionais diferentes; colocá-las na mesma página não produz um elo causal entre a reentrada catalogada e a história de Conde.

## O que mudou desde o capítulo 10

Antes, **uma recontagem de 93 pontuações em 28 épocas** preservara uma pequena vantagem da média dos doadores em horizontes disjuntos mais longos. Agora, **C243-T10** mostrou que a mesma família de estimadores **não vence no agregado das 51 previsões da próxima época**: persistência em primeiro, quadrático à frente da média. A **reexecução independente #60** revelou uma ressalva importante: entre as 18 previsões separadas por **7–30 dias**, a média conjunta vence ambos os baselines no próprio estrato. Não existe vencedor universal entre horizontes. **A história que avançou foi a da capacidade de previsão, não a da localização da queda.**

A restrição condicional que podemos escrever é estritamente **numérica e documental**: *dado o espelho fixado, as definições dos seis modelos e o protocolo sequencial pós-hoc, os 51 alvos avaliados apresentam os erros acima*. Isso **não reduz um domínio físico autenticado de trajetórias admissíveis** e não constitui teorema Lean 4.35.0 sobre o caso. Sem novos dados primários, erro dinâmico validado e holdout posicional, o simulador não tem como escolher Conde, outro lugar ou hora terminal. A situação física permanece **indeterminada**, e mesmo uma reentrada comprovada não provaria impacto no solo.

A próxima pergunta é mais exigente: **o efeito de usar objetos do mesmo lançamento sobreviveria a um teste posicional verdadeiramente cego, com efemérides instrumentais originais, referencial e erros declarados, inclusive se o alvo fosse 527 ou 528?** Um resultado contrário deveria poder derrubar a hipótese favorita. Até obter essa fonte, é mais honesto deixar a previsão simples vencer do que deixar um gráfico elegante escolher o endereço.

---

**Ficha de rastreabilidade:** [C243-T10 na matriz da PR #20](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/evidence_matrix_C001-C238_2026-11-11.md), [método e resultados T10](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/texugo_holdout_529.md), [replay no SHA `054f605`](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338), [PR #57, auditoria independente do capítulo anterior](https://github.com/franklinbaldo/conde-incident/pull/57), [PR #60, auditoria independente e estratos do capítulo 11](https://github.com/franklinbaldo/conde-incident/pull/60), [Parquet secundário pinado](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet). **Grau de verificação:** números reexecutados e arquivo secundário conferido por hash; primários NASA/FBIS inspecionados em imagem quanto à data e ao relato; **dados instrumentais de 1963, independência observacional e impacto: não verificados**. Revisão factual independente do 🦅 Gavião e integração/publicação pelo 🐘 Elefante pendentes.

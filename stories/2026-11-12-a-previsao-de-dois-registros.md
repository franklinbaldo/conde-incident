---
title: "A previsão que só precisou de dois registros"
date: "2026-11-12"
summary: "Depois de perder para a persistência, o modelo que aproveita dados de três objetos recebeu um desafio ainda mais simples: prolongar a tendência entre apenas dois registros anteriores. No teste retrospectivo de movimento médio, essa conta venceu. A vitória, porém, não entrega a órbita de reentrada."
chapter: "13"
author: "Coruja · Caderno de investigação"
status: "C243-T12: comparação retrospectiva em espelho secundário; nenhuma previsão posicional, restrição física autenticada ou impacto verificado"
---

# A previsão que só precisou de dois registros

**E se, para prever o próximo número de um objeto espacial, os dois últimos registros desse próprio objeto fossem mais úteis que todo o histórico reunido de seus vizinhos?** A investigação vinha tentando descobrir o que os objetos NORAD 527 e 528 poderiam ensinar sobre o 529, todos associados ao mesmo lançamento. A hipótese era atraente: uma história orbital compartilhada talvez ajudasse a preencher as lacunas de cada um. Mas os testes começaram a cobrar uma pergunta incômoda: **a informação dos vizinhos está ajudando ou estamos complicando uma previsão que o próprio alvo já permitiria fazer?**

A resposta desta rodada surpreende pela economia. Um modelo com **apenas os dois últimos valores catalogados do 529**, sem consultar 527 ou 528, apresentou o menor erro quadrático médio entre os modelos examinados no novo confronto. Isso aconteceu num **teste retrospectivo de números de catálogo**, não numa previsão da posição espacial de um satélite. A diferença é o centro da história.

## Primeiro, o modelo sofisticado perdeu para a imobilidade

O [capítulo 11](https://github.com/franklinbaldo/conde-incident/pull/59) já havia contrariado a expectativa de que transferir informação entre os objetos sempre ajudaria. Ao prever a *próxima época catalogada* do NORAD 529, a estratégia de simplesmente **repetir o último valor conhecido** superou, no erro agregado, o ajuste quadrático do próprio 529 e a média da curvatura numérica dos vizinhos.

Era uma vitória do procedimento mais simples. Mas também era uma pergunta deixada pela metade. Repetir o último número presume que ele não mudou. **E se os dois números mais recentes já indicassem para onde o próximo iria?**

O 🦡 [Texugo transformou essa dúvida no teste C243-T12, na PR #20](https://github.com/franklinbaldo/conde-incident/pull/20). Em vez de pedir novos dados ou selecionar o melhor corte depois da execução, acrescentou **dois controles de desenho fixo** ao mesmo teste sequencial já usado no capítulo anterior. O primeiro traça uma reta entre os dois últimos valores anteriores à previsão e a estende até a próxima data, respeitando a distância real entre as épocas. O segundo ajusta uma reta aos **três** registros mais recentes do próprio 529. Nenhum deles consulta 527 ou 528, e nenhum pode olhar o valor que deverá prever.

Esses controles foram especificados antes **desta** execução, mas concebidos depois de conhecidos os resultados dos testes anteriores. Esse detalhe limita a força da descoberta: trata-se de uma comparação **pós-hoc**, não de um concurso prospectivo previamente registrado.

## A conta curta venceu

O novo confronto conservou o mesmo conjunto de alvos: **53 possibilidades de próxima época, 51 efetivamente pontuadas e 2 NOT_RUN** por histórico insuficiente. Para cada uma das 51 previsões, os modelos receberam informações anteriores à data de origem e foram avaliados pelo erro no **movimento médio** do 529, expresso em revoluções por dia. Movimento médio é um parâmetro orbital catalogado, não uma latitude, longitude nem um instante de queda.

O resultado, em raiz do erro quadrático médio (**RMSE**, menor é melhor), mudou a ordem dos concorrentes:

| Maneira de prever a próxima época do 529 | RMSE (revoluções/dia) |
| --- | ---: |
| **Reta pelos dois últimos registros do próprio 529** | **0,010935** |
| Reta ajustada aos três últimos registros do 529 | 0,014544 |
| Repetir o último registro do 529 | 0,026904 |
| Quadrático global do 529 | 0,074988 |
| Transferir o modelo do 528 | 0,079369 |
| **Média das informações de 527 e 528** | **0,097122** |

A média dos dois vizinhos, que parecia uma forma de aproveitar o parentesco do lançamento, teve erro agregado maior que o da reta construída com apenas dois registros recentes do próprio alvo. Até a persistência, vencedora do confronto anterior, foi ultrapassada. **Não é que dois pontos tenham revelado a física do objeto. É que, neste conjunto de próximos valores catalogados, o passado recente previu melhor do que a curvatura compartilhada proposta.**

O [relatório de C243-T12](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/research/texugo_holdout_529.md) preserva o desenho, os resultados adversos e a ressalva de seleção posterior. A [matriz cumulativa, ocorrência C243-T12](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/research/evidence_matrix_C001-C238_2026-11-11.md), associa o confronto à cadeia de custódia. O [GitHub Actions #43187482795](https://github.com/franklinbaldo/conde-incident/actions/runs/43187482795) terminou com **164 testes Python aprovados** no SHA **69e603e351526f0450f6cfb8382b4d5d15fa5071**, reabrindo e comparando o espelho Parquet fixado com o CSV derivado; o [artefato #13929476267](https://github.com/franklinbaldo/conde-incident/actions/runs/43187482795/artifacts/13929476267) conserva as previsões e seus erros. O [HEAD posterior da PR #20](https://github.com/franklinbaldo/conde-incident/commit/d31b86486283adb1fad5764285b16b2e73d07439) também passou pelos workflows de holdout, custódia e verificações científicas, mas isso não torna as fontes instrumentais primárias.

## O que essa vitória **não** resolveu

É tentador concluir que a comparação enterrou definitivamente a utilidade dos objetos irmãos. Não enterrou. A pergunta testada era restrita: **qual modelo prediz melhor, por RMSE agregado, o próximo valor de movimento médio numa série secundária de 1963?** O próprio [Gavião demonstrou na revisão independente do capítulo 11, PR #60](https://github.com/franklinbaldo/conde-incident/pull/60), que a preferência por modelos muda quando se separam horizontes de até um dia, de um a sete e de sete a trinta dias. Um vencedor agregado pode perder em uma faixa específica.

Há pelo menos três explicações abertas para o novo placar. O movimento médio catalogado pode ter tido **tendências locais** que uma reta curta acompanha melhor que um quadrático global; os ajustes mais longos podem reagir mal a mudanças ou ruídos de uma série irregular; e os registros podem refletir condições e escolhas do próprio catálogo, não apenas forças físicas. O resultado não distingue essas alternativas. A vitória dos dois registros não prova ausência de influência gravitacional ou arrasto compartilhado, tampouco permite transportar uma fórmula do 529 ao 528.

Outro obstáculo é a independência. Os números vieram do [arquivo Parquet oxzoid/Space-Track de 1963, revisão fixa `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. É **uma linhagem secundária**; três números de catálogo não são três observatórios independentes. As previsões sucessivas também compartilham histórico de treino, de modo que 51 pontuações não equivalem a 51 experimentos independentes.

O teste exclui somente uma expectativa forte **neste desenho retrospectivo**: a de que a média dos vizinhos seria a melhor dentre esses modelos para o próximo movimento médio do 529. Ele **não exclui** um modelo dinâmico conjunto bem especificado que use posições, velocidades, erros instrumentais, referenciais compatíveis e validação cega. A escolha de janela mais adequada para outro período permanece **não validada prospectivamente**.

## Dois documentos de 1963, nenhuma posição

O documento contemporâneo [NASA, *Satellite Situation Report*, de 15 de novembro de 1963, página impressa 8 (décima página do PDF)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) registra **1963 3B** com decaimento catalogado em **8 NOV 63**. Reinspecionado visualmente, não informa hora, longitude, latitude nem objeto recuperado. As ocorrências **C131/C197** remetem a esse mesmo documento; não são duas medidas independentes.

Também reinspecionei o fac-símile [FBIS 03, página 1, EOP-UAP-D001](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf). As ocorrências **C01/C02** documentam uma notícia transmitida pela **Rádio Tupi** sobre uma esfera em Conde. Essa cadeia jornalística não constitui observação física, fotografia autenticada da queda ou ligação com a trajetória orbital. NASA e FBIS registram assuntos diferentes: o calendário comum não fornece uma posição.

## O que mudou desde o capítulo 12

No [capítulo 12, PR #62](https://github.com/franklinbaldo/conde-incident/pull/62), uma contraprova J2 mostrou, **sob premissas estreitas**, que dezesseis segundos de diferença de época não explicam **85,6259° de diferença entre os valores de RAAN** atribuídos ao 528. A revisão [G12-B1 do Gavião, PR #63](https://github.com/franklinbaldo/conde-incident/pull/63), também corrigiu uma armadilha de linguagem: diferença entre RAANs não é automaticamente ângulo entre os planos orbitais. A correção foi feita na própria PR #62, sem ocupar um capítulo adicional.

**Agora a surpresa é outra:** ao testar a próxima entrada de **movimento médio do 529**, a [nova auditoria C243-T12](https://github.com/franklinbaldo/conde-incident/pull/20) revelou que a reta dos **dois últimos registros** supera, neste placar retrospectivo, tanto o simples congelamento do último valor quanto a transferência de informações dos outros dois objetos. A equipe aprendeu mais sobre o desenho do experimento do que sobre o endereço de uma reentrada.

No fluxo documento → matriz → premissa Lean → domínio admissível → simulação calibrada → holdout, o teste para na **auditoria numérica secundária e na comparação retrospectiva de modelos**. Não forneceu elementos instrumentais primários de 1963 com quadro, época e covariância; não produziu nova prova Lean 4.35.0, domínio físico autenticado não vazio e reduzido, ajuste posicional independente ou simulação terminal. **Conde continua indeterminado.** Uma reentrada catalogada não prova que algo atingiu o solo.

O próximo experimento capaz de distinguir as hipóteses seria comparar, **com protocolo e janelas definidos antes de ver os resultados**, a reta local, a persistência e um modelo físico conjunto sobre **posições ou observações instrumentais originais**, com referência temporal comum, estimativa de erro e períodos de validação realmente separados. Se a transferência vencer nessas condições, há motivo para reexaminar seu valor; se perder, a hipótese da vantagem preditiva entre objetos ficará mais restrita. Até lá, a conta curta venceu apenas o teste que de fato disputou.

---

**Ficha de fonte, grau e independência:** **C243-T12** [matriz científica](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/research/evidence_matrix_C001-C238_2026-11-11.md), [metodologia e resultados](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/research/texugo_holdout_529.md), [script de reprodução](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/tools/texugo_holdout_529.py), [CI do SHA verificado](https://github.com/franklinbaldo/conde-incident/actions/runs/43187482795); **inferência quantitativa retrospectiva** sobre **um espelho numérico derivado**, não observação histórica independente. **Primários contemporâneos inspecionados em imagem:** NASA 15/11/1963, p. impressa 8 / PDF página 10, **C131/C197**, e FBIS 03 p.1, **C01/C02**; este último é **transcrição de notícia** e não perícia física. **Não verificados/recuperados:** pares TLE NORAD instrumentais originais com erros e referencial, ligação material entre S00528 e esfera, estado terminal e impacto. Revisão independente 🦅 e integração/publicação 🐘 ainda obrigatórias, exclusivamente no site Conde.

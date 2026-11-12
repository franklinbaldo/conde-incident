---
title: "O registro de fevereiro que mudou o placar"
date: "2026-11-12"
summary: "Uma previsão construída com dois registros venceu o placar de 51 alvos. Mas o protocolo exigia um terceiro registro para aceitar cada tentativa. Quando uma época de fevereiro entrou na conta, o erro cresceu. A auditoria revela o que significa escolher quem pode disputar uma previsão."
chapter: "14"
author: "Coruja · Caderno de investigação"
status: "C243-T13: cobertura numérica auditada de um espelho secundário; resultados retrospectivos, sem trajetória, prova física ou impacto"
---

# O registro de fevereiro que mudou o placar

**Como uma previsão que precisa de apenas dois registros pode deixar de fora uma data em que esses dois registros já existiam?** No [capítulo 13](https://github.com/franklinbaldo/conde-incident/pull/65), a conta mais curta parecia ter dado uma lição aos modelos complicados: projetar a tendência entre os dois últimos valores catalogados do NORAD 529 produziu o menor erro agregado entre os concorrentes. Mas havia uma pergunta anterior à própria fórmula: **quem recebeu autorização para entrar nesse placar?**

O 🦅 [Gavião encontrou a diferença na auditoria G13-E1, PR #66](https://github.com/franklinbaldo/conde-incident/pull/66). Dois valores eram os **operandos** da reta, não o conjunto de condições necessário para pontuar o experimento. O 🦡 [Texugo voltou ao arquivo na PR #20](https://github.com/franklinbaldo/conde-incident/pull/20) e refez a contagem sob regras específicas para cada modelo. O novo teste, identificado como **C243-T13**, descobriu que uma época antes excluída mudava sensivelmente o erro anunciado. Não apareceu um novo satélite nem uma observação desconhecida: mudou o universo de avaliação.

## A porteira escondida na fórmula

A experiência anterior comparava modelos diferentes nos **mesmos 51 alvos**, o que é um cuidado legítimo: não se deve declarar vencedor quem recebeu perguntas mais fáceis. Para tornar essa comparação possível, o protocolo conjunto exigia ao menos **três épocas anteriores do 529 e três anteriores de cada um dos vizinhos 527 e 528**. Assim, a reta curta usava dois valores do 529 para calcular sua previsão, mas só era avaliada depois de o histórico ter cumprido requisitos mais amplos.

Havia **54 épocas distintas do 529** no [espelho histórico secundário oxzoid/Space-Track, revisão `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet). Da segunda em diante, surgem **53 oportunidades** de prever a próxima entrada do catálogo. Uma estratégia que repete o último valor já pode tentar as 53. A reta de dois pontos só pode começar quando existem dois valores anteriores, portanto tem **52** oportunidades. A regressão de três pontos precisa de três valores anteriores e começa com **51**.

Essas são regras aritméticas do arquivo, não observações do céu. E uma ressalva evita o diagnóstico fácil, mas errado: **neste espelho, depois que o 529 tem três épocas anteriores, a exigência de histórico dos doadores não elimina mais nenhum alvo**. As duas primeiras exclusões vieram do início do histórico do próprio 529. A auditoria não demonstra que 527 ou 528 esconderam outras previsões legítimas.

## A data que entrou e alterou o erro

O Texugo acrescentou ao relatório `rolling_target_only_coverage`: três estratégias sem doadores, cada uma avaliada também sobre **todo o histórico em que sua própria fórmula é elegível**. A [ocorrência C243-T13 na matriz científica](https://github.com/franklinbaldo/conde-incident/blob/546e6bd3936ba5af26e1c469291637fea9b43e1c/research/evidence_matrix_C001-C238_2026-11-11.md) e o [relatório do teste](https://github.com/franklinbaldo/conde-incident/blob/546e6bd3936ba5af26e1c469291637fea9b43e1c/research/texugo_holdout_529.md) preservam essa distinção.

| Estratégia com histórico apenas do 529 | Alvos em que pode atuar | RMSE no próprio universo (rev/dia) | RMSE nos 51 alvos comuns (rev/dia) |
| --- | ---: | ---: | ---: |
| Repetir o último valor (≥1 anterior) | **53** | 0,026415 | 0,026904 |
| Reta pelos dois últimos valores (≥2 anteriores) | **52** | **0,014168** | **0,010935** |
| Reta ajustada aos três últimos valores (≥3 anteriores) | **51** | 0,014544 | 0,014544 |

*RMSE* é a raiz do erro quadrático médio: um resumo dos desvios entre valores previstos e valores catalogados; **menor é melhor para o mesmo conjunto de alvos**. A unidade é revoluções por dia, não distância, posição, altitude ou horário de queda. Os números nas duas colunas de RMSE não são um campeonato entre modelos com conjuntos distintos.

A reta de dois pontos recuperou uma previsão adicional, correspondente à época catalogada de **7 de fevereiro de 1963**. Seu RMSE passou de **0,010935**, quando se avaliavam os 51 alvos comuns, para **0,014168** entre os seus próprios 52 alvos. Já a persistência passou de 51 para **53** avaliações, incluindo também a época de **18 de janeiro**. A regressão de três pontos permaneceu com 51.

O resultado surpreendente não é que o modelo simples tenha sido desmentido. **Ele continuou com o mesmo erro nos mesmos 51 alvos.** A surpresa é que bastou acrescentar uma data anteriormente inelegível para mudar a fotografia agregada da sua precisão. Um conjunto de testes não é apenas uma planilha de números: é também a decisão sobre quais perguntas entram na prova.

## Três interpretações e uma conclusão mais estreita

Uma explicação seria que a reta curta lida pior com as primeiras mudanças da série. Outra é que a irregularidade dos intervalos ou os ajustes do próprio catálogo façam uma extrapolação de dois pontos ser instável em certas datas. Uma terceira é que a seleção retrospectiva das janelas, desenhadas **depois** dos resultados anteriores, tenha favorecido um recorte específico. **C243-T13 não distingue essas explicações.** Não há covariâncias instrumentais históricas, sensores independentes nem prova de um regime físico em fevereiro.

A revisão independente [G13-E2 do Gavião](https://github.com/franklinbaldo/conde-incident/blob/1a474361da3417faac3686a635bc5171e035c078/research/gaviao_ch13_review.md) já havia encontrado outra fronteira: nos **18 alvos** cujo horizonte até a próxima época era superior a 7 e até 30 dias, a reta de três valores obteve erro levemente menor que a de dois, embora a de dois vencesse no agregado dos 51. Não se trata de contradição: **o vencedor depende do que se pergunta e do universo em que se pergunta**. Ambos os testes são retrospectivos, com observações e períodos correlacionados.

O [workflow científico do Texugo #43196380743](https://github.com/franklinbaldo/conde-incident/actions/runs/43196380743), no commit `546e6bd3936ba5af26e1c469291637fea9b43e1c`, executou a auditoria real, verificou a origem do Parquet pelo SHA-256 e sua correspondência com o CSV, e concluiu com **194 testes Python aprovados**. O [artefato da execução](https://github.com/franklinbaldo/conde-incident/actions/runs/43196380743/artifacts/13933546145) conserva as previsões, datas, erros e estados `NOT_RUN`. O corpus é **uma única linhagem secundária**; novos cálculos sobre ela não se tornam testemunhas instrumentais independentes.

## O que mudou desde o capítulo 13

Antes, o resultado era: **a secante de dois registros vence por RMSE agregado entre 51 previsões comparáveis**. Isso continua verdadeiro para aquele protocolo. Agora sabemos também que o próprio modelo era elegível para uma 52ª previsão e que incluí-la eleva seu erro agregado de **0,010935** para **0,014168 rev/dia**. A frase “apenas dois registros” exigia, portanto, uma segunda metade: *dois entram na conta, mas o placar original impunha condições adicionais para aceitar a tentativa*. A correção editorial correspondente foi incorporada à [PR #65](https://github.com/franklinbaldo/conde-incident/pull/65).

O que não mudou é a prova histórica. A [NASA, *Satellite Situation Report*, 15/11/1963, p. impressa 8 (PDF p. 10)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), registra o **decaimento catalogado de 1963-003B em 8 de novembro**, sem hora ou posição. O [FBIS 03, p. 1, EOP-UAP-D001](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) preserva o **relato da Rádio Tupi** sobre uma esfera em Conde, não uma constatação física de impacto. Os mesmos boletins correspondem respectivamente a **C131/C197** e **C01/C02** na matriz: IDs múltiplos não significam observações independentes.

O novo teste avança a **auditoria de elegibilidade e incerteza do modelo numérico secundário**, não o domínio físico admissível. Não fornece observação primária com época, referencial e erro; não habilita nova restrição física Lean 4.35.0, nem estabelece conjunto orbital autenticado não vazio e reduzido, simulação terminal calibrada ou ligação material entre NORAD 528 e Conde. Uma data de reentrada catalogada não comprova impacto. **O resultado sobre Conde permanece indeterminado.**

A próxima pergunta pode mudar o rumo desta série: **se definirmos antes do teste os alvos, as épocas elegíveis, os horizontes e os modelos, a reta curta ainda vence quando confrontada com registros posicionais instrumentais originais e validação fora da amostra?** Se perder, a aparente vantagem era mais frágil do que o placar sugeria. Se vencer, terá sobrevivido a uma exigência que os dados disponíveis ainda não permitem cumprir.

---

**Ficha de fontes e limites.** **C243-T13**, [matriz na revisão fixa `546e6bd`](https://github.com/franklinbaldo/conde-incident/blob/546e6bd3936ba5af26e1c469291637fea9b43e1c/research/evidence_matrix_C001-C238_2026-11-11.md), [método e resultados](https://github.com/franklinbaldo/conde-incident/blob/546e6bd3936ba5af26e1c469291637fea9b43e1c/research/texugo_holdout_529.md), [script reproduzível](https://github.com/franklinbaldo/conde-incident/blob/546e6bd3936ba5af26e1c469291637fea9b43e1c/tools/texugo_holdout_529.py), [Actions no SHA de origem](https://github.com/franklinbaldo/conde-incident/actions/runs/43196380743). **Classe:** inferência numérica retrospectiva sobre um arquivo derivado com SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; **não é observação primária**. **G13-E1/E2**, [revisão independente Gavião #66](https://github.com/franklinbaldo/conde-incident/pull/66), é contraprova metodológica no mesmo corpus, não nova estação observadora. **Primários contemporâneos reinspecionados:** NASA, p. impressa 8/PDF 10 (C131/C197), e FBIS, p. 1 (C01/C02, retransmissão). **Ausentes:** TLEs NORAD instrumentais originais, frame/covariância, observação terminal independente, identificação material S00528, localização e evidência de impacto. Revisão final 🦅 e integração/publicação 🐘 ainda necessárias, exclusivamente no site Conde.

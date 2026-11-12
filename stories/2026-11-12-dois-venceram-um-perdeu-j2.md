---
type: Story
title: "Dois satélites deram razão à gravidade; o terceiro discordou"
description: "Capítulo 22 do Caderno Conde: teste cego ao futuro de um proxy J2 em 527/528/529, com vitória parcial, contraprova e origem secundária compartilhada."
date: "2026-11-12"
summary: "Uma previsão baseada no achatamento da Terra se aproximou mais dos registros tardios de dois objetos. No terceiro, a linha reta venceu. O teste mediu um catálogo, não a queda em Conde."
chapter: "22"
author: "Coruja · Caderno de investigação"
status: "Resultado numérico reproduzível de fonte secundária; sem medição instrumental independente nem localização de reentrada"
---

# Dois satélites deram razão à gravidade; o terceiro discordou

**E se a gravidade previsse melhor o que aconteceu meses depois com os companheiros do objeto 528?** No [capítulo 21](https://github.com/franklinbaldo/conde-incident/pull/181), procurávamos horas de radar de novembro de 1963, mas encontramos uma janela que pertencia a outro satélite. A pergunta sobre a posição terminal do NORAD 528 continuou sem resposta. Agora, a [experiência C241-P2 do Polvo, integrada pela PR #209](https://github.com/franklinbaldo/conde-incident/pull/209), oferece um resultado diferente: não um relógio nem uma coordenada, e sim um **teste de previsão** que pode falhar.

## Um planeta que não é perfeitamente redondo

O plano de uma órbita não aponta para sempre na mesma direção. A Terra é ligeiramente achatada nos polos e a parcela gravitacional convencionalmente chamada **J2** faz a linha dos nodos de muitas órbitas girar lentamente. O ângulo usado para descrever essa orientação é o **RAAN**, em graus. Uma aproximação secular clássica combina a inclinação, a excentricidade e o movimento médio para calcular quanto esse ângulo mudaria por dia. [Uma derivação independente da equação](https://github.com/bryanwweber/orbital-mechanics-notes/blob/main/chapter-4/7-effects-of-the-earths-oblateness.md) explica o princípio; a forma implementada nesta pesquisa está explicitada no [memorando técnico C241-P2](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/C241-P2_j2_frozen_long_holdout.md).

O experimento usou três identificadores do mesmo lançamento: **527**, **528** e **529**. Em vez de ajustar parâmetros enquanto via o futuro, congelou os elementos de cada objeto na **última época de ajuste anterior a agosto de 1963**. Daí calculou uma taxa J2 por objeto. A concorrente era uma linha de tendência simples, ajustada apenas aos dados anteriores ao corte. Uma terceira concorrente, ainda mais modesta, mantinha constante o último ângulo conhecido.

**A regra era decisiva:** não recalibrar o modelo depois de ler os registros tardios. As avaliações de outubro a dezembro teriam de julgar as previsões já fixadas. Trata-se de um ensaio retrospectivo com corte pré-declarado, não de experimento independente ou prospectivo.

## O placar que não obedeceu a uma única história

O erro escolhido foi a média do desvio angular absoluto, **MAE, em graus**, respeitando que 359° e 1° estão separados por 2°, não 358°. Menos é melhor. Os números publicados e preservados no [workflow de auditoria](https://github.com/franklinbaldo/conde-incident/actions/runs/43285011757) foram:

| Objeto | Épocas tardias | Linha reta: MAE | Proxy J2: MAE | Melhor |
|---|---:|---:|---:|---|
| 527 | 4 | **0,192°** | 0,511° | Linha reta |
| 528 | 8 | 2,908° | **0,680°** | J2 |
| 529 | 23 | 3,744° | **1,138°** | J2 |

A taxa J2 congelada ficou perto de **−1,1° por dia** nos três objetos, mas cada taxa foi calculada com os próprios elementos catalogados daquele objeto. Não é lícito emprestar a taxa ou o erro do 529 ao 528. O modelo que usa J2 venceu a tendência linear nos registros tardios do 528 e do 529. **Perdeu no 527.** A derrota é parte do resultado, não uma observação inconveniente a esconder. O 527 tinha apenas quatro épocas tardias, o que também torna perigosa qualquer conclusão geral sobre seu desempenho.

A previsão de persistência, que não fazia o plano orbital girar, foi muito pior nas três séries. Isso mostra que a mudança de orientação é importante nesse conjunto. Não certifica qual modelo explica corretamente a trajetória real de um objeto no céu de 1963.

## O que a comparação realmente mediu

A fonte numérica é o [espelho histórico de TLEs oxzoid/Space-Track, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), com SHA-256 do Parquet **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. O CSV derivado também foi fixado por hash na [PR #209](https://github.com/franklinbaldo/conde-incident/pull/209). A pesquisa contabilizou 119 épocas distintas no conjunto dos três objetos, das quais **35** entraram nessa avaliação tardia (4 + 8 + 23). Os três objetos estão na **mesma linhagem de catálogo secundário**. Isso não constitui três instrumentos independentes nem três verificações externas.

Há uma diferença essencial entre uma tabela que prevê outra linha do mesmo arquivo e uma câmera, um radar ou um registro contemporâneo que confirma a posição real. Os elementos orbitais originais, o referencial histórico e as incertezas instrumentais ainda não foram recuperados aqui. A tolerância pequena usada na comparação de extratos numéricos serve para detectar erro de serialização, **não** para afirmar precisão de sensores.

O [*Satellite Situation Report* da NASA de 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), registra para o NORAD 528 **8 de novembro de 1963** como dia de decaimento. Não fornece um RAAN terminal, uma hora nem o ponto de reentrada. O resultado J2 não preenche essa lacuna e não cria uma ligação física com a [notícia de Conde preservada em transcrição FBIS/Tupi](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf).

## A descoberta é um limite

O teste melhorou a descrição numérica de duas séries e refutou a ideia de superioridade **universal** desse proxy J2 sobre a linha reta. Nada nele reduz, com validade instrumental demonstrada, o conjunto de posições e velocidades admissíveis para a reentrada do 528. O domínio físico de hipóteses permanece **inalterado e não quantificado**.

**Próximo passo:** conseguir rastreamentos originais com épocas, referências de coordenadas e erros, de preferência de linhagem independente, e só então confrontar os resíduos de propagação com observações que o ajuste ainda não viu. Essa é a diferença entre um modelo que acerta a própria planilha e uma reconstrução capaz de dizer algo responsável sobre o céu da Bahia.

---

**Ficha de verificabilidade.** Resultado científico integrado: [PR #209](https://github.com/franklinbaldo/conde-incident/pull/209), [memo C241-P2 com método, dados e valores integrais](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/C241-P2_j2_frozen_long_holdout.md) e [execução Actions #43285011757](https://github.com/franklinbaldo/conde-incident/actions/runs/43285011757). Fonte secundária única: Parquet oxzoid fixado por versão/hash; observação primária histórica NASA apenas para **dia de decaimento**, não para comparação RAAN. O modelo J2 é um proxy físico comparado com o catálogo, sem calibração de incertezas instrumentais. **Nenhuma nova prova de impacto em Conde.**

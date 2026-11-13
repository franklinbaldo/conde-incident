---
type: Story
title: "Dois acertos, uma derrota: o teste de J2 no catálogo de 1963"
description: "Caderno 12: teste retrospectivo de precessão J2 contra baseline linear nos objetos 527, 528 e 529, com controle negativo e limites de fonte."
date: "2026-11-13"
summary: "J2 venceu a linha reta nos registros tardios de 528 e 529, mas perdeu no 527. A contraprova evita confundir um acerto no catálogo com uma reentrada observada."
chapter: "12"
author: "Coruja · Caderno de investigação"
status: "Teste retrospectivo C241-P2 reproduzido em CI; dados secundários correlacionados, sem observação terminal do 528"
---

# Dois acertos, uma derrota: o teste de J2 no catálogo de 1963

No [capítulo 11](https://franklinbaldo.github.io/conde-incident/stories/2026-11-13-os-dois-que-ficaram/), os boletins da NASA deixaram uma pergunta sobre a mesa: as órbitas publicadas para **527 e 529**, mesmo depois da retirada do **528**, poderiam ajudar a testar a física empregada na investigação? Um modelo pode parecer convincente quando explica os registros que já conhece. A prova difícil é prever outros registros sem reajustar os parâmetros. Foi o que a [experiência C241-P2, integrada pela PR científica #209](https://github.com/franklinbaldo/conde-incident/pull/209), tentou fazer: comparar um proxy gravitacional J2 com uma linha reta e uma previsão de persistência. E o modelo supostamente mais físico **perdeu em um dos três objetos**.

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

A previsão de persistência, que não fazia o plano orbital girar, teve erros maiores nas três séries. Isso mostra que acompanhar a mudança de orientação ajuda a reproduzir esse conjunto catalográfico. **Não certifica qual modelo descreveu a posição real de um objeto no céu de 1963.**

## O que a comparação realmente mediu

A fonte numérica é o [espelho histórico de TLEs oxzoid/Space-Track, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), com SHA-256 do Parquet **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. O CSV derivado também foi fixado por hash na [PR #209](https://github.com/franklinbaldo/conde-incident/pull/209). A pesquisa contabilizou 119 épocas distintas no conjunto dos três objetos, das quais **35** entraram nessa avaliação tardia (4 + 8 + 23). Os três objetos estão na **mesma linhagem de catálogo secundário**. Isso não constitui três instrumentos independentes nem três verificações externas.

Há uma diferença essencial entre uma tabela que prevê outra linha do mesmo arquivo e uma câmera, um radar ou um registro contemporâneo que confirma a posição real. Os elementos orbitais originais, o referencial histórico e as incertezas instrumentais ainda não foram recuperados aqui. A tolerância pequena usada na comparação de extratos numéricos serve para detectar erro de serialização, **não** para afirmar precisão de sensores.

O [*Satellite Situation Report* da NASA de 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), registra para o NORAD 528 **8 de novembro de 1963** como dia de decaimento. Não fornece um RAAN terminal, uma hora nem o ponto de reentrada. O resultado J2 não preenche essa lacuna e não cria uma ligação física com a [notícia de Conde preservada em transcrição FBIS/Tupi](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf).

## A descoberta é um limite

O teste melhorou a descrição numérica de duas séries e refutou a ideia de superioridade **universal** desse proxy J2 sobre a linha reta. Nada nele reduz, com validade instrumental demonstrada, o conjunto de posições e velocidades admissíveis para a reentrada do 528. O domínio físico de hipóteses permanece **inalterado e não quantificado**.

**Próximo passo verificável:** conseguir rastreamentos originais com épocas UTC, referenciais de coordenadas, estação e erros, preferencialmente de linhagem independente. Só então confrontar os resíduos de propagação com observações não utilizadas no ajuste. Enquanto isso, a derrota de J2 no 527 é uma contraprova real da afirmação de superioridade universal, **não uma evidência de sobrevoo, descarte ou queda no município de Conde**.

---

**Ficha de verificabilidade.** Resultado científico integrado: [PR #209](https://github.com/franklinbaldo/conde-incident/pull/209), [memo C241-P2 com método, dados e valores integrais](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/C241-P2_j2_frozen_long_holdout.md) e [execução Actions #43285011757](https://github.com/franklinbaldo/conde-incident/actions/runs/43285011757). Fonte secundária única: Parquet oxzoid fixado por versão/hash; observação primária histórica NASA apenas para **dia de decaimento**, não para comparação RAAN. O modelo J2 é um proxy físico comparado com o catálogo, sem calibração de incertezas instrumentais. **Nenhuma nova prova de impacto em Conde.**

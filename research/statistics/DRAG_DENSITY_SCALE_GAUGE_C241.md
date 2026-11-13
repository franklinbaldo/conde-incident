---
type: Experiment
title: "C241-P27: calibre de densidade e coeficientes balísticos no integrador J2"
description: "Contraprova de identificabilidade estrutural do produto densidade vezes CdA/m, testada no propagador real, sem estimativa histórica."
experiment_id: C241-P27
model_ref: src/lib/orbitPhysics.ts
inputs_ref: tests/orbitDragDensityGauge.test.mjs
verification_status: SYNTHETIC_CONDITIONAL_TEST
---

# C241-P27. Densidade e coeficientes balísticos não separam sem âncora externa

## Pergunta e base verificável

O motor físico de \`src/lib/orbitPhysics.ts\` usa gravidade central + J2 e arrasto co-rotacional. Na função \`dragAccelerationKmS2\`, a força contém \`rho * cdAreaOverMassM2Kg\`; o termo é calculado em km/s², com densidade kg/m³, velocidade relativa km/s e coeficiente balístico \`Cd A / m\` em m²/kg. Isto é código do projeto, não uma medição de 1963. Os dados NASA SSR registrados no grafo \`research/constraints/ssr_1963_observable_graph.json\` são valores editoriais compilados, sem densidade instrumental, CdA/m identificado, épocas individuais e covariâncias.

Pergunta discriminante: **observações orbitais arbitrariamente precisas de 527, 528 e 529 permitiriam distinguir a escala atmosférica comum dos três CdA/m particulares?**

## Resultado exato, condicionado ao modelo de escala

Se a densidade for \`rho(t,r) = A * f(t,r)\`, com forma \`f\` conhecida, mesmo que dependa da hora absoluta, e \`A > 0\` livre, escreva \`B_j = Cd_j A_j / m_j > 0\` para cada objeto. O arrasto de cada satélite depende somente do produto \`A * B_j\`.

Para qualquer \`c > 0\`, a transformação

\`(A, B_527, B_528, B_529) -> (c*A, B_527/c, B_528/c, B_529/c)\`

preserva exatamente a aceleração em cada ponto do espaço de estados e, portanto, qualquer trajetória com mesmo estado inicial sob unicidade do fluxo. Isso independe da quantidade de épocas ou de observações dos controles pós-08/11. A dependência de \`f\` no tempo absoluto **não** quebra esta simetria de amplitude, embora possa quebrar um gauge temporal diferente.

Na parametrização logarítmica \`d_j = log(A*B_j)\`, o jacobiano máximo de três produtos em quatro parâmetros é \`[[1,1,0,0],[1,0,1,0],[1,0,0,1]]\`. Posto **3/4**, com vetor nulo exato \`(1,-1,-1,-1)\`. Isso é um **limite superior condicional** ao posto extraível dos produtos se fossem observáveis perfeitamente, não uma estimativa do posto dos dados orbitais de 1963. Se a forma \`f\` também for desconhecida, poderá haver ainda mais ambiguidade.

Um modelo de densidade **externamente calibrado em amplitude**, ou um coeficiente \`B_j\` medido independentemente, elimina este gauge específico. Não elimina automaticamente erros de relógio, de estado, dependência instrumental, outros parâmetros físicos ou falta de identificabilidade orbital. Uma prior de amplitude só escolhe uma distribuição sob premissas, não transforma a evidência em identificação.

## Reprodução e controles

\`node --test tests/orbitDragDensityGauge.test.mjs\` usa exatamente \`accelerationKmS2\`, \`dragAccelerationKmS2\` e \`propagate\` do motor físico, gravidade J2 ativa, três estados **sintéticos distintos**, densidade positiva variável no tempo e fator de escala 2. Compara acelerações e estados previstos em 600, 1800 e 3600 s, prova posto/nullidade inteiros, compara o caso com densidade alterada mas \`B_j\` fixo e inclui densidade zero. Nenhuma posição ou densidade utilizada é uma medição dos NORAD reais.

## Dependências, incertezas e decisões

- Física: [issue #4](https://github.com/franklinbaldo/conde-incident/issues/4), \`src/lib/orbitPhysics.ts\`.
- Linhagem documental e observações pendentes: [issue #396](https://github.com/franklinbaldo/conde-incident/issues/396); \`C241-L22\`, NASA SSR 30/06/1963, [NTRS 19630012130](https://ntrs.nasa.gov/citations/19630012130). O boletim não calibra \`A\` nem \`B_j\`.
- Incertezas **não fornecidas**: \`A\`, \`B_j\`, forma \`f\`, época e convenção de estado, sensor, seleção, covariância, procedência instrumental e tradução de elementos médios TLE para estados osculadores.
- \`active_constraint=false\`; \`historical_holdout=NOT_RUN\`; \`historical_mcmc=NOT_RUN\`; \`historical_domain_reduction=NOT_EVALUABLE\`; \`terminal_time_and_location=UNKNOWN\`; \`conde_claim=NOT_SUPPORTED\`.

**Próxima observação discriminante:** procurar medição de densidade absoluta calibrada na altitude/época relevante ou geometria/massa/arrasto de ao menos um objeto com proveniência independente. Novas observações orbitais sozinhas podem identificar produtos efetivos, não esta escala comum. Não inventar priors, intervalos, likelihood ou probabilidade de queda.

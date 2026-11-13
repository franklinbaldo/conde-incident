---
type: Guide
title: '🦌 Cervo: gauge temporal de fluxo autônomo além da dinâmica afim'
description: 'Prova geral por propriedade de grupo, contrafactual acelerado racional e limite de força externamente datada.'
---

# C241-P18: o relógio livre continua ambíguo mesmo com aceleração

Continuação de [#518](https://github.com/franklinbaldo/conde-incident/issues/518) / [PR #520](https://github.com/franklinbaldo/conde-incident/pull/520), agora na [issue #536](https://github.com/franklinbaldo/conde-incident/issues/536). **Estado:** `EXACT_CONDITIONAL_STRUCTURAL_ONLY`. Não foram adquiridos sensores novos ou medidas do objeto 528 nesta fatia.

## Resultado geral, não restrito ao movimento retilíneo

Seja `φ_t` o **fluxo de um sistema dinâmico autônomo**, com `φ_(t+h) ∘ φ_(-h) = φ_t`, estado inicial livre `x0`, relógio do alvo `δ` e origem temporal da efeméride da estação `ε` igualmente livre. A linha de visada é `π_pos φ_(t_i+δ)(x0) - S_i(t_i+δ+ε)`; `S_i` pode ser qualquer função conhecida de tempo e `π_pos` extrai posição.

Para todo `h` em que o fluxo exista, a transformação

`(x0, δ, ε) -> (φ_-h(x0), δ+h, ε-h)`

preserva **exatamente** a posição do alvo e a da estação em todas as épocas. Preserva, portanto, também as direções angulares, distâncias e quaisquer observáveis puramente derivados dessas posições. Nem número arbitrário de visadas nem curvatura temporal da trajetória eliminam sozinhos este **gauge específico**. A não-identificação global é estrutural e independe do jacobiano ou de MCMC. A simetria requer fluxo autônomo e um estado inicial livre; não é uma prova de que toda física orbital real admita esse gauge.

## Prova executável e contraprova de alcance

`tools/autonomous_time_gauge.py` implementa como testemunha um sistema de aceleração **constante, não nula**, com posições quadráticas e velocidades variáveis, usando apenas `fractions.Fraction`. Quatro épocas distintas e uma efeméride de estação também quadrática produzem linhas de visada idênticas antes/depois do gauge. Testes adversariais removem compensações e rompem a identidade. O código não integra a órbita dos NORAD 527/528/529.

Há também uma **contraprova à extensão indevida do teorema**: para a força externamente datada `q''(t)=g*t`, as posições têm termo cúbico `g*t³/6`. Sob mudança de relógio `h`, qualquer escolha de nova posição e velocidade inicial deixa na diferença de posições um coeficiente quadrático `g*h/2`. Em três épocas igualmente espaçadas `(0,1,2)`, a segunda diferença é `g*h`, não nula quando ambos o são. Assim, um forçamento explicitamente dependente de **tempo absoluto confiável** pode quebrar *esta* simetria, mas não prova identificabilidade completa de um estado orbital.

**Implicação observacional:** o experimento anterior de movimento transversal calibrado exige uma referência de tempo verificável; não basta trocar o movimento retilíneo por gravidade autônoma, J2 estacionário ou uma propagação numericamente mais cara. Termos externos datados exigem efemérides, referência temporal e incertezas independentes; inserir um forçamento fictício só para tornar o posto completo seria pseudoidentificação.

## Dependências e estado histórico

Buscar com 🐢 Tartaruga [#396](https://github.com/franklinbaldo/conde-incident/issues/396) registro instrumental independente do alvo, estação, escala UTC/UT1/TDB, época de exposição, sincronização, erros e origem temporal de efemérides. 🦫 Castor [#4](https://github.com/franklinbaldo/conde-incident/issues/4) deve explicitar se seu propagador é autônomo ou externamente datado, inclusive no referencial inercial e no modelo de densidade/arrasto. NASA SSR com datas de edição e a data catalográfica de decaimento de 08/11/1963 **não fornecem por si sós** essa calibração.

Conectividade: C241-P16 -> C241-P17 -> C241-P18 -> `autonomous_flow_phi`, `target_initial_state_x0`, `target_clock_delta`, `station_epoch_epsilon`, `absolute_time_forcing`, `external_ephemeris_calibration`. Nenhuma nova desigualdade física é ativada: `active_historical_constraint=false`, `HISTORICAL_MCMC=NOT_RUN`, `CONDE_GEOGRAPHIC_REDUCTION=NOT_EVALUABLE`.

Reproduzir: `python3 -m unittest discover -s tests -p test_autonomous_time_gauge.py -v`; `python3 tools/autonomous_time_gauge.py`. A prova analítica acima é geral sob as premissas, ao passo que os testes são testemunhas exatas num caso especial, não prova Lean nem verificação de forças orbitais históricas.

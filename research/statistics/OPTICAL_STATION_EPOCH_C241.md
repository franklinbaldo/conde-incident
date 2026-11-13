---
type: Guide
title: '🦌 Cervo: época da estação como gauge adicional'
description: 'Auditoria racional do relógio do alvo quando a efeméride da estação tem origem temporal desconhecida.'
---

# C241-P17: movimento transversal só calibra relógio com época externa

Continuação da [PR #505](https://github.com/franklinbaldo/conde-incident/pull/505), exclusivamente **desenho sintético**. A identificação local 7/7 do relógio comum naquele experimento pressupunha que as posições e velocidades das estações estivessem registradas no tempo absoluto. Essa premissa não foi autenticada para nenhum registro de 1963.

## Operador e prova

Modelo do alvo: r(t) = r0 + v(t + δ). Modelo de estação: s_i(t) = s_i0 + w_i(t + δ + ε), em referencial inercial hipotético. δ desloca a época do alvo; ε é a **origem temporal desconhecida** das efemérides das estações relativamente ao relógio do alvo. As oito incógnitas são r0[3], v[3], δ e ε.

Para cada visada u_i, o projetor P_i = I - u_i u_iᵀ/(u_iᵀu_i) produz o jacobiano tangente [P_i, t_i P_i, P_i(v-w_i), -P_i w_i], avaliado em δ = ε = 0. Sob a transformação exata

(δ, ε, r0) → (δ+h, ε-h, r0-vh)

todas as diferenças alvo-estação permanecem **iguais**. A direção (-v, 0_3, 1, -1) pertence ao núcleo do jacobiano para toda direção, época e velocidade. Mais visadas não separam os dois relógios quando a origem temporal da estação permanece livre.

| Quatro visadas sintéticas | Posto / 8 | Nulidade |
| --- | ---: | ---: |
| Estações imóveis, origem temporal livre | 6/8 | 2 |
| Uma estação transversal, origem temporal livre | 7/8 | 1 |
| Estação transversal com âncora temporal externa | 8/8 | 0 |
| Movimento apenas radial, época calibrada | 7/8 | 1 |

Direções artificiais x, y, z e (1,1,1), épocas 0,1,2,3 e velocidade alvo (2,-1,3); somente a quarta estação pode mover-se. A âncora do terceiro caso é a equação **externa ideal** ε=0, não observação recuperada nem prior atribuída a 1963. Arredondamento, erros reais de relógio, posição, orientação, seleção instrumental e efeitos de dinâmica orbital não estão modelados. Posto completo é somente local e condicional.

## Encadeamento e próxima aquisição discriminante

C241-P14 (paralaxe) → C241-P15 (visadas assíncronas) → C241-P16 (erro de relógio comum) → C241-P17 (origem temporal da efeméride da estação). As variáveis novas são station_ephemeris_epoch_offset_epsilon e external_station_time_reference, com dependências de custódia e calibração.

Buscar em fontes primárias da [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396): identificação de estação, épocas instrumentais, escala e sincronização de tempo, efemérides referidas ao tempo absoluto, transformações de referencial, erro angular e de relógio. Relatórios NASA SSR e espelhos TLE não substituem esses registros. Até haver operador físico e calibradores auditados, a restrição histórica permanece **inativa**, a likelihood e o MCMC histórico são **NOT_RUN**, e a geografia segue **NOT_CONSTRAINED**.

Reproduzir com os comandos python3 tools/optical_station_epoch_alignment.py e python3 -m unittest discover -s tests -p test_optical_station_epoch_alignment.py.

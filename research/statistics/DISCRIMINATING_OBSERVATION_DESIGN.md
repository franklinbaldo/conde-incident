---
type: Guide
title: "Cervo: observações que quebram ou preservam o gauge circular de RAAN"
description: "Experimento estrutural auditável, sem novas observações e sem posterior histórica, ligado à issue #242"
---

# Observações discriminantes: teste de identificabilidade antes do MCMC

**Estado: CONDITIONAL_STRUCTURAL_DESIGN_ONLY.** Issue [#242](https://github.com/franklinbaldo/conde-incident/issues/242). O programa `tools/raan_observation_design.py` usa o extrato secundário da única linhagem Space-Track/NORAD e o manifesto retrospectivo congelado, nas ocorrências **C25#1, C179#1, C180#1, C181#1 e C241-L3**. Nenhuma nova observação, covariância, fase, prior histórica ou propagação orbital foi incluída. A data de decaimento registrada na fonte NASA C197 (08/11/1963) **não contém hora nem coordenadas**, e não é uma observação RAAN terminal.

## Modelo e prova condicional

Considere três fases angulares livres (NORAD 527, 528, 529) e um deslocamento angular comum desconhecido do catálogo. O componente circular abstrato da previsão é

`Omega[j,t] = wrap( f[j,t] + phase[j] + bias[catalog] )`.

`f[j,t]` é **fixo e hipotético** para esta análise de posto; este programa não implementa nem valida os elementos médios TLE, referencial, dinâmica J2 ou o operador de Castor. A transformação **global e exata em S¹** `phase[j] += alpha; bias[g] -= alpha` para todos os objetos e todas as fontes de offset livre deixa cada previsão intacta, mesmo que haja várias épocas. Seu vetor nulo inicial é `(1,1,1,-1)`. A matriz racional de incidência tem **posto 3, quatro colunas, nulidade 1**, em cada bloco histórico, após remover duplicatas: **61 fit, 23 validation, 35 evaluation**. Essa é uma afirmação estrutural sobre o modelo aditivo, **não** um teste de validade instrumental nem prova de identificabilidade de uma órbita física real.

| Candidato de observação, ainda **não recuperado** | Posto / parâmetros | Nulidade | Fase absoluta? |
|---|---:|---:|---|
| Acrescentar épocas da **mesma linhagem** para 528 | 3 / 4 | 1 | Não |
| Medir somente contraste relativo 528 menos 529 | 3 / 4 | 1 | Não |
| Nova linhagem medindo só 528, com offset desconhecido próprio | 4 / 5 | 1 | Não |
| Nova linhagem medindo os três, com offset desconhecido próprio | 4 / 5 | 1 | Não |
| Observação independente de **fase absoluta 528**, calibrada em quadro inercial e época | 4 / 4 | 0 | Sim, **somente no modelo condicional** |
| Calibração externa independente do zero angular da linhagem catalográfica | 4 / 4 | 0 | Sim, **somente no modelo condicional** |

**Ponto discriminante:** multiplicar arquivos ou sensores não basta. Uma linhagem verdadeiramente independente com referência angular desconhecida introduz ao mesmo tempo mais um observável e **mais um parâmetro livre**. A nulidade global permanece. Uma âncora absoluta calibrada forneceria a restrição faltante **se** fosse documentalmente independente, geodeticamente referenciada, datada, compatível em quadro/época com `H`, com erro finito e covariância defensável. Este inventário **não afirma que tal documento exista**. Nem a observação de fase absoluta no modelo aditivo resolve, isoladamente, estados orbital completos ou a localização de reentrada.

## Priors, dependência e holdouts

Uma prior concentrada no viés ou na fase pode escolher um zero angular para simulação, mas **não é uma observação que quebre a simetria dos dados**. No modelo circular histórico, priors, concentração von Mises, correlação entre épocas, catálogo retrospectivamente formatado e seleção dos rastreamentos continuam sem calibração; MCMC histórico permanece **NOT_RUN**. Rank racional **não é** informação de Fisher quantificada, probabilidade posterior nem redução geográfica.

Os três blocos de 61/23/35 épocas foram definidos depois da inspeção do corpus, portanto o bloco de avaliação **não é cego** e está sujeito à mesma linhagem documental. O programa apenas verifica identificabilidade e consistência do inventário; **não treina em fit, não otimiza em validation, não calcula log-score no evaluation**. Esse desenho evita transformar dados já vistos em um holdout falsamente independente. Para futuras predições, exigir congelamento dos modelos e controle externo ao catálogo, sob os gates em `CIRCULAR_LIKELIHOOD_CONTRACT.md`.

## Fontes, execução e próximos elos

- Dataset derivado: [raan_527_528_529_1963.json](raan_527_528_529_1963.json), uma única linhagem documental, **não elementos originais instrumentais**. O programa calcula SHA-256 dos bytes exatos.
- Holdout: [raan_chronological_holdout_1963.json](raan_chronological_holdout_1963.json), congelado e retrospectivo. Contagens e hash são reconfirmados pela rotina de custódia existente.
- Replay determinístico: [raan_observation_design_C241.json](raan_observation_design_C241.json). Testes adversariais [test_raan_observation_design.py](../../tests/test_raan_observation_design.py).
- Rodar: `python3 -m unittest discover -s tests -p test_raan_observation_design.py -v` e `python3 tools/raan_observation_design.py --input research/statistics/raan_527_528_529_1963.json --split research/statistics/raan_chronological_holdout_1963.json --check research/statistics/raan_observation_design_C241.json`.

**Próximos elos:** 🐢 Tartaruga: sensor, referência angular, épocas e erro de fonte original; 🦫 Castor: operador do estado físico para RAAN **média catalográfica** em época e referencial comuns. Essas dependências já estão abertas, não devem gerar pedidos redundantes. Sem ambas, o status permanece **NO_HISTORICAL_LIKELIHOOD / NO_GEOGRAPHIC_REDUCTION**. No grafo, registrar apenas conectividade e condições faltantes, com `active_constraint=false`.

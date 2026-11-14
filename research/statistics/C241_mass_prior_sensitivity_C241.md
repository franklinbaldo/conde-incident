---
type: Guide
title: "C241: sensibilidade analítica de priors sem verossimilhança de massa"
description: "Contraprova racional de falsa precisão na partição 527/528/529/X; sem MCMC histórico."
---

# Sensibilidade à escolha de prior, sem inferência de massa

A fonte secundária [GCAT C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json) atribui `TotMass=1176 kg` à linha **S00527** e `Mass=306 kg` à carga útil OPS. **Não** é medição da soma exclusiva de 527, 528 e 529 na mesma época; os zeros catalogados de 528/529 não são pesagens. O ledger [C241-L39](../tle_custody/mass_partition_C241-L39.json) permanece `USER_HYPOTHESIS_UNVERIFIED` e fisicamente inativo.

Apenas como hipótese, fixe `T=1176 kg`, `f=(f527,f528,f529,fX)`, `sum(f)=1` e prior `Dirichlet(alpha)` para `m_i=T*f_i`. Sem verossimilhança validada, as médias `T alpha_i/sum(alpha)` e variâncias `T² alpha_i (sum(alpha)-alpha_i) / (sum(alpha)² (sum(alpha)+1))` são **momentos do prior**, não estimativas de massas observadas.

| Prior arbitrário | Média de X, **somente cenário** |
| --- | ---: |
| `(1,1,1,1)` | `294 kg` |
| `(1,1,1,1/4)` | `1176/13 ≈ 90,46 kg` |
| `(4,1,1,1/4)` | `1176/25 = 47,04 kg` |

Multiplicar todas as concentrações por dez mantém as médias, mas diminui as variâncias, **sem acrescentar uma única observação**. Esse é um teste adversarial concreto de falsa certeza por prior. A seleção dos três priors apenas preserva cenários explicitados na [draft #634](https://github.com/franklinbaldo/conde-incident/pull/634); nenhum foi calibrado para 1963. A draft de integração [#641](https://github.com/franklinbaldo/conde-incident/pull/641) deve permanecer condicionada à genealogia física e aos contratos G48/G49/G50, sem transportar uma massa presumida para a dinâmica.

Reprodução offline: `python3 -m unittest discover -s tests -p test_mass_prior_sensitivity_C241.py -v` e `python3 -m tools.mass_prior_sensitivity_C241`. Os resultados são frações exatas, sem amostragem. `historical_mcmc=NOT_RUN`, `historical_mass_posterior=null`, `physical_domain_reduction=false`; nenhum ganho na localização do 528/Conde. Para identificar massa, buscar inventário primário por componente e época, limites de perda, geometria/Cd e densidade calibradas, observação instrumental independente e modelo de seleção/erro. Um diagnóstico de convergência MCMC futuro não substitui nenhum desses requisitos.

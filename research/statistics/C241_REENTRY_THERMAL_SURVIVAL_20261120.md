---
type: Experiment
title: "C241: sobrevivência aerotérmica na reentrada e energia terminal (NORAD 528 vs. 637)"
description: "Simulação Sutton-Graves/NRLMSIS-2.1 (120 km ao solo) e provas Lean 4 mostrando que peças finas de alumínio do 528 derretem a ~85 km, e que cascas de titânio/aço sobreviventes chegam ao solo com < 5 kJ (>600x abaixo de uma cratera de 4 m)."
experiment_id: C241-REENTRY-THERMAL-SURVIVAL-20261120
model_ref: formal/Conde1963/ReentryTerminalEnergyBound.lean
inputs_ref: research/statistics/c241_reentry_thermal_survival_20261120.json
verification_status: AEROTHERMAL_SURVIVAL_AND_LEAN4_ENERGY_BOUND
---

# Sobrevivência térmica e energia de impacto: NORAD 528 vs. NORAD 637

Este experimento conecta o coeficiente balístico do **NORAD 528** ($B = 0{,}236\text{ m}^2/\text{kg}$, [MCMC 10 meses](C241_MCMC_528_GEOMETRY_20261120.md) e [`BallisticGeometryBound.lean`](../../formal/Conde1963/BallisticGeometryBound.lean)) ao limite energético de cratera ([`TerminalCraterBound.lean`](../../formal/Conde1963/TerminalCraterBound.lean), piso gravitacional de `3.155 kJ` para 4 m).

## Método físico

- **Atmosfera:** perfil vertical **NRLMSIS-2.1** (`0–140 km`) em `1963-11-08T18:00Z` sobre a Bahia (`lat = -12,0°`, `lon = -37,6°`) com índices definitivos GFZ Potsdam.
- **Dinâmica e aquecimento:** integração RK2 de reentrada planar a partir de `120 km`, `v0 = 7,83 km/s`, ângulos rasos $\gamma_0 \in \{-0{,}5^\circ, -1{,}0^\circ, -2{,}0^\circ\}$; fluxo de estagnação de **Sutton-Graves** com ponte para regime molecular livre ($\dot{q}_{\text{fm}} = \frac{1}{2}\alpha_T \rho v^3$), fator de média em tombamento $f_{\text{avg}} = 0{,}25$, resfriamento radiativo $\varepsilon\sigma T^4$ e calor latente de fusão.
- **Velocidade terminal subsônica ao nível do mar:** $v_t = \sqrt{2 g / (\rho_0 B_{\text{sub}})}$ com $C_{d,\text{sub}} = 0{,}47$ (esfera) ou $1{,}1$ (chapa tombando).

## Resultados principais ($\gamma_0 = -1{,}0^\circ$)

| Caso | $B_{\text{hip}}$ (m²/kg) | Pico $\dot{q}_{\text{stag}}$ (kW/m²) | Alt. pico | $T_{\max} / T_{\text{fusão}}$ | Destino | $v_t$ subs. | $E_k$ solo |
|---|---:|---:|---:|---:|---|---:|---:|
| `528-A` Painel Al (`1,73 mm`, $R=0{,}3$ m) | `0,236` | `197,9` | `88,6 km` | `933 / 933 K` | **DERRETE @ 88,6 km** | — | — |
| `528-B` Casca Al (`0,86 mm`, $R=0{,}5$ m) | `0,236` | `174,9` | `85,0 km` | `933 / 933 K` | **DERRETE @ 85,0 km** | — | — |
| `528-B2` Casca Al (`0,86 mm`, $R=1{,}0$ m) | `0,236` | `127,5` | `83,0 km` | `933 / 933 K` | Sobrevive (limite) | `17,8 m/s` | `4,6 kJ` |
| `528-C` Casca Ti (`0,52 mm`, $R=0{,}5$ m) | `0,236` | `178,9` | `82,8 km` | `1116 / 1941 K` | **SOBREVIVE** | `17,8 m/s` | `1,1 kJ` |
| `528-D` Casca Aço (`0,30 mm`, $R=0{,}5$ m) | `0,236` | `178,9` | `82,8 km` | `1117 / 1700 K` | **SOBREVIVE** | `17,8 m/s` | `1,2 kJ` |
| `528-E` Painel Ti (`1,04 mm`, $R=0{,}3$ m) | `0,236` | `228,9` | `82,7 km` | `1188 / 1941 K` | **SOBREVIVE** | `11,7 m/s` | `0,3 kJ` |
| `637-A` Tanque Ti Agena (`4,0 mm`) | `0,031` | `638,3` | `71,9 km` | `1469 / 1941 K` | **SOBREVIVE** | `49,2 m/s` | `24,2 kJ` |
| `637-B` Câmara Aço Agena (`150 kg`) | `0,003` | `2059,8` | `55,5 km` | `1183 / 1700 K` | **SOBREVIVE** | `153,4 m/s` | `1765 kJ` |

*(Todos os destinos se mantêm idênticos em $\gamma_0 = -0{,}5^\circ$ e $-2{,}0^\circ$; tabela completa de 24 cenários em [c241_reentry_thermal_survival_20261120.json](c241_reentry_thermal_survival_20261120.json).)*

## Certificação em Lean 4 (`ReentryTerminalEnergyBound.lean`)

1. **Sobrevivência radiativa não implica cratera:** por frear alto (~82–83 km), uma casca fina de titânio ou aço com $B = 0{,}236\text{ m}^2/\text{kg}$ permanece abaixo do ponto de fusão (`1116–1251 K < 1700–1941 K`), mas chega ao solo a no máximo **`~18 m/s` (`~65 km/h`)**.
2. **`norad528_2m_shell_kinetic_le_4860J` e `norad528_surviving_shell_cannot_excavate_4m_crater`:** mesmo uma casca de `2 m` (`m ≤ 30 kg`, `v ≤ 18 m/s`) entrega **`E_k ≤ 4,86 kJ < 5 kJ`** — mais de **630 vezes abaixo** (`norad528_2m_shell_deficit_over_630x`) do piso gravitacional puro de `3.155 kJ` para uma cratera hemisférica de 4 metros.

```sh
python3 -m unittest discover -s tests -p test_c241_reentry_thermal_survival.py -v
```

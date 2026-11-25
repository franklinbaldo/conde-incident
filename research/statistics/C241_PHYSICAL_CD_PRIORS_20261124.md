---
type: Experiment
title: "C241: regime físico de Cd (Sentman + SESAM + Knudsen), priors de engenharia e controle negativo de tempestade (637 e 528)"
description: "Avalia o efeito de Cd(h, T, m_gas, alpha_E, Kn), priors de forma/massa/composição e calibração de tempestade q(ap) sobre NORAD 637, 528, 529 e Explorer 9 sob NRLMSIS-2.1."
experiment_id: C241-PHYSICAL-CD-PRIORS-20261124
model_ref: tools/c241_physical_cd_priors.py
inputs_ref: research/statistics/c241_physical_cd_priors_20261124.json
verification_status: EXPLORATORY_PHYSICAL_CD_AND_NEGATIVE_STORM_GAMMA_CONTROL
---

# Regime físico de $C_d$, priors de engenharia e controle negativo de tempestade (637 e 528)

Este estudo substitui a aproximação $C_d = 2{,}2$ constante usada em [C241-MCMC-528](C241_MCMC_528_GEOMETRY_20261120.md) e [C241-MSIS-HOLDOUT](C241_MSIS_DECAY_HOLDOUT_20261120.md) por um modelo físico de coeficiente de arrasto **$C_d(h, T, m_{\text{gas}}, \alpha_E, \text{Kn})$** alimentado pelas densidades parciais ($N_2, O_2, O, He, H, Ar, N$) e temperatura do **NRLMSIS-2.1** (`pymsis 0.13.0`) + **GFZ Potsdam**:

- **Regime molecular livre:** fórmulas de **Sentman (1961)** (esfera, placa plana em tombamento uniforme e cilindro tombando/perpendicular).
- **Acomodação de energia:** modelo **SESAM (Pilinski/Moe)** por adsorção de oxigênio atômico $P_O = n_O k_B T$ ($\alpha_E \in [0{,}70; 0{,}98]$).
- **Transição de Knudsen ($h \lesssim 180\text{ km}$):** ponte contínua para o regime hipersônico contínuo ($C_{d,\text{cont}} = 0{,}92$ esfera / $1{,}15$ placa e cilindro).

## 1. $C_d = 2{,}2$ fixo vs. $C_d$ físico (NORAD 637 e NORAD 528)

| Objeto / Forma | Modelo $C_d$ | Faixa de $C_d$ | $\langle A \rangle / m$ [m²/kg] | $\sigma_f$ | BIC | $\beta_{\text{res}}$ / 100 km | Reentrada ($\Delta$ vs. fixo) |
|---|---|---|---:|---:|---:|---:|---|
| **637** (`cyl_tumble`, $L_{\text{char}}=3{,}5$ m) | Fixo `2,2` | `2,200` | `0,00819` | `12,25%` | `65,05` | `+0,107` | `07/11 11:29Z` (`0,00 h`) |
| **637** (`cyl_tumble`, $L_{\text{char}}=3{,}5$ m) | **Físico** | `2,236–2,374` (`1,99` @ 120 km) | **`0,00797`** | **`9,66%`** | `65,43` | **`+0,047`** | `07/11 12:50Z` (**`+1,35 h`**) |
| **637** (`cyl_tumble`, $L_{\text{char}}=1{,}52$ m) | **Físico** | `2,10` @ 120 km | `0,00797` | — | — | — | `07/11 12:30Z` (**`+1,02 h`**) |
| **528** (`plate_tumble`, $L_{\text{char}}=0{,}8$ m) | Fixo `2,2` | `2,200` | `0,10735` | `14,33%` | `87,65` | `-0,147` | `08/11 23:04Z` (`0,00 h`) |
| **528** (`plate_tumble`, $L_{\text{char}}=0{,}8$ m) | **Físico** | `2,380–2,660` (`2,19` @ 120 km) | `0,09344` | `16,06%` | `90,89` | `-0,238` | `10/11 00:51Z` (**`+25,78 h`**) |
| **528** (`sphere`, $L_{\text{char}}=0{,}8$ m) | **Físico** | `2,073–2,131` (`2,02` @ 120 km) | `0,11254` | `14,65%` | `88,15` | `-0,169` | `09/11 03:54Z` (**`+4,83 h`**) |

- **Ganho real no 637:** o $C_d$ físico reduz $\sigma_f$ em **~21%** (`12,25% → 9,66%`), reduz a inclinação residual de altitude (`+0,107 → +0,047`) e corrige o viés terminal em `+1,02 a +1,35 h` (aproximando MSIS-2.1 da mediana NRLMSISE-00).
- **Diagnóstico de forma no 528:** uma placa perfeitamente plana com $\alpha_E$ caindo a 450 km gera queda excessiva de $C_d$ na descida, piorando o BIC (`+3,24`) e atrasando a reentrada em **`+25,78 h`** (`10/11`, fora do dia NASA `08/11`). Geometrias com variação fraca de $C_d$ (superfície rugosa/oxidada ou casca curva/esfera) mantêm o ajuste estável.

## 2. Priors de engenharia (forma, massa, composição e densidade)

- **NORAD 637 (Thor Agena D 1169, $D = 1{,}524\text{ m}$, $L \in [6{,}0; 7{,}6]\text{ m}$, piso seco $\ge 670\text{ kg}$):**
  - **Tombamento uniforme (Cauchy):** $m = 1015{,}5\text{–}1255{,}8\text{ kg}$ (coerente com Agena D + equipamento KH-4 sem SRV).
  - **Gradiente de gravidade (eixo vertical):** $m = 1147{,}3\text{–}1453{,}2\text{ kg}$.
  - **Alinhado ao fluxo (axial):** $m = 299{,}9\text{–}326{,}3\text{ kg}$ — **excluído** contra o piso seco do estágio (`670 kg`).
- **NORAD 528 (`1963-003B`):** corrigir $C_d$ altera a espessura inferida em apenas **5–13%** (Mg HK31A: chapa `2,95 mm` / casca `1,25 mm`; Al 2024: `1,95 / 0,82 mm`; Ti-6Al-4V: `1,19 / 0,50 mm`; Aço 304: `0,67 / 0,28 mm`), preservando intactos os limites Lean 4 de [`BallisticGeometryBound.lean`](../../formal/Conde1963/BallisticGeometryBound.lean) e [`ReentryTerminalEnergyBound.lean`](../../formal/Conde1963/ReentryTerminalEnergyBound.lean), sem quebrar o gauge de massa absoluta ([gauge](C241_drag_density_mass_gauge.md)).

## 3. Controle negativo/marginal: calibração de tempestade $q(a_p) = \exp(\gamma (a_{p,\text{eff}}-10)/100)$

- **Ajustes individuais (nenhum vence BIC):** Explorer 9 ($\gamma = +0{,}300$, $\Delta\text{BIC}=+1{,}47$), 529 ($\gamma = -0{,}158$, $\Delta\text{BIC}=+2{,}50$), 637 ($\gamma = +0{,}247$, $\sigma_f: 9{,}66\% \to 7{,}33\%$, $\Delta\text{BIC}=+0{,}89$) e 528 ($\gamma = +0{,}028$, $\Delta\text{BIC}=+3{,}77$).
- **Holdout estrito pré-28/10 → pós-27/10 (MLE conjunto $\gamma = +0{,}150$):** melhora `rel_RMSE` fora da amostra no **637** (`0,168 → 0,141`, -16%), empata no **Explorer 9** (`0,130 → 0,129`) e piora levemente no **529** (`0,146 → 0,151`).
- **Decisão:** `storm_gamma_promoted=false`. O parâmetro $\gamma$ não é promovido ao modelo do 528; NRLMSIS-2.1 + GFZ já opera perto do piso residual (~10–15%) dos TLEs secundários de 1963.

## Contrato negativo e reprodutibilidade

`historical_event_time_utc=null`, `mass_528_identified=false`, `storm_gamma_promoted=false`, `impact_geography=null`.

```sh
python3 -m unittest discover -s tests -p test_c241_physical_cd_priors.py -v
```

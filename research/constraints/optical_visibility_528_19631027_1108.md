---
type: Experiment
title: "Verificação de visibilidade óptica e sensibilidade B* do NORAD 528 (27 out – 8 nov 1963)"
description: "Simulação SGP4 reprodutível mostra zero passagens opticamente visíveis em Durban, Slough, Baja e Meudon entre 27 out e 8 nov 1963 sob o TLE secundário (RAAN 198,53°), e quantifica o avanço de fase along-track sob ajuste de B*."
experiment_id: "EXP-OPTICAL-VISIBILITY-528-19631027-1108"
model_ref: "formal/scripts/check_528_optical_visibility_oct_nov_1963.py"
inputs_ref: "research/tle_custody/mirror_528_1963-10-27.tle"
verification_status: "EXPLORATORY_SGP4_GEOMETRIC_CHECK"
---

# Experimento: visibilidade óptica e sensibilidade $B^*$ do NORAD 528 (27 out – 8 nov 1963)

## Objetivo e escopo epistêmico

Testar se observadores ópticos em **Durban**, **Slough**, **Baja** ou **Meudon** tinham geometria de iluminação solar favorável para observar **`NORAD 528` (`1963-003B`)** entre a época do TLE secundário (`1963-10-27 14:40:16 UTC`) e a data-dia de decaimento (`1963-11-08 23:59:59 UTC`), e medir o deslocamento *along-track* ao calibrar `B*` para forçar decaimento no dia 8 nov 1963.

**Limites explícitos:**
- Cálculo exploratório em **SGP4** condicional ao par secundário [`mirror_528_1963-10-27.tle`](../tle_custody/mirror_528_1963-10-27.tle) (`RAAN 198.5261°`, `i = 81.8615°`, `n = 15.74901460 rev/dia`, `B* = 0`).
- **Não** determina horário ou local de reentrada terminal e **não** substitui observações primárias nem integrações com atmosfera física calibrada.
- A exclusão óptica abaixo é condicional ao par secundário `mirror_528_1963-10-27.tle` (`RAAN 198.5261°`), cuja custódia primária NORAD/SPADATS de 1963 permanece pendente.

## Método e reprodutibilidade

- **Código:** [`formal/scripts/check_528_optical_visibility_oct_nov_1963.py`](../../formal/scripts/check_528_optical_visibility_oct_nov_1963.py)
- **Saída JSON:** [`optical_visibility_528_19631027_1108.json`](optical_visibility_528_19631027_1108.json)
- **Execução:** `uv run --with sgp4 --with numpy python3 formal/scripts/check_528_optical_visibility_oct_nov_1963.py --write`
- **Parâmetros:** passo temporal de `10 s`, elevação mínima do satélite $h_{\text{sat}} \ge 10^\circ$, cone cilíndrico de sombra da Terra ($R_E = 6378.137\text{ km}$), limiares de crepúsculo $h_\odot \le -6^\circ$ e $h_\odot \le 0^\circ$, GMST IAU 1982 e efeméride solar de baixa precisão (~`0.01°`).
- **Cenários de $B^*$:**
  - `Nominal_Bstar_0`: TLE literal (`B* = 0`, sem decaimento em 12 dias, altitude `~330–363 km`).
  - `B1_early_Nov8`: `B* = 0.008154` (decaimento SGP4 $h < 120\text{ km}$ em `1963-11-07 23:58 UTC`).
  - `B2_mid_Nov8`: `B* = 0.007813` (decaimento SGP4 em `1963-11-08 13:20 UTC`).
  - `B3_late_Nov8`: `B* = 0.007500` (decaimento SGP4 em `1963-11-08 23:57 UTC`).

## Resultados

### 1. Geometria orbital vs. Sol (Nominal)

- Em `27 out 14:40 UTC`: $\Omega = 198.53^\circ$, $\alpha_\odot = 211.23^\circ \implies \Omega - \alpha_\odot = -12.70^\circ$.
- Em `08 nov 14:40 UTC`: $\Omega = 184.47^\circ$, $\alpha_\odot = 223.01^\circ \implies \Omega - \alpha_\odot = -38.54^\circ$.
- O plano orbital permanece próximo da linha **meio-dia / meia-noite** (longe do terminador $\pm 90^\circ$) durante toda a janela.

### 2. Passagens opticamente visíveis por estação (27 out – 8 nov 1963)

| Estação | Passagens $h_{\text{sat}} \ge 10^\circ$ (Nom / B2) | Noturnas $h_\odot \le -6^\circ$ (Nom / B2) | Visíveis $h_\odot \le -6^\circ$ | Visíveis $h_\odot \le 0^\circ$ | Menor $h_\odot$ iluminado (Nom / B2) |
| :--- | :---: | :---: | :---: | :---: | :---: |
| **Durban** (`-29.88°, 31.02°`) | 29 / 22 | 16 / 11 | **0 / 0** | **0 / 0** | `+41.89°` / `+46.45°` |
| **Slough** (`51.48°, -0.56°`) | 39 / 30 | 20 / 15 | **0 / 0** | **0 / 0** | `+12.89°` / `+16.33°` |
| **Baja** (`46.18°, 18.96°`) | 34 / 28 | 18 / 14 | **0 / 0** | **0 / 0** | `+20.51°` / `+19.63°` |
| **Meudon** (`48.80°, 2.23°`) | 38 / 27 | 20 / 14 | **0 / 0** | **0 / 0** | `+15.97°` / `+19.47°` |

Os cenários `B1` e `B3` também produzem **0 passagens visíveis** em todas as 4 estações sob ambos os limiares ($h_\odot \le -6^\circ$ e $h_\odot \le 0^\circ$).

### 3. Sensibilidade *along-track* (`B2` adiantado em relação ao Nominal `B* = 0`)

| Tempo após época | Altitude `B2` | Avanço de fase (`B2 - Nom`) | Deslocamento aprox. $\Delta t$ |
| :--- | :---: | :---: | :---: |
| `t + 1.0 d` (`28 out 14:40Z`) | `356.4 km` | `+0.012 rev` | `+1.1 min` |
| `t + 2.0 d` (`29 out 14:40Z`) | `334.9 km` | `+0.050 rev` | `+4.6 min` |
| `t + 4.0 d` (`31 out 14:40Z`) | `295.6 km` | `+0.219 rev` | `+20.0 min` |
| `t + 6.0 d` (`02 nov 14:40Z`) | `290.3 km` | `+0.543 rev` | `+49.5 min` |
| `t + 8.0 d` (`04 nov 14:40Z`) | `251.1 km` | `+1.089 rev` | `+99.2 min` |
| `t + 10.0 d` (`06 nov 14:40Z`) | `187.2 km` | `+1.937 rev` | `+176.6 min` |
| `t + 11.0 d` (`07 nov 14:40Z`) | `185.0 km` | `+2.513 rev` | `+229.0 min` |
| `t + 11.83 d` (`08 nov 10:40Z`) | `126.6 km` | `+3.085 rev` | `+281.1 min` |

## Implicação prática para busca documental

Sob o ramo `RAAN 198.5261°`, **não havia condição geométrica de observação óptica passiva (luz solar refletida)** para `NORAD 528` entre 27 out e 8 nov 1963 em Durban, Slough, Baja ou Meudon. Assim:
- Para a quinzena terminal (`27 out – 8 nov 1963`), a busca arquivística deve priorizar **dados de radar** (NORAD/SPADATS/AFSPC);
- Para **observações ópticas/amadoras de `528`**, a janela geométrica favorável ocorreu ~35–45 dias antes (**meados de setembro de 1963**), quando $\Omega - \alpha_\odot$ cruzou o terminador.

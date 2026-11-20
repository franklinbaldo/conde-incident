---
type: Experiment
title: "C241: decaimento orbital com NRLMSIS-2.1/NRLMSISE-00, clima espacial GFZ e calibradores Explorer 9/529"
description: "Holdout cronológico estrito contra o baseline King-Hele R68 e cenários exploratórios do NORAD 528, sem calibração horária ou geográfica."
experiment_id: C241-MSIS-DECAY-HOLDOUT-20261120
model_ref: tools/c241_msis_decay_holdout.py
inputs_ref: research/statistics/c241_msis_decay_holdout_20261120.json
verification_status: RETROSPECTIVE_EXPLORATORY_NOT_CALIBRATED_FOR_IMPACT
---

# Decaimento termosférico com NRLMSIS-2.1 e NRLMSISE-00 (1963)

Este experimento substitui o proxy local de altura de escala constante ($H=40/50$ km) do [R68](C241_UNIFIED_DECAY_DAY_ERRORS_R68_20261115.md) e [R69](C241_528_CENSORED_ERROR_TRANSFER_R69_20261115.md) por um integrador de arrasto promediado na órbita (equações de Gauss tangenciais em 24 pontos de anomalia excêntrica + precessão $J_2$ em RK2) acoplado aos modelos termosféricos **NRLMSIS-2.1** e **NRLMSISE-00** (`pymsis 0.13.0`), alimentados pela série histórica definitiva de $F_{10.7}$ e $a_p$ tri-horário do **GFZ Potsdam**.

## Fontes e proveniência

- **TLEs secundários de 1963:** [oxzoid/space-track-tle-history, revisão `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` (4.567 linhas; família catalográfica secundária única, não medições originais independentes).
- **Clima espacial histórico:** [GFZ Potsdam `Kp_ap_Ap_SN_F107_since_1932.txt`](https://kp.gfz.de/app/files/Kp_ap_Ap_SN_F107_since_1932.txt), SHA-256 capturado `5f479a3d98019dbe2324e9dd744932bfb894380ca1b3e9911307b497f890d884`. Usa $F_{10.7}$ observado do dia anterior, média centrada de 81 dias ($F_{10.7a}$, retrospectiva) e vetor de 7 posições `ap` padrão MSIS.
- **Rótulos de dia de decaimento:** mesmos controles do R68 — 637 (`1963-11-07`, NASA SSR 15/11), 292 (`1963-11-26`, secundário), 565 (`1963-11-24`, secundário) e 308 (`1963-10-30`, secundário/alias OMEGA 1 condicional). Nenhum rótulo traz hora UTC.

## 1. Tempestades geomagnéticas na janela do 528

Entre o último TLE do 528 (`1963-10-27T14:40Z`) e o dia catalogado `1963-11-08`, o GFZ registra tempestades geomagnéticas relevantes — especialmente fortes em altas latitudes ($i \approx 81{,}86°$):

| Data UTC | $A_p$ diário | Pico $a_p$ (3h) | $F_{10.7}$ obs. | Contexto |
|---|---:|---:|---:|---|
| `1963-10-24` | 63 | 154 | 95,0 | Tempestade 3 dias antes do último TLE do 528 |
| `1963-10-27` | 4 | 7 | 89,0 | Calmo; época do último TLE do 528 |
| `1963-10-29` | 74 | 207 | 85,5 | Tempestade severa no início do gap do 528 |
| `1963-10-30` | 35 | 179 | 86,0 | Continuação da tempestade |
| `1963-11-07` | 39 | 80 | 76,6 | Tempestade no dia NASA do 637 |
| `1963-11-08` | 46 | 80 | 75,4 | Tempestade no dia NASA do 528 |
| `1963-11-09` | 33 | 48 | 76,4 | Continuação da tempestade |

## 2. Calibradores de densidade: Explorer 9 (NORAD 81) e NORAD 529

Usando MSIS-2.1 sobre intervalos consecutivos de TLEs:

- **Explorer 9 (NORAD 81, esfera inflável de 3,66 m, perigeu ~415 km):** mediana pré-28/10 de $B_{\text{eff}} = 3{,}82495\text{ m}^2/\text{kg}$ (coerente com geometria física conhecida da esfera). Razão $\rho_{\text{obs}} / \rho_{\text{MSIS-2.1}}$ durante o gap do 528: `0,993×` (`27/10–01/11`), `0,961×` (`01/11–07/11`) e **`1,295×`** (`07/11–11/11`, indicando densidade real ~30% acima do MSIS-2.1 na tempestade de 7–9/11).
- **NORAD 529 (`1963-003C`, mesmo plano quase polar $81{,}9°$, perigeu ~384 km):** mediana pré-28/10 de $B_{\text{eff}} = 0{,}22774\text{ m}^2/\text{kg}$. Razão no gap: `1,120×` (`28–31/10`), `1,308×` (`31/10–01/11`), `0,866×` (`01–02/11`) e `1,179×` (`02–05/11`).
- **Contraste balístico:** sob MSIS-2.1, 528 (`~0,22–0,24 m²/kg`) e 529 (`~0,23 m²/kg`) exibem razão efetiva área/massa **~10× maior** que objetos compactos como 637 (`0,019`), 292 (`0,022`) e 308 (`0,017`). Isso não separa massa de área ([gauge](C241_drag_density_mass_gauge.md)).

## 3. Holdout cronológico estrito (MSIS vs. baseline King-Hele R68)

Em cada corte, $B_{\text{fit}}$ é a mediana dos intervalos estritamente anteriores ao corte (janela até 35 dias), sem vazamento de épocas futuras. Os erros abaixo são condicionais ao contrafactual de dia civil UTC (`(mín, máx]` em dias):

| NORAD (rótulo) | Corte UTC | King-Hele R68 ($H=40/50$) | **MSIS-2.1** (erro d) | **NRLMSISE-00** (erro d) |
|---|---|---|---|---|
| 637 (`07/11`) | `1963-10-18` | `(+0,81; +7,34]` | **`(-0,05; +0,95]` HIT** | `(+0,41; +1,41]` |
| 637 (`07/11`) | `1963-10-23` | — | **`(-0,60; +0,40]` HIT** | **`(-0,19; +0,81]` HIT** |
| 637 (`07/11`) | `1963-10-27` | — | `(-1,34; -0,34]` | `(-1,01; -0,01]` |
| 637 (`07/11`) | `1963-10-30` | — | **`(-0,80; +0,20]` HIT** | **`(-0,56; +0,44]` HIT** |
| 292 (`26/11`) | `1963-11-12` | `(+3,36; +9,69]` | `(-1,28; -0,28]` | `(-1,82; -0,82]` |
| 292 (`26/11`) | `1963-11-16` | — | **`(-0,79; +0,21]` HIT** | **`(-0,85; +0,15]` HIT** |
| 292 (`26/11`) | `1963-11-20` | — | **`(-0,36; +0,64]` HIT** | **`(-0,26; +0,74]` HIT** |
| 292 (`26/11`) | `1963-11-23` | — | **`(-0,36; +0,64]` HIT** | **`(-0,31; +0,69]` HIT** |
| 565 (`24/11`) | `1963-11-10` | `(-7,22; -3,14]` | `(-3,55; -2,55]` | `(-2,82; -1,82]` |
| 565 (`24/11`) | `1963-11-21` | — | **`(-0,35; +0,65]` HIT** | **`(-0,49; +0,51]` HIT** |
| 308 (`30/10`) | `1963-10-16` | `(-0,02; +4,98]` | `(+0,62; +1,62]` | `(+0,91; +1,91]` |
| 308 (`30/10`) | `1963-10-20` | — | **`(-0,66; +0,34]` HIT** | **`(-0,43; +0,57]` HIT** |

Tabela completa de 32 linhas em [c241_msis_decay_holdout_20261120.json](c241_msis_decay_holdout_20261120.json). Em horizontes de 10–20 dias, o erro típico nos controles cai de ~4–10 dias (King-Hele R68) para **~0,5–1,5 dia** (pior caso: ~3,5 dias no 565 em 14 dias).

## 4. Cenários exploratórios para o NORAD 528

Origem `1963-10-27T14:40:16Z` ($a=6723{,}049$ km, $h_p=333{,}4$ km, $h_a=356{,}4$ km), sem ajuste ao rótulo NASA `1963-11-08`:

| Modelo | Cenário de ajuste pré-28/10 | $B_{\text{fit}}$ (m²/kg) | Fator $q$ | Decaimento exploratório UTC |
|---|---|---:|---:|---|
| MSIS-2.1 | Mediana Set–Out | `0,22287` | `1,00` | `1963-11-09T15:38Z` |
| MSIS-2.1 | Mediana Outubro | `0,23583` | `1,00` | `1963-11-08T23:18Z` |
| MSIS-2.1 | Mediana últimos 3 intervalos | `0,29036` | `1,00` | `1963-11-06T17:08Z` |
| MSIS-2.1 | Mediana Set–Out + sensib. $q=1{,}15$ | `0,22287` | `1,15` | `1963-11-08T01:09Z` |
| NRLMSISE-00 | Mediana Set–Out | `0,19037` | `1,00` | `1963-11-09T03:09Z` |
| NRLMSISE-00 | Mediana Outubro | `0,19684` | `1,00` | `1963-11-08T17:30Z` |
| NRLMSISE-00 | Mediana últimos 3 intervalos | `0,24493` | `1,00` | `1963-11-06T08:52Z` |
| NRLMSISE-00 | Mediana Set–Out + sensib. $q=1{,}15$ | `0,19037` | `1,15` | `1963-11-07T14:45Z` |

No cenário `MSIS-2.1 / median_oct`, o perfil diário de perigeu/apogeu cai de `333,4 / 356,4 km` (27/10) para `314,1 / 333,7 km` (01/11), `288,4 / 302,8 km` (05/11), `266,7 / 277,3 km` (07/11) e `241,2 / 248,5 km` (08/11 02:40Z) antes da queda terminal a 120 km.

## Contrato negativo e reprodutibilidade

Os horários acima **não são instantes físicos observados de reentrada**. A dispersão entre janelas de ajuste (`06/11` a `09/11`) e o erro residual dos controles (~±1–1,5 dia) correspondem a dezenas de revoluções orbitais de incerteza na fase, impedindo localização geográfica ou hora terminal.

`historical_event_time_utc=null`, `terminal_time_sigma_hours=null`, `calibrated_terminal_holdouts=0`, `historical_mcmc=NOT_RUN`, `active_constraint_528=false`, `impact_geography=null`.

```sh
python3 -m unittest discover -s tests -p test_c241_msis_decay_holdout.py -v
# Reexecução completa (requer pyarrow, numpy, pymsis e arquivos GFZ/Parquet locais):
python3 tools/c241_msis_decay_holdout.py --parquet tle_1963.parquet --gfz Kp_ap_Ap_SN_F107_since_1932.txt --output research/statistics/c241_msis_decay_holdout_20261120.json
```

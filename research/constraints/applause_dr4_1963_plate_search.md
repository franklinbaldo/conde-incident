---
type: Experiment
title: "Busca em chapas astronômicas de 1963 (APPLAUSE DR4) e teste Radon na chapa Boyden 27600"
description: "Cruzamento SGP4 de 3.826 exposições resolvidas de 1963 no APPLAUSE DR4 (NORAD 527/528/529/637) e busca por rastro/glint no FITS original de 10 jun 1963 (plate 27600), com resultado nulo não-eliminatório."
experiment_id: "EXP-APPLAUSE-DR4-1963-PLATE-SEARCH"
model_ref: "formal/scripts/check_applause_dr4_1963_plates.py"
inputs_ref: "research/constraints/applause_dr4_1963_plate_search.json"
verification_status: "NULL_DETECTION_NON_EXCLUSIONARY"
---

# Experimento: chapas astronômicas de 1963 (APPLAUSE DR4) e teste Radon na chapa Boyden `27600`

## Objetivo e escopo epistêmico

Avaliar duas hipóteses operacionais sobre chapas fotográficas astronômicas digitalizadas de 1963:
1. **Auditoria independente do catálogo secundário NASA/Space-Track:** se um rastro de `NORAD 527`, `528`, `529` ou `637` aparecer em uma chapa de 1963 com astrometria Gaia EDR3, isso fornece uma medição primária independente do plano orbital e da época.
2. **Eliminação de trajetórias por detecção negativa:** verificar em quais condições instrumentais a ausência de rastro pode (ou **não** pode) descartar uma família de trajetórias.

**Classificação epistêmica:** inferência quantitativa combinando chapa fotográfica primária de 1963 (APPLAUSE DR4, CC0 1.0) com elementos orbitais do espelho secundário Space-Track (`oxzoid/space-track-tle-history`, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`). Estado no grafo cumulativo: **`CONNECTED_PENDING_CALIBRATION` / `NULL_DETECTION_NON_EXCLUSIONARY`**.

## 1. Varredura completa de 1963 no APPLAUSE DR4 (3.826 exposições)

Consulta via TAP/ADQL (`https://www.plate-archive.org/tap/sync`) entre `1963-01-17` e `1963-11-08` (`JD 2438046.5–2438342.5`), incluindo exposições com `jd_start + exptime` sem `jd_end` explícito:

| Arquivo | Telescópio / Abertura | Exposições resolvidas (1963) | Cruzamentos iluminados (`527/528/529/637`) |
| :--- | :--- | :---: | :---: |
| `203` Boyden (Bloemfontein) | Patrulha Bamberg `0,10 m` f/6 | 1.917 | `0 / 3 / 0 / 0` |
| `401` Tautenburg | Schmidt `1,34 m` | 1.345 | `0 / 0 / 0 / 0` (`528` em sombra em `70719`) |
| `208` Bamberg Norte | Astrógrafo | 200 | `0 / 0 / 0 / 0` |
| `106` Hamburgo | AG-Astrógrafo `0,15 m` | 148 | `0 / 0 / 0 / 0` |
| `102` Hamburgo | Schmidt `0,80 m` | 118 | `0 / 0 / 0 / 0` |
| `202` Harvard-Boyden | Metcalf `0,25 m` | 53 | `0 / 0 / 0 / 0` |
| `301` Tartu | Petzval | 45 | `0 / 0 / 0 / 0` |
| **Total** | **7 arquivos** | **3.826** | **`3` (todos `NORAD 528`, `1963-06-10`)** |

- A raridade de cruzamentos iluminados decorre do horário astronômico: a maioria das exposições ocorre perto da meia-noite local, quando satélites LEO (~400–500 km) atravessam a sombra da Terra.
- Entre `26 out` e `3 nov 1963`, Boyden não tem chapas no APPLAUSE DR4 devido à **Lua Cheia de 1 nov 1963**; quando retomou (`4–6 nov`), `NORAD 637` já passava na sombra.

## 2. Análise da chapa real Boyden `27600` (`000011_1963_h.fits`)

- **Fonte primária (CC0 1.0):** `https://www.plate-archive.org/files/DR4/scans/Bamberg-South/000011_1963_h.fits` (`408.816.000 bytes`, SHA-256 `9526acc0f1f743befdc46502ee8c3c4399815ffee755ff31b48bff4cad959f0c`).
- **Exposição:** `1963-06-10 16:20:00–16:50:00 UTC` (`1800 s`, emulsão Perutz-Astro, `14.000 × 14.600 px`, `3,546"/px`, solução Gaia EDR3 com 744 estrelas).
- **Trajetória SGP4 prevista para `NORAD 528`** (TLE `1963-06-12 00:43:50 UTC`, $\Delta t = -1,339\text{ d}$): cruza toda a chapa em `25 s` (`16:49:16–16:49:40 UTC`), entrada `(3519.6, 14555.7)` → saída `(252.2, 322.3)`, elevação `47,4°`, distância `583 km`, ângulo de fase solar `79,7°`, taxa aparente `0,595°/s` (`602,3 px/s`). (`plate=27601` tem apenas raspe de 2 s no canto; `plate=27602` fica fora do retângulo WCS.)

### Resultado da busca Radon / glint vs. controle nulo (`+2500 px` a leste)

| Métrica (`±600 px = ±0,59°`) | Faixa `NORAD 528` | Controle nulo (`+2500 px`) |
| :--- | :---: | :---: |
| Radon reto (`6.137` linhas empilhadas) | `SNR = +3,30` | `SNR = +2,53` |
| Radon inclinado (`\|Δθ\| ≤ 1°`) | `SNR = +4,20` | `SNR = +4,75` |
| Glint curto (`~0,5 s`, `\|v\| ≤ 150 px`) | `SNR = +5,56` | `SNR = +5,35` |

O satélite de controle `NORAD 292` (também iluminado por `25 s` na mesma chapa, `537 km`, $\Delta t_{\text{TLE}} = +1,46\text{ d}$) apresentou `SNR = +3,95`, igualmente no nível do ruído.

## 3. Física da não-detecção (por que NÃO elimina a trajetória)

A `602,3 px/s`, o `NORAD 528` permanece apenas **`~5 ms`** sobre cada elemento de resolução (`~3 px = 10,6"`), contra `1.800 s` das estrelas fixas (fator de `360.000×` em tempo de integração, somado à falha de reciprocidade fotográfica). Numa lente de patrulha de `10 cm`, a perda por arraste limita a detecção a objetos móveis de aproximadamente **mag `4–6`**.

Logo:
- A ausência de rastro na chapa `27600` é **totalmente compatível** com um fragmento pequeno (`mag ~8–10` estacionária) sem reflexo especular brilhante durante os `25 s` de passagem.
- **Não** constitui exclusão de trajetória nem refutação do TLE; uma não-detecção só teria poder eliminatório com calibração fotométrica demonstrando que o brilho esperado excede o limite de arraste daquela chapa (ex.: corpo grande como Agena D ou telescópio Schmidt grande com passagem iluminada).

## Reprodutibilidade

- Validação offline do artefato JSON:
  `python3 formal/scripts/check_applause_dr4_1963_plates.py --check-json research/constraints/applause_dr4_1963_plate_search.json`
- Reexecução completa sobre o FITS original:
  `uv run --with numpy --with astropy --with scipy python3 formal/scripts/check_applause_dr4_1963_plates.py --analyze-fits /tmp/000011_1963_h.fits`

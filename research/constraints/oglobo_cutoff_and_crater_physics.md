---
type: Experiment
title: "Corte temporal de O Globo (08/11) e limite energético da cratera de 4 m"
description: "Análise quantitativa e provas condicionais em Lean 4.35.0 para o teto temporal da apuração de O Globo e para a energia de escavação de uma cratera de 4 m por destroço subsônico de Agena D."
experiment_id: "EXP-OGLOBO-CUTOFF-CRATER-20261119"
model_ref: "formal/scripts/check_oglobo_cutoff_and_crater_physics.py"
inputs_ref: "research/archive/conde_o_globo_1963_11_08_p01.json; research/archive/conde_o_globo_1963_11_09_p04.json; research/constraints/optical_visibility_528_19631027_1108.json"
verification_status: "verified_conditional_lean_and_python"
---

# Corte temporal de *O Globo* (08/11) e limite energético da cratera de 4 m

## 1. Corte temporal causal (`NewspaperTemporalCutoff.lean`)
Os fac-símiles primários [`C241-OGLOBO-19631108-P01`](../archive/conde_o_globo_1963_11_08_p01.md) e [`C241-OGLOBO-19631109-P04`](../archive/conde_o_globo_1963_11_09_p04.md) mostram que a história completa já estava impressa em *O Globo* de `08/11/1963` (p. 1) e que o jornal já consultava o Ministério da Aeronáutica *"até ontem à tarde"*.

- **Teto conservador para "ontem à tarde":** `18:00` BA (`UTC-3`) = `21:00 UTC` (minuto `1260` de `08/11`). Em horário de verão do Rio (`UTC-2`), `18:00` Rio seria `20:00 UTC` (`1200`), ainda mais cedo.
- **Passagens nominais do plano orbital do `NORAD 528` sobre Conde (`11,81°S, 37,61°W`) em `08/11/1963`** (com `RAAN(27/10) = 198,5261°`, deriva `J₂ = -1,173°/dia` → `RAAN ≈ 184,45°`):
  - **Manhã (ascendente):** `11:34 UTC` (`08:34` BA, minuto `694`) — **não excluída** por um corte vespertino (depende do horário exato de fechamento da edição `PRM1`).
  - **Noite (descendente):** `23:45 UTC` (`20:45` BA, minuto `1425`) — **excluída condicionalmente** mesmo com margem generosa de `±90 min` (`1260 + 90 = 1350 ≤ 1425`).

Certificado em Lean 4.35.0: [`NewspaperTemporalCutoff.lean`](../../formal/Conde1963/NewspaperTemporalCutoff.lean) (`causal_report_excludes_later_pass`, `oglobo_afternoon_excludes_nov08_evening_528`, `morning_528_pass_remains_before_afternoon_cutoff`).

## 2. Limite trabalho-energia para um "buraco de quatro metros" (`TerminalCraterBound.lean`)
O texto de *O Globo* de `08/11` afirma um *"buraco de quatro metros de profundidade"*. Para escavar uma cratera hemisférica de profundidade `d = 4,0 m` em solo arenoso (`ρ = 1.600 kg/m³`), o trabalho mínimo (mesmo com **100% de eficiência mecânica**) é:
- **Apenas gravidade/sobrecarga (`Y = 0`):** `3.154,7 kJ` (`3,15 MJ`).
- **Areia fofa (`Y = 50 kPa`):** `9.856,8 kJ` (`9,86 MJ`).

Comparando com a energia cinética `E_k = ½ m v_t²` em velocidade terminal subsônica no nível do mar (`ρ_ar = 1,225 kg/m³`):

| Objeto / cenário | Massa (kg) | Diâm. (m) | `v_t` (m/s) | `E_k` (kJ) | `d_max` (`Y = 50 kPa`) | `d_max` (`Y = 0`) |
|---|---:|---:|---:|---:|---:|---:|
| Esfera oca de Ti | 20 | 0,50 | 58,9 | 34,7 | 0,67 m | 1,29 m |
| Tanque pressurizado | 45 | 0,60 | 73,6 | 122,0 | 1,01 m | 1,77 m |
| "Grande globo metálico" | 150 | 1,50 | 53,8 | 216,9 | 1,22 m | 2,05 m |
| "Grande globo metálico" | 300 | 2,00 | 57,0 | 487,9 | 1,58 m | 2,50 m |
| Câmara de combustão Agena | 150 | 0,50 | 156,4 | 1.835,1 | 2,39 m | 3,49 m |
| Agena D seco inteiro de nariz | 700 | 1,52 | 111,1 | 4.322,6 | 3,11 m | 4,32 m |

**Conclusão condicional:** nenhum globo metálico oco nem fragmento realista de Agena D em velocidade terminal subsônica possui energia cinética suficiente para escavar um buraco hemisférico de `4,0 m` de profundidade em areia fofa (e todos os fragmentos realistas ficam abaixo até do piso de sobrecarga pura `3.155 kJ` com `Y = 0`).

Certificado em Lean 4.35.0: [`TerminalCraterBound.lean`](../../formal/Conde1963/TerminalCraterBound.lean) (`energy_deficit_excludes_crater_depth`, `hollow_globe_cannot_excavate_4m_crater`, `dense_agena_fragment_below_4m_overburden_floor`, `high_energy_impactor_satisfies_4m_bound`).

## Limites epistêmicos
- O kernel Lean certifica implicações lógicas das premissas, não a autenticidade do `RAAN = 198,5261°` nem medições geotécnicas de Conde em 1963.
- Reprodução: `python3 -O formal/scripts/check_oglobo_cutoff_and_crater_physics.py`.

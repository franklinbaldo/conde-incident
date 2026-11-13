---
type: Guide
title: "C241-P7#1: confronto físico condicionado dos períodos nodais NASA"
description: "Nova ocorrência numérica rastreada ao boletim NASA C241-L12, com controles 3A/3C e ausência de filtro orbital físico."
---

# C241-P7#1 — comparação congelada de períodos nodais publicados

**Origem:** [matriz cumulativa C01–C238](../evidence_matrix_C001-C238_2026-11-11.md) → [C241-L12#1](evidence_matrix_C241-L12_2026-11-12.md) → [análise C241-P7](../constraints/C241-P7_nasa_oct15_kepler_j2_nodal.md). Primário **documental**: NASA Goddard, *Satellite Situation Report*, **15/10/1963**, vol. 3 nº 20, tabela *Objects in Orbit*, p. impressa 5/PDF p. 7, [NTRS 19640000428](https://ntrs.nasa.gov/citations/19640000428), PDF SHA-256 `fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2` (286.417 bytes), ver ledger C241-L12. A NASA compilou dados de rastreamento não disponibilizados: **três linhas de uma publicação**, sem independência instrumental demonstrada.

**Operador reproduzível:** alturas de apogeu/perigeu (km) e inclinação (graus) → semieixo e excentricidade hipotéticos → períodos Kepler e J2 secular (minutos) → resíduos assinados contra período nodal impresso (segundos), com parâmetros físicos declarados, zero parâmetros estimados e sete testes. Objeto principal 1963-003B (associação moderna secundária com 528); 3A e 3C controles documentais, **não** observações independentes.

**Resultado:** MAE nas três linhas 3,875630 s Kepler versus 3,460938 s J2; J2 melhora 3B (4,503412→2,859514 s) e 3C (3,768888→3,569948 s), **piora 3A** (3,354590→3,953351 s). A tese de ganho J2 universal é rejeitada; discrepâncias ficam próximas da granularidade impressa (0,1 min). Sem TLE original, época de medição, definição histórica exata do período/altitudes e σ, **nenhum modelo calibrado** e **nenhuma restrição orbital Lean** são ativados.

**Antes/depois:** Θ de estados físicos de 527/528/529 permanece **Θ→Θ**; não-vazio físico não reavaliado, sem erro geográfico/holdout instrumental ou conclusão sobre impacto. Status **CONNECTED_PENDING_CALIBRATION**. O script `tools/ssr_oct15_kepler_j2_nodal.py` rejeita mutações do ledger versionado por validação de C241-L12; não revalida pixels PDF nem aproxima RAAN 284,1520° de 198,5261°.

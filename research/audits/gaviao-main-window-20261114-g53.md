---
type: Guide
title: '🦅 G53: gatilhos da simulação conjunta de 1,5 milhão'
description: Auditoria retrospectiva das integrações após G52 e da cobertura do replay C241 do dia NASA.
---

# G53: uma mudança na fonte precisa acionar o replay científico

**Janela:** `cae934b9` (exclusivo) → `9baf7b17` (inclusivo): **13 integrações first-parent, 13 commits no DAG, zero merges convencionais**. Lista de commits e limites dos checks históricos no manifesto JSON adjacente. Os checks históricos individuais não examinados permanecem `NOT_CHECKED`.

## G53-F1: o caminho alterado podia não disparar o simulador

A integração [#692](https://github.com/franklinbaldo/conde-incident/pull/692) introduziu um experimento condicional de 1.500.000 amostras e workflow próprio. `tools/c241_joint_orbit_day_heatmap.py::load_sources` lê três arquivos científicos diretos que **não apareciam** nos filtros `on.pull_request.paths` e `on.push.paths` desse workflow: `mirror_528_1963-10-27.tle`, `C241_nov8_two_sided_day_likelihood_2026-11-13.json` e `c241_528_unweighted_2000km_scenarios.json`. Alterar apenas um desses arquivos não acionaria o replay especializado.

**Contraprova reproduzida:** regressão Python stdlib inspecionou os filtros reais e falhou nos dois eventos, listando os três caminhos omitidos. Após o reparo proposto na [PR #698](https://github.com/franklinbaldo/conde-incident/pull/698), a regressão passou e é executada pelo próprio job antes dos testes numéricos. Isto prova a falha de cobertura de filtro, **não** que alguma CI histórica foi indevidamente aprovada.

**Limites científicos:** TLE secundário, dia NASA sem hora/erro instrumental documentado e cenários sintéticos não autorizam inferir reentrada real, posição de fragmento ou `P(impacto histórico em Conde)`. Nenhuma evidência observacional nova. Verificar CI integral da PR no SHA exato antes de merge.

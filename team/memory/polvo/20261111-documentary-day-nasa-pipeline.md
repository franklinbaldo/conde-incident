---
type: AgentMemory
agent: polvo
title: "Dia de decaimento NASA em Lean sem inventar hora ou local"
description: "Issue #15 / PR #17: restrição rastreável C131/C197 e contramodelos"
date: "2026-11-11"
tags: [lean, conde, documentary-constraints, nasa, provenance, negative-evidence]
---

## Retomada e entrega

- Retomada issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15), PR [#17](https://github.com/franklinbaldo/conde-incident/pull/17), base [#1](https://github.com/franklinbaldo/conde-incident/pull/1). A PR #28 do mesmo domínio ainda aguarda revisão de Gavião e integração pelo Elefante.
- `formal/Conde1963/DocumentaryDay.lean`: primeira restrição efetivamente vinculada a uma observação documental da matriz, em vez de predicados físicos arbitrários. `ReportedDecayDay` declara só `day = 19631108` em um cenário que interpreta `ReentryCandidate.day` como *dia de decaimento informado*, não como data/hora de impacto.
- Registros C131 e C197 separados, com a **mesma cadeia NASA/NORAD**. Teoremas sobre equivalência da restrição duplicada, não independência, duas regiões logicamente possíveis, ausência de identificação espacial e contramodelo sem impacto (não é uma previsão). `nasaReportedDayRule` tem predicado Boolean certificado e dois exemplos positivos e um negativo **sintéticos**.
- `Conde1963.lean`, `AxiomAudit.lean` e README atualizados. Workflow Lean agora usa `set -euo pipefail` antes de `lean | tee`, evitando mascarar eventual falha do processo.
- Mudanças em branch própria, sem rebase/force-push, sem merge, blog, contatos ou dados inventados. Commit principal [dbe8eb8](https://github.com/franklinbaldo/conde-incident/commit/dbe8eb817e7b62a0e0b170908d95e7b6901af1b), documentação [815f763](https://github.com/franklinbaldo/conde-incident/commit/815f763befd8e5610ff53ab61aca1daf9600f78b).

## Linhagem e limites

- Fonte: NASA/Goddard *Satellite Situation Report*, vol. 3 no. 22, 15/11/1963, p. impressa 8, NTRS [19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf). Matriz: [C131 L502](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) e [C197 L905](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905); snapshot Git blob SHA1 `a7978c3a75a153b16ab70118a92c434bba674cb7`. Fac-símile **não reinspecionado nesta rodada**. C131/C197 são *uma* fonte, não duplicação da evidência empírica.
- Prova Lean não informa hora/longitude/latitude, não certifica autenticidade do registro, não determina lugar de reentrada nem estabelece que ocorreu impacto terrestre. Não houve TLE novo nem contato com arquivos.
- ZIP Lean histórico contendo `Evidence.lean`, gerador, registro 154/151 e hashes externos de custódia **continua ausente**: recuperação/importação histórica `NOT_RUN`. Conflito de RAAN ~198,5261° vs 284,1520° permanece aberto.
- Contramodelos são proposições sobre classes de estados didáticos. Não implicam ausência de queda real.
- Validação exigida no HEAD final: `cd formal && lake build && lake env lean Conde1963/AxiomAudit.lean`, Python `unittest`, verificação SHA/linhas da matriz e Web build no CI oficial. Anotar resultado e run exato no handoff; não inferir PASS desta memória.

## Próximo

- Revisar o CI e corrigir se algum teorema não compilar; registrar HEAD SHA e run real após completar.
- Gavião auditar `ReportedDecayDay` quanto ao uso condicionado da data NASA e a duplicação C131/C197; Elefante integra apenas após CI/revisão e resolução da dependência #1.
- Castor deve usar esse predicado apenas como calendário do registro, combinado com parâmetros orbitais calibrados e holdouts; sem isso **Conde excluído/forçado/horário específico: NOT_PROVED**.

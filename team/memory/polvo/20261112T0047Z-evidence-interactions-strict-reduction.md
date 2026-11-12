---
type: AgentMemory
agent: polvo
title: "Fatia Lean de interações: testemunha de redução e redundância de fontes"
description: "Issue #15 / PR #17: critério de domínio não vazio e estritamente reduzido; provas de não duplicação e contraindicação decisiva"
date: "2026-11-12"
tags: [lean, conde, evidence, constraints, provenance, conditional-proof, negative-result]
---

## Retomada e fontes
- Retomada da única issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15) na PR própria [#17](https://github.com/franklinbaldo/conde-incident/pull/17), empilhada sobre a PR #1. Leitura de `AGENTS.md` e `team/polvo.md` na main e da matriz integral C01–C238 na branch #17: Git blob SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7`, 241 ocorrências / 238 IDs, colisões C44-C46 (164–177).
- Fonte NASA descrita em C131 (L502) / C197 (L905): NASA/Goddard, *Satellite Situation Report*, 15/11/1963, p. impressa 8, NTRS 19640001198, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf. Nenhuma reinspeção nova de fac-símile; mesma publicação não conta como duas observações independentes.
- O boletim Tupi/FBIS C01/L19, as dimensões de C02, o solo C44#1, a estimativa C46#1 e os registros catalográficos secundários C139–C140, cálculos derivados C141 e a proposta não executada C142 são apenas candidatos a relações condicionais a investigar; sem relação física calibrada atual.

## Alteração
- `Conde1963/Interactions.lean` define `StrictReduction`: exige modelo não vazio, inclusão de domínios, e exemplo antes admissível agora rejeitado. Prova que uma regra repetida (incluindo dia NASA C131/C197) não cria redução estrita; registro não admitido também não muda o conjunto.
- Prova que um novo filtro produz redução genuína apenas com testemunhas de sobrevivência/exclusão, que impactos admissíveis em regiões contraditórias barram conclusões de Conde forçado ou excluído, e que força condicional persiste na interseção só quando resta testemunha.
- `Conde1963.lean` importa novo módulo, `AxiomAudit.lean` fiscaliza seus sete teoremas; README documenta relações possíveis e pré-requisitos físicos. Sem coordenadas, TLEs ou probabilidades inventadas.

## Limitações e validação
- Importação do ZIP Lean original (Evidence.lean, 154 proposições / 151 rótulos, gerador e hashes) = NOT_RUN; bytes não encontrados no repositório. Conflito RAAN 198,5261° versus 284,1520° = NÃO RESOLVIDO.
- Confronto físico/holdout do 529 e propagação histórica a Conde = NOT_RUN; os resultados são apenas teoremas condicionais sobre predicados abstratos, não localização.
- **CI e SHA final:** registrar no comentário da PR após a execução dos jobs no HEAD efetivo. Esta memória deliberadamente não inventa PASS.
- Handoff: 🦅 revisar correspondência entre premissas e conclusões, 🐘 integrar exclusivamente após base #1 e CI verde; 🦫 fornecer testemunhas de redução com entradas físicas verificadas.

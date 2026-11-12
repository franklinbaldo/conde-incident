---
type: AgentMemory
title: "Polvo: provar indistinguibilidade por data e auditar links da matriz"
description: "Issue #15; C01 corrigido, C44–C46 desambiguados, prova Lean e gate de snapshot"
agent: polvo
timestamp: "2026-11-11T22:42:17Z"
tags: [conde, lean, lineage, c44-c46, matrix-citations, negative-results]
---

## Retomada e entrega
- Retomada da issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15) e PR [#17](https://github.com/franklinbaldo/conde-incident/pull/17), empilhada na #1. Lidos integralmente `AGENTS.md` e `team/polvo.md` na main, duas memórias prévias, abertas PRs/issues e matriz C001–C238 (na base #1). Nenhuma ação em blog, SEI, arquivos externos ou terceiros; sem merge/rebase/force-push.
- Defeito documentável: no `ResearchLedger.tsx`, link C01 apontava à **linha 20, C02**, não à linha 19 (C01). Corrigido. Linha C197 (=905) é `| **C197** |`, não rótulo simples; auditor a interpreta corretamente.
- `formal/scripts/verify_matrix_refs.py` valida SHA-1 **Git blob** do instantâneo `a7978c3a75a153b16ab70118a92c434bba674cb7` (commit `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`) e linhas C01=19, C131=502, C197=905, C44=164/175, C45=165/176, C46=166/177. Preserva as seis ocorrências heterogêneas sem deduplicar. `test_verify_matrix_refs.py` contém seis testes **sintéticos** com casos negativos (hash alterado, off-by-one, perda de colisão) e ID Markdown bold. CI passou a executar o script sobre a matriz **real** versionada.
- `Provenance.lean` contém dois teoremas condicionais novos: dois estados admissíveis com mesma observação e regiões distintas impedem um decoder determinístico correto em ambos; predicado de **dia** sozinho mantém esse contraexemplo. Dois `#print axioms` novos. Isto não representa integração orbital nem estima órbita de 528.
- `ResearchLedger.tsx` agora aponta separadamente para as seis colisões C44–C46 com commit+linha e explicação explícita de que não são seis observações independentes. README e índice de colisões atualizados.

## Fontes e limites
- Corpus: [matriz versionada da PR #1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md). Fonte original descrita nela: NASA/Goddard, *Satellite Situation Report*, 15/11/1963 p. 8, NTRS [19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf); FBIS/Tupi [fac-símile](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf). **Fontes primárias não reinspecionadas** nesta rodada; verificadas as linhas da matriz, não autenticidade das fontes.
- C131/C197 são uma fonte NASA documental comum (dia de decaimento, sem lugar/hora). C44–C46 são colisões **na matriz**, não prova de equivalência com colisões alegadas do pacote Lean histórico. Nova prova é uma implicação sob premissas, não previsão nem identificação física.
- Resultado negativo: o ZIP histórico Lean 4.35.0, `Evidence.lean`, gerador, `evidence_registry.json`, hashes independentes e 154 proposições/151 rótulos originais não estão disponíveis na árvore atualmente auditada. Importação real: **NOT_RUN**. `PINNED_MATRIX_ROWS_PASS_ONLY` autentica apenas o *snapshot Git*, não a proveniência dos PDFs.

## Validação e handoff
- HEAD funcional antes desta memória: [`6fef505112f2496ff5995647286c6891c8b5fb96`](https://github.com/franklinbaldo/conde-incident/commit/6fef505112f2496ff5995647286c6891c8b5fb96).
- GitHub Actions [Scientific checks #43114937450](https://github.com/franklinbaldo/conde-incident/actions/runs/43114937450): **PASS 2/2**, incluindo `lake build`, 11 `#print axioms`, 14 testes Python sintéticos e verificação efetiva do blob/linhas da matriz, lint e build Web. Este PASS refere-se ao HEAD funcional **antes desta memória**. O HEAD após commit de memória deve ser consultado novamente antes de integração.
- Revisão independente 🦅 Gavião e integração 🐘 Elefante, somente após CI no SHA final e solução da base PR #1. Manter Draft; não inventar corpo Lean ausente.

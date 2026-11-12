---
type: AgentMemory
agent: polvo
title: "Matriz C01-C238 integral indexada e condicionais Lean com 241 ocorrências"
description: "Issue #15 / PR #17: cobertura sem dupla contagem e contrato JSON para Castor"
date: "2026-11-11"
tags: [lean, conde, evidence, provenance, constraints, negative-evidence, typed-contracts]
---

## Retomada e alteração substancial

- Retomei a própria [issue #15](https://github.com/franklinbaldo/conde-incident/issues/15) e [PR #17](https://github.com/franklinbaldo/conde-incident/pull/17), empilhada na [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1). Consultei `AGENTS.md`, `team/polvo.md`, PRs abertas, política ainda proposta [#28](https://github.com/franklinbaldo/conde-incident/pull/28) e toda a matriz cumulativa.
- A matriz Git blob SHA-1 `a7978c3a75a153b16ab70118a92c434bba674cb7` contém **241 linhas reais**, **238 IDs**, incluindo colisões C44-C46 com duas ocorrências por ID: linhas 164/175, 165/176, 166/177. Nenhum ID ausente entre 1 e 238.
- Novo `formal/Conde1963/MatrixEvidence.lean`: 241 referências tipadas (ID numérico, ocorrência, linha, papel físico conservador). `formal/scripts/evidence_registry.py` verifica bytes, preserva identidade integral e exporta `source_status`, texto de cada linha, seção, citações permalink e contrato JSON à integração do Castor. `formal/tests/test_evidence_registry.py` contém **8 novos testes**, incluindo contraexemplos de perda de ID, perda de colisão e promoção injustificada a filtro orbital.
- Provas: `evidence_matrix_row_count`, `two_primary_nasa_matrix_occurrences`, `context_rows_add_no_orbital_information`, `full_matrix_has_only_nasa_day_filter`, `full_matrix_does_not_identify_region`; `AxiomAudit.lean` expandido. O filtro físico atual da **matriz inteira** permanece somente o dia NASA, vinculado a C131/C197 (a **mesma fonte**). As outras 239 ocorrências estão rastreadas, mas sem um mapeamento físico validado para uma reentrada terminal. Esse estado NÃO desqualifica seu valor historiográfico ou como evidência em outros problemas.
- CI atualizado para checkout/assert do SHA **head real** em vez do ref sintético de merge, gate do inventário, Lean, 22 testes Python e artifact JSON `conde-evidence-contracts` (somente se sucesso). Web e README científico mantidos; nenhum blog alterado.
- Commits desta fatia: gerador `b7d4e7525eebe2fb9a97135ed53268ac47339768`, Lean `5237450fceb6d9014f2e2c397aa3f84c4a76a1de`, testes `2d89e20d9c9e109599c309dcada110819912fce1`, gate CI `c718c8c5cf42c35a8833a24510de48cc46a5624b`, correção prova `4cc83a7d701a00a3c6dc1fe95e16cfcf0ee1784b`, import auditoria `e6c59425e619b5f99103b36203d7fea13f08ef05`.

## Fontes e limites epistêmicos

- Matriz congelada na PR #1: https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md . Contratos apontam cada linha de origem; o texto integral é preservado sem reinterpretação automática de graus de verificação.
- Documento primário já descrito nos registros C131/C197: NASA/Goddard, *Satellite Situation Report*, 15/11/1963, p. impressa 8, NTRS 19640001198, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf . Os dois registros atestam um **dia de decaimento publicado** de NORAD 528, não lugar/hora/impacto no solo; fontes primárias **não reinspecionadas** nesta rodada.
- C44-C46 são colisões semânticas efetivas, não corroboração. Um URL de matriz autentica sua própria linha/versão, não os documentos externos. Nenhuma classificação automática transforma hipóteses, OCR, resultados negativos ou séries atmosféricas desacopladas em medições de posição orbital.
- A biblioteca antiga original `Evidence.lean` (154 proposições/151 rótulos), ZIP, gerador e hashes de custódia originais permanecem ausentes: importação **NOT_RUN**. RAAN ~198,5261° versus 284,1520° sem resolução. Testes de física e holdout 529 nesta fatia **NOT_RUN**. Não há prova de Conde forçado/excluído ou de impacto, nem coordenadas, hora, probabilidade ou TLE novos.

## Validação e registro de falhas

- [CI #43126034255](https://github.com/franklinbaldo/conde-incident/actions/runs/43126034255): FAIL no SHA `c718c8c` por limite de recursão e case-split Lean; erro corrigido, não encoberto.
- [CI #43126270113](https://github.com/franklinbaldo/conde-incident/actions/runs/43126270113): `lake build` **PASS** no SHA `4cc83a7`, mas auditoria FAIL por import ausente de `MatrixEvidence` no módulo de axiomas; corrigido.
- [CI #43126376040](https://github.com/franklinbaldo/conde-incident/actions/runs/43126376040): **2/2 PASS** no SHA `e6c59425e619b5f99103b36203d7fea13f08ef05`; `lake build` 8 jobs, `lake env lean Conde1963/AxiomAudit.lean` sem `sorryAx`, axiomas novos nenhum ou `propext`; **22/22** testes Python; SHA/blob/241 linhas PASS; Web lint/build PASS. Artefato de 241 contratos: https://github.com/franklinbaldo/conde-incident/actions/runs/43126376040/artifacts/13903447455 .
- **PENDENTE:** checar o último CI no SHA final *desta memória*; não atribuir a ela o PASS de SHA anterior. PR permanece Draft e sem merge.

## Handoff ao Gavião, Castor e Elefante

- 🦅 Auditar se a classificação `contextOnly` expressa corretamente **ausência de filtro orbital atual**, sem negar evidências documentais; validar pinagem e as colisões.
- 🦫 Consumir as 241 referências exportadas, acrescentar **somente** restrições numericamente ligadas a documentos/épocas/linhagens independentes, com erro/holdouts, e evitar reclassificação automática. A duplicação NASA dia C131/C197 não aumenta confiança estatística.
- 🐘 Após revisão independente, base #1 integrada e CI verde **no último SHA**, decidir integração. Implementador não faz merge, rebase, force-push, publicação ou contato externo.

---
type: AgentMemory
title: "Polvo: CI Lean reparado, custódia limitada e C44–C46 desambiguados"
description: "Retomada da PR #17, falha de import Lean corrigida, testes ZIP ampliados e links da matriz pinados"
agent: polvo
timestamp: "2026-11-11T21:50:00Z"
tags: [conde, lean, provenance, c44-c46, ci, negative-results]
---

## Retomada e mudanças verificáveis
- Releitura integral de `AGENTS.md` e `team/polvo.md` da `main`; revista a matriz original no blob `a7978c3a75a153b16ab70118a92c434bba674cb7` da PR #1 e a própria issue #15/PR #17; não há `formal/` ou matriz na `main`.
- GitHub Actions [#43098816777](https://github.com/franklinbaldo/conde-incident/actions/runs/43098816777), no head anterior `47772bd1`, falhou porque `import` vinha depois de doc comment em dois módulos Lean. Corrigido em `formal/Conde1963/Provenance.lean` e `AxiomAudit.lean`, sem acrescentar axiomas.
- GitHub Actions [#43106050033](https://github.com/franklinbaldo/conde-incident/actions/runs/43106050033), head `d1bc4c1c6b545813ad2e18a08159d4e87d6579f7`: **PASS** nos jobs Web e Lean; `lake build`, auditoria de axiomas e testes Python executados.
- Auditor de ZIP passou a retornar `STRUCTURE_PASS_ONLY`, `provenance_status=NOT_VERIFIED`, `semantic_status=NOT_RUN`, porque o teste pode construir um ZIP sintético com hashes coerentes. Adicionadas contraprovas para path traversal, duplicatas de membros, SHA-1 ausente e chave de rótulo ausente.
- O ledger Web agora liga diretamente C01, C131, C197 às linhas L20, L502, L905 da matriz congelada, sem confundir C131/C197 com observações independentes; PDF NASA p. impressa 8 = viewer #page=10, conforme revisão independente registrada na issue #16.
- GitHub Actions [#43106433868](https://github.com/franklinbaldo/conde-incident/actions/runs/43106433868) **PASS** em `116169be2f5d7d3b6b47fbddc5ac046760d359df` (antes da presente memória). Esta memória e o índice de colisões formam novo head e **exigem CI nesse head antes de integração**.
- Novo `formal/provenance_c44_c46.md`: seis ocorrências das colisões editoriais em L164–L166 e L175–L177, com URL, sentido e limites; separadas da alegação sobre colisões no corpus Lean histórico.

## Fonte, lacunas e fronteiras
- Fonte documental indireta desta rodada: [matriz C01–C238](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md), proveniente da PR #1; relato Tupi/FBIS e relatório NASA/NTRS `19640001198` já inspecionados na pesquisa de base, **não relidos aqui como fac-símiles originais**.
- Resultado negativo: busca no repositório e PR #1 não localizou bytes originais do pacote Lean 4.35.0, `Evidence.lean`, registro com 154/151 entradas e gerador, nem pares de SHA-1/SHA-256 com origem externa independente. **Importação histórica NOT_RUN**. A colisão da matriz não prova que coincide com o registro indisponível.
- Sem radar, sem localização ou instante terminal, sem reconstrução orbitária nova. Sem contato com arquivos/pessoas, nenhuma publicação externa, sem rebase, force-push ou merge.

## Próxima rodada
- Conferir CI do **head após esta memória** e registrar URL/SHA, inclusive `lake build`, `#print axioms`, testes ZIP e Web build. Submeter ao Gavião, manter draft até revisão. Requerer o ZIP antigo com proveniência dentro do escopo autorizado, não reconstruir por hipótese.

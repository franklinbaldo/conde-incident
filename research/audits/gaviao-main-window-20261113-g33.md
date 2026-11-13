---
type: Guide
title: 'G33: 18 integrações e integridade da genealogia SSG'
description: 'Auditoria retrospectiva de merges, fontes e código, com contraprova de linhagem órfã.'
---

# G33: revisão retrospectiva

**Janela congelada:** `c98ccd9a2ef66d202108c8e6bf7f430b6eb25368..c9b4482f7850434a9124dfe6a12c540006aa468f` em 13/11/2026. [Manifesto SHA por SHA](gaviao-main-window-20261113-g33.json): **18 integrações**, 15 squash, três merges convencionais, **38 commits DAG** (20 laterais) e nenhum commit direto. PRs #377, #379, #380, #381, #382, #384, #386, #385, #387, #389, #390, #391, #392, #394, #393, #395, #398 e #399. O manifesto informa os SHAs, pais, PRs, títulos e arquivos; o corte é anterior à própria correção G33.

**Achado G33-F1:** `archivePages()`, mesmo após a proteção de ciclos da #381, exigia genealogia para cada citação, mas não exigia citação para cada genealogia. Uma entrada `citation_lineages` adicional, de `source_id` inexistente no feed curado, era silenciosamente ignorada. A contraprova **sintética** adiciona uma genealogia órfã preservando as 29 entradas originais. A correção exige correspondência de cada genealogia declarada ao par `(snapshot_ref, source_id)` de uma citação curada. Controle positivo preserva o corpus válido; não há evidência de manipulação histórica.

**Limites científicos e editoriais:** #377, #394 e #399 mantêm datas de publicação NASA distintas de épocas instrumentais; a errata de perigeu julho 1963 3C, 425→452 km, não cria medida independente. #398 compara impressos de 15/11 e 30/11, com holdout por **data de publicação**, não observações de sensor. #386/#387 são provas Lean condicionais; #391 ensaia covariância sintética, sem ajuste histórico. #382/#389 registram mapas e fotos posteriores sem atribuir geocódigo de impacto; #385 diferencia códigos meteorológicos de 2014 sem retroprojeção a 1963. #380 melhora custódia ON20, sem criar novas testemunhas. #384 reforça política de CI; #390/#392/#393 migram tipagem e rotas SSG; #395 altera contraste visual, não interpretação orbital.

**Testes locais:** `python3 -m unittest formal.tests.test_ssr_november tests.test_tle_nasa_ssr_jul_dec_audit tests.test_ci_event_policy_all_workflows -v`: **35/35 PASS** na janela congelada. `python3 formal/scripts/compile_ssr_november.py --check`: PASS. O Jatobá interrompeu Node e Prek local por limite RSS; a contraprova JavaScript deve ser validada no CI da PR no HEAD final. Nenhum PDF NASA foi readquirido/reinspecionado visualmente nesta rodada, e testes de ledger não autenticam observações instrumentais.

**Conclusão:** rigor de custódia e catálogo reforçado, mas a hipótese de queda em Conde permanece indeterminada. Não foi demonstrada hora nem posição terminal. O blog pessoal não foi alterado.

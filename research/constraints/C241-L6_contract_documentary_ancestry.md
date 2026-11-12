---
type: Guide
title: C241-L6 ancestralidade documental pinada em contratos Lean
description: Ponte reproduzível Abelha para Polvo nos três contratos documentais do caso Conde, sem nova restrição física.
---

# C241-L6: contrato, ocorrência, fonte e ancestral documentado

**Pergunta falsificável:** depois da integração da [PR #155](https://github.com/franklinbaldo/conde-incident/pull/155), o Lean consegue transportar a ancestralidade documental explícita dos contratos, sem unir C151 de snapshots diferentes nem transformar a ficha NTRS em um segundo instrumento de rastreamento?

**Fonte de custódia:** matriz cumulativa [C01–C238](../evidence_matrix_C001-C238_2026-11-11.md), blob Git a7978c3a75a153b16ab70118a92c434bba674cb7, 241 ocorrências. Feed curado **para esta transformação documental**, não uma medição física nova: [Abelha, PR #155](https://github.com/franklinbaldo/conde-incident/pull/155), public/data/conde-declared-dependence.json, gerado de research/provenance/lineages.json com tools/export_documentary_dependence.py, ligado ao feed canônico public/data/conde-source-citations.json. É uma fonte curada **derivada** e não independente dos documentos de 1963. O teste recompila o companion do ledger no mesmo SHA; mudança inesperada falha.

**Entrada documental:** três contratos (C179_ORBITAL_GRAPH, C179_C151_BRIDGE, C197_DOCUMENTARY) e oito vinculações contrato-ocorrência. Saída Lean 4.35.0: formal/Conde1963/ContractLineage.lean, com oito linhas tipadas, fonte, família, obra, ID+ocorrência+snapshot, estado do contrato e **uma cadeia ancestral explícita** (C198#1: NTRS_19640001198, relation catalogue_of_same_work, para NASA_SSR_19631115). Reutilizações de C179#1 e C197#1 em contratos distintos não são dados instrumentais adicionais.

**Controle de colisão:** C151#1 refere-se à fonte moderna NOAA IGRA Recife **somente** no blob a7978c3. C151 do acervo Lean legado de 154 linhas descrevia outro assunto: não pode ser combinado pelo rótulo sem snapshot. As colisões C44–C46 também exigem sufixo de ocorrência.

**Teste adversarial:** trocar o snapshot de C151, transformar a relação NTRS→NASA em independent_tracking ou promover o estado a ACTIVE_HARD rejeita a geração. A falta de aresta ancestral não equivale a independência. O gerador não ativa predicados, atribui probabilidades ou duplica observações.

**Domínio antes/depois:** as restrições físicas admissíveis do Castor permanecem **inalteradas** (zero cortes novos, zero observações numéricas geradas). A aplicação numérica à trajetória e erros de holdout, em graus para RAAN ou quilômetros para posição, foi **NOT_RUN**, pois falta rastreamento primário 527/528/529 com época instrumental, frame, matriz de covariância e controle independente. A própria região física não foi recontada nem sua não-vacuidade reavaliada nesta fatia. Não há afirmação de impacto ou local de reentrada.

**Reprodução no HEAD exato da PR:**

    python3 tools/export_documentary_dependence.py --check-site
    python3 formal/scripts/compile_contract_lineage.py --check
    python3 -m unittest discover -s formal/tests -p 'test_documentary_links.py' -v
    cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean

O workflow Lean 4.35 core proof audit executa lake build e a suíte de testes contra o SHA real; Prek policy (OKF and 20KB) verifica esta nota e os limites. Para **redução física verdadeira**, rastrear os TLE originais, epochs e convenções de elementos do 528 e controlar resíduos de 527/529 com erro conhecido, sem tratar catálogo e ficha de índice como sensores distintos.

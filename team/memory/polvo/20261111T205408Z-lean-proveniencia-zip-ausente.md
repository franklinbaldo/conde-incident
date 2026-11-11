---
type: AgentMemory
title: "Custódia do ZIP Lean ausente e teoremas condicionais"
description: "Issue #15; ponte de auditoria de ZIP e provas de não identificabilidade; sem inventar as 154 proposições originais"
agent: polvo
timestamp: "2026-11-11T20:54:08Z"
tags: [conde, lean, proveniencia, nao-identificabilidade]
---

## O que mudou
- Issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15), branch `feature/polvo-lean-audit-conditional-15` empilhada na PR [#1](https://github.com/franklinbaldo/conde-incident/pull/1), base inicial `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`. Não alterar branch #1, não mesclar esta PR.
- Novo `formal/Conde1963/Provenance.lean`: teoremas condicionais sobre dois candidatos de regiões diferentes, restrições adicionais e cadeia compartilhada. `formal/Conde1963/AxiomAudit.lean` para listar axiomas; importação em `formal/Conde1963.lean`.
- `formal/scripts/audit_zip.py` verifica dois hashes externos obrigatórios, CRC, caminhos, nomes e colisões; `formal/tests/test_audit_zip.py` possui **somente corpus sintético de estrutura**, sem texto histórico.
- `.github/workflows/science.yml` inclui `lake build`, auditoria de axiomas e `unittest` no head; README e `ResearchLedger.tsx` conectam C01/C131/C197 à matriz e URLs de fontes com limites.
- Referência do último commit funcional pré-memória: [aafe511c](https://github.com/franklinbaldo/conde-incident/commit/aafe511c1823b8942c8dc47f00d0a011a6c33fde). SHA final e execução Actions só podem ser apurados depois de abrir PR.

## Evidência, dependências e resultado negativo
- Matriz em PR #1, blob `a7978c3a75a153b16ab70118a92c434bba674cb7`. C01 provém da cadeia Rádio Tupi→FBIS, sem segunda testemunha; C131 e C197 remetem ao **mesmo** boletim NASA de 15/11/1963, p. 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf). A fonte informa dia, não lugar/hora. Conteúdo primário **não foi relido nesta sessão**, dependemos da auditoria documental da matriz.
- Inspeção recursiva da árvore de PR #1: **não há ZIP original**, `Evidence.lean`, `evidence_registry.json` nem gerador. Na `main`, tampouco há pacote formal; o inventário está em PR #1. Não reconstruir conteúdo histórico por dedução. Recuperação 154 proposições/151 rótulos/C44–C46 = **NOT_RUN**.
- Ocorrem rótulos C44–C46 em seções históricas diferentes da matriz cumulativa. Essa duplicidade é metadado de auditoria, não duas observações e não autoriza deduplicação destrutiva.
- Até a execução do GitHub Actions no SHA da PR, compilação e testes da nova fatia = **PENDING/NOT_RUN**, sem atribuir PASS. Nenhum contato, escrita externa, acesso a blog ou confirmação de localização.

## Próxima rodada
1. Ler run no SHA final e corrigir erros Lean/Python/TypeScript encontrados, sem alterar evidências alheias.
2. Identificar local autorizado do ZIP original **dentro do escopo Conde**, hashes de custódia e schema real. Só então auditar e importar `Evidence.lean` e o registro sem descartar colisões.
3. Revisão independente do 🦅 Gavião e integração pelo 🐘 Elefante após CI verde.

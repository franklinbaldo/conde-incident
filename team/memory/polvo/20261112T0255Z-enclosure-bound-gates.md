---
type: AgentMemory
agent: polvo
title: "Envelopes de erro condicionais e gate de impacto material"
description: "Issue #15 PR #17: Lean distingue cobertura numérica, evento de solo, amostragem finita e proveniência documental; contrato Castor fail-closed"
date: "2026-11-12"
tags: [lean, conde, numerical-enclosures, provenance, falsification, finite-grid, holdout]
---

## Leitura, escopo, autoria

- Lidos `AGENTS.md` da main (Git blob `e9058f64c1eb68d25536b9ff306b9d676833b488`) e `team/polvo.md` (blob `3e1534f215e2eb07c3672a0609789fe629cfe8ec`), issue própria [#15](https://github.com/franklinbaldo/conde-incident/issues/15), PR científica de base [#1](https://github.com/franklinbaldo/conde-incident/pull/1), PR própria [#17](https://github.com/franklinbaldo/conde-incident/pull/17), proposta de fluxo [#28](https://github.com/franklinbaldo/conde-incident/pull/28), e interface de física de Castor [#5](https://github.com/franklinbaldo/conde-incident/pull/5). #28 ainda não estava integrada à main, mas suas condições epistêmicas foram seguidas.
- A main não possui ainda a matriz; lida integralmente do HEAD da PR #17 (`research/evidence_matrix_C001-C238_2026-11-11.md`, Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`), **241 ocorrências, 238 rótulos e C44–C46 duplicados por conteúdo distinto**. Nenhuma renumeração/reconstituição.
- Única issue ativa #15; retomada da branch `feature/polvo-lean-audit-conditional-15` sobre `research/scientific-integrity-foundation`, sem merge, rebase, force-push, blog ou contato externo.

## Fatia entregue

1. `formal/Conde1963/Enclosures.lean`: `ImpactEnvelope` possui `predict`, `contains`, `soundForPredictions` e `SimulationAudit` declarativo; sete teoremas sob `#print axioms` formalizam exclusão de Conde, forçamento ou janela alternativa **somente** com cobertura para todo parâmetro admissível, domínio não vazio, gate de impacto no solo e disjunção espacial adequada. Uma janela sobreposta a Conde não certifica exclusão uniforme; um gate de altitude do Castor não certifica impacto material. Contraexemplo simbólico com `Bool`: resultado nulo num grid parcial não exclui impacto em todo o domínio. `TimeLocation` é parâmetro simbólico sem coordenadas inventadas.
2. Importado o módulo em `formal/Conde1963.lean` e `AxiomAudit.lean`. O teorema da grade finita depende da proposicionalidade extensional `propext`, os três teoremas principais de envelopes não dependem de axiomas adicionais; nenhum `sorryAx`.
3. `formal/scripts/evidence_registry.py` exporta `enclosure_interface` aditivo em JSON para Castor, com obrigações e chaves tipadas, três classes condicionais e `null/false` para janela, domínio global e verificações físicas inexistentes. `formal/tests/test_evidence_registry.py` cobre gate fail-closed, IDs e linhagem. README explica que `GroundImpactAdmissible` usa flags DECLARADAS, não é certificado de autenticidade físico por si.
4. Fonte documental original de referência, **não reinspecionada nesta fatia**: NASA/Goddard, *Satellite Situation Report*, 15/11/1963, p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), [C131 L502](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) e [C197 L905](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905): **mesma** fonte primária documental, relata dia de decaimento 08/11, nenhuma hora ou posição, dia físico real ainda pendente. [C01 L19](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L19) é cadeia Tupi/FBIS, prova apenas relato, não queda. Nenhuma fonte instrumental independente nova obtida.

## Validação reproduzível e resultado negativo

- Commit funcional pré-memória `280d0518bfbed01d06a8369ccaed26314dab23b7` depois do novo módulo `00a61a3845bb74964f38e15d499bc978ef405983`, imports `d559c8b64950463d1bfca7d0bafa460647e18955`/`b09c304fed62cd380cfcb61c568c8ea64c61d31e`, contrato `c37c2d2793863cb0e6d1116049700a34c43f883b`, teste `7087d22d7b7b0b04703f3dec810260c26de37dbf`, ajustes `7936b339cab50ba3b750dde9ee5f1646c9d8dfe9` e README `280d0518bfbed01d06a8369ccaed26314dab23b7`.
- [CI do HEAD pré-memória #43144223359](https://github.com/franklinbaldo/conde-incident/actions/runs/43144223359): **web e lean SUCCESS**, com checkout do PR HEAD. [CI #43144103626](https://github.com/franklinbaldo/conde-incident/actions/runs/43144103626), SHA `7087d22`, também **2/2 SUCCESS**: Lean 4.35.0 `lake build` 12 jobs; sete `#print axioms` novos, sem `sorryAx`; Python **34/34 tests PASS**, inventário `MATRIX_IDENTITY_PASS_ONLY`, 241/238 e 238 avaliações de incerteza individuais ainda pendentes. Artifact: [contrato JSON](https://github.com/franklinbaldo/conde-incident/actions/runs/43144103626/artifacts/13911186775). A CI do **commit final de memória** precisa ser verificada separadamente.
- **Negativos/ausências:** ZIP original Lean 4.35.0 com `Evidence.lean`, `evidence_registry.json`, gerador, 154 proposições/151 rótulos e hashes independentes ainda NÃO RECUPERADO, importação `NOT_RUN`. Sem observação terminal de 1963, TLEs NORAD instrumentais originais, conciliação primária de RAAN 284,1520° vs 198,5261°, holdout físico independente 529, erros numéricos calibrados, prova de sobrevivência material ou coordenadas de queda. Teoremas provam **implicações condicionais em modelos**, nunca acontecimento em Conde.

## Próximo passo verificável

- Quando Castor exportar trajetórias com épocas, quadros, modelos e **limites de erro justificados**, ligar `ImpactEnvelope.soundForPredictions` a um certificado de erro verificável e provar **cobertura global da região parametrizada**, não só do grid. Somente promover uma restrição da matriz se primária, independente e mapeada fisicamente. Manter revisão científica 🦅 e integração exclusiva 🐘 depois da base #1; PR #17 permanece draft.

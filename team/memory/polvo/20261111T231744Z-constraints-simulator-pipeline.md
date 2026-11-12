---
type: AgentMemory
title: "Polvo: conectar evidências e restrições Lean ao simulador"
description: "Issue #15, critérios formais para excluir/forçar Conde, interface finita de parâmetros e diretriz comum PR #28"
agent: polvo
timestamp: "2026-11-11T23:17:44Z"
tags: [conde, lean, constraints, provenance, simulation, epistemic-limits]
---

## Entrega da rodada
- Retomada da issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15) e PR [#17](https://github.com/franklinbaldo/conde-incident/pull/17), empilhada na PR #1. `formal/Conde1963/Constraints.lean` introduz parâmetros abstratos, admissibilidade, consistência, distinção entre exclusão, localização, identificação de hora/posição e contradição; todos os resultados são condicionais ao modelo.
- Um `SourcedConstraint` leva rótulo/ocorrência da matriz (C44–C46 colidem), cadeia, grau, uso e predicado, impedindo que cada documento seja automaticamente tomado como restrição física. `ExecutableRule` requer prova de equivalência entre teste booleano e predicado Lean. `filterCandidateGrid` seleciona parâmetros finitos para consumo por simulação; NÃO certifica cobertura contínua nem cálculo orbital.
- `formal/Conde1963.lean` importa `Constraints`; `AxiomAudit.lean` expõe dependências de axiomas das novas provas; `formal/README.md` documenta contrato de handoff ao Castor e o significado limitado de qualquer prova de região/tempo.
- Diretriz do proprietário foi registrada em [PR #28](https://github.com/franklinbaldo/conde-incident/pull/28), separada da pilha #1/#17 porque `AGENTS.md` e `team/polvo.md` existem na main, mas não na base antiga da PR #1. É documentação aguardando integração do 🐘.
- Atualizados prompts das nove rotinas relacionadas (oito animais e investigação histórica independente), preservando agenda e responsabilidades. Cada novo documento deve alimentar a matriz e, apenas quando justificar, restrições Lean e domínios da simulação, com feedback de holdouts e contraprovas.

## Fontes, limites e observações negativas
- C131/C197 indicam a mesma fonte NASA/Goddard, *Satellite Situation Report*, 15/11/1963 p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), via matriz C001–C238 da PR #1. Registro de decaimento apenas pelo dia; NÃO fornece local/hora, tampouco prova de queda. Nenhum fac-símile original foi reinspecionado nesta rodada.
- TLE 528 e conflito RAAN 198,5261° versus 284,1520° seguem sem resolução de proveniência. Nenhuma efeméride foi ajustada e nenhum parâmetro orbital histórico foi inventado.
- ZIP Lean histórico, `Evidence.lean`, registro 154/151 e gerador originais continuam não recuperados; importação NÃO EXECUTADA.
- O Lean demonstra implicações condicionais; sem solver físico calibrado, análise de erro e prova de exaustividade, não há exclusão/queda real provada em Conde nem previsão pontual.

## Próximos passos
- Confirmar `lake build`, `#print axioms`, testes Python e web no SHA final da PR #17; revisar caso o CI falhe.
- 🦅 Gavião revê a cadeia epistemológica e os teoremas; 🐘 Elefante integra a PR #28 e, após dependência #1, avalia a #17.
- 🦫 Castor liga a interface de parâmetros aceitos ao integrador numérico, valida unidades/holdout NORAD 529 e devolve limites e contraexemplos documentados.

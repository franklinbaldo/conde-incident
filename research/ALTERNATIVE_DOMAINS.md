# Alternativas documentais não são restrições simultâneas

Esta fatia complementa o [gate de domínio #37](https://github.com/franklinbaldo/conde-incident/pull/37) e o [fluxo documental → Lean → parâmetros → simulação #28](https://github.com/franklinbaldo/conde-incident/pull/28). O problema concreto é a **falsa contradição**: o site anterior do Conde usa RAAN 284.1520°, enquanto uma série histórica alternativa registra aproximadamente 198.5261°. Sem comprovação da procedência, época e referencial de ambas, não se pode tratá-las como medições simultaneamente válidas, calcular sua média ou intersectá-las.

## Contrato

Execute `node scripts/audit-alternative-domains.mjs arquivo.json`. O JSON tem `schema: conde.alternative-domains/v1`, um objeto `common` que obedece ao contrato `conde.admissible-domain/v1` da #37 e pelo menos duas entradas em `scenarios`. Cada entrada precisa de `id`, `reason` e `restrictions` não vazias. As restrições comuns são aplicadas em cada cenário; as alternativas são auditadas **separadamente**, nunca misturadas numa só interseção.

Exemplo estritamente **sintético**: parâmetro x no intervalo inicial [0,10], versão A restringe x a [0,4] e versão B a [6,10]. As duas versões são individualmente não vazias. Intersectá-las todas produziria uma contradição artificial. O script não usa valores orbitais verdadeiros nem afirma que essas duas variantes sejam todas as possibilidades.

Cada restrição exige ID e ocorrência, URI da fonte, cadeia declarada, grau de verificação, referência formal Lean e premissa explícita, conforme #37. A saída inclui esses campos declarados para rastreabilidade. Para evidência histórica, exigir vínculo real com a matriz cumulativa, mas este script **não abre ou verifica a matriz**.

## Interpretação dos resultados

- `MULTIPLE_DECLARED_FEASIBLE`: mais de um cenário conserva intervalos não vazios, sem provar várias órbitas físicas.
- `ONE_DECLARED_FEASIBLE`: apenas um dos cenários **listados** conserva intervalos não vazios; não prova exclusão de cenários não listados.
- `NO_DECLARED_FEASIBLE`: todas as alternativas declaradas contradizem os limites introduzidos; não prova a impossibilidade do evento histórico.

Nenhum status implica lugar ou hora de reentrada, queda no solo ou probabilidade. O programa mantém `source_authenticity=NOT_VERIFIED`, `matrix_occurrences=NOT_VERIFIED`, `source_independence_between_scenarios=NOT_VERIFIED`, `physical_feasibility=NOT_VERIFIED`, `lean_proofs=NOT_VERIFIED`, `numerical_holdouts=NOT_RUN` e `location_and_impact=NOT_INFERRED`. Rejeita qualquer alegação de cenários exaustivos sem prova externa.

## Handoff e validação

A 🐢 Tartaruga deve auditar as épocas, o frame, a custódia e a identidade dos elementos NORAD 527/528/529 antes da seleção empírica entre versões. O 🐙 Polvo formaliza restrições condicionais por cenário, com `lake build` e axiomas auditados; 🦫 Castor valida por integração física e holdouts; 🦅 Gavião revisa independência e limitações; 🐘 Elefante só integra após revisão e CI no SHA final.

Testes: `node --test tests/admissible-domain.test.mjs tests/alternative-domains.test.mjs`. São contraprovas sintéticas, **não** execução Lean, autenticação de TLE ou reconstrução da órbita. Matriz de referência: [C01–C238 da PR #1](https://github.com/franklinbaldo/conde-incident/blob/research/scientific-integrity-foundation/research/evidence_matrix_C001-C238_2026-11-11.md). O blog pessoal e o deploy Pages permanecem fora desta fatia.
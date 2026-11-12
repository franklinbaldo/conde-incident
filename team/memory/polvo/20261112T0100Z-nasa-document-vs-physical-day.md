---
type: AgentMemory
agent: polvo
title: "Retificação epistemológica: data NASA observada no documento, dia físico testável"
description: "Issue #15 / PR #17: hipótese da data de decaimento sem filtro rígido; 241 incertezas explícitas"
date: "2026-11-11"
tags: [lean, conde, provenance, uncertainty, nasa, falsifiability]
---

## Correção em resposta à crítica epistemológica

- Issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15), branch `feature/polvo-lean-audit-conditional-15` da [PR #17](https://github.com/franklinbaldo/conde-incident/pull/17), base PR #1. Mantida sem merge, sem rebase, sem contatos externos ou publicação.
- O boletim NASA/Goddard 15/11/1963, p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), consta na matriz C131 [L502](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) e C197 [L905](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905) como **uma única fonte** da data de decaimento **registrada** de 1963-003B: 08/11/1963.
- Não há dados primários sobre método de atribuição da data, última detecção positiva, primeiro rastreamento sem detecção, hora ou local do decaimento. A igualdade entre dia físico e dia catalogado **NÃO decorre da transcrição**. Nem mesmo se sabe se a data foi obtida por um método de rastreamento direto, previsão ou decisão administrativa.
- `Conde1963/DocumentaryDay.lean` separa `NasaRecordStatesNovemberEighth` (enunciado **documental**) de `PhysicalDayMatchesCatalogue` (hipótese física). C131/C197 agora `use := .scenarioOnly`, nunca `.admitted`. Há demonstrações de que a publicação NÃO implica dia físico, e contratos condicionais mutuamente exclusivos `ConditionallyForcesNasaDay`, `ConditionallyExcludesNasaDay`, `DayRemainsUnderdetermined`; os contraexemplos são exclusivamente didáticos, não órbitas reais.
- `Conde1963/MatrixEvidence.lean` e gerador `formal/scripts/evidence_registry.py`: **241 ocorrências** / **238 IDs** ainda preservados com C44–C46 separados. Cada linha agora inclui `EpistemicUncertainty`. C01 = relato confirmado como texto, ocorrência física desconhecida; C131/C197 = data publicada, dia físico desconhecido. Outras **238 ocorrências requerem avaliação epistemológica individualizada no módulo Lean**; o estado pendente é **explícito**, não significa desconfiança ou falsidade dos seus textos. Os qualificadores originais estão preservados por inteiro no JSON/matriz, e nenhum intervalo de erro numérico é fabricado.
- `AllMatrixEvidence` registra documentação sem impor restrições ao espaço físico. Restrições futuras dependem de modelo de observação auditado e simulação/holdout. `Interactions.lean` mantém comparação de filtros apenas como cenário hipotético.
- Novos testes: rejeição de promoção indevida de incerteza, exigência de status e ausência de intervalo fictício, mais teoremas e auditoria de axiomas.

## Validação, falhas e limites

- A execução [#43131020417](https://github.com/franklinbaldo/conde-incident/actions/runs/43131020417) encontrou falha `Decidable` no Lean para definição opaca; corrigido desdobrando explicitamente as definições no módulo.
- [#43131143569](https://github.com/franklinbaldo/conde-incident/actions/runs/43131143569) falhou por divergência entre `MatrixEvidence.lean` recomposto e `FOOTER` do gerador, corrigida sem mudar a matriz.
- **CI verde** [#43131263343](https://github.com/franklinbaldo/conde-incident/actions/runs/43131263343), HEAD `c9ede0f200ece113363d659afb643ec6a8a4847f`: **2/2 jobs PASS**, `lake build` 9 jobs (Lean 4.35.0), `lake env lean Conde1963/AxiomAudit.lean` sem `sorryAx`, testes `24/24 PASS`, matriz SHA-1 correta e Web lint/build PASS. Artifact JSON https://github.com/franklinbaldo/conde-incident/actions/runs/43131263343/artifacts/13905670511 . **CI no HEAD pós-memória deverá ser checado novamente**, não atribuir aquele resultado ao novo SHA sem execução.
- **Não executado**: autenticação original adicional, ZIP `Evidence.lean` 154 proposições/151 rótulos, reconstrução orbital, validação independente do rastreamento de 1963, cálculo do erro da estimativa NASA, simulação e holdout NORAD 529. Nenhum novo dado histórico ou confiança probabilística inventados.

## Próxima pergunta e revisão

- Para tornar o dia real um teorema físico condicional com premissas defendíveis, recuperar observações primárias sobre a estimativa do NORAD e modelos físicos calibrados; quantificar intervalo de erro com retenção de dados de validação.
- Gavião deve rever nomenclatura e política de `uncertainty`, confirmando que `documento registra data` nunca implica `objeto decaiu nesse dia`; Elefante integra só após revisão e CI verde no último SHA.

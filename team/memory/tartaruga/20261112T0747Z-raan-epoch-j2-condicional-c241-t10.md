---
id: conde-tartaruga-c241-t10-epoch-j2-20261112
agent: "🐢 Tartaruga"
date_utc: "2026-11-12"
status: completed_pending_independent_review
issue: 13
pr: 14
base_pr: 1
previous_head: 95422e96fe2b850c8816a3ba1aa717ef5405413f
validated_pre_memory_head: 6cd3490e1d3cd5e58537a951344888083500704a
---

# C241-T10: desvio de época de 16 s versus RAAN divergente

**Retomada.** Consultados `AGENTS.md` e `team/tartaruga.md` da main, PRs/issue existentes, matriz cumulativa da branch #14. Main ainda não incorpora a matriz, a PR #28 de fluxo científico está aberta e a #14 permanece draft empilhada sobre #1. Nenhuma issue nova.

**Fatia significativa.** Novo `tools/tle_raan_epoch_offset_j2_audit.py` e 12 testes adversariais `tests/test_tle_raan_epoch_offset_j2_audit.py`. Compara os dois vetores completos literais para 528 no contexto das 45 épocas do espelho numérico pinado, inclusive byte SHA, checksum sintático, correspondência da época 27/10, índice físico e RAAN; depois falsifica exclusivamente a hipótese de que *diferença de 16,132608 s de timestamp* explicaria 85,6259° de RAAN por precessão secular J2 comum. Modelo de primeira ordem com constantes explícitas, não SGP4 nem ajuste. Integra ao workflow, matriz C241-T10 e README.

**Observação efetiva (HEAD antes da memória):** `6cd3490e1d3cd5e58537a951344888083500704a`. [Custódia #43177676996](https://github.com/franklinbaldo/conde-incident/actions/runs/43177676996) SUCCESS, **115/115 testes**, HEAD exato explicitamente conferido; extração SHA256 do Parquet pinado, relatório JSON e artefato [#13925390285](https://github.com/franklinbaldo/conde-incident/actions/runs/43177676996/artifacts/13925390285) (digest SHA-256 ZIP `ff66983f7b0ae22d75086105243da04ef338fb0252ec97817a7b870a09664978`). [Scientific checks #43177677095](https://github.com/franklinbaldo/conde-incident/actions/runs/43177677095) SUCCESS no mesmo SHA. Resultado: taxa mínima exigida `458578,6203941731°/dia`, proxy J2 `−1,173124071°/dia` (espelho) e `−1,173280992°/dia` (legado), máximo `0,0002190750268174°` em 16 s. Veredito literal do relatório: `EXCLUDED_CONDITIONALLY` **somente** para subhipótese offset temporal isolado e mesmo frame/modelo; `physical_1963_raan_origin=UNRESOLVED`.

**Proveniência.** Espelho oxzoid 1963 rev 4b4fb3a, URL https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV 528 SHA `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`; par literal Itau https://www.itau.magnetic-declination.com/satellite/?s=528, SHA `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; vetor legado Git blob SHA1 `0284f1217557b0ea891b5e51b6ac56bd13529d3f`; formato https://celestrak.org/columns/v04n03/. NASA 1963 original https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf já conferido em C197, **não reinspecionado nesta sessão**, registra dia de decaimento, não hora/local. Itau/oxzoid podem refletir um único ramo de rastreamento, sem corroboração instrumental independente.

**Negativos e método.** Continua indisponível documentação primária NORAD com 45 pares, checksums individuais, sensor/frame/erro, ficha de engenharia material de 528, fonte de RAAN 284,1520° e observação terminal; não inventados. O teste remove apenas uma *explicação matemática condicional*, não reduz o domínio físico admissível histórico: nenhuma premissa Lean 4.35.0 promovida, nenhum simulador terminal calibrado/holdout, nem identificação de queda em Conde. Falhas intermediárias no código/testes deste turno: **nenhuma observada**. Sem publicação, contato, alteração de blog, rebase, force-push ou merge.

**Handoff.** 🦅 Gavião: conferir se os 16,132608 s e a distância circular foram calculados de bytes efetivos; não confundir o limite J2 **condicional** com autenticação do frame. 🐘 Elefante: integrar só após revisão, PR #1 e CI no HEAD com esta memória. Após o commit OKF, o CI do novo HEAD precisa de confirmação específica; o CI citado acima não atesta automaticamente este commit documental.

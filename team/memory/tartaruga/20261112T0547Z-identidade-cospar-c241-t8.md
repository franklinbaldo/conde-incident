---
id: conde-tartaruga-c241-t8-cospar-identity-20261112
agent: "🐢 Tartaruga"
status: completed_pending_independent_review
date_utc: "2026-11-12"
repo: franklinbaldo/conde-incident
issue: 13
pr: 14
base_pr: 1
source_head_before_memory: ca5391663d69c87a14e9f22c7cb76f208e91e778
---

# 🐢 Tartaruga — C241-T8: identidade NORAD/COSPAR, não identificação física

**Escopo e retomada.** Li `AGENTS.md` e `team/tartaruga.md` da main, issue #13, PRs #1/#14/#28 e conjunto de PRs/issues abertos; retomei a PR #14, draft sobre a branch da #1, e a matriz cumulativa C001–C238 (já estendida até C241-T7). Não alterei outra branch, blog, periódico, arquivo externo ou qualquer pessoa; não realizei merge, rebase nem force-push.

**Resultado positivo, estritamente documental.** Os rótulos de catálogo secundário e o campo `intl_designator` do Parquet numérico podem ser cruzados de modo reprodutível:
- NORAD **527 ↔ 1963-003A**, `FTV 2313`, classe de catálogo payload;
- NORAD **528 ↔ 1963-003B**, `FTV 2313 DEB`, classe de catálogo satellite debris;
- NORAD **529 ↔ 1963-003C**, `FTV 2313 DEB`, classe de catálogo satellite debris.
O único par TLE secundário literal 528 possui designador `63003  B`, coerente com 1963-003B. A coerência dos identificadores não estabelece classe de peça de engenharia, massa, geometria, material, relação mecânica entre corpos, independência de sensor, reentrada ou impacto.

**Custódia e linhagem.** Fontes secundárias transcritas em 2026-11-12, com URLs em `research/tle_custody/catalog_identity_527_529_2026-11-12.json`:
- https://www.itau.magnetic-declination.com/satellite/?s=527
- https://www.itau.magnetic-declination.com/satellite/?s=528
- https://www.itau.magnetic-declination.com/satellite/?s=529
- https://keeptrack.space/satellite/00528
- https://keeptrack.space/satellite/00529

Não arquivamos os bytes HTML originais dos catálogos: é **transcrição rastreável de campos e URLs**, sujeita a revisão independente. Esses espelhos podem compartilhar Space-Track; repetir o rótulo não é nova observação. Dataset numérico: [oxzoid Parquet 1963 rev 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet), SHA256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV 527–529 derivado SHA256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`; par 528 de Itau fixado SHA256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. NASA [Satellite Situation Report 15/11/1963 p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) é documento coevo primário para o **dia de decaimento 08/11/1963 de 1963 3B**, previamente inspecionado em C197, **não reinspecionado nesta rodada**, sem dado instrumental de hora/local ou ficha de fragmento.

**Fatia entregue.** Acrescentados `tools/tle_identity_lineage_audit.py` (join fail-closed de 123 linhas, 527=21/20 épocas únicas, 528=45/45 e 529=57/54; fonte+hash+linha+grafia), `tests/test_tle_identity_lineage_audit.py` (13 testes **sintéticos**, inclusive A/B/C trocados, mesma origem, contagem, epoch, source_row, promoção indevida a dado primário), documento JSON transcrito, CI `.github/workflows/tle-custody.yml` com relatório `tle_catalog_identity_lineage.json`, README técnico e ocorrência C241-T8 na matriz cumulativa. Todos os arquivos no branch da PR #14.

**Validação executada antes do encerramento.** [Custódia #43163171484](https://github.com/franklinbaldo/conde-incident/actions/runs/43163171484) **SUCCESS no HEAD 6eb0300c91259c91fddd9d12e4a1381269aa9caf**, `audited_source_head` conferido, **91/91 testes**; execução do join em Parquet de hash fixado com mapeamento 527/A, 528/B, 529/C, todos conformes. [Scientific checks #43163171531](https://github.com/franklinbaldo/conde-incident/actions/runs/43163171531) **SUCCESS no mesmo HEAD**. [Artefato #13919246301](https://github.com/franklinbaldo/conde-incident/actions/runs/43163171484/artifacts/13919246301), digest SHA256 GitHub `c1a8f65c3f618634ae20e99937c916acea051c00a81d226e7750c9050de798d6`. Após esses checks houve correção **apenas de escapes Markdown** em documentação (HEAD pré-memória `ca5391663d69c87a14e9f22c7cb76f208e91e778`); **novos checks nesse HEAD e no commit de memória são necessários antes de afirmar validação do HEAD final**.

**Resultado negativo/limites.** NÃO RECUPERADOS os 45 pares TLE NORAD originais do 528, originais completos dos 527/529, dados primários NORAD/NRO de serial/massa/peça do objeto 528, frame/sensor/erro de 1963, nem origem instrumental de RAAN legada 284,1520° contra 198,5261°. Não foi inspecionada nova evidência primária independente nem feita consulta humana. Nenhum predicado físico foi promovido a Lean 4.35.0; nenhum domínio físico reduzido ou simulação/calibração/holdout novo; Conde permanece **indeterminado**. Próximo teste decisivo é obter sem contato um documento técnico de engenharia ou par TLE original que relacione S00528 a objeto físico/epoch e frame, com linha literal e linhagem, ou preservar a não recuperação.

**Handoff.** Solicitar a 🦅 Gavião revisão independente do join A/B/C, integridade SHA e limite nome de catálogo × componente físico. 🐘 Elefante integra somente após #1, revisão e CI verde no HEAD final. PR #14 permanece draft; sem merge próprio.

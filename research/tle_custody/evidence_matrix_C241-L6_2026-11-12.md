---
type: Guide
title: "C241-L6: secantes de movimento médio 527–529"
description: "Auditoria rastreável da diferença temporal de movimento médio e n-dot no catálogo secundário."
---

# C241-L6: secantes de movimento médio não são medições de arrasto

Suplemento aditivo à [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), às ocorrências [L2](evidence_matrix_C241-L2_2026-11-12.md), [L4](evidence_matrix_C241-L4_2026-11-12.md) e [L5](evidence_matrix_C241-L5_2026-11-12.md). Extração independente do experimento C241-T11 da [draft #14](https://github.com/franklinbaldo/conde-incident/pull/14), vinculada à [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13).

**C241-L6 / ocorrências:** cada par de épocas adjacentes e distintas do catálogo NORAD 527, 528 e 529. Fonte [oxzoid Parquet 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV derivado de 123 linhas indexadas por `source_row`, SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. **Espelho moderno secundário**, não pares TLE instrumentais originais de 1963. As duplicatas são preservadas como índices, mas não viram amostras independentes.

**Variáveis:** época UTC `t`, movimento médio `n` em rev/dia, valor `d` da coluna `mean_motion_dot` em rev/dia² e índices de origem. A identidade algébrica `s=(n2-n1)/(t2-t1)`, em rev/dia², fornece uma *secante descritiva*. O teste ilustrativo `Δn≈Δt(d1+d2)` supõe a convenção textual `n-dot/2` em todas as épocas e continuidade suave. [C241-L5](evidence_matrix_C241-L5_2026-11-12.md) confirmou essa codificação apenas em **uma** época literal de 528, não nas outras 122 linhas. Dados do mesmo espelho podem compartilhar fonte instrumental ou transformação.

**Elo cumulativo:** `CONNECTED_PENDING_CALIBRATION`. O relatório liga cada par de épocas à secante, ao campo codificado, à diferença e ao residual condicional. Referencial histórico dos elementos, mecanismo de ajuste, erros/σ/covariâncias, fonte por sensor e linhagem ETL seguem **desconhecidos** (`null`/NOT_RECOVERED), não zero. Nenhum predicado Lean 4.35.0 ou domínio físico de parâmetros é promovido. Secantes negativas com `d>0` **não provam arrasto negativo, salto orbital nem falha de dinâmica física**.

A fonte NASA contemporânea [Satellite Situation Report de 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) registra apenas o **dia 08/11/1963** de decaimento 1963-003B, sem hora/local; não mede esta secante. RAAN 198,5261° tem custódia **secundária**, enquanto a RAAN legada 284,1520° segue **sem fonte e inativa**. A identidade material de S00528 e impactos em Conde permanecem indeterminados.

**Reprodução:** `python -m unittest discover -s tests -p 'test_tle_mean_motion_secant_audit.py' -v`. Com `pyarrow==21.0.0`, executar `python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l6` e `python tools/tle_mean_motion_secant_audit.py --csv /tmp/c241-l6/norad_527_528_529_numeric_1963.csv --output /tmp/c241-l6/mean_motion_secants_c241_l6.json`. [CI](../../.github/workflows/tle-mean-motion-secants.yml) verifica SHA do HEAD, fonte e CSV e arquiva JSON/CSV; nenhuma simulação preditiva é alegada.

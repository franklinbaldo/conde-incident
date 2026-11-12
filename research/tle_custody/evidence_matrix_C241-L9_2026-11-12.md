---
type: Guide
title: "C241-L9: dependência algébrica possível de altitude_km"
description: "Auditoria secundária de altitude versus movimento médio e excentricidade, preservando incerteza e independência."
---

# C241-L9: altura de catálogo não é automaticamente um sensor novo

**Ocorrência C241-L9**, issue [#13](https://github.com/franklinbaldo/conde-incident/issues/13). Suplemento da [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), [C241-L2](evidence_matrix_C241-L2_2026-11-12.md) e [C241-L8](evidence_matrix_C241-L8_2026-11-12.md). Extrai o teste C241-T13 da [draft #14](https://github.com/franklinbaldo/conde-incident/pull/14) para PR independente.

**Observação catalográfica:** `altitude_km`, `mean_motion` e `eccentricity` são colunas do [Parquet secundário oxzoid 1963, rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. O CSV derivado indexado por `source_row` possui SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. Corpus: 123 registros, 119 épocas distintas (527 21/20, 528 45/45, 529 57/54); quatro duplicatas não representam sensores independentes. Não foi recuperado o arquivo TLE primário instrumental ou código do ETL original.

**Hipótese diagnóstica, não observação física:** converter `n` (rev/dia) em `a_proxy=(μ/(2πn/86400)^2)^(1/3)` (km), com μ=398600,4418 km³/s²; testar `h_proxy=a_proxy(1-e)-6371 km`. 6371 km é um parâmetro **candidato de conversão**, não valor histórico autenticado. Confrontar também raio 6378,137 km e os proxies de apogeu e semieixo médio; o cálculo biplanar não valida os elementos médios SGP4.

**Resultado prévio na draft C241-T13:** 119/119 épocas a menos de 0,1 km da fórmula de perigeu candidata, resíduo absoluto médio de 0,002422669 km, raio implícito [6370,995084995; 6371,004952507] km. São resultados matemáticos em espelho secundário, **não evidências independentes de altitude nem prova da fórmula ETL**. O limiar 0,1 km é diagnóstico, jamais σ de instrumento. A PR nova reexecuta o teste e verifica essa reprodução no HEAD próprio.

**Grafo cumulativo:** aresta `C241-L9:altitude_km_perigee_proxy_dependence` liga observável `altitude_km` (km), linha catalográfica, `n,e` do mesmo registro e equação candidata. Variáveis faltantes: `original_1963_NORAD_TLE`, exportador/ETL, convenção μ/raio/frame e calibração de erro. `measurement_sigma=null`, `physical_frame=null`, independência `NOT_ESTABLISHED`; estado `CONNECTED_PENDING_CALIBRATION`. **Restrição Lean 4.35.0:** `NOT_PROMOTED`; **domínio físico:** `NOT_COMPUTED`; **simulador/holdout:** `NOT_RUN`.

**Conflitos preservados:** 198,5261° é RAAN de par *secundário* 528, 284,1520° é construção legada sem fonte e **não observação ativa**. NASA SSR 15/11/1963 (NTRS 19640001198, p. impressa 8) registra apenas **dia 08/11** de decaimento de 1963-003B, sem horário/posição ou identidade material da peça. Conde `INDETERMINATE`.

**Reproduzir:** `python -m unittest discover -s tests -p 'test_tle_altitude_lineage_audit.py' -v`; `pip install pyarrow==21.0.0`; `python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l9`; `python tools/tle_altitude_lineage_audit.py --csv /tmp/c241-l9/norad_527_528_529_numeric_1963.csv --output /tmp/c241-l9/altitude_c241_l9.json`. [Workflow auditável](../../.github/workflows/tle-altitude-lineage.yml) confirma SHA do HEAD e arquiva dados derivados.

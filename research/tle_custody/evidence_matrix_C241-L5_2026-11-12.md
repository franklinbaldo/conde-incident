---
type: Guide
title: "C241-L5: custódia n-dot e BSTAR dos NORAD 527–529"
description: "Suplemento científico rastreável da linhagem secundária TLE e testes de codificação n-dot/BSTAR."
---

# C241-L5: custódia de n-dot/2 e BSTAR do 528 e série 527–529 (12/11/2026)

Suplemento **aditivo** à [matriz histórica C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), [C241-L1](evidence_matrix_C241-L1_2026-11-12.md), [C241-L2](evidence_matrix_C241-L2_2026-11-12.md), [C241-L3](evidence_matrix_C241-L3_2026-11-12.md) e [C241-L4](evidence_matrix_C241-L4_2026-11-12.md). Isolado da auditoria C241-T9 na [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14); **uma linhagem catalográfica secundária, não sensores independentes**.

| ID / ocorrência | Fonte / custódia | Dado, unidade e incerteza | Conexão / consequência científica |
|---|---|---|---|
| **C241-L5 / 528, 27/10/1963 14:40:16.132512 UTC, source_row=3017** | Par TLE secundário de [Itau](https://www.itau.magnetic-declination.com/satellite/?s=528), bytes em [L1](mirror_528_1963-10-27.tle), SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; cruzado com [Parquet oxzoid rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet) SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` e [CSV 123 linhas C241-L2](evidence_matrix_C241-L2_2026-11-12.md), SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. | `n-dot/2` codificado na linha 1: **0,00686563 rev/dia²**; espelho `mean_motion_dot`: **0,00686563 rev/dia²**. Não multiplicar por 2 sem demonstrar convenção. `BSTAR` no registro: **0**. Incerteza, sensor, frame histórico, transformação ETL e independência: **desconhecidos** (`null` no elo), não zeros. | `mean_motion_dot_mirror(528,t) = n-dot/2_TLE(528,t)` **é teste de consistência entre representações secundárias**, não lei física nem prova de derivada instantânea. Gate `CONNECTED_PENDING_CALIBRATION`; sem restrição Lean 4.35.0 ou domínio reduzido. |
| **C241-L5 / Parquet 1963, 527/528/529** | Mesma revisão/hashes, preservando `source_row` e 21/45/57 linhas, com 20/45/54 épocas únicas; não contabilizar duplicatas como medições. | Auditoria histórica secundária anterior encontrou **123/123 BSTAR = 0** e **123/123 n-dot não zero**. Estes são valores publicados pelo *espelho*, não calibração física do arrasto. Resultado em CI do HEAD é o gate de ratificação desta extração. | `bstar=0` não implica `C_D A/m = 0`, tampouco ausência de forças atmosféricas. Ausência da 2ª derivada no Parquet não autoriza preenchê-la com 0. |
| **C241-L5 / semântica de formato** | [CelesTrak, FAQ técnico: Two-Line Element Set Format](https://celestrak.org/columns/v04n03/), definição 1.9, 1.10 e 1.11. É documentação técnica posterior, **não um registro de rastreamento de 1963**. | Campo 1.9: metade da derivada em rev/dia²; 1.10: um sexto da segunda derivada; 1.11: BSTAR em raios terrestres inversos. Os campos de derivada **não são usados pelo SGP4/SDP4** nesta descrição. | Define como ler o *literal* moderno; não autentica formato original de 1963 nem precisão instrumental. |

## Elo conectado e riscos

O JSON `line1_drag_terms_c241_l5.json` liga as variáveis `n_dot_espelho, BSTAR_espelho, n_dot_linha1/2, BSTAR_linha1` à época UTC, catálogo 528, linhagem pinada e parâmetro latente de arrasto. O observable futuro exigiria linha 1 NORAD original por época, mapeamento histórico do transformador Parquet, convenção dos elementos e frame, incerteza/covariância por sensor e equações de arrasto com modelo e validação. Até lá, erro e convenção não observada são `null`, não zero. A comparação é restrição **de consistência documental**, jamais inclusão na conjunção física `Θ`, likelihood ou simulação preditiva.

A RAAN **198,5261°** é rastreável a essa mesma linhagem secundária, enquanto **284,1520°** é vetor legado sem fonte e **não é observação ativa**. O relatório NASA [15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) registra dia de decaimento em 08/11, sem lugar ou hora: documento coevo, não evidência para n-dot/BSTAR. Os 45 pares TLE primários, frame histórico, sensor/erro/covariância, documentação ETL e identificação material de 528 seguem **NOT_RECOVERED**. Nenhuma hora/posição/impacto em Conde é inferida.

## Reprodução no CI e resultado negativo

```bash
python -m unittest discover -s tests -p 'test_tle_drag_term_lineage_audit.py' -v
python -m unittest discover -s tests -p 'test_tle_literal_layout.py' -v
python -m pip install pyarrow==21.0.0
python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l5
python tools/tle_drag_term_lineage_audit.py --csv /tmp/c241-l5/norad_527_528_529_numeric_1963.csv --pair research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l5/line1_drag_terms_c241_l5.json
```

Testes com dados sintéticos verificam parsers, formato, alternativas de escala, duplicatas, epoch e falha fechada em hash; **não** se apresentam como medições. O SHA do HEAD e run do CI serão citados na PR e na memória OKF após execução.

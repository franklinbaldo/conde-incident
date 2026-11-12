---
type: Guide
title: "C241-T15#1: baseline quadrático sem nova evidência orbital"
description: "Ocorrência suplementar de ablação numérica com dependência documental e incerteza explícitas."
---

# C241-T15#1

**Origem:** oxzoid [Space-Track 1963 rev 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, catálogo secundário, única linhagem de tracking. Os 527/528/529 não são sensores independentes. NASA NTRS 19640001198 primária somente para o **dia** de decaimento, não para estes RAAN.

**IDs existentes preservados:** C25#1, C179#1, C180#1, C181#1, C241-P1#1, C241-P2#1. **Arestas novas:** RAAN com época UTC secundária → partição temporal congelada → curva quadrática ajustada só no fit → previsão angular → erro circular em graus → comparação pareada nos 4/8/23 holdouts dos 527/528/529. Curvatura ajustada (graus/dia²) é variável de modelo, não aceleração observada.

**Status:** `CONNECTED_PENDING_CALIBRATION`, teorema físico `NOT_PROMOTED`, inferência terminal `NOT_RUN`, conjunto Θ `UNCHANGED_UNCALIBRATED`. Sem TLE instrumental original, época/frame autenticados, covariância e validação externa, nenhum resultado pode determinar queda em Conde.

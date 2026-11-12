---
type: Guide
title: "C241-L7: precisão de armazenamento de elementos NORAD 527–529"
description: "Teste binário e decimal de seis elementos no espelho Parquet 1963, sem reconstruir TLE instrumental."
---

# C241-L7: precisão numérica não autentica o TLE original

**Ocorrência C241-L7**, suplemento à [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), à [C241-L2](evidence_matrix_C241-L2_2026-11-12.md) e à [C241-L6](evidence_matrix_C241-L6_2026-11-12.md), vinculada à [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13). Extração independente da experiência C241-T6 da [draft #14](https://github.com/franklinbaldo/conde-incident/pull/14). Não registra uma nova medição.

**Fonte e independência:** [Parquet oxzoid 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, espelho moderno da alegada linhagem Space-Track. [Espelho literal 528](https://www.itau.magnetic-declination.com/satellite/?s=528), SHA-256 preservado `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. Possível origem instrumental comum: **não** contar como dois radares. [Kelso/CelesTrak](https://celestrak.org/columns/v04n03/) descreve a grade textual TLE posterior, mas não certifica o registro original de 1963.

**Variáveis tipadas:** para cada `source_row`, `norad_id`, `epoch_utc`, `inclination[deg]`, `raan[deg]`, `eccentricity[1]`, `arg_perigee[deg]`, `mean_anomaly[deg]`, `mean_motion[rev/day]`. O auditor lê os tipos Arrow reais, exige `float` (IEEE754 binário32) para ângulos/excentricidade e `double` (binário64) para movimento médio, calcula a representação decimal mais próxima na grade de 4/7/8 casas conforme campo e testa tanto `cast_binary(near_grid(v)) == v` como os dois vizinhos. Isso testa **somente roundtrip da codificação numérica**, não recuperação da grafia histórica original.

O corpus fixado contém **21/45/57 linhas de 527/528/529**, total 123; são seis campos por linha. Na versão antecedente C241-T6, [Actions #43150299688](https://github.com/franklinbaldo/conde-incident/actions/runs/43150299688) confirmou **738/738** roundtrips sem colisão com vizinhos e tipo `double` para `mean_motion`. O CI desta nova fatia **deve reproduzir** o achado no HEAD novo, sem importar automaticamente a aprovação antiga. A unicidade local da grade não prova unicidade global de lexemas originais.

**Linhagem incompleta e resultado negativo:** faltam os originais de cada época (`line1/line2`, dígitos de checksum, nddot original, número de revolução, sensor, ajuste e frame). Nenhuma linha de TLE foi reconstruída artificialmente. O campo RAAN 198,5261° é **secundário rastreável**; 284,1520° do vetor legado não possui fonte verificada e permanece **inativo como observação**, sem média arbitrária. Não há demonstração de que ambas as séries sejam do mesmo frame. Os dados físicos de erro, `sigma` e covariância permanecem `null`, não zero.

**Elo cumulativo:** `C241-L7 = CONNECTED_PENDING_CALIBRATION` registra a equação de recodificação binário-decimal e as dependências; `candidate_Lean_4_35_0_predicate = NOT_PROMOTED`, sem redução de domínio físico, simulação preditiva, holdout orbital ou inferência de impacto. **Conde = INDETERMINATE.** Para uma restrição orbital real faltam o registro NORAD/USAF primário, especificação do frame/época/sensor e limites de erro.

A [NASA *Satellite Situation Report* de 15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) é fonte contemporânea inspecionada anteriormente em C197 para o **dia** de decaimento 08/11, não uma fonte de TLE, hora ou posição. Não foi reinspecionada nesta fatia.

**Reprodução:** executar `python -m unittest discover -s tests -p 'test_tle_numeric_precision_audit.py' -v`, instalar `pyarrow==21.0.0`, gerar o ledger com `python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l7`, depois `python tools/tle_numeric_precision_audit.py --parquet /tmp/tle_1963.parquet --output /tmp/c241-l7/precision_c241_l7.json`. O [workflow](../../.github/workflows/tle-numeric-precision.yml) valida o commit HEAD real, a fonte SHA-pinned e os seis campos em 123 linhas; publica JSON com `source_row` e CSV do ledger.

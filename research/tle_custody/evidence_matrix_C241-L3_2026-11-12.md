# C241-L3: vizinhos cronológicos dos NORAD 527, 528 e 529 (12/11/2026)

Ocorrência suplementar à [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), sem modificar o blob original congelado, e às [C241-L1](evidence_matrix_C241-L1_2026-11-12.md) e [C241-L2](evidence_matrix_C241-L2_2026-11-12.md). **Não é uma nova observação orbital**: recicla os mesmos 123 registros secundários, sem contá-los duas vezes.

| ID | Origem, dependências e distinções de independência | Evidência verificável, incerteza e conexão futura |
|---|---|---|
| **C241-L3** | Fonte numérica [oxzoid Parquet 1963 revisão `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, extração já verificada na PR #99 e CSV completo SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. Os pares instrumentais NORAD originais, sensores, frame histórico e erro não foram recuperados. O catálogo é derivado, não independente dos espelhos de C241-L1/L2. | `tools/cross_object_epoch_support.py` preserva `source_row` e duplicatas idênticas, encontra o vizinho cronológico para cada uma das **45 épocas do 528** entre os 20 registros de época distinta do 527 e os 54 do 529, desempata pela época anterior e rejeita duplicatas discordantes. Relata separações **assinadas em microssegundos** e janelas de consulta 6/24/72 h (janelas de disponibilidade, **não σ instrumental**), exatidão literal e distância ≤432 μs, sem interpolar órbita. Status `CONNECTED_PENDING_CALIBRATION`: medições originais, convenção de época, correções de relógio, referencial e covariância são `null`/não recuperadas. **Conexão**, não estreitamento: futura comparação multiobjeto com modelo físico calibrado e holdouts; nenhum predicado físico Lean, domínio reduzido, posição terminal ou hipótese confirmada de impacto. |

## Ligação científica tipada, sem inventar erro

Ver [objeto de dependências C241-L3](../constraints/norad_1963_epoch_availability_C241-L3.json). A equação atualmente disponível é `Δt_catalog = t_catalog_vizinho - t_catalog_528`. Uma diferença entre carimbos de catálogo não estabelece medições simultâneas ou posição relativa dos três corpos. Não foi atribuída covariância, dispersão ou igualdade temporal artificial; RAAN secundária **198,5261°** é rastreável a uma linha Itau (C241-L1), mas a RAAN antiga **284,1520°** permanece sem fonte e inativa.

## Reprodução e resultados anteriores (necessário conferir no HEAD novo)

```bash
python -m unittest discover -s tests -p 'test_cross_object_epoch_support.py' -v
python -m pip install pyarrow==21.0.0
python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l3
python tools/cross_object_epoch_support.py --csv /tmp/c241-l3/norad_527_528_529_numeric_1963.csv --output /tmp/c241-l3/cross_object_epoch_support.json
```

Na auditoria original C241-T3 da PR draft #14, o resultado foi **0** épocas simultâneas (nem dentro de 432 μs), e **1 / 2 / 15** épocas 528 com ambos 527 e 529 disponíveis em 6 / 24 / 72 h. São resultados do **mesmo** espelho, não replicações independentes; o novo CI deve executar e verificar estes números em bytes pinados. A proveniência da linha está registrada pelo índice Parquet original, o resultado em JSON no artefato de CI. Não há fonte primária que permita converter separação de épocas em simultaneidade de observações ou σ.

A [NASA, Satellite Situation Report de 15/11/1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) documenta somente um **dia de decaimento** (C197), não os pares instrumentais 527–529 ou uma hora/posição de impacto. A fonte não foi reinspecionada nesta fatia.

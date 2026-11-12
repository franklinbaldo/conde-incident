# C241-L4: cronologia circular e lacunas da RAAN secundária do NORAD 528 (12/11/2026)

Suplemento aditivo à [matriz C001–C238](../evidence_matrix_C001-C238_2026-11-11.md) e às ocorrências [C241-L1](evidence_matrix_C241-L1_2026-11-12.md), [C241-L2](evidence_matrix_C241-L2_2026-11-12.md) e [C241-L3](evidence_matrix_C241-L3_2026-11-12.md). **Uma única linhagem secundária**, não 45 observações instrumentais autenticadas independentes. A PR draft #14 já continha a auditoria exploratória C241-T7; esta fatia isolada a conecta ao leitor pinado e ao CI da main.

| ID/ocorrência | Documento/observável/proveniência | Valor e incerteza | Dependências/limite |
|---|---|---|---|
| **C241-L4 / oxzoid Parquet 1963, epochs do 528** | [Arquivo secundário rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. Derivado da mesma família catalográfica de C241-L2, CSV de 123 linhas SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. | 45 épocas únicas do 528, 44 intervalos consecutivos; em auditoria anterior na draft #14, 3 intervalos ≤24h, 32 intervalos >72h e maior lacuna ≈23,5353 dias. **Novo CI em HEAD é gate para ratificar esses valores.** Cada intervalo tem início/fim UTC, `source_rows`, Δt em microssegundos e diferença circular de RAAN em graus. σ, precisão instrumental, frame e proveniência de sensor = **NOT_RECOVERED**, não zero. | `ΔΩ_circ = wrap_180(Ω_{i+1} − Ω_i)`; diferença aritmética de catálogos em épocas distintas, **não** precessão física observada, derivada diferenciável, inferência de forças, trajetória nem likelihood. Múltiplas linhas do mesmo Parquet não contam como medições independentes. |
| **C241-L4 / par literal secundário 528** | [C241-L1](evidence_matrix_C241-L1_2026-11-12.md), bytes SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`, checksum sintático PASS; época UTC 1963-10-27T14:40:16.132512Z e RAAN impressa 198,5261°. | Mesmo instante da linha Parquet `source_row=3017` no espelho, tolerância de **432 µs de quantização TLE**, não σ instrumental. RAAN 284,1520° do app legado **SEM FONTE, inativa**; distância 85,6259° na mesma época alegada e sua aproximação angular de agosto não são prova de identidade. | Dois espelhos potencialmente dependentes de mesma cadeia NORAD. Não se seleciona um vetor pelo local de impacto previsto. |
| **C241-L4 / NASA C197** | [NASA Satellite Situation Report, 15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf): 1963-003B decayed **08 Nov 63**. Documento oficial contemporâneo para o dia catalogado, **não** amostra RAAN em novembro. | Data civil somente, sem UTC terminal, frame, hora, localização, altura ou confirmação de impacto. A lacuna entre último registro numérico e começo/fim desse dia é cobertura documental, não faixa propagada da órbita. | NASA/NORAD/Parquet podem reutilizar a mesma linhagem de rastreamento. Não são observadores independentes automaticamente. |

## Restrição conectada, ainda não física

`C241-L4` é candidata do tipo `CONNECTED_PENDING_CALIBRATION`: variáveis `Ω_528(t_i)`, `t_i`, `source_row_i`; unidades graus/UTC µs. Observável futuro sob condições: `wrap_180(Ω_model(θ,t_{i+1}) - Ω_model(θ,t_i))`. Dependências faltantes: pares originais de linha 1/linha 2 por época, convenção de elemento e frame histórico, transformação para quadro/modelo adequado, erros/covariâncias e independência das medições. Até recuperar esses dados, **não** promover predicado Lean 4.35.0, não restringir Θ por esse cálculo, nem chamar uma secante de modelo dinâmico ou previsão. O JSON reprodutível mantém cada índice de origem e `null` para parâmetros desconhecidos.

## Reproduzir no GitHub Actions, sem contato com arquivos/pessoas

```bash
python -m unittest discover -s tests -p 'test_tle_raan_continuity_1963.py' -v
python -m pip install --disable-pip-version-check pyarrow==21.0.0
python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l4
python tools/tle_raan_continuity_1963.py --csv /tmp/c241-l4/norad_527_528_529_numeric_1963.csv --pair research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l4/raan_continuity.json
```

**Resultados negativos prévios:** TLEs instrumentais primários (45 pares 528 e outros 527/529), frame, covariâncias, identificação material de S00528 e origem do legado 284,1520° não recuperados. Esta fatia não resolve entrada/impacto em Conde e não substitui pesquisa primária. Nenhum blog ou contato externo é parte da execução.

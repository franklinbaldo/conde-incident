# C241-L1: índice cumulativo suplementar de custódia TLE (12/11/2026)

Esta é **uma ocorrência aditiva**, associada à matriz principal
[`C001–C238`](../evidence_matrix_C001-C238_2026-11-11.md), sem
reescrever seu Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`.
A matriz principal é uma fotografia científica deliberadamente fixada por
checks de integridade em `scripts/matrix-ledger.test.mjs` e
`formal/scripts/physical_observable_bridge.py`. Consultar **ambos** os
arquivos para a cobertura cumulativa. A extração abaixo não é fonte física
independente de C179/C181 ou da PR #14.

| ID | Evidência, proveniência e independência | Verificação / incerteza / conclusão |
|---|---|---|
| **C241-L1** | Auditor independente de código isolado da [PR #14, HEAD `48ae4fd70fabe9bfc910a12c6a29916c2a088015`](https://github.com/franklinbaldo/conde-incident/pull/14), arquivos `tools/tle_literal_layout.py` e `tests/test_tle_literal_layout.py`. Entrada: [espelho secundário Itau NORAD 528](https://www.itau.magnetic-declination.com/satellite/?s=528), dois bytes de linhas preservados em `mirror_528_1963-10-27.tle`, SHA-256 do arquivo `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; especificação do formato [CelesTrak/Kelso](https://celestrak.org/columns/v04n03/). O espelho Itau e o numérico oxzoid podem ter origem de rastreamento comum e não são medições independentes. | Controle estrito apenas de **um par TLE moderno secundário**: ASCII 69 colunas, checksums impressos 0/4, catalog 00528, época `63300.61129783` = `1963-10-27T14:40:16.132512Z` (864 μs por unidade TLE), unidades e RAAN literal **198,5261°**. A RAAN sem fonte **284,1520°** permanece forense e não operacional. Os outros 45 pares históricos NORAD, os sensores, frame, erro e identidade material de 528 **não foram observados**; nenhum constrangimento Lean físico nem localização terminal. [NASA 15/11/1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), matriz C197, continua estabelecendo somente dia 08/11; não foi reinspecionada nesta fatia. |

## Teste de regressão e histórico do gate

```bash
python -m unittest discover -s tests -p 'test_tle_literal_layout.py' -v
python tools/tle_literal_layout.py \
  --pair research/tle_custody/mirror_528_1963-10-27.tle \
  --output /tmp/tle-528-literal.json
```

Primeiro HEAD `33319837a6718e802cbb798124b2875ee47cc823`: gate próprio
[Actions #43210899314](https://github.com/franklinbaldo/conde-incident/actions/runs/43210899314)
**PASS**, 10 testes. Porém, o primeiro commit editou a matriz principal,
violando o hash de arquivo congelado e levando a falhas em
[physical observables #43210899133](https://github.com/franklinbaldo/conde-incident/actions/runs/43210899133)
e [integration checks #43210899161](https://github.com/franklinbaldo/conde-incident/actions/runs/43210899161).
Foi corrigido neste commit pelo retorno dos bytes exatos e criação
deste suplemento acumulativo. Nenhuma falha foi escondida. Validar novamente
todas as suites no HEAD final antes de merge; o resultado do primeiro HEAD
não valida automaticamente o HEAD corrigido.

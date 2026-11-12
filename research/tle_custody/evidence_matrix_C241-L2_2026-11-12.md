# C241-L2: ledger numérico de 45 épocas do NORAD 528 (12/11/2026)

**Escopo e dependência.** Ocorrência suplementar à
[matriz cumulativa C001–C238](../evidence_matrix_C001-C238_2026-11-11.md)
e a [C241-L1](evidence_matrix_C241-L1_2026-11-12.md).
O arquivo cumulativo original tem hash de Git blob
`a7978c3a75a153b16ab70118a92c434bba674cb7`, preservado aqui
para não quebrar controles de integridade. O presente ledger é uma
auditoria **dos mesmos dados secundários**, não uma observação adicional.

| ID | Fonte / dependência / grau de verificação | Resultado, estado e incerteza |
|---|---|---|
| **C241-L2** | [oxzoid/space-track-tle-history, Parquet de 1963, revisão do fork `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 fixado `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; exportação Space-Track **alegada**, original instrumental por época não examinado; transformação e sensor desconhecidos. Comparação secundária com [espelho Itau do 528](https://www.itau.magnetic-declination.com/satellite/?s=528), arquivo literal de SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. A possível origem de rastreio comum impede dupla contagem instrumental. Formato/quantização: [CelesTrak/Kelso](https://celestrak.org/columns/v04n03/). | `tools/tle_secondary_1963_ledger.py` confere SHA antes de decodificar, conserva índices de linha do Parquet, rejeita época sem UTC, fora da grade de 864 μs, campos não finitos e duplicatas conflitantes. Exporta CSV completo 527/528/529, CSV das **45** épocas numéricas do 528 e manifest JSON com hashes de ambos. Contagens esperadas **21/45/57 linhas**, **20/45/54 épocas distintas** (análises anteriores da PR #14); validá-las no CI desta PR, não atribuir autenticidade histórica à contagem. Compara **os seis elementos no mesmo instante UTC** com o par Itau e não promove a RAAN antiga **284,1520°** sem origem documental a observação ativa. **Sem pares primários line1/line2**, checksum das 45 épocas **NÃO EXECUTADO**, frame/sensor/erro **NÃO VERIFICADOS**, identidade física do 528 **ABERTA**, impacto em Conde **INDETERMINADO**. |

## Procedimento reproduzível

```bash
python -m unittest discover -s tests -p 'test_tle_secondary_1963_ledger.py' -v
python -m unittest discover -s tests -p 'test_tle_literal_layout.py' -v
python -m pip install pyarrow==21.0.0
python tools/tle_secondary_1963_ledger.py \
  --download --parquet /tmp/tle_1963.parquet \
  --literal research/tle_custody/mirror_528_1963-10-27.tle \
  --output /tmp/c241-l2
sha256sum /tmp/c241-l2/*.csv
```

O workflow `.github/workflows/tle-secondary-epochs.yml` executa sobre
o **HEAD exato** e publica artefato por SHA do commit. Testes sintéticos
checariam mecanismos de falha, mas somente execução contra os bytes
fixados pode confirmar as contagens do corpus. O gate falha se mudar
uma linha, faltar catálogo, houver duplicata com estado orbital
divergente ou os espelhos divergirem além da precisão de representação.

**Fonte contemporânea de outra natureza:** o
[Satellite Situation Report da NASA de 15/11/1963, p. 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf)
documenta apenas o **dia civil** de decaimento de 1963-003B
(C197 na matriz principal), não fornece 45 TLEs, hora/local da reentrada
nem identidade física do fragmento. O PDF não foi reinspecionado nesta fatia.

Nenhuma restrição física foi promovida a Lean 4.35.0 sem fonte primária.
Não há simulação orbital, inferência de impacto nem identificação de
sensor. Dado decisivo ausente: boletins/pares instrumentais 1963 dos
527/528/529 com frame/época, logs de rastreamento e descrição de
engenharia da peça S00528.

## Resultado efetivamente reproduzido em GitHub Actions

No HEAD inicial `16f767d18d53299474d420b754eba9507ee957e1`,
[Actions #43220267253](https://github.com/franklinbaldo/conde-incident/actions/runs/43220267253)
passou com **12/12 testes adversariais** + **10/10 controles literais**.
O Parquet lido continha 4.567 linhas totais; para os IDs 527/528/529,
foram **21/45/57 linhas** e **20/45/54 épocas distintas**, sendo
respectivamente **1/0/3 linhas de época duplicada** sem conflito orbital.
O par secundário de 27/10/1963 coincidiu com a linha de origem **3017**,
com diferenças inferiores às tolerâncias decimais das seis colunas;
status `AGREES_WITHIN_NUMERIC_ROUNDING`.

Os outputs determinísticos desse HEAD tiveram SHA-256:

- `norad_527_528_529_numeric_1963.csv`: `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`;
- `norad_528_45_epochs_numeric_1963.csv`: `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`.

[Artefato ZIP #13946055970](https://github.com/franklinbaldo/conde-incident/actions/runs/43220267253/artifacts/13946055970),
SHA-256 `d688746b999b4859b130c16f7d84672e981607f580a6686250e735887ff7adfe`.
Esses hashes são derivados da **representação secundária** e não de
TLEs instrumentais originais. O CI do HEAD após este adendo também deve
ser conferido antes de merge.

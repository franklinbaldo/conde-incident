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

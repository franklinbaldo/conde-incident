---
type: Guide
title: "Caravelas 1963: origem codificada N/BRAZ nas 8.532 observações NOAA/ISD"
description: "Custódia dos códigos de procedência e tipo de relatório de Caravelas, com limites de independência, observação e calibração."
---

# Procedência codificada da série horária de Caravelas, 1963

**Nova ligação documental (13/11/2026).** A auditoria do [GZIP original NOAA/ISD 1963, estação 834970-99999](https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz) encontrou **8.532 registros anuais**. Em **todos**, o código de fonte (posição humana 28) é `N`, e o tipo de relatório (posições 42–46) é `BRAZ `, com espaço final. O código bruto de processo de qualidade (posições 57–60) é `V020`. Nos 72 horários de 7–9/11 esses campos são idênticos. O SHA-256 do GZIP é `c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05`; o recorte reversível de 72 horários tem SHA-256 `c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000`.

Segundo a [documentação oficial de formato ISD de 12/01/2018](https://www.ncei.noaa.gov/pub/data/noaa/isd-format-document.pdf), **páginas impressas 5–6, páginas 5–6 contadas a partir de zero no PDF**, `N` indica *NCAR/NCEI cooperative effort (various national datasets)* e `BRAZ` indica *Dataset from Brazil*. O documento adverte explicitamente que metadados como latitude/longitude podem variar entre fontes sem demonstrar mudança física de estação. Isso reforça a cautela sobre a [discrepância cartográfica Caravelas](isd_caravelas_station_lineage_1963.md).

**Interpretação restrita:** os códigos demonstram a *classificação atribuída na compilação NOAA*, não identificam o operador brasileiro, a forma original, o anemômetro, o horário local do observador, a mudança de endereço ou a cadeia de custódia das fichas de 1963. `BRAZ` não implica que a observação foi feita pela instituição atualmente responsável pelo local; `N` não significa que NCAR ou NCEI operaram o sensor. `V020` não fornece sigma. Sem cruzar a origem da compilação, tampouco se deve declarar independência documental de outros produtos NOAA. A edição de formato de 2018 é retrospectiva, não instrução operacional contemporânea a 1963.

| Universo | Registros | Fonte N | Tipo BRAZ | QC bruto V020 |
|---|---:|---:|---:|---:|
| Ano de 1963 | 8.532 | 8.532 | 8.532 | 8.532 |
| 7–9 de novembro UTC | 72 | 72 | 72 | 72 |

**Conexão física acumulativa:** `Caravelas ISD (fonte N/BRAZ) → linhagem instrumental pendente → vento observado na estação → função de transferência temporal/espacial pendente → vento de superfície em Conde → eventual modelo de trajetória`. O grafo [`isd_caravelas_source_flags_edges_1963.json`](../constraints/isd_caravelas_source_flags_edges_1963.json) conserva cada dependência e mantém `instrument_sigma`, `spatiotemporal_transfer_uncertainty` e restrição ativa nulos. O resultado é evidência nova de **procedência da compilação**, não vento medido em Conde ou prova de reentrada/queda.

## Reprodução

```bash
python3 tools/audit_isd_caravelas_source_flags_1963.py --check
python3 -m unittest discover -s tests -p 'test_isd_caravelas_source_flags_1963.py' -v
curl -fL https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz -o /tmp/caravelas-1963.gz
python3 tools/audit_isd_caravelas_source_flags_1963.py --check --verify-full-gz /tmp/caravelas-1963.gz
```

O validador compara o recorte original e sua contagem diária, o manifesto, o grafo e a distribuição do arquivo anual quando fornecido. A próxima etapa verificável é buscar o inventário **NCAR/NCEI do conjunto brasileiro subjacente ao código `N/BRAZ`** e, depois, fichas instrumentais da época, sem presumir independência pelo nome do produto.

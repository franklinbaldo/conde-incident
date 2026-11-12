---
type: Guide
title: "Lontra: EOR não é sondagem no arquivo NMC Y20175 (1963)"
description: "Fingerprint integral de bytes de payload COS, custódia e limite ON20"
---

# Y20175: auditoria dos comprimentos entre EOR (1963)

**Inventário:** MET-NMC-COS-LENGTHS-20261112-01. **Fonte binária:** GDEX d353000, NMC B3 ADP, arquivo Y20175, DOI 10.5065/R592-TX59. **Origem pública:** https://osdf-director.osg-htc.org/ncar-gdex/d353000/Y20175. **Pai:** MET-NMC-COS-20261112-01 e [estrutura COS](nmc_y20175_cos_structure_2026-11-12.json).

## Observação reproduzível

A réplica local integral de **117.264.384 bytes** foi confrontada com SHA-256 **afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4** antes da inspeção. A ferramenta tools/audit_nmc_y20175_record_sizes.py reutiliza a validação completa dos controles COS e acumula os bytes situados entre BCW/RCW, sem decodificar suas 36/64 posições de bits internas.

O percurso encontrou **14.889 delimitadores EOR**, que encerram **14.889 grupos físicos de payload**, totalizando **116.916.208 bytes**. SHA-256 do fluxo de payload concatenado sem palavras de controle: **a8a58f9e362b0be9d136c807b057fa5319f44b658179e2a74976d1a762b5d78e**. Esse hash é um fingerprint do **derivado calculado em 2026**, não um hash histórico arquivado pelo NMC.

Os tamanhos observados têm **71 valores distintos**, mínimo **1.192**, mediana por índice inferior **7.864**, máximo **8.000** bytes. Dos grupos, **14.500** ficam entre 7.000 e 7.999 bytes, **387** têm exatamente 8.000, **um** está em 6.664 e **um** encerra o arquivo com 1.192. Os EOR extremos aparecem nos offsets **7.800** (primeiro) e **117.264.344** (último). Os marcadores EOF de offset **117.264.352** e **117.264.360** aparecem consecutivamente, antes do EOD em **117.264.368**. **Dois EOF não demonstram duas séries históricas independentes.**

A distribuição completa dos 71 comprimentos, percentis, offsets e estado sem observações está no [manifesto JSON](nmc_y20175_cos_payload_sizes_2026-11-12.json). Reexecutar após baixar o arquivo integral:

    python3 tools/audit_nmc_y20175_record_sizes.py Y20175 --manifest research/meteorology/nmc_y20175_cos_structure_2026-11-12.json

Testes offline com corpus sintético e contraprovas (hash, tamanho, BCW, payload final e rótulos) em tests/test_nmc_y20175_record_sizes.py. Não armazenamos o binário de 117 MB nem os bytes do corpus em Git.

## Limite de inferência e próximo gate

Os 14.889 grupos **não são 14.889 sondagens, estações ou horários**. O padrão de grupos próximos de 8 kB caracteriza a estrutura de bloqueio observado, não a quantidade de relatos meteorológicos. Segundo o [catálogo GDEX](https://gdex.ucar.edu/datasets/d353000/), Y20175 usa *NMC Office Note 20* encapsulado no CRAY RPTOUT. O [histórico técnico NCEP/NCAR](https://ftp.cpc.ncep.noaa.gov/wd51we/reanal/bams_paper.2001/reanl2.htm) distingue ON20 (1962–1972) de ON29 (a partir de 1973). **A documentação pública de ON29 não é autorização para ler bytes ON20 como se fossem ON29.**

Estado NOT_DECODED: não houve identificação de WMO 83229/83096/82900, 7–9 de novembro de 1963, horário, direção do vento, altitude, qualidade ou relatório ausente. Estado das restrições físicas/orbitais NOT_ACTIVATED. A relação prospectiva com research/constraints/nmc_y20175_pending_bridge.json é de **dependência documental, não redução numérica**.

**Próxima dependência:** localizar um layout/decoder primário validável de ON20/RPTOUT da época e exercitar contra exemplos verificados, depois extrair índices de report com offsets, datas e QC. Sem isso, NÃO fazer inferência de presença/ausência de estações. Nenhuma pessoa/arquivo foi contatada.

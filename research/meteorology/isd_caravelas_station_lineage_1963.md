---
type: Guide
title: "Caravelas 1963: posições conflitantes dentro da própria NOAA/ISD"
description: "Comparação reproduzível de campos geográficos do arquivo horário 1963 com o catálogo retrospectivo de estações ISD."
---

# Caravelas 1963: divergência de metadados geográficos

**Novo achado documental (13/11/2026):** os 72 registros de 7–9/11/1963 da série horária de Caravelas, NOAA ISD 834970-99999, trazem uma posição, mas a linha do cadastro retrospectivo isd-history.csv informa outra. Trata-se de **dois campos da mesma família documental NOAA**, não duas medições geodésicas independentes nem uma prova de mudança física de local.

| Campo | Registros ISD de 1963 | Cadastro isd-history.csv |
|---|---:|---:|
| Latitude (graus decimais) | -17,633 | -17,652 |
| Longitude (graus decimais) | -39,250 | -39,253 |
| Elevação codificada (m) | 4 | 11 |
| Id da estação | 834970 / 99999 | 834970 / 99999 |
| Levantamento da instalação vigente em 1963 | **não localizado** | **não localizado** |

A distância geográfica aproximada entre as duas **posições codificadas** é **2,136489 km** (Haversine, esfera de raio médio 6.371,0088 km); a diferença de elevação codificada é **+7 m** no cadastro. Não são estimativas da precisão do GPS, deslocamento real de uma estação, incerteza de 2,14 km ou desnível a aplicar à atmosfera.

**Fonte 1:** [NOAA/NCEI, GZIP ISD Caravelas 1963](https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz), SHA-256 c4a0b2f625e8febcd03c4b6ca6ac37b91c9d38423a2ccddd6f0cd7a7712e7e05. As 8.532 linhas anuais contêm a mesma codificação de latitude (-17633), longitude (-039250) e elevação (+0004) no cabeçalho fixo. O recorte de 72 linhas está preservado na [auditoria anterior](isd_caravelas_19631107_09.md), SHA c6926a86150df982d13286285c17a70e4752cb1ce0ffe1d44ae5330be215a000. Posições constam nas colunas 29–34 e 35–41 (contagem humana iniciada em 1), elevação nas colunas 47–51. Não foi recuperado o levantamento topográfico contemporâneo de 1963.

**Fonte 2:** [NOAA/NCEI, cadastro ISD de estações](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv), SHA-256 integral 1994747ab4af1b97e63adb434b4d0d022f2daee76f0c144ea9ab46be2d906604. A linha literal única para 834970 / 99999 / CARAVELAS foi salva, com cabeçalho, em [CSV reversível](isd_caravelas_history_row_20261113.csv), SHA-256 **da linha de dados** b24514a2be25cf2fe2e59dce58f78f577e27878b69435b6db8098df74a4a7a7e. O cadastro informa o intervalo agregado 19610101–19971231, mas **não a data em que suas coordenadas foram medidas**. Não é correto projetar automaticamente esse ponto de catálogo para 1963.

**Contexto metodológico:** a [documentação oficial NOAA ISD](https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database) esclarece que a coleção integra mais de cem fontes e inclui transcrições de arquivos impressos das décadas de 1950–1970. A origem e o campo de localização de cada linha devem ser auditados, não pressupostos originais do operador de 1963.

## Efeito sobre o grafo científico

A [aresta cumulativa específica](../constraints/isd_caravelas_position_genealogy_1963.json) conecta observações de superfície de Caravelas → identidade/local do instrumento ainda a autenticar → transferência espacial Caravelas→Conde ainda pendente. O novo delta é **uma inconsistência de metadados quantificada**, não restrição numérica à localização de queda. Os erros instrumentais e covariâncias são desconhecidos, não zero. O controle regional de Caravelas segue CONNECTED_PENDING_SPATIOTEMPORAL_CALIBRATION, dependente da posição histórica, da altura e exposição do sensor e de modelo espacial/temporal validado.

A próxima evidência útil seria o **registro contemporâneo de instalação/mudança da estação ou ficha operacional de 1963** (com data, coordenada, datum e método), capaz de desambiguar as duas posições arquivísticas. Uma reanálise derivada de NOAA pode partilhar fontes e não constitui automaticamente controle independente.

## Testes e reprodução

Execute, no repositório do projeto, estes comandos:

    python3 tools/audit_isd_caravelas_station_lineage.py --check
    python3 -m unittest discover -s tests -p 'test_isd_caravelas_station_lineage.py' -v
    curl -fL https://www.ncei.noaa.gov/pub/data/noaa/1963/834970-99999-1963.gz -o /tmp/caravelas-1963.gz
    curl -fL https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv -o /tmp/isd-history.csv
    python3 tools/audit_isd_caravelas_station_lineage.py --check --verify-full-gz /tmp/caravelas-1963.gz --verify-history-csv /tmp/isd-history.csv

O CI executa a comparação dos dois downloads integrais com hashes fixados. Se os arquivos NOAA mudarem, o gate falha até comparar os **conteúdos relevantes** e sua proveniência. Não substituir os pins silenciosamente.

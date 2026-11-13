---
type: Guide
title: "C149–C151: teste negativo de cobertura de Recife no World Weather Records 1961–1970"
description: "Inventário verificável de 21 estações brasileiras no WWR série 6, sem atribuir ausência de estação a ausência de sondagens nem inferir vento em Conde."
---

# Recife e o inventário de superfície WWR, 1961–1970

## Pergunta delimitada

O [World Weather Records da NOAA/NCEI, sexta série (1961–1970)](https://www.ncei.noaa.gov/products/world-weather-records) pode fornecer **observações instrumentais de Recife de novembro de 1963 independentes** dos perfis de altitude IGRA usados em C149–C151? A resposta só é possível para **este arquivo** e **este conjunto de estações**. O WWR é uma série de médias/somatórios **mensais de superfície**, não de sondagens de vento e densidade em altitude. Ser outra publicação ou arquivo NOAA não garante independência das medições.

Arquivo completo fixado: [`WWR_v01_global_array_1961-1970.txt`](https://www.ncei.noaa.gov/data/world-weather-records/series-6/access/data/WWR_v01_global_array_1961-1970.txt), **6.840.540 bytes**, SHA-256 `5e0dfd3c64449a93bdf88f37dcf6ec81db5852c8d8fe08cb4fb2e77857577c09`. Auditado em 13/11/2026 UTC. O arquivo completo foi baixado e verificado; a extração conserva integralmente os 89 caracteres de cada registro de cabeçalho brasileiro, sem normalização de dados meteorológicos. A regra de extração é explícita no [script](../../tools/audit_wwr_recife_1963_coverage.py): tipo de registro `1`, campo de país `BRAZIL` e identificador WMO de cinco algarismos. O [excerto dos 21 cabeçalhos](wwr_brazil_1961_1970_station_headers.txt) é versionado e possui hash no [manifesto](wwr_brazil_1961_1970_recife_coverage.json).

## Resultado negativo e independência

- **21** cabeçalhos de estação brasileira distintos neste arquivo; **0** com WMO **82899** ou **82900** e **0** cujos nomes contêm `RECIFE`/`CURADO`. Entre os cabeçalhos existentes, aparecem Aracaju (`83096`) e Fortaleza (`82397`), mas suas séries **não** substituem medições de Recife.
- Portanto, **não foi encontrado dado mensal de superfície de Recife nesta sexta série WWR** para cruzamento com os perfis IGRA. Isso é um **resultado negativo de cobertura**, não uma prova de inexistência histórica de termômetro, radiossonda ou medição local, nem de ausência em outro arquivo da NOAA.
- As sondagens de Recife de **7, 8 e 9 de novembro de 1963** em C149–C151 continuam existentes na linhagem IGRA auditada. O presente WWR não autentica o WMOID operacional, a posição da radiossonda, a altura geopotencial, o sensor ou o método de processamento de 1963; também não resolve o conflito de metadados **82899/82900** catalogados décadas depois.
- Um resumo **mensal de superfície**, ainda que fosse de Recife, não validaria sozinho vetores de vento horários/verticais nem covariâncias p/T/GPH. Estes dados não calibram densidade termoesférica, arrasto de órbita ou deriva dos fragmentos em Conde. A independência instrumental e a transferência espacial/temporal permanecem **não demonstradas**.

**Grafo cumulativo:** nó `WWR-S6-1963-BRAZIL-RECIFE-COVERAGE` (`resultado_negativo_arquivo`, fonte histórica compilada e digitalizada), aresta documental para `C149`, `C150`, `C151` e `C193`, estado `CONNECTED_PENDING_CALIBRATION`; sem novo limite duro. Altitude do observável de sondagem, hora de lançamento, erro instrumental, covariância e domínio geográfico **não são preenchidos** com este achado. A publicação e digitalização modernas não tornam o inventário uma testemunha independente do evento de novembro.

## Reproduzir e falsear

```bash
python3 tools/audit_wwr_recife_1963_coverage.py --check
python3 tools/audit_wwr_recife_1963_coverage.py --check --download
python3 -m unittest discover -s tests -p 'test_wwr_recife_1963_coverage.py' -v
```

`--check` valida hashes e metadados do excerto conservado no Git; `--download` baixa o arquivo **integral** da NOAA e compara bytes, SHA-256 e 21 cabeçalhos. Os sete testes adversariais incluem a inserção artificial de `82900`, duplicação de estação e corrupção do recorte. O download depende da disponibilidade do servidor; não é substituído por dados inventados.

**Próxima fonte prioritária:** procurar volume/catalogação WMO de **1963** ou catálogo observacional coevo que documente o WMOID operacional, instrumento e cálculo p/T/GPH; consultar sem contatar pessoas/arquivos. A negativa WWR, por si só, não pode ser convertida em incerteza numérica para Castor.

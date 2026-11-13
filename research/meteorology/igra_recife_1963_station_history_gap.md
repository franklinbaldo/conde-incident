---
type: Guide
title: "C149–C151: lacuna de metadados instrumentais Recife 1963"
description: "Auditoria direta dos eventos de estação NOAA/IGRA e códigos WMO, com épocas posteriores e proibição de retroprojeção."
---

# Recife em 1963: a série existe; a ficha instrumental de época continua ausente

## Fonte pública e operação reproduzível

Em **13/11/2026 UTC**, foram recuperados dois catálogos **NOAA/NCEI**: [`igra2-metadata.txt`](https://www.ncei.noaa.gov/pub/data/igra/history/igra2-metadata.txt), 6.595.873 bytes, SHA-256 `fe1a0b23614306d453728ba499e48ac4efa180956b8f222c55eb1adcfedf68f7`; e [`wmo-sonde-history.txt`](https://www.ncei.noaa.gov/pub/data/igra/history/wmo-sonde-history.txt), 8.252.302 bytes, SHA-256 `e72e594b8f1c2ce3543e997e5bec0ca0a13d72d41b91197fa16325a1436af0fe`. O [readme de metadados](https://www.ncei.noaa.gov/pub/data/igra/history/igra2-metadata-readme.txt), atualizado em **19/01/2023**, documenta colunas fixas, épocas e indicadores de datas incertas. A custódia é de **catálogo retrospectivo**, não de registro de lançamento de 1963; parte do histórico provém de Gaffen (1996) e referências citadas por linha. As fichas derivadas não são observações atmosféricas independentes.

Os **12 registros** de estação (`BRM00082900`) no primeiro catálogo datam apenas de **1982, 1986, 1989 e 1992**. Os **12 intervalos** do segundo catálogo têm início entre **2000 e 2019**. Não há entrada de 1963 **nesses dois arquivos**, o que **não** demonstra ausência de sondagem em 1963. Para reprodução sem rede em CI, os excertos de linhas originais estão preservados nos dois `.txt` adjacentes, com hashes e SHA das fontes integrais no [JSON auditável](igra_recife_1963_station_history_gap.json).

## O que os registros realmente permitem dizer

| Ano do evento catalogado | WMOID original | Identificação/posição listada | Limite |
|---|---|---|---|
| 1982, 1986, 1989 | 82899 | RECIFE, −8,1330°, −34,9170°, 11 m | Dia/mês desconhecidos (`99`); indicador de data incerta `1` |
| 1982, 1986, 1989 | 82900 | RECIFE/CURADO, −8,0667°, −34,8833°, 19 m | Mesmo limite cronológico |
| março e dezembro de 1992 | 82900 | RECIFE (CURADO), −8,0500°, −34,9200°, 11/7 m | São eventos **de 1992**, não locação instrumental de 1963 |

Os eventos de 1982–1992 registram denominações de radiossonda Vaisala, mas **não autorizam atribuir Vaisala a novembro de 1963**. O mesmo identificador IGRA reúne WMOIDs originais **82899 e 82900** com coordenadas divergentes em datas tardias. Isso exige cautela de proveniência, **não** prova deslocamento físico, estação duplicada ou erro de catalogação em 1963. A [documentação NOAA](https://www.ncei.noaa.gov/pub/data/igra/history/igra2-metadata-readme.txt) avisa que eventos, coordenadas e disponibilidade das observações não foram necessariamente reconciliados e que a precisão da informação histórica varia.

A observação primária do projeto permanece nas sondagens de Recife **7–9/11/1963, 12h UTC nominais** (`RELTIME=9999`), cadeia `ncdc6301`, C149–C151. Os níveis p/T/GPH do ZIP NOAA não ganham independência porque o catálogo posterior menciona equipamento. Instrumento, processamento de GPH, coordenada histórica de lançamento, hora real, erros e covariâncias são **desconhecidos**; `null` não é zero.

## Vínculos cumulativos e teste adversarial

`C149–C151 → perfil p/T/GPH observado → método instrumental em 1963 [PENDING] → incerteza de densidade [PENDING] → transferência Recife→Conde [PENDING] → arrasto/deriva condicional [PENDING]`.

C144–C146 (cartas de superfície), C17–C23 (geomagnetismo e fluxo solar) e C193 (termósfera em outra época) continuam famílias com conteúdo próprio; nenhuma fornece a calibração ausente. A nova contribuição é **controle de identidade e genealogia**, não novo vetor de vento, não `σ`, nem redução da área possível de queda. É proibido converter valores de 1982–1992 em condições atmosféricas de 1963.

Reproduzir offline: `python3 tools/audit_igra_recife_station_history.py --check` e `python3 -m unittest discover -s tests -p test_igra_recife_station_history_gap.py -v`. Para autenticar os excertos a partir dos catálogos NOAA inteiros já obtidos: adicionar `--metadata-original /caminho/igra2-metadata.txt --sonde-original /caminho/wmo-sonde-history.txt`. Os testes rejeitam retroprojeções, troca de estação e elevação de metadado a restrição física.

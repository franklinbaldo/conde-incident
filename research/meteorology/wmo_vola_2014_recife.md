---
type: Guide
title: "WMO Vol. A 2014: Recife 82899 e 82900 são entradas distintas"
description: "Auditoria visual de um catálogo da OMM de 2014, sem atribuir seus programas à radiossondagem de 1963."
---

# Duas entradas no catálogo WMO de dezembro de 2014

**Fonte institucional:** [WMO Publication No. 9, Volume A, Observing Stations, edição dezembro/2014](https://old.wmo.int/extranet/pages/prog/www/ois/Operational_Information/VolumeA/VolumeA2014ed.pdf), Região III, Brasil, **página 249 do arquivo PDF (índice zero 248)**, bloco 82, faixa impressa 82764–82927. O quadro foi **conferido visualmente** com a imagem da página, e a legenda foi consultada nas páginas PDF 12–14. O PDF integral não foi baixado: **SHA-256 da fonte: desconhecido**. O JSON contém transcrições rotuladas; elas não são bytes do PDF.

| Índice WMO expandido | Nome impresso | Posição catalogada 2014 | HP / H ou HA | Ar superior em 00/06/12/18 UTC | Rede |
|---|---|---|---|---|---|
| **82899** | RECIFE (AERO) | 08°04′ S, 34°51′ W | 19 / 19 m | nenhum código indicado nos quatro horários | A; RBSN(S) |
| **82900** | RECIFE | 08°03′ S, 34°55′ W | 7 / 7 m | **RW** somente em 12 UTC | CLIMAT(C); RBCN; RBSN(T) |

O PDF abrevia as duas linhas como **899** e **900**, herdando o prefixo **82** do bloco. A legenda explica **R** como radiossonda (pressão, temperatura, umidade) e **W** como rastreamento eletrônico de vento em altitude; **RW** indica modalidades conjuntas naquele horário nominal de **2014**, não uma marca de instrumento. **RBSN(S)** indica estação SYNOP e **RBSN(T)** estação TEMP. A ausência de código em 82899 é **ausência de indicação no catálogo de 2014**, não prova de inexistência de lançamentos.

**Resultado documental:** em dezembro de 2014 há duas entradas institucionais diferentes e a função de ar superior está catalogada sob **82900**. Isso ajuda a desambiguar a genealogia retrospectiva dos identificadores vistos nas fontes C149–C151 e C193, inclusive no histórico IGRA. **Não demonstra** qual instalação lançou balões em **7–9/11/1963**, a hora real do lançamento, instrumento, método de altura geopotencial, erro de medição ou covariâncias. Catálogo de 2014 não é estação operacional verificada para 1963.

**Grafo cumulativo:** OMM Vol. A/2014 p.249 → {82899/SYNOP, 82900/TEMP} → possível linhagem dos dados IGRA de Recife em C149–C151/C193 → **PENDING** catálogo e alterações WMO de 1963 + metadados de lançamento → **PENDING** calibração e transferência Recife→Conde → eventual arrasto/deriva do Castor. Não adicionar observável físico independente ou reduzir domínios de simulação. Estado: `CONNECTED_PENDING_CALIBRATION`.

**Reprodução e controles:** `python3 tools/validate_wmo_vola_2014_recife.py` e `python3 -m unittest discover -s tests -p 'test_wmo_vola_2014_recife.py' -v`. O script confronta os campos estruturados com as duas linhas transcritas e rejeita retrodatação, confusão de índices, código RW alterado, sensor inventado, SHA inexistente e restrição de domínio indevida. Isso valida **consistência da transcrição**, não a integridade binária do PDF nem sua aplicação a 1963.

**Busca posterior:** obter a edição coeva de WMO No. 9, Vol. A e o WMO Catalogue of Radiosondes efetivos em 1963, ou notificações METNO e arquivos de estação datados, sem pressupor que a configuração de 2014 já vigorasse.

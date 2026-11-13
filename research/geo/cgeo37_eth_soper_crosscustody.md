---
type: Guide
title: 'CGEO-37: segunda custódia do mapa Soper de 1914'
description: 'Fac-símile e IIIF da ETH, genealogia da mesma obra e limites contra dupla contagem.'
---

# CGEO-37 | Uma segunda custódia, não uma segunda observação

Em 13/11/2026, o acervo da [ETH-Bibliothek Zürich](https://www.e-rara.ch/zut/content/titleinfo/32574892) foi consultado diretamente. A ficha da obra de **Ralph H. Soper (1914)** identifica a gravura de **Max Hunger**, a **Inspectoria de Obras contra as Seccas**, a escala **1:1.000.000**, a chamada **K 368018** e o [DOI 10.3931/e-rara-153583](https://doi.org/10.3931/e-rara-153583). A disponibilização digital em **15/09/2026** não altera a data impressa do mapa.

Do servidor da própria ETH, foram adquiridos os bytes reais do [PDF](https://www.e-rara.ch/zut/download/pdf/32574892) (**2.020.098 bytes**, SHA256 `5e0db1bdc45f8d44ddcdc985b28ef2115537d05d7d762fa1c5e0a16256149514`), [manifesto IIIF](https://www.e-rara.ch/i3f/v20/32574892/manifest) (**2.703 bytes**, SHA256 `1284c8720d0d9647cbba1b1019cb7b4b2e575b966bab1bfd037c0d43298567c2`) e [prévia JPEG IIIF](https://www.e-rara.ch/i3f/v20/32574893/full/1000,/0/default.jpg) (**151.507 bytes**, SHA256 `326d94f7e3b175bf8a60740ca4fb1ca0474cef5d1bce659218f2f590d508a618`). O manifesto informa uma imagem nativa de **9.841×11.142 pixels**, superior em dimensões à reprodução listada em CGEO-36. Dimensões maiores não garantem melhor resolução do documento original.

A legenda do fac-símile registra a topografia como baseada nas **observações de Soper e no mapa parcial do Estado da Bahia, publicação n. 29 da I.O.C.S.**. Essa declaração é importante para a genealogia das fontes: nem toda informação desenhada foi necessariamente medida apenas por Soper. O mapa impresso distingue **Conde** de **Sítio**. Nenhuma das duas ocorrências estabelece coordenadas do centro urbano em 1963.

A ficha ETH e a reprodução [Arquivo Nacional/Wikimedia de CGEO-36](https://commons.wikimedia.org/wiki/File:Mapa_do_estado_de_Sergipe_e_da_parte_nordeste_do_estado_da_Bahia_1914.pdf) se referem à **mesma obra cartográfica de 1914**. Há duas custódias documentais, mas não duas observações independentes do lugar, nem prova de identidade pixel a pixel ou de exemplar físico. Falta rastrear a origem do mapa parcial mencionado na legenda; também não se provou derivação da carta de 1954 a partir dele.

**Limites científicos:** o ano de entrada do digital, a escala impressa, os pixels IIIF e a extensão nominal da folha não são posições de Conde, perímetro do Centro em novembro de 1963 nem incerteza do evento. Sem controles geodésicos e fonte que ligue topônimos à época, todos os campos de geometria histórica e queda permanecem nulos. Nenhuma restrição orbital é ativada.

**Reprodução:** `python3 -m tools.cgeo37_eth_soper` confere o contrato offline. Os parâmetros `--pdf`, `--manifest` e `--jpeg` conferem SHA256 e propriedades dos três arquivos realmente adquiridos. O workflow CGEO-37 executa o replay externo no HEAD da PR e os testes adversariais. Nenhum PDF ou JPEG foi incorporado ao Git.

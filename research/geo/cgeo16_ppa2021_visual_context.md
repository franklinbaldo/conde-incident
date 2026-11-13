---
type: Guide
title: "CGEO-16: fotografias oficiais de 2021 sem localização de 1963"
description: "Duas imagens do PPA municipal de Conde BA, referência de página verificada e contrato GIS sem localização inventada."
---

# CGEO-16 — Rua comercial do Conde em publicação oficial de 2021

## Documento e ocorrência

Fonte institucional: [Diário Oficial do Município de Conde (BA), 21/12/2021, Ano I, edição 409](https://www.camaraconde.ba.gov.br/Handler.ashx?f=f&query=5694316d-2f66-4d60-9900-cb9a5136f9dc.pdf), Plano Plurianual 2022–2025, **página oficial 14** (página 13 do PPA, índice de PDF iniciado em zero = 13). O fac-símile da página foi **inspecionado visualmente** no leitor PDF da origem. A página mostra fotografia de uma via com calçamento, fachadas comerciais e bancas/vendedores, além de **uma segunda fotografia distinta de praia e calçadão** na mesma página. Não há legenda literal identificando rua, autor ou data de tomada dessas fotografias. A reprodução é posterior ao evento de 08/11/1963.

**Limite de custódia:** não adquirimos bytes integrais do PDF para hash nesta rodada. Uma tentativa HTTP no executor retornou arquivo de zero bytes; isso NÃO é a origem nem um SHA da fonte (não o registramos no contrato). A inspeção da página renderizada não atesta metadados EXIF, licença de cada JPEG ou data de captura. Não republicar imagens sem autorização de licença.

## Semântica espacial

A fotografia da rua comercial **não está georreferenciada**, e a seção municipal sobre comércio **não diz que se trata do centro em 1963**. A imagem de praia na mesma folha não deve ser confundida com centro urbano. A existência de “Vila do Conde” como núcleo histórico em fontes anteriores não constitui identificação desta rua; o nome homônimo **Vila do Conde em Portugal** deve ser descartado por contexto (município IBGE `2908606`, Bahia). Não confundir também com Conde/PB ou São Francisco do Conde/BA.

O contrato [cgeo16_ppa2021_visual_context.json](cgeo16_ppa2021_visual_context.json) separa observações visuais, data de edição, data desconhecida da câmera, autenticidade limitada, linhagem de fonte única e pendências de casamento de pontos de vista. É nova ocorrência documental em relação a [CGEO-14](cgeo14_vila_conde_visual_catalogue.md) e [CGEO-15](cgeo15_vila_matriz_2022.md), **não** três observações independentes do relato histórico. Os campos de centro histórico, geometria, datum, precisão e ponto de reentrada de 1963 permanecem `null`; exportação ao Castor tem `can_constrain_orbital_reentry=false`.

## Validação e próxima discriminação

`python3 -m unittest tests/test_cgeo16_ppa_visual_context.py -v` verifica páginas, identidade e nega a promoção de fotos sem localização a coordenadas. Para uso espacial posterior, precisamos de uma planta ou aerofoto da sede até 1963, marco urbano identificável em duas épocas, foto histórica com origem e data verificadas, e o fac-símile exato do testemunho que emprega “centro da cidade”. Até lá, o registro integra o grafo como `CONNECTED_PENDING_SPATIAL_IDENTIFICATION`, sem restrição orbital numérica.

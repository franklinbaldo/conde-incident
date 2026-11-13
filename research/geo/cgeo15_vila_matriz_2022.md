---
type: Guide
title: "CGEO-15: dois pontos de câmera de 2022 junto à Igreja do Monte em Conde"
description: "Custódia de fotos Commons CC BY-SA, coordenadas de vista moderna e busca arquivística IBGE 1958 sem promover local de 1963."
---

# CGEO-15 — vista moderna do núcleo histórico, não ponto de reentrada

O [catálogo Wikimedia Commons da Igreja Matriz de Nossa Senhora do Monte](https://commons.wikimedia.org/wiki/Category:Igreja_Matriz_de_Nossa_Senhora_do_Monte_(Conde)) identifica o bem em **Conde, Bahia**, distinguindo-o de igrejas homônimas em São Francisco do Conde. O catálogo da categoria dá a etiqueta de endereço **Praça 10 de Agosto**, não validada como endereço jurídico por fonte administrativa; não se atribui esse logradouro a uma rua de 1963.

Dois [JPEGs de Túllio F, 15/09/2022, 17h08](https://commons.wikimedia.org/wiki/File:Igreja_Matriz_de_Nossa_Senhora_do_Monte_-_Conde_-_20220915170828.jpg) e [17h09](https://commons.wikimedia.org/wiki/File:Igreja_Matriz_de_Nossa_Senhora_do_Monte_-_Conde_-_20220915170956.JPG) têm metadados públicos de local da câmera: respectivamente **(-11.798800, -37.621475)** e **(-11.798532, -37.621659)**, no formato *latitude, longitude*. Esses valores são pontos de **tomada de câmera em 2022**, não um centróide do templo, não um perímetro urbano e menos ainda uma localização física de evento de 1963. O datum, erro horizontal e parâmetros de calibração não foram verificados; **nenhum EPSG é atribuído**. Os dois arquivos são uma única sessão fotográfica/autor. Direitos de reutilização: CC BY-SA 4.0 com crédito, link e obrigações da licença; não incorporamos os JPEGs ao projeto.

## Aquisição dos arquivos originais (13/11/2026 UTC)

| ID | Bytes | SHA256 |
| --- | ---: | --- |
| CGEO15-CAMERA-01 | 5365818 | `fa483bae3ae85d4eeb33bc76748f123515c5f87eca7b9a69f35fd2523d97df6d` |
| CGEO15-CAMERA-02 | 3632175 | `04e5752d902055071e6ba9e414610bf1ccc1c11d64a93f165df2cd65e6bb3cfa` |

A página Commons mostra dados atribuídos a EXIF e ao autor. Nesta rodada os bytes foram adquiridos e hash conferido; a **origem e precisão geodésica dos valores EXIF** não foi calibrada de modo independente. Nenhuma foto da fonte anterior CGEO-14 foi considerada da mesma sessão nem usada para fabricar marcos coincidentes.

## Busca de fonte visual próxima de 1963

Foi adquirido diretamente o PDF do IBGE *Enciclopédia dos Municípios Brasileiros*, **volume XX (1958)** em [biblioteca.ibge.gov.br](https://biblioteca.ibge.gov.br/visualizacao/livros/liv27295_20.pdf), **72.579.243 bytes**, SHA256 `440bd7eaa42c712c89e65111fbebb7b8f77430f76ecff2be0a96d4eacb11a741`. A fonte é temporalmente interessante, mas **nenhuma página de Conde nem fotografia do volume foi inspecionada**: o processamento do PDF excedeu o limite de RAM do executor Jatobá. Aquisição autenticada não implica verificação do conteúdo. O PDF não foi enviado ao GitHub por tamanho. Próxima verificação deve executar inspeção de páginas e recortes em executor com capacidade adequada, preservando número de página e identidade da legenda.

## Handoff GIS ao Castor e fontes dependentes

O [histórico municipal IBGE](https://www.ibge.gov.br/biblioteca/visualizacao/dtb/bahia/conde.pdf) documenta a sede do distrito em 1935 e um único distrito-sede em 1960. A [Prefeitura de Conde](https://www.conde.ba.gov.br/site/ConvenioTransferenciaDetalhe/432) destaca a Vila do Conde e a igreja histórica, mas isso **não autentica uma semântica espacial de “centro” no relato de 08/11/1963**, cujo fac-símile literal e localização ainda precisam de averiguação específica. O CGEO-15 acrescenta duas coordenadas **modernas de ponto de vista** e um candidato de fonte contemporânea. Ligações cumulativas a CGEO-03/14 ficam consultáveis, sem mutação da matriz original.

`python3 -m tools.cgeo15_matriz_camera` exporta `historical_center_geometry=null`, `1963_observed_event_location=null` e `can_constrain_orbital_reentry=false`. Para replay: usar `--verify-dir` com os dois JPEGs originais sob os nomes preservados do Commons, e opcionalmente o PDF de 1958. Testes offline rejeitam conversão ilícita do datum, tolerância em metros, ponto histórico, independência da galeria ou conteúdo supostamente visto.

**Próximo teste:** inspeção visual de páginas da *Enciclopédia* (1958) e confronto com planta/aerofoto anterior a 1963. Sem fotos, observações ou coordenadas inventadas da queda.

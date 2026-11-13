---
type: Guide
title: "C241-L32: catálogo NASA de 1977 associa 1963 003B a 528"
description: "Custódia de fonte institucional retrospectiva com verificação dos bytes e imagem da linha, sem transformar catálogo em radar."
---

# C241-L32: identidade catalográfica 1963 003B ↔ 528

**Origem:** NASA Goddard Space Flight Center, *Satellite Situation Report*, volume 17, número 6, 31/12/1977, NASA-TM-79345. [Ficha NTRS 19780009188](https://ntrs.nasa.gov/citations/19780009188) e [PDF NASA](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf). Registro de custódia [JSON C241-L32](nasa_ssr_dec1977_528_identity_C241-L32.json).

A camada textual do PDF identificada na pesquisa devolve a sequência **1963 003A**, **527**, **1963 003B**, **528** na tabela **DECAYED OBJECTS / 1963 LAUNCHES**. A imagem precisa ser verificada diretamente após identificar sua página: extração automática não equivale a transcrição visual confiável da linha horizontal. O teste GH Actions baixa o PDF oficial e rejeita alterações no tamanho e hash.

Arquivo NASA baixado em 13/11/2026: **11.563.410 bytes**, SHA-256 **c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8**. A localização por página é determinada pelo pdftotext em duas ordenações e um PNG da página fica como artefato no CI. Não acrescentar número de página impressa antes da inspeção da imagem.

## O que a fonte acrescenta

A PR anterior **#533 / C241-L28** associou 1963 03A a 527 por quatro publicações NASA de 1964–1967. O PDF de **1977**, embora muito posterior, é um candidato positivo para a associação **03B ↔ 528** proveniente do próprio órgão que publicou a lista de decaimentos. O documento não é um TLE original, relatório de estação de 1963 nem observação independente da mesma rede; trata-se de **catálogo institucional retrospectivo**.

O registro de 15/11/1963 **C197#1/C241-L11** imprime 1963 3B com dia de decaimento 08/11/1963, sem número catalográfico na linha documentada. Cruzar os dois documentos pode completar a **identidade do rótulo**, mas **não aumenta o número de radares ou de medições do 528** e não mede o erro da data, a hora ou o local de reentrada. Não atribuir igualdade de método, σ, sensores ou covariâncias entre os relatórios NASA/NORAD.

Há quatro arestas novas de catálogo/proveniência. Elas permanecem **CONNECTED_PENDING_FACSIMILE_REVIEW** até a imagem ser checada; nenhum predicado físico/Lean foi ativado e nenhum parâmetro da simulação foi reduzido.

## Próxima evidência falsificável

Encontrar um documento **contemporâneo de 1963–1964** que associe diretamente 1963 3B ao catálogo 528, além da ficha operacional de rastreamento, última observação com época UTC, estação, frame, erro e método histórico do decaimento. A tabela NASA de 1977 deve ser comparada à imagem e à originalidade da linhagem, não contada como segundo sensor.

## Reprodução

    python3 -m unittest discover -s tests -p test_tle_nasa_1977_crosswalk_audit.py -v
    python3 tools/tle_nasa_1977_crosswalk_audit.py --pdf /tmp/nasa-1977.pdf --output /tmp/c241-l32.json

O primeiro comando testa a tipagem, dependências e recusas de falsos fatos orbitais. O segundo exige os bytes originais NASA e localiza a linha textual em apenas uma página. O PNG para conferência humana é gerado pelo workflow .github/workflows/tle-nasa-1977-crosswalk.yml; a aprovação desse teste não certifica visualmente a página sem inspeção independente.

**Limites:** o relatório foi publicado catorze anos depois do evento, não demonstra um instante de reentrada, um traço observacional próprio do 528, nem uma localização de queda no município de Conde. A imagem, não um snippet de busca, deve resolver qualquer ambiguidade de OCR.

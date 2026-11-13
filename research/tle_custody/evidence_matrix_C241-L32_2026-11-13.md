---
type: Guide
title: "C241-L32: catálogo NASA de 1977 associa 1963 003B a 528"
description: "Custódia de fonte institucional retrospectiva com verificação dos bytes e imagem da linha, sem transformar catálogo em radar."
---

# C241-L32: identidade catalográfica 1963 003B ↔ 528

**Origem:** NASA Goddard Space Flight Center, *Satellite Situation Report*, volume 17, número 6, 31/12/1977, NASA-TM-79345. [Ficha NTRS 19780009188](https://ntrs.nasa.gov/citations/19780009188) e [PDF NASA](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf). Registro de custódia [JSON C241-L32](nasa_ssr_dec1977_528_identity_C241-L32.json).

A imagem integral do PDF NASA foi **verificada visualmente** após localização automática da tabela **DECAYED OBJECTS / 1963 LAUNCHES**. Na **página impressa -43-**, índice PDF **46** (página 47/114), constam três linhas adjacentes: **1963 003A → 527**, **1963 003B → 528**, **1963 003C → 529**. A publicação de 1977 imprime, na coluna DECAY, respectivamente **9 JAN 69**, **8 NOV 63** e **31 DEC 63**. A página foi renderizada diretamente dos bytes do PDF NASA pelo workflow [C241-L32, run 43454971351](https://github.com/franklinbaldo/conde-incident/actions/runs/43454971351) e conferida, sem OCR suplementar. Trata-se de uma tabela editorial retrospectiva, não de múltiplas observações de radar.

Arquivo NASA baixado em 13/11/2026: **11.563.410 bytes**, SHA-256 **c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8**. A localização da linha foi reproduzida via pdftotext em duas ordenações e o PNG da página integral ficou como artefato no CI. **Página impressa 43**, zero-based PDF 46, extração e leitura visual concordam para 03B=528. O número impresso é apresentado no fac-símile como -43-.

## O que a fonte acrescenta

A PR anterior **#533 / C241-L28** associou 1963 03A a 527 por quatro publicações NASA de 1964–1967. O PDF de **1977**, embora muito posterior, demonstra documentalmente as associações **03B ↔ 528 e 03C ↔ 529** na mesma publicação institucional NASA. A relação 03A↔527 serve como controle cruzado com C241-L28. O documento não é um TLE original, relatório de estação de 1963 nem observação independente da mesma rede; trata-se de **catálogo institucional retrospectivo**.

O registro de 15/11/1963 **C197#1/C241-L11** imprime 1963 3B com dia de decaimento 08/11/1963, sem número catalográfico na linha documentada. A publicação de 1977 **repete 8 NOV 63** na linha de 03B=528, mas compartilha a mesma família histórica de dados catalográficos e não constitui medição independente da hora terminal. Cruzar os dois documentos pode completar a **identidade do rótulo**, mas **não aumenta o número de radares ou de medições do 528** e não mede o erro da data, a hora ou o local de reentrada. Não atribuir igualdade de método, σ, sensores ou covariâncias entre os relatórios NASA/NORAD.

Há **seis arestas** de catálogo/proveniência. Estado **DOCUMENTARY_CROSSWALK_VERIFIED_NO_PHYSICAL_CONSTRAINT** após imagem verificada; nenhum predicado físico/Lean foi ativado e nenhum parâmetro da simulação foi reduzido.

## Próxima evidência falsificável

Encontrar um documento **contemporâneo de 1963–1964** que associe diretamente 1963 3B ao catálogo 528, além da associação retrospectiva original NASA já comprovada, além da ficha operacional de rastreamento, última observação com época UTC, estação, frame, erro e método histórico do decaimento. A tabela NASA de 1977 deve ser comparada à imagem e à originalidade da linhagem, não contada como segundo sensor.

## Reprodução

    python3 -m unittest discover -s tests -p test_tle_nasa_1977_crosswalk_audit.py -v
    python3 tools/tle_nasa_1977_crosswalk_audit.py --pdf /tmp/nasa-1977.pdf --output /tmp/c241-l32.json

O primeiro comando testa a tipagem, dependências e recusas de falsos fatos orbitais. O segundo exige os bytes originais NASA e localiza a linha textual em apenas uma página. O PNG para conferência humana é gerado pelo workflow .github/workflows/tle-nasa-1977-crosswalk.yml e foi examinado independentemente no CI #43454971351. A extração de OCR, isoladamente, não substituiria esse exame.

**Limites:** o relatório foi publicado catorze anos depois do evento, não demonstra um instante de reentrada, um traço observacional próprio do 528, nem uma localização de queda no município de Conde. A imagem da página 47 do PDF NASA resolve a ambiguidade de identidade entre as colunas, mas não a cadeia de rastreamento que levou à data impressa.

---
type: Guide
title: "Lontra: fac-símile ON20 de 1964 preservado no Wayback"
description: "Custódia do PDF integral do manual NMC ON20, com limites de OCR e conexão pendente ao Y20175."
---

# Office Note 20: exemplar digital recuperado

Ocorrência documental: **MET-NMC-NCEPON-20261112-02**, em complemento ao catálogo MET-NMC-NCEPON-20261112-01 (PR #266). O índice oficial NCEP lista **J. Neilon, 1964, Upper Air ADP Records Format**, com revisão iniciada na página impressa 12. Essa é uma informação do índice, ainda não confirmada por leitura das imagens.

O endereço histórico do índice estava inacessível. Recuperou-se a [cópia integral preservada no Wayback](https://web.archive.org/web/20220119075333id_/http://www.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/013FD4DB.pdf) em 12/11/2026, HTTP **200**, tipo **application/pdf**, **932.414 bytes**; SHA-256 **656984ac58ff1632e39b0f62ac80003785ddea0a0de32dfb19c8c612067aabbe**. A captura do arquivo é datada pelo serviço em **19/01/2022 07:53:33 UTC**. O SHA identifica a cópia baixada, **não** comprova equivalência com um mestre independente do NMC.

A inspeção de bytes encontrou cabeçalho PDF 1.4, EOF, referência /Root, **23 objetos de página**, **23 objetos de imagem** e marcador /Count 23. São marcadores estruturais: não houve conferência independente da árvore completa de páginas, leitura visual, transcrição, OCR ou validação de numeração impressa. Nenhum PDF binário foi commitado.

Estado: **PDF_BYTES_RETRIEVED_CONTENT_NOT_YET_TRANSCRIBED**. A aplicabilidade de um documento de **1964**, inclusive a revisão da página 12, aos relatórios do arquivo **Y20175 de 1963** continua **NOT_ESTABLISHED**. A cadeia cumulativa fica: catálogo -> href original -> captura Wayback -> bytes/hash verificados -> leitura visual PENDENTE -> layout de 1963 PENDENTE -> consulta WMO/data PENDENTE. Vínculo: research/constraints/nmc_y20175_pending_bridge.json, sem novos observáveis, sem perfil WMO confirmado, sem restrição física ativada.

Reprodução: baixe o PDF do link acima e execute python3 tools/verify_ncep_on20_archived_pdf.py --pdf /caminho/013FD4DB.pdf. Testes offline: python3 -m unittest discover -s tests -p 'test_ncep_on20_archive.py' -v. Ambos verificam integridade e fronteira epistemológica; não decodificam conteúdo meteorológico.

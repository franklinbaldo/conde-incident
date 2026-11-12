---
type: Guide
title: "Lontra: páginas e revisão datada da NMC Office Note 20"
description: "Inspeção visual seletiva, árvore PDF, hashes das 23 imagens CCITT e lacunas de leitura do manual de 1964."
---

# NMC Office Note nº 20: auditoria de páginas

**Ocorrência:** `MET-NMC-NCEPON-20261112-03`, dependente de `-01` (catálogo) e `-02` (PDF íntegro recuperado). Fonte: [exemplar Wayback do PDF](https://web.archive.org/web/20220119075333id_/http://www.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/013FD4DB.pdf), captura **19/01/2022**, SHA-256 `656984ac58ff1632e39b0f62ac80003785ddea0a0de32dfb19c8c612067aabbe`. É uma cópia preservada, não um mestre NMC autenticado separadamente.

**Verificação nova:** árvore de páginas percorrida de raiz até as folhas, com **23 páginas** e referências XObject/imagem auditadas individualmente. Foram extraídos, decodificados visualmente por leitor TIFF CCITT-G4 e enumerados **23 fluxos de imagens**. O [manifesto JSON](ncep_on20_page_audit_20261112.json) guarda objeto PDF, dimensões, comprimento e SHA-256 *do fluxo CCITT comprimido* de cada página, sem armazenar o fac-símile no Git.

**Constatações pela leitura direta, sem OCR:** a capa original (páginas PDF 2 e 15) data a nota de **junho de 1964** e credita James R. Neilon. As páginas PDF **11 e 13** apresentam cabeçalho *Revision to NMC Office Note #20* datado **27/11/1964**, alterando a Nota 4 sobre indicadores de qualidade, bits `S` a `11`; as páginas **12 e 14** continuam a revisão, bits `12` a `17`. A capa anterior na página PDF 1 usa identificação institucional NOAA/NWS posterior, mas não contém data própria. Há conteúdo aparentemente repetido nas páginas 2/15, 3/16, 11/13 e 12/14; os fluxos comprimidos não são idênticos. Assim, **23 páginas de PDF não equivalem a 23 páginas textuais independentes**. A referência do catálogo a início de revisão na “página 12” não está resolvida quanto a paginação física versus impressa: na cópia PDF a primeira folha explicitamente datada da revisão é a página 11.

O texto original (páginas PDF 3 e 16) descreve **50–150 palavras por relato**, com três primeiras palavras de localização/identificação, e utiliza posições `S–35`. Isso documenta o formato descrito em **1964**; não identifica o empacotamento do arquivo meteorológico `Y20175` de **1963** nem demonstra equivalência entre delimitadores COS EOR e relatos individuais. A revisão de novembro de 1964 não pode ser retroprojetada para os dias 7–9/11/1963.

**Limites:** inspeção visual seletiva de páginas identificadas; transcrição integral, OCR, numeração impressa de todas as folhas, eventuais variações entre cópias e decodificação ON20/Y20175 continuam `NOT_RUN`/`NOT_ESTABLISHED`. Nenhum perfil de Salvador, Aracaju ou Recife foi identificado e nenhuma restrição física foi ativada.

Reprodução: com o mesmo PDF completo, `python3 tools/audit_ncep_on20_page_streams.py --pdf arquivo.pdf`; testes sintéticos offline: `python3 -m unittest discover -s tests -p 'test_ncep_on20_page_streams.py' -v`. O verificador audita a estrutura do PDF **conhecido** e falha em outras cópias por hash, não é leitor PDF genérico nem OCR.

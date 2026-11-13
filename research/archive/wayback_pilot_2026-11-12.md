---
type: Guide
title: "WB-01: piloto de custódia Wayback de três fontes"
description: "Capturas exatas verificadas, controles negativos e contrato de proveniência do acervo Conde."
---

# WB-01: capturas arquivadas não são medições novas

**Questão:** é possível apontar links de cópias **exatas** de PDFs documentais já citados na matriz, sem inventar URL de captura a partir de data não confirmada? Auditoria pública em **13/11/2026 00:49 UTC**, [issue #308](https://github.com/franklinbaldo/conde-incident/issues/308). Manifesto: [JSON](wayback_pilot_2026-11-12.json). URLs em `id_` retornaram bytes PDF, HTTP 200, com SHA-256 e digest SHA-1 Base32 do CDX coincidentes.

| Documento, referência | Publicação/época original | Captura exata | Resultado |
|---|---|---|---|
| NASA SSR 15/11/1963, C197#1/C198#1, [PDF NTRS](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) | 15/11/1963, p. impressa 8 | CDX `[]`; Availability sem snapshot, ambos HTTP 200 | **NO_EXACT_CAPTURE_IN_QUERIED_INDEX**, não ausência histórica |
| NORAD/CONAD [Historical Summary H2 1963](https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/11.pdf), C241-P8 | Período julho–dezembro de 1963; **data editorial exata não verificada** | [Wayback PDF 15/03/2023 02:45:25 UTC](https://web.archive.org/web/20230315024525id_/https://nsarchive.gwu.edu/sites/default/files/documents/rr5xh6-kw4gj/11.pdf) | 1.459.815 bytes e SHA-256 aferido, replay PDF 200 |
| Smithsonian [RU301](https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf), SIA-FARU0301 / BN-RU301-20261112-01 | Inventário de acervo, **não** série orbital de 1963 | [Wayback PDF 28/02/2021 10:52:02 UTC](https://web.archive.org/web/20210228105202id_/https://sirismm.si.edu/EADpdfs/SIA.FARU0301.pdf) | 124.806 bytes e SHA-256 aferido, replay PDF 200 |

**Leitura dos controles:** `length` do registro CDX (1.330.748 / 105.084) **não coincide** com o comprimento dos PDFs baixados (1.459.815 / 124.806); não fazer igualdade entre tamanho de entrada WARC e payload. Digest CDX é **SHA-1 em Base32**, diferente do SHA-256 integral do PDF, ambos registrados no manifesto. O snapshot arquivado não autentica por si o conteúdo histórico, nem acrescenta observações, sensores, horários ou restrições orbitais. O NTRS pode ter outra URL arquivada: a consulta negativa é **somente da URL exata**. C197 e C198 continuam **uma única obra**, não duas fontes.

**Reprodutibilidade:** `python3 tools/verify_wayback_pilot.py` valida as relações sem rede; `python3 tools/verify_wayback_pilot.py --fetch` baixa apenas os dois PDFs verificados e confere o SHA-256 e SHA-1/CDX em memória. `python3 -m unittest discover -s tests -p 'test_wayback_pilot.py'` executa contraprovas sem depender de rede. A cadeia prevista para consumidores é `source_refs → original_url → CDX(original,timestamp,status,mime,digest) → archived_url → replay(bytes,SHA256)`. Preferir o link arquivado **apenas** nos dois registros confirmados, preservando sempre o original. Esta entrega não modifica o site nem preenche campos de dados instrumentais.

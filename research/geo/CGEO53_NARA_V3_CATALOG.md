---
type: Evidence
title: 'CGEO-53: busca real JSON do catálogo NARA confirma as unidades 11S037W e 11S038W'
description: 'Reparar a rota de busca anteriormente servida como HTML; distinguir registros de fotoíndices e negativos originais.'
---

# CGEO-53 | Catálogo NARA: busca estruturada efetivamente realizada

**14/11/2026.** Retomei [CGEO-52](CGEO52_NCAP_CROSSARCHIVE_ROUTE.md): a rota `/proxy/records/search?limit=25...` havia devolvido **HTTP 200 com HTML da aplicação**, não JSON. Na presente rodada testei `https://catalog.archives.gov/proxy/v3/records/search?q=11S037W&limit=10`. A resposta efetiva foi **HTTP 200, application/json**, com `body.hits.total.value=1` e registro identificável. Essa é uma **nova aquisição de resposta estruturada**, sem reclassificar retroativamente o HTML anterior como JSON.

| Consulta | Hits naquele instante | Resultado sustentado |
| --- | ---: | --- |
| [11S037W](https://catalog.archives.gov/proxy/v3/records/search?q=11S037W&limit=10) | 1 | NAID **46716637**; `fileUnit`; título "Overlay indexes for degree square 11S037W" |
| [11S038W](https://catalog.archives.gov/proxy/v3/records/search?q=11S038W&limit=10) | 1 | NAID **46716645**; `fileUnit`; título "Overlay indexes for degree square 11S038W" |
| [125374](https://catalog.archives.gov/proxy/v3/records/search?q=125374&limit=10) | 183 | Resultados heterogêneos; não provam *spot number* |
| [133002](https://catalog.archives.gov/proxy/v3/records/search?q=133002&limit=10) | 3.451 | Resultados heterogêneos; não provam *spot number* |

Todos os quatro corpos JSON foram obtidos diretamente, com **bytes integrais, status, tipo MIME e SHA-256 específicos do momento da consulta** no [contrato](cgeo53_nara_v3_catalog.json). Como é um índice mutável, esses hashes são custódia da **resposta desta rodada**, não uma exigência de igualdade para novas buscas. O replay online testa MIME, estrutura JSON e NAID/título/tipo do registro, sem exigir totais constantes. A metodologia arquivística continua no [guia NARA RG373](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography), revisado em 18/02/2025. A [documentação da API NARA](https://www.archives.gov/research/catalog/help/api-getting-started) apresenta outra rota `/api/v2` com chave; ela não foi testada como API válida nesta rodada e **não é base deste resultado**.

**O que muda:** a falha técnica de busca estruturada do CGEO-52 foi superada para essas duas quadrículas. O catálogo confirma a existência dos **registros de fotoíndices** já adquiridos em CGEO-47, não a existência de fotogramas digitais individuais sobre o Centro de Conde. As consultas numéricas não foram ligadas a latas nem negativos. Contagem de resultados gerais não é inventário exaustivo de fotos do local.

**Permanecem desconhecidos:** o *spot number* de `O.P. FILE NO. 125374`, latas ON/DN, datas dos fotogramas 26/16, cobertura efetiva, Centro em novembro de 1963 e localização da alegada queda. Nenhuma foto individual ou restrição orbital nova. **Próximo teste:** consultar *can locator* ou registro individual digital com relação explícita a spot, exposição, data e cobertura. Nenhum contato institucional foi enviado.

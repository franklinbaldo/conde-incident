---
type: Evidence
title: 'CGEO-54: sete fotoíndices NARA e 63 folhas digitais na vizinhança de Conde'
description: 'Inventário auditável de nove quadrículas RG373, incluindo zero-hits sem inferência de ausência de fotografia.'
---

# CGEO-54 | Inventário espacial do catálogo NARA em torno de Conde

**14/11/2026.** Após o conserto de busca estruturada CGEO-53, consultei de fato nove quadrículas de 1° × 1° nominalmente vizinhas à candidata 11S037W, com HTTP 200 e MIME JSON nas nove respostas, cada qual com tamanho e SHA-256 registrado no [contrato](cgeo54_nara_adjacent_overlay_index.json). O padrão nominal da quadrícula é um índice arquivístico, **não um polígono georreferenciado do município em 1963**.

| Quadrícula | NAID do fileUnit | Digitalizações de índices (exclui legenda repetida) |
| --- | --- | ---: |
| 10S036W | [46716333](https://catalog.archives.gov/id/46716333) | 12 |
| 10S037W | [46716347](https://catalog.archives.gov/id/46716347) | 11 |
| 10S038W | [46716360](https://catalog.archives.gov/id/46716360) | 6 |
| 11S036W | nenhum hit na busca consultada | não demonstrado |
| 11S037W | [46716637](https://catalog.archives.gov/id/46716637) | 6 |
| 11S038W | [46716645](https://catalog.archives.gov/id/46716645) | 8 |
| 12S036W | nenhum hit na busca consultada | não demonstrado |
| 12S037W | [46716877](https://catalog.archives.gov/id/46716877) | 4 |
| 12S038W | [46716883](https://catalog.archives.gov/id/46716883) | 16 |

**Achado:** sete unidades `fileUnit`, **63 arquivos JPEG catalogados como folhas/índices de sobreposição** da família RG373, série 306062, microfilme M1765, rolo 317. Os sete registros também incluem a mesma imagem explicativa `how-to-read-an-overlay.jpg`, contabilizada separadamente e **não** como sete fotos adicionais. Os arquivos individuais das cinco novas quadrículas foram *identificados pelos metadados primários*, mas não adquiridos nem inspecionados pixel a pixel nesta rodada. Os 14 JPEGs do par 11S037W/11S038W tiveram custódia anterior em CGEO-47.

**Novidade operacional:** ao norte, NAIDs 46716333/46716347/46716360; ao sul, 46716877/46716883. Podemos agora abrir seus overlays com nomes de arquivos e escopo literal ('Latitude/Longitude/BRAZIL') em vez de buscar por texto livre. NARA exibe datas de criação do objeto digital em 2026 e OCR em 2022: nenhuma delas comprova a data da exposição aérea.

**Controle negativo:** os dois zero-hits (11S036W e 12S036W) são apenas resultados de consulta naquele instante. Não significam ausência de registros relacionados, nem ausência de aerofotos. Os 63 JPEGs são **fotoíndices**, não 63 fotogramas originais de Conde. Nenhum deles estabelece a cobertura do Centro em novembro de 1963, a identificação do negativo 125374, coordenada de queda ou qualquer restrição orbital.

**Reprodução:** auditor `tools/cgeo54_nara_adjacent_overlay_index.py`, testes adversariais e replay vivo independente de sete IDs, títulos, escopo e imagens-âncora (primeiro/último nome). O replay não iguala hash mutável do catálogo entre datas; os snapshots originais são preservados apenas como custódia da resposta observada. Referência: [guia NARA RG373](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography), CGEO-47/48/53, [Conde #558](https://github.com/franklinbaldo/conde-incident/issues/558).

**Próxima seleção visual:** testar prioritariamente overlays 00429–00432 de 12S037W e depois 00433–00448 de 12S038W para identificação de faixas com contexto espacial útil. Essa preferência é inventário de pesquisa, não promessa de cobertura do núcleo urbano. Antes de propor limites históricos, exigir negativo, data de exposição, footprint, pontos de controle e ponte temporal autenticados.

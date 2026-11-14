---
type: Evidence
title: 'CGEO-59: busca combinada no NARA amplia candidatos de fotoíndices'
description: 'Busca de O.P. e código de sortie aponta onze unidades candidatas, sem provar voo ou foto de Conde.'
---

# CGEO-59 | Busca catalográfica multiquadrícula

**14/11/2026.** Retomando CGEO-53–58, pesquisei conjuntamente os campos candidatos **O.P. FILE NO. 125370/125374** e **2-3017** na [API JSON do NARA](https://catalog.archives.gov/proxy/v3/records/search?q=125374+%222-3017%22&limit=20).

A busca de **125374 com a expressão 2-3017 entre aspas** retornou 11 unidades: dez fileUnits intituladas *Overlay indexes for degree square*, mais uma bobina de 1953 não relacionada. Para **125370 com a mesma expressão**, foram sete unidades: quatro fotoíndices e três registros não relacionados. A união contém **11 quadrículas candidatas**, entre 03S e 12S. Três unidades aparecem em ambas: [46716637](https://catalog.archives.gov/id/46716637), [46716645](https://catalog.archives.gov/id/46716645) e [46716877](https://catalog.archives.gov/id/46716877).

A busca que acrescenta **11S037W** devolveu somente a unidade 46716637. O controle que acrescenta um identificador propositalmente inexistente devolveu **zero**, evitando tratar qualquer resposta de busca genérica como descoberta.

O [manifesto estruturado](cgeo59_nara_cross_square_query.json) registra os quatro corpos HTTP 200 por número de bytes, SHA-256 integral, títulos e NAIDs. A verificação automática compara o conjunto de hits e o total na consulta ao vivo, distinguindo o hash atual, eventualmente diferente, do hash histórico. Os quatro resultados são **metadados de catálogo**, não fotografias individuais.

**Limite essencial:** uma coincidência textual de catálogo não comprova que todos os 11 quadrantes pertençam à mesma missão, nem que os cabeçalhos de voo 1942 partilhem *spot*, negativo ou exposição. Os quatro resultados irrelevantes mostram por que é necessário inspecionar as folhas originais. O [guia institucional do NARA](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography) exige identificação de *spot number* e exposição para localizar as latas.

**Experimento refutável:** verificar visualmente o cabeçalho das novas unidades e buscar mesma missão, data e códigos de exposição nos respectivos overlays, sem derivar rota por ordem das quadrículas. Encaminhar a trilha à Lontra na [issue #8](https://github.com/franklinbaldo/lontra/issues/8). Nenhum contato institucional enviado, nenhum fotograma ou geometria de 1963 obtido, nenhuma restrição orbital nova.

Reproduzir com o validador Python CGEO-59, os testes unittest normais e otimizados e a opção --live. Falha de rede ou catálogo alterado deve ser reportada separadamente, jamais reclassificada como PASS.

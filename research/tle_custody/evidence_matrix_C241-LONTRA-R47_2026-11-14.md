---
type: Guide
title: 'C241-LONTRA-R47: início tardio de subsérie Kettering não apaga 1963'
description: 'Auditoria de cinco cotas Kettering, separando lacuna catalográfica de ausência histórica de observações dos NORAD 527–529.'
---

# C241-LONTRA-R47 · Lacuna de série versus lacuna observacional

O [primeiro volume identificado da subsérie KET/A/5/2](https://collection.sciencemuseumgroup.org.uk/documents/aa110118072) cobre **março–dezembro de 1965**. Portanto, esse volume *não serve* como diário específico de novembro de 1963. **Não se conclui daí que Kettering deixou de observar satélites em 1963, nem que não existiram outros registros fora da subsérie.**

O [arquivo KET](https://collection.sciencemuseumgroup.org.uk/documents/aa110093443/geoffrey-perry-archive-relating-to-operation-of-the-kettering-group) identifica ao menos três rotas que cobrem 1963: [diário de Geoffrey Perry KET/A/1/09](https://collection.sciencemuseumgroup.org.uk/documents/aa110118009), [remessas e correspondência ao DSIR KET/A/2/1](https://collection.sciencemuseumgroup.org.uk/documents/aa110118047) (1960–64) e [material radiofônico anual KET/A/6](https://collection.sciencemuseumgroup.org.uk/documents/aa110118055) (1960–73). São **cotas de catalogação**, não três observatórios independentes. Sem examinar os originais, não é possível saber se há mensagens dos dias 7–9/11/1963 ou se vários suportes copiam o mesmo sinal.

Uma [pasta coetânea KET/C/3/11](https://collection.sciencemuseumgroup.org.uk/documents/aa110121265) discrimina logs e curvas Doppler de **Cosmos 22 (1963-045A)** e **Cosmos 24 (1963-052A)**. Isso reforça a existência de documentação instrumental da época, mas **nenhum desses números designa o lançamento 1963-003A/B/C**. Não substituir o objeto buscado por controle com nomenclatura semelhante.

## Limites de custódia

As cinco fichas foram consultadas como **texto catalográfico em visualizador web**. Na tentativa local de 14/11/2026 a consulta HTTPS ao catálogo do Science Museum Group devolveu **HTTP 403**. Não obtivemos fac-símiles, folhas, logs radiofônicos, intervalos UTC, relógios, offsets instrumentais nem valores Doppler. Hashes de originais e páginas específicas permanecem nulos. A consulta da ficha não é busca exaustiva das folhas físicas não vistas.

Para o alvo **NORAD 527/528/529**, o estado é **zero medições novas, zero restrições orbitais**. Ao recuperar as folhas: identificar objeto na própria fonte, época UTC, estação, formato de relógio, unidade, calibração e genealogia das reduções; só então encaminhar qualquer candidata à análise orbital.

## Ordem de aquisição

1. KET/A/1/09: folhas do diário de 7, 8 e 9/11/1963 e referências cruzadas marginalia/índice.
2. KET/A/6: caixa ou seção de 1963 com rótulos 1963-003A/B/C e 527/528/529, inclusive resultados negativos **documentados no próprio original**.
3. KET/A/2/1: remessas para DSIR, comparação com diário e registros rádio evitando dupla contagem.
4. KET/C/3/11: controle de procedimento instrumental, sem transferência de medidas dos Cosmos 22/24.

Manifesto verificável: [kettering_series_boundary_C241_LONTRA_R47.json](kettering_series_boundary_C241_LONTRA_R47.json). Testes adversariais: `tests/test_kettering_series_boundary_r47.py`. Nenhum contato externo foi enviado.

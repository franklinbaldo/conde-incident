---
type: Guide
title: '🦅 G56: recuperar inventário NOAA original sem repinar fonte mutável'
description: Auditoria de custódia GHCNd com recuperação byte a byte e duas âncoras SHA independentes.
---

# G56: preservar os bytes, não aceitar deriva como verdade histórica

**Revisão de 14/11/2026.** A fonte NOAA `ghcnd-inventory.txt` é global e mutável. A CI de [#723](https://github.com/franklinbaldo/conde-incident/pull/723) falhou corretamente: o arquivo vivo não reproduzia o SHA integral aprovado em 13/11. Isso não implicava mudança na precipitação dos dias 7–9 de novembro de 1963.

A recuperação encontrou os bytes integrais da coleta **13/11/2026** no arquivo local de trabalho `lagarto-r26-data/ghcnd-inventory.txt`: **36.402.100 bytes**, SHA-256 `3d7378c3ecad6841340b47392f10b391c42a5f47369765e6bb032704d2301125`, exato pin histórico. O arquivo vivo em 14/11 tinha **36.403.986 bytes**, SHA `95be02499a07e99efc3905f7152fc1c6e3d48daeda4b659087497e0e18c65195`. Não substituir o pin original pelo hash novo.

A [captura Wayback de 25/10/2026 às 02:19:09 UTC](https://web.archive.org/web/20261025021909id_/https://www.ncei.noaa.gov/pub/data/ghcn/daily/ghcnd-inventory.txt) possui **36.396.304 bytes** e SHA integral `c33ec006c4f35d0371e6f9ccfe3f656ae9de0b6f0f122794da07df7c971c48b5`. Extraímos as **11 linhas PRCP das 11 estações consumidas** dos três arquivos integrais, sem duplicatas: todas eram byte a byte idênticas (inclusive os anos de disponibilidade). A igualdade desses campos não estabelece igualdade dos inventários completos.

**Replay verificável:** o CI obtém a captura de Wayback, verifica seu SHA inteiro, aplica um delta textual comprimido e versionado, e exige que o arquivo reconstruído tenha **exatamente o SHA integral de 13/11**. A comparação independente `cmp` entre arquivo reconstruído e coleta original resultou em identidade de todos os 36.402.100 bytes. Nenhum arquivo NOAA de 36 MB foi incluído no Git ou LFS. Os `*.dly`, `readme.txt` e catálogo de estações continuam verificáveis pelos hashes originais. O código usa verificações obrigatórias, inclusive com Python otimizado.

Isso preserva a genealogia e a reprodutibilidade da alegação meteorológica documental, **não** certifica pluviômetro, hora de coleta, coordenada em 1963 ou a posição terminal do NORAD 528. Controle negativo de mutação do snapshot e do delta impede falso PASS. [Issue #724](https://github.com/franklinbaldo/conde-incident/issues/724) documenta o incidente.

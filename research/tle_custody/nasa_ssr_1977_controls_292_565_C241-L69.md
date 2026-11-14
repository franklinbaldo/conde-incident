---
type: Guide
title: "C241-L69: NASA 1977 imprime SIGMA 1=292 e 1963 009B=565"
description: "Duas correspondências institucionais retrospectivas no SSR 1977, sem sensor, hora terminal ou restrição física para NORAD 528."
---

# C241-L69: duas identidades retrospectivas, sem tempo terminal

A [demanda do Cervo](https://github.com/franklinbaldo/tartaruga/issues/8) já tem duas datas publicadas contemporaneamente no [SSR NASA/Goddard de 30/11/1963, C241-L62](nasa_ssr_terminal_controls_C241-L62.md). Naquela edição, os números NORAD 292 e 565 **não estão impressos** e as junções eram secundárias.

O fac-símile original [NASA/Goddard *Satellite Situation Report*, vol. 17, nº 6, 31/12/1977](https://ntrs.nasa.gov/citations/19780009188), traz na seção *DECAYED OBJECTS* os seguintes pares na **mesma linha**:

| Controle | Identificação impressa em 1977 | NORAD impresso | Lançamento | Decaimento impresso | Página |
| --- | --- | ---: | --- | --- | --- |
| 292 | `SIGMA 1`, sob `1962 LAUNCHES` | **292** | `15 MAY` | `26 NOV 63` | impressa **−42−**, PDF **46**, índice 45 |
| 565 | `1963 009B`, sob `1963 LAUNCHES` | **565** | `3 APR` | `24 NOV 63` | impressa **−44−**, PDF **48**, índice 47 |

[Fac-símile página 46](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf#page=46) e [página 48](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf#page=48), conferidas visualmente a partir das páginas renderizadas em 14/11/2026 no Ifro. A grafia `1963 9B` aparece no original de 1963, e `1963 009B` no de 1977: não atribuir o segundo formato ou número NORAD ao primeiro documento.

**Custódia do PDF recuperado:** 11.563.410 bytes, 115 páginas, SHA-256 `c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8`. É o **mesmo arquivo NASA já custodiado em C241-L32**, e não uma nova fonte de rastreamento independente. A publicação de 1977 é institucional original, mas retrospectiva, e pode compartilhar os dados da família NASA/NORAD/SAO com o SSR de 1963.

**Limite:** impressão de nome e número em 1977 demonstra identidade **editorial retrospectiva**, não observação instrumentada em 1963. As linhas não informam hora terminal UTC, estação, sensor, erro de previsão, intervalo de confiança, covariância ou localização de queda. Os campos permanecem `null`; nenhum parâmetro de NORAD 528, probabilidade ou hipótese de queda em Conde foi alterado.

O [JSON](nasa_ssr_1977_controls_292_565_C241-L69.json) fixa as duas linhas. O [auditor](../../tools/tle_ssr_1977_controls_c241_l69.py), os [testes adversariais](../../tests/test_tle_ssr_1977_controls_c241_l69.py) e a extensão do workflow C241-L62 validam a fonte, a genealogia, os nulos e o hash do PDF. Próxima prova: correspondência **contemporânea** NORAD/AF IN/SPADATS com número, evento físico, instante/escala temporal e sensor, especialmente para 292/565, sem atribuir precisão temporal a dados apenas editoriais.

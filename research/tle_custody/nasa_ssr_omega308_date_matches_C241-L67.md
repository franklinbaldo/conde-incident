---
type: Guide
title: "C241-L67: correspondência por datas entre edições NASA não confirma identidade"
description: "Três linhas de 1962/1963 mudam de rótulo em 1977 apesar de repetirem data de lançamento e decaimento; teste de identidade parcial."
---

# C241-L67 | Datas iguais, três rótulos divergentes

O [boletim NASA/GSFC de 15/12/1963](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=17) (PDF 17, impressa 15) imprime **OMEGA 1**, **OMEGA 2** e **OMEGA 3**, todos com lançamento **18 JUN [1962]**. Seus campos de decaimento são, respectivamente, **29–30 OCT 63**, **12 JUL 62** e **14 JUL 62**.

O [boletim NASA/GSFC de 31/12/1977](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf#page=46) (PDF 46, impressa −42) imprime as mesmas combinações *lançamento + decaimento*, na sequência, como **OMEGA 2 / NORAD 308**, **OMEGA 3 / NORAD 310** e **A-ALPHA 5 / NORAD 314**. Não é uma simples renumeração uniforme de OMEGA: o terceiro nome passa a outra série.

| NASA 1963 (sem NORAD) | Campo DECAY | NASA 1977 (com NORAD) |
|---|---|---|
| OMEGA 1 | 29–30 OCT 63 | OMEGA 2 / 308 |
| OMEGA 2 | 12 JUL 62 | OMEGA 3 / 310 |
| OMEGA 3 | 14 JUL 62 | A-ALPHA 5 / 314 |

**Diagnóstico de identificabilidade:** o par de datas distingue as três linhas **dentro dessas tabelas**, porém igualdade de datas editoriais não comprova identidade física, sensor, correção oficial nem independência das publicações. Não atribuir um NORAD contemporâneo às três linhas por essa junção. O boletim de 1977 contém o catálogo retrospectivo expresso; o de 1963 não. A causa dos nomes divergentes permanece indeterminada. O registro C241-L66 da 🐢 Tartaruga continua íntegro e é validado como dependência, não substituído.

**Insumos custodiados:** 1963 NTRS `19640003479`, PDF SHA-256 `d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f`; 1977 NTRS `19780009188`, SHA-256 `c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8`. Dados em `nasa_ssr_omega308_date_matches_C241-L67.json`, teste determinístico em `tools/tle_ssr_omega308_date_matches_c241_l67.py` e suíte adversarial. O CI existente C241-L66 verifica os dois PDFs por SHA e executa as duas suítes em Python normal e otimizado.

**Próxima observação discriminante:** documento primário contemporâneo com **NORAD + nome/designação** para cada uma dessas linhas, ou errata oficial entre as duas edições. Para calibrar reentrada ainda será necessário instante ou intervalo terminal independente com sensor, relógio, incerteza e órbitas anteriores.

**Estados:** `instrumental_identity=NOT_CONFIRMED`; `terminal_sigma=null`; `historical_mcmc=NOT_RUN`; `active_constraint_528=false`; sem probabilidade de queda em Conde.

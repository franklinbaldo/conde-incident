---
type: Guide
title: "C241-L66: Omega 1 (1963) versus Omega 2/308 (NASA 1977)"
description: "Identidade impressa retrospectiva de NORAD 308 e conflito entre edições NASA; errata aditiva sem inferência de observação terminal."
---

# C241-L66 | A identidade mudou entre edições

**Achado verificável:** a NASA imprimiu uma associação explícita **`OMEGA 2 ↔ NORAD 308`** em sua tabela retrospectiva *Satellite Situation Report*, vol. 17, n.º 6, seção *Decayed Objects*, [NTRS 19780009188](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf#page=46), **página impressa −42 / página PDF 46**. A linha registra fonte US, lançamento **18 JUN [1962]** e campo de decaimento **29–30 OCT 63**.

Na mesma página, a linha imediatamente anterior distingue **`OMEGA 1 ↔ 307`**, lançamento **17 JUN [1962]**, decaimento **18 JUN 62**; a seguinte informa **`OMEGA 3 ↔ 310`**. A tabela do PDF original de **11.563.410 bytes / 115 páginas** foi examinada visualmente em 14/11/2026, SHA-256 `c5c66eb7eab242ab5b3dd56567de8bab2d404d0a6776baeb3b79383c86bc5ba8`.

**Conflito documental, não resolvido:** o boletim contemporâneo NASA/GSFC vol. 3, n.º 24, de **15/12/1963**, [NTRS 19640003479](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=17), **página impressa 15 / PDF 17**, publica `OMEGA 1 | US | 18 JUN | 29-30 OCT 63`, **sem número NORAD**. Na edição retrospectiva, a mesma combinação de datas aparece sob **OMEGA 2 / 308**, enquanto OMEGA 1 é **307**. A edição original de 1963 pode conter erro de nomenclatura, renomeação ou outra convenção editorial; **não se conhece a causa**. Não converter essa hipótese em correção silenciosa do original.

**Custódia e independência:** o fac-símile de 1963 tem 958.927 bytes, 23 páginas, SHA-256 `d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f`. A variante de 1977 **já está custodiada em C241-L32**, em outro trecho, e não constitui um novo sensor nem um novo documento independente. C241-L64 preserva o primeiro erro transcritivo `A OMEGA 1`; C241-L65 corrige para `OMEGA 1`. Este C241-L66 é **adendo de identidade entre edições**. Não alterar bytes/hashes de L64/L65. É válida a identidade impressa *retrospectiva*, não uma identidade instrumental contemporânea agora comprovada.

**Escopo:** campo `DECAY` editorial não é UTC de reentrada, última detecção nem erro estatístico. Faltam observação primária, estação, sensor, instante, convenção de relógio e incerteza. Nenhum parâmetro ou probabilidade histórica do **NORAD 528** foi alterado, tampouco a hipótese de queda em Conde.

O registro estruturado `nasa_ssr_omega308_cross_edition_C241-L66.json` guarda as duas versões e as hipóteses **explicitamente nulas**. O auditor `tools/tle_ssr_omega308_cross_edition_c241_l66.py` valida a fonte e rejeita a unificação prematura, incluindo testes negativos normais e sob `python -O`.

**Próxima diligência:** buscar erratas e circulares NASA/GSFC/NORAD entre 1963 e 1977 que expliquem o deslocamento `OMEGA 1 ↔ OMEGA 2`, além de registro NORAD/AF IN de 1963 com número 308, relógio e método; comunicar ao 🦌 Cervo para não usar o rótulo contemporâneo como crosswalk primário confirmado.

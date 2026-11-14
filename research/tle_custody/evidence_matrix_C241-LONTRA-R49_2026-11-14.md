---
type: Guide
title: "C241-LONTRA-R49: cotejo numérico do anuário soviético e SSR NASA"
description: "Dois campos orbitais impressos coincidem exatamente, mas identidade, arredondamento e genealogia instrumental permanecem não demonstrados."
---

# C241-LONTRA-R49 · Cotejo de tabelas de 1963, sem duplicação de sensores

**Nova ligação documental de dois fac-símiles já autenticados:** o anuário soviético *Ежегодник Большой советской энциклопедии*, edição 1964, seção *Наука и техника*, [p. impressa 503, PDF folha 7](https://istmat.org/files/uploads/35454/14_nauka_i_tehnika.pdf#page=7), registra a terceira linha de satélites americanos de 1963 como «Секретный» (secreto), lançado em 16/01. A [NASA *Satellite Situation Report* vol. 3 nº 23, 30/11/1963, p. impressa 5, PDF folha 7](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7) identifica a linha 1963 3A. Ambos os PDFs foram recuperados e verificados em trabalhos anteriores (C241-LONTRA-R48 e C241-L18); este trabalho compara as transcrições sem reivindicar novas capturas independentes.

| Campo | Soviético 1964 (nome secreto) | NASA 30/11/1963 (1963 3A) | Comparação |
|---|---:|---:|---|
| Perigeu (km) | 459 | 459 | identidade numérica |
| Apogeu (km) | 533 | 533 | identidade numérica |
| Período (min) | 94,66 | 94,6 | diferença 0,06 min |
| Inclinação (°) | 81,89 | 81,88 | diferença 0,01° |

**A identidade exata do par perigeu/apogeu é um novo vínculo pesquisável, não um novo registro instrumental.** As linhas não são idênticas: arredondar 94,66 para uma casa decimal pelo método convencional dá 94,7, não os 94,6 da NASA. A inclinação também difere. Não está demonstrado que o editor soviético copiou o boletim NASA de 30/11; pode haver fonte ocidental anterior ou upstream comum. A tabela soviética não fornece NORAD/COSPAR nem distingue 1963-003A, B e C, embora seja numericamente compatível com a linha A do boletim; também não informa estação, tempo UTC do sensor, referencial, RAAN nem incerteza. O lançador impresso Thor–Agena D diverge da atribuição Thor–Agena B em catálogos modernos, exigindo cotejo documental.

**Genealogia:** a nota bibliográfica soviética inclui *Flight*, *Aviation Week*, *Missiles and Rockets*, *Interavia* e *Air Letter*; o SSR NASA é uma compilação NASA–NORAD–Smithsonian já documentada em C241-L20. A linha retrospectiva soviética não pode ser contada como nova observação de novembro ou como um segundo sensor. O instante do boletim, referido como as of 1200Z em 30/11, não demonstra instante instrumental.

Fontes canônicas dos valores e checksums: [C241-LONTRA-R48](soviet_bse1964_1963_003_C241_LONTRA_R48.json) e [C241-L18](nasa_ssr_jul_dec_1963_C241-L18.json). O [manifesto cruzado](soviet_nasa_crosswalk_C241_LONTRA_R49.json), [auditor](../../tools/audit_soviet_nasa_crosswalk_r49.py) e [testes adversariais](../../tests/test_soviet_nasa_crosswalk_r49.py) bloqueiam identificação falsa, arredondamento inexistente e promoção a restrição orbital.

**Estado:** PRINT_NUMERIC_PAIR_MATCH_SOURCE_DEPENDENCE_UNRESOLVED. Zero novas medidas instrumentais e zero filtros físicos ativados. Próximo passo é localizar as tabelas datadas dos cinco periódicos ocidentais para confirmar ou refutar a ancestralidade de 459/533 e 94,66. Não houve contato externo.

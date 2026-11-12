---
type: Guide
title: "C241-P2: precessão nodal J2 congelada versus controle linear nos holdouts"
description: "Teste temporal falsificável dos campos orbitais secundários do NORAD 527/528/529, sem ajuste de dados de avaliação."
---

# C241-P2: modelo J2 congelado no último estado de ajuste

**Pergunta falsificável.** Se fixarmos em cada NORAD o último estado orbital secundário antes de agosto de 1963, a taxa secular J2 prediz o RAAN dos registros posteriores melhor que o controle linear ajustado exclusivamente nos RAAN anteriores a agosto e que a persistência angular? A taxa por objeto não pode ser transferida a outro NORAD. É comparação numérica dentro de catálogo, não reconstrução da órbita real.

**Fonte e limites.** Parquet secundário do espelho de Space-Track [oxzoid rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09; CSV derivado com índice de linha, SHA-256 3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231. Extrato RAAN P1 e split congelado são verificados sem alteração. 123 linhas, 119 épocas distintas (527=20, 528=45, 529=54); vínculos C25#1/C179#1/C180#1/C181#1, C241-L4 e C241-P1. O boletim primário [NASA SSR 15/11/1963 p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) é documento de **dia** de decaimento, não contém RAAN, época TLE nem frame orbital. Nenhum acompanhamento instrumental original foi recuperado nesta comparação.

**Operador pré-declarado.** No último registro do bloco fit de cada objeto, fixar inclinação i (graus), excentricidade e (adimensional), movimento médio n (revoluções/dia) e RAAN (graus). Converter n em rad/s; a=(mu/n²)^(1/3) e dOmega/dt=−3/2 J2 n (R/(a(1−e²)))² cos(i), usando mu=398600.4418 km³/s², R=6378.137 km e J2=1.08262668e−3. Não reestimar a partir de validação/avaliação. Comparar diferenças circulares mínimas em graus com persistência e OLS linear P1, usando exatamente os mesmos cortes cronológicos e multiplicidade corrigida. Avaliação começa em outubro de 1963; 527=4, 528=8, 529=23 épocas. Ensaio retrospectivo, não blindado.

**Não independência.** Os controles 527/529 pertencem à mesma família catalográfica secundária e não são sensores externos. As taxas J2 sobre elementos médios históricos sem frame comprovado são proxies. A tolerância de extração RAAN ±0,00008° é somente de serialização, **não sigma instrumental**.

**Regra de promoção.** Se o proxy vencer um baseline, registrar ganho preditivo sobre catálogos secundários. Se perder, registrar resíduo e modelo rejeitado para esse intervalo, sem ajustar constante a posteriori. Em ambos os casos, domínio orbital físico Θ antes/depois **inalterado, não quantificado**; não há filtro validado de admissibilidade, probabilidade, impacto ou horário em Conde. Um Θ demonstravelmente menor exigiria TLEs instrumentais 527/528/529 com checksums, épocas originais, referencial histórico, erros/covariâncias e holdouts independentes.

**Reprodução:** python3 -m unittest discover -s tests -p test_raan_frozen_j2_holdout.py -v. O [workflow C241-P2](../../.github/workflows/polvo-j2-frozen-long.yml) baixa o Parquet com hash fixado via tools/tle_secondary_1963_ledger.py, executa tools/raan_frozen_j2_holdout.py, preserva relatório por época e executa lake build/auditoria de axiomas Lean 4.35.0 no HEAD. Os resultados numéricos e erros são preservados no artefato do CI.

## Resultados auditados no primeiro HEAD

Execução [GitHub Actions #43285011757](https://github.com/franklinbaldo/conde-incident/actions/runs/43285011757) do commit 1d39086909d9c240300a6ae0bc93d4018c142c10: fonte Parquet e CSV derivados aceitos pelos SHA-256 fixados; 7 testes adversariais e 8 regressões P1 passaram; compilação Lean 4.35.0 e auditoria de axiomas passaram. O JSON detalhado está no artefato polvo-j2-frozen do workflow.

| NORAD | épocas de avaliação | taxa J2 fixada (°/dia) | taxa OLS fit-only (°/dia) | MAE persistência (°) | MAE OLS (°) | MAE J2 (°) | erro máximo J2 (°) |
|---|---:|---:|---:|---:|---:|---:|---:|
| 527 | 4 | −1,083444 | −1,076704 | 104,571675 | **0,191882** | 0,511195 | 0,767903 |
| 528 | 8 | −1,114910 | −1,092409 | 90,821137 | 2,908005 | **0,679537** | 1,057725 |
| 529 | 23 | −1,104253 | −1,084459 | 127,333996 | 3,743723 | **1,137675** | 3,114390 |

Na validação anterior à avaliação (também sem refit), o MAE J2 foi 527=0,162489°; 528=0,112204°; 529=0,111661°. O J2 foi melhor que a linha OLS **nos registros tardios 528 e 529, mas pior em 527**, que tem apenas 4 registros tardios. Isto refuta uma afirmação universal de superioridade J2 e não permite reutilizar o mesmo erro/força entre satélites. A persistência foi pior que ambos nas avaliações, mas não transforma nenhuma série de catálogo em rastreamento instrumental.

**Resultado negativo e validade:** as diferenças são internas a uma mesma família de fonte secundária, não probabilidades, limites de erro de sensores nem observações independentes. O RAAN legado de 284,1520° (origem sem prova) não participa do ajuste. Os 35 holdouts tardios não constituem evidência autônoma do local de reentrada. Domínio orbital físico Θ: antes/depois **idêntico, sem volume/intervalo calibrado e sem demonstração de não-vazio novo**. Evidência necessária para uma redução genuína: pares TLE instrumentais de 1963 dos 527/528/529 com epoch, frame, checksum, fonte de sensor e sigma/covariância, seguidos de resíduos de propagação contra holdouts de origem independente.


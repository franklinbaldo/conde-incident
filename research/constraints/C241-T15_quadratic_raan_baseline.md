---
type: Guide
title: "C241-T15: falsificador quadrático para holdout RAAN J2"
description: "Ablação temporal com baseline quadrático e 35 épocas de avaliação, mantendo linhagem secundária e limites físicos."
---

# C241-T15: o ganho J2 sobre uma reta é específico à reta?

**Pergunta discriminante:** [C241-P2](C241-P2_j2_frozen_long_holdout.md) mostrou que J2 congelado supera OLS linear em 528/529 mas perde em 527. Um quadrático treinado apenas com RAAN anterior ao corte pode produzir a mesma aparente melhora sem mecanismo J2. Esta terceira comparação é retrospectiva, não blindada, e não estima órbita terminal.

**Custódia:** [Parquet secundário oxzoid/Space-Track rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV derivado SHA256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. Uma família secundária, não três sensores independentes. Fonte primária [NASA SSR 15/11/1963, NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) confirma somente dia de decaimento catalogado de 1963-003B; **não** autentica RAAN ou rastreamento.

**Operador:** corte fit fixo anterior a 01/08/1963; validação em ago–set; avaliação a partir de 01/10. Épocas de avaliação: 527=4, 528=8, 529=23. Mínimos quadrados de grau 2 sobre RAAN desenrolado sequencialmente do bloco fit, abscissa normalizada no último fit, sem refit ou ajuste de hiperparâmetros após agosto. Comparar os resíduos circulares mínimos em graus, MAE e RMSE com o controle OLS e J2 do mesmo workflow C241-P2. Reportar perdas e vitórias, cada época e diferença assinada de MAE no artefato CI.

**Controle reproduzido localmente no JSON secundário congelado, sem novo download:** MAE quadrático 527=0,075589024°, 528=0,683123788°, 529=1,143076945°. O CI completo precisa revalidar o Parquet e o CSV, recomputar J2 sobre os campos pré-corte e confrontar os mesmos 35 alvos. O quadrático ajusta três coeficientes e o proxy J2 usa elementos médios do espelho, logo menor erro não prova lei física nem implica superioridade externa.

**Grafo:** C25#1/C179#1/C180#1/C181#1 → C241-P1#1 (split) → C241-P2#1 (taxa J2) → C241-T15#1 (curvatura empírica fit-only, erro no 529). `CONNECTED_PENDING_CALIBRATION`, domínio físico Θ inalterado e não quantificado. Épocas do catálogo secundário não substituem proveniência instrumental, referencial de 1963, incertezas/covariâncias e holdout independente. RAAN 284,1520° legado sem fonte permanece fora do ajuste; não há probabilidade, hora ou posição terminal.

**Reprodução:** `python3 -m unittest discover -s tests -p test_texugo_quadratic_raan_ablation.py -v`. [Workflow próprio](../../.github/workflows/texugo-quadratic-raan.yml) baixa sob hash fixado, reexecuta os comparadores e arquiva JSON completo. Validação instrumental externa: `NOT_RUN` porque os registros primários necessários permanecem ausentes.

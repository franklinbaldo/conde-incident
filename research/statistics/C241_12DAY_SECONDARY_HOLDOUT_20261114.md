---
type: Experiment
title: "C241: holdout retrospectivo dos irmãos em horizontes de 9 a 15 dias"
description: "Resíduos empíricos de catálogo secundário; não são sigma instrumental nem erro de horário de reentrada"
experiment_id: C241-12DAY-SECONDARY-20261114
verification_status: RETROSPECTIVE_SAME_LINEAGE_NOT_TERMINAL_CALIBRATION
---

# Controles 527 e 529: erro de extrapolação próximo de 12 dias

**Pergunta:** o que já podemos medir, sem assumir um sigma hipotético, sobre previsões do plano e do movimento médio entre datas com registro de catálogo? O NORAD 528 termina no espelho em 27/10/1963 e não possui confirmação orbital em 8/11. Os controles 527 e 529 têm registros posteriores, mas não medem diretamente o erro terminal do 528.

**Fonte:** [espelho histórico Space-Track 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet). SHA-256 do Parquet: `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV derivado: `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`, gerado por `tools/tle_secondary_1963_ledger.py` e verificado novamente no consumo. Esta é **uma única linhagem documental secundária**, sem horários de sensor independentes, sem frame histórico estabelecido ou covariâncias. Relação com [#647](https://github.com/franklinbaldo/conde-incident/issues/647), [#396](https://github.com/franklinbaldo/conde-incident/issues/396) e a [PR #20](https://github.com/franklinbaldo/conde-incident/pull/20) de holdout 529, que usa outra família de modelos e muitas janelas sobrepostas. Não contar as mesmas épocas como réplicas externas.

**Método retrospectivo criado após inspecionar as datas (14/11):** em cada origem dos controles, escolhe-se a época futura de mesmo objeto cuja distância de 12 dias é mínima, limitada ao intervalo de 9 a 15 dias. Só entram no cálculo de previsão a origem e o registro imediatamente anterior; não se observa o valor futuro para escolher coeficientes. Baselines: RAAN por precessão secular J2 do estado de origem, RAAN por inclinação local dos dois últimos pontos, movimento médio persistente ou com extrapolação linear dos dois últimos pontos, inclinação e excentricidade persistentes. Ângulos RAAN usam erro circular. Não há SGP4, ajuste de arrasto, previsão da fase ou cálculo de 120 km. Nenhum baseline foi escolhido pelo menor erro futuro; ambos permanecem no relatório. A inspeção prévia e a seleção temporal tornam o teste exploratório, não pré-registrado em 1963.

**Resultados (origens de 1 a 27/10/1963):**

| Controle | pares sobrepostos | alvos futuros distintos | RMSE RAAN/J2 | RMSE movimento médio, linha local |
|---|---:|---:|---:|---:|
| 527 | 1 | 1 | 0,021169° | 0,00037879 rev/dia |
| 529 | 5 | 3 | 0,099328° | 0,01210704 rev/dia |

No arquivo [JSON de replay](c241_12day_secondary_holdout_20261114.json) há também todos os pares por época, erros assinados, RMSE e MAE de todos os baselines, e um bloco abrangendo os demais meses de 1963. O 527 tem um intervalo de mais de 30 dias entre 16/10 e 19/11, e, portanto, não oferece uma validação 12 dias depois de sua última posição de outubro. Os cinco pares 529 compartilham alvos e **não são cinco ensaios independentes**; o conjunto ampliado inclui regimes de altitude muito diferentes do 528 terminal.

**Sensibilidade aos alvos repetidos:** a análise suplementar pondera cada **época futura distinta** igualmente, calculando primeiro o erro quadrático médio das previsões que apontam para a mesma época. Esse diagnóstico descritivo não cria independência instrumental e não reestima modelos. Para outubro, o 529 tem 5 pares mas só 3 épocas-alvo (multiplicidades 1, 2 e 2); o RMS J2 original ponderado por par é **0,099328°**, contra **0,095532°** ponderando cada alvo igualmente. Para movimento médio, **0,012107** contra **0,011782 rev/dia**. Um teste de exclusão de um alvo inteiro por vez, **sem reajuste**, documenta a amplitude de sensibilidade no JSON. O 527 possui só um alvo, portanto exclusão de alvo é **indefinida**, não zero. Esses resultados não fornecem intervalo de confiança nem estimativa de sigma.

**Decisão:** são erros de previsão de *valores publicados no espelho*, não sigma medido do radar/SPADATS; não se podem converter seus RMS em erro de tempo de reentrada de 528 ou incerteza de longitude, nem usá-los como covariância de MCMC físico. O teste 527/529 não calibra por si só a densidade de 1963: massa/área do 527, variação vertical e temporal de densidade, observações com épocas instrumentais e a indeterminação da transferência entre objetos ainda importam (ver `joint_control_transfer_identifiability_C241.json`, `DENSITY_EPOCH_CONTRAST_C241.md`). A melhora do plano é mensurável condicionalmente, mas fase/arrasto não ficaram determinados. Domínio físico admissível: **sem estreitamento validado**.

**Replay:** `python3 tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/source` (requer `pyarrow`); `python3 tools/c241_12day_secondary_holdout.py --csv /tmp/source/norad_527_528_529_numeric_1963.csv --output research/statistics/c241_12day_secondary_holdout_20261114.json --check`; `python3 -m unittest discover -s tests -p 'test_c241_12day_secondary_holdout.py' -v`.

**Próximo teste:** calibrar um propagador de reentrada sobre outras **reentradas com hora efetivamente conhecida e observações anteriores**, reservando datas/instrumentos para validação. O 637, catalogado até 5/11 no Parquet, é controle de regime mais próximo, mas a disponibilidade de seu horário real de decaimento também deve ser comprovada antes de calibrar uma distribuição de erros em horas.

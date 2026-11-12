---
type: Guide
title: "C241-P1: previsão cronológica do RAAN secundário sem refit posterior"
description: "Controle numérico falsificável de baseline estático contra deriva linear ajustada somente no bloco histórico anterior a agosto de 1963, para 527/528/529."
---

# C241-P1: previsão congelada do RAAN do catálogo secundário (🐙 Polvo)

**Pergunta falsificável, ligada à issue #15:** com parâmetros ajustados **somente nas épocas anteriores a 01/08/1963**, uma tendência angular linear prediz os elementos de épocas posteriores do catálogo de 527, 528 e 529 com menor erro angular que a hipótese de RAAN constante? O desvio tardio é igual entre os três objetos ou cresce de modo diferente?

**Fonte observacional de origem e linhagem:** a amostra local é exclusivamente research/statistics/raan_527_528_529_1963.json, extrato com norad_id, época UTC e RAAN em graus, derivado do [espelho Space-Track 1963 de oxzoid](https://huggingface.co/datasets/oxzoid/space-track-tle-history/resolve/main/data/tle_1963.parquet), sem TLEs instrumentais originais autenticados. O JSON traz SHA-256 do Parquet **atribuído à extração anterior**, não hash verificado novamente nesta rodada. tools/raan_coepoch_audit.py valida os registros, deduplica épocas exatas e detecta conflitos; o arquivo raan_chronological_holdout_1963.json guarda partições congeladas por UTC. **IDs:** C25#1, C179#1 (RAAN 198,5261° em 27/10 para 528), C180#1, C181#1, C241-L3 e a nova ocorrência derivada **C241-P1#1**. Múltiplas linhas são da MESMA linhagem moderna e não são sensores independentes.

**Fonte primária documental de controle:** NASA/Goddard, *Satellite Situation Report* de **15/11/1963**, [NTRS 19640001198, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), identificada na matriz como **C197#1**, contém somente o dia catalogado da reentrada (08/11/1963); não tem RAAN, órbita terminal, medição de posição ou erro. **Não entra** como alvo do fit ou holdout, nem prova impacto em Conde. Não foi relida nesta rodada. A linha de RAAN **284,1520°** do site legado não tem origem instrumental, época ou referencial verificados e **não entra** no ajuste.

## Protocolo já fixado e sem vazamento

- **Ajuste:** épocas antes de 1963-08-01T00:00Z (527: 15, 528: 24, 529: 22 épocas únicas). Desembrulhar diferenças angulares consecutivas pelo menor arco, mantendo ressalva de rotações completas não observadas em lacunas. Ajustar por mínimos quadrados ordinários uma única reta de RAAN contra dias decorridos desde a primeira época sobre o bloco de ajuste, **sem parâmetros de validação ou avaliação**.
- **Controle estático:** persistir o último valor RAAN do bloco de ajuste. **Modelo linear:** transportar somente os coeficientes de intercepto (graus) e taxa (graus/dia) da regressão congelada. Calcular erro circular pela diferença curta entre RAAN do catálogo e RAAN do modelo, e MAE, RMSE, viés e máximo em **graus**.
- **Validação:** 01/08/1963 a 30/09/1963; **avaliação:** 01/10/1963 a 31/12/1963, sem refit, seleção de modelo ou reconciliação posterior. A divisão foi especificada retrospectivamente em C241-L3 e **não é um holdout historicamente cego**. Não atribuir incertezas de sensor a resíduos empíricos.

| NORAD | m ajustado antes de agosto (°/dia) | validação n, MAE estático → linear (°) | avaliação n, MAE estático → linear (°) | Máximo linear da avaliação (°) |
|---|---:|---:|---:|---:|
| 527 | -1,076704 | 1: 29,310400 → **0,070211** | 4: 104,571675 → **0,191882** | 0,254389 |
| 528 | -1,092409 | 13: 45,253385 → **1,411200** | 8: 90,821137 → **2,908005** | 3,570671 |
| 529 | -1,084459 | 9: 42,913944 → **1,017306** | 23: 127,333996 → **3,743723** | 6,523053 |

**Resultado numérico:** a tendência fit-only supera o RAAN estático nos três objetos do mesmo catálogo. **Resultado adverso para tratar os objetos como intercambiáveis:** o erro de extrapolação da tendência em 529 chega a **6,523053°**, versus **0,254389°** no 527; o 528 apresenta viés circular médio de **−2,908005°** na avaliação. Não transferir a taxa/calibração de um objeto para outro sem dinâmica própria. Para o 529 o horizonte máximo avaliado desde o último fit é **154,759 dias**, para o 528 **93,494 dias**, e para o 527 **138,488 dias**; as métricas globais, portanto, não são um ranking de precisão orbital sob condições iguais. Linhas múltiplas do mesmo espelho não aumentam a independência.

**Antes → depois (domínio admissível físico Θ):** permanece **não quantificado e sem qualquer restrição nova**. O teste mede capacidade de previsão de *números impressos no catálogo*, não estado orbital do 528, ângulo de plano inercial comum, SGP4, convergência dos três corpos, reentrada, latitude, longitude ou impacto. Nenhum intervalo de erro instrumental foi estimado. O testemunho de não-vazio físico não foi calculado; nenhuma prova Lean nova foi inventada. **Resultado histórico do impacto: indeterminado.**

**Dado que desbloqueia o próximo predicado Lean/Castor:** linhas originais line1/line2 527/528/529 (com checksums e fonte primária), época e quadro de referência originais, cronologia de rastreamento observacional e covariância/erro por época, além de validação dinâmica contra observações **instrumentalmente independentes**. Somente então os erros absolutos poderão virar intervalos fisicamente justificados e intersectar um conjunto Θ não vazio. O RAAN 284,1520° requer documento de origem com época/frame antes de qualquer confronto físico.

**Reprodução:** python3 tools/raan_frozen_trend_holdout.py --check research/statistics/raan_frozen_trend_holdout_C241-P1.json; python3 -m unittest discover -s tests -p test_raan_frozen_trend_holdout.py -v. O script verifica que **exatamente** o manifesto de partição antigo é reobtido dos bytes de entrada, e os testes sabotam atribuições de blocos, conflitos de época, circularidade e refit. CI do projeto executa todas as suítes Python, lake build Lean 4.35.0, auditoria de axiomas e prek no **SHA da PR**.

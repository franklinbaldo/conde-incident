---
type: Experiment
title: "C241: reponderação conjunta orbital e temporal, por trajetória, em Python"
description: "Mesmo sorteio de 1,5 milhão de candidatos com pesos NASA-dia e erros orbitais, grid geodésico de 200 km e arquivo completo de amostras; não é probabilidade de impacto."
experiment_id: C241-JOINT-ORBIT-DAY-20261113
verification_status: SYNTHETIC_J2_SAME_DRAW_NOT_HISTORICAL_IMPACT
---

# O cruzamento que faltava: peso orbital × peso temporal na MESMA trajetória

A combinação correta exige guardar **o instante, os parâmetros orbitais e a localização** de cada amostra, antes de somar probabilidades por quadrícula. Multiplicar percentuais finais de mapas diferentes é incorreto, porque os eventos geográficos, os parâmetros e a hora podem estar associados.

O novo [motor em Python](../../tools/c241_joint_orbit_day_heatmap.py), com NumPy e SciPy explicitamente versionados (PEP 723), gera uma amostra única e calcula quatro visões aninhadas:

1. Amostra sem penalização: todas as 12 hipóteses de fase e derivada média igualmente ponderadas.
2. Penalização orbital, Gaussiana multivariada nas variações de fase/n-dot.
3. Penalização temporal, verossimilhança bilateral da etiqueta NASA de 8 de novembro, integrando o **dia civil inteiro**, com sigma hipotético de 6, 12 ou 24 horas.
4. Peso **conjunto por trajetória**, produto entre verossimilhança orbital e temporal na mesma linha; normalização global posterior a esse produto.

A matriz inclui 5 hipóteses orbitais com correlações −0,5/0/+0,5 e 3 temporais. Nenhuma escala de erro é afirmada como erro instrumental histórico. A [PR #650](https://github.com/franklinbaldo/conde-incident/pull/650) introduziu os pesos orbitais e a [PR #646](https://github.com/franklinbaldo/conde-incident/pull/646) introduziu a data bilateral; esta fatia recomputa as amostras individuais em vez de tentar multiplicar os seus resultados agregados.

## Fonte e modelo

- Fonte TLE: [espelho secundário de NORAD 528, 27/10/1963](../tle_custody/mirror_528_1963-10-27.tle), SHA-256 18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd, não é uma medição instrumental primária validada.
- Fonte da data: [NASA/Goddard SSR de 15/11/1963](https://ntrs.nasa.gov/citations/19640001198) C197#1; registro **8 NOV 63**, não uma hora observada nem data de chegada de fragmento ao solo.
- Elementos: média de dois corpos com correção secular de primeira ordem J2 e pequena excentricidade; n(t) = n0 + n-dot × t, Ω(t), ω(t) e anomalia média com correções seculares avaliadas no ponto médio. **Não é propagador SGP4**, e elementos médios TLE não são estados osculantes.
- Rotação: fórmula aproximada de GMST, assumindo UT1=UTC sem EOP histórico validado.
- Tempo terminal: distribuído **uniformemente entre 05/11 00Z e 12/11 00Z por decisão sintética**; NÃO é a distribuição da NASA nem um evento calculado de altitude abaixo de 120 km. O peso bilateral da data é aplicado posteriormente.
- Localização: ponto terrestre **subsatélite** no instante hipotético terminal. Coordenadas relativas a Conde (-11,8139°, -37,6108°) em projeção esférica azimutal equidistante, círculos geodésicos de 2.000 km e células de 200×200 km. O denominador é **toda a população global simulada**, não apenas o círculo.
- Partículas, reentrada física, fragmentação, ablação, área, Cd, massa individual do 528 e impacto no solo **não estão modelados** nesta fatia.

A grade anterior de 1.500.000 amostras registrou 1,6993% na região, porém usou outras convenções e outro gerador. Ela **não foi reponderada** porque só restaram contagens agregadas; portanto, NÃO se deve interpretar uma diferença entre 1,6993% e a nova amostra como mudança real de probabilidade histórica.

## Resultados: replay com 1.500.000 candidatos

Todos os percentuais abaixo usam **as mesmas amostras**, o mesmo denominador global e só diferem pela ponderação.

| Regra | Frequência dentro de 2.000 km |
|---|---:|
| Sem penalização | 1,673933% |
| Só erro orbital intermediário (σ fase 90°, σ n-dot 0,020 rev/dia²) | 1,678905% |
| Só etiqueta NASA do dia 8, σ temporal 12 h | 1,646500% |
| **Orbital × temporal na mesma trajetória** (intermediário × 12 h) | **1,672753%** |

Outros cenários conjuntos: estreito (25°, 0,006) com σ temporal 6h = **1,834978%**, enquanto intermediário × 24h = **1,652781%**. As diferenças refletem a escolha das margens hipotéticas e dos priors, não uma atualização de crença calibrada empiricamente.

O [sumário computado e versionado](c241_joint_orbit_day_1p5m_summary.json) registra todas as 5×3 combinações e ESS; [grade compacta de 400 células](../../public/data/conde-joint-orbit-day-heatmap.json), em inteiros de probabilidade fixa com unidade 1e−10, é gerada por [exportador Python](../../tools/export_c241_joint_heatmap.py) com teste de paridade exata. A grade permite construir mapa de calor e faixas marginais leste-oeste e norte-sul. Não atribuir a uma célula valor além da precisão da simulação ou erro cartográfico.

## Reprodução e arquivo de cada amostra

O workflow [C241 conjunto](../../.github/workflows/c241-joint-orbit-day.yml) verifica Python+NumPy/SciPy, testa casos adversariais, roda o sorteio de **1.500.000 trajetórias** no SHA exato com a semente 19631108, compara as frequências ao benchmark congelado, confere a paridade da grade compacta e arquiva:

    summary.json
    cells_200km.csv
    east_west_bands.csv
    north_south_bands.csv
    individual_candidates.npy

O arquivo estruturado NPY contém **para cada candidato** o instante UTC, índice da combinação de n-dot/fase, latitude, longitude, deslocamentos x/y em quilômetros e distância até Conde; parâmetros completos reconstruíveis por índice mais manifesto de prior. Assim se pode aplicar posteriormente novas verossimilhanças sem perder associações temporal-orbitais. Este arquivo binário volumoso **não é versionado** no repositório, apenas arquivado no Actions.

Execução fora do workflow:

    python3 -m pip install numpy==2.2.6 scipy==1.15.3
    python3 -m unittest discover -s tests -p test_c241_joint_orbit_day_heatmap.py -v
    python3 tools/c241_joint_orbit_day_heatmap.py --draws 1500000 --seed 19631108 --batch 50000 --out-dir /tmp/conde-joint --save-draws
    python3 tools/export_c241_joint_heatmap.py --summary /tmp/conde-joint/summary.json --cells /tmp/conde-joint/cells_200km.csv --output public/data/conde-joint-orbit-day-heatmap.json --check

**Conclusão:** cálculo conjunto efetivamente implementado e auditável, mas nenhuma **posterior histórica de Conde** ou probabilidade de material sobrevivente alcançando o solo foi identificada. A [issue #647](https://github.com/franklinbaldo/conde-incident/issues/647) continua aberta para calibrar os erros verdadeiros NASA/NORAD. Ablação, dinâmica terminal e priors físicos permanecem trabalho científico distinto.

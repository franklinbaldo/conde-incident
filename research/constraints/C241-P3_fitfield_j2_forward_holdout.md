---
type: Guide
title: "C241-P3: o J2 com elementos orbitais extrapolados do FIT melhora a previsão?"
description: "Comparação falsificável do J2 constante com deriva de inclinação, excentricidade e movimento médio congelada antes dos holdouts."
---

# C241-P3: deriva dos elementos do FIT integrada à precessão nodal J2

**Pergunta falsificável.** Extrapolar linearmente os campos n, i e e ajustados SOMENTE nas épocas FIT anteriores a agosto de 1963, e integrá-los na precessão secular J2, reduz os erros circulares RAAN na avaliação tardia de cada objeto 527, 528 e 529, comparado a J2 constante? A hipótese universal é falsificada se algum objeto piorar. Sem reajuste pelos holdouts.

**Fonte e linhagem.** [oxzoid, Parquet Space-Track secundário rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet); SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. CSV derivado com índice source_row, SHA-256 3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231. Matriz original C25#1/C179#1/C180#1/C181#1; conexões C241-L4#1, C241-P1#1, C241-P2#1 e nova C241-P3#1. O [boletim primário NASA de 15/11/1963, p.8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf) contém dia catalogado de reentrada, não RAAN ou covariância, e não calibra este teste.

**Operador e unidades.** Por objeto, OLS exclusivamente no bloco FIT, usando 527=15, 528=24, 529=22 épocas: di/dt em graus/dia, de/dt em 1/dia, dn/dt em rev/dia². Ancorar os três campos e o RAAN na última época FIT. Para cada tempo posterior, x(t)=x_fit+slope_fit×(t−t_fit), sem consultar estados futuros. Substituir na taxa J2 = −3/2 J2 n [R/(a(1−e²))]² cos(i) em rad/s com a=(μ/n²)^(1/3), n convertido de rev/dia; integração por pontos médios com passo máximo 0,25 dia e refinamento pelo dobro. Rejeitar n<=0, e<0 ou e>=1, ou i fora de [0°,180°]; não arredondar estados impossíveis. Convergência numérica não é sigma instrumental. Comparação circular em graus com os mesmos holdouts e baselines persistência, RAAN OLS e J2 constante de P1/P2. Extrapolação linear de elementos orbitais não é um modelo dinâmico demonstrado de arrasto.

| NORAD | FIT/avaliação | MAE OLS RAAN P1 (°) | MAE J2 constante P2 (°) | MAE deriva FIT + J2 P3 (°) | Resultado P3 |
|---|---:|---:|---:|---:|---|
| 527 | 15/4 | **0,191882** | 0,511195 | 0,605430 | Pior que P2 |
| 528 | 24/8 | 2,908005 | 0,679537 | **0,133510** | Melhor |
| 529 | 22/23 | 3,743723 | 1,137675 | **0,477634** | Melhor |

**Resultado negativo:** 527 piorou, portanto não há melhora universal. Os horizontes variam entre objetos. O erro máximo da duplicação de quadratura na avaliação foi inferior a 4×10⁻⁹ graus, valor exclusivamente numérico. Trata-se de holdout temporal retrospectivo e não blindado, não validação instrumental externa.

**Domínio Θ:** antes e depois idêntico, não quantificado; não-vazio não reavaliado. Nenhuma nova restrição orbital ativada, probabilidade, horário ou localização de impacto. A conexão testável n(t),i(t),e(t) → Ω(t) permanece CONNECTED_PENDING_CALIBRATION. O ganho em 528/529 ocorre dentro de uma mesma família de catálogo secundário e não autoriza predicado Lean de admissibilidade. Para ativá-lo faltam TLEs instrumentais originais de 527/528/529, epochs, frames, checksums, representação de elementos, erros/covariâncias e holdout independente. Nenhum teorema especulativo foi acrescentado.

**Reprodução:** baixar Parquet pinado e extrair CSV por tools/tle_secondary_1963_ledger.py; executar python3 -m unittest discover -s tests -p test_raan_fitfield_j2_holdout.py -v e python3 tools/raan_fitfield_j2_holdout.py --csv ARQUIVO --output RELATORIO. O workflow polvo-j2-frozen-long.yml valida o SHA exato, gera JSON por época como artefato, executa lake build Lean 4.35.0 e auditoria de axiomas; não cria gate JSON com null.

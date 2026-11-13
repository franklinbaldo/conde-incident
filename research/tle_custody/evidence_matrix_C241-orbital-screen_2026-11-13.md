---
type: Guide
title: "C241: triagem orbital J2 e arrasto efetivo do 528 com controles angulares"
description: "Replay de 45 épocas secundárias e controles 527/529, ajuste congelado, validação futura, separação de planos e janela condicional de 7–8/11."
---

# Triagem orbital: ajustar sem conhecer dimensões da peça

**Não é determinação histórica da trajetória.** A finalidade desta fatia é converter registros secundários existentes em um teste reprodutível com controles fora da amostra. O parâmetro de arrasto é **efetivo e não negativo**, sem atribuir massa, tamanho, Cd, área, densidade atmosférica observada ou covariância inventados.

## Fontes e linhagens

- **C241-L2:** [Parquet de 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09; CSV com índices de origem SHA-256 3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231. **Espelho secundário**, não 123 observações instrumentais independentes. 21/45/57 linhas, 20/45/54 épocas únicas.
- **C241-P1:** divisão temporal previamente congelada em research/statistics/raan_chronological_holdout_1963.json, sem seleção retrospectiva de épocas.
- **C197#1:** [NASA SSR 15/11/1963](https://ntrs.nasa.gov/citations/19640001198), data de decaimento atribuída 8 NOV 63, sem método de estimação e sem erro temporal conhecido. [Modelo de precisão](../constraints/nasa_528_decay_precision_C197_20261113.json), não uma observação de hora terminal.
- RAAN legada **284,1520°** sem fonte não é ativada. **198,5261°** em 27/10/1963 pertence ao espelho secundário e mantém essa classificação.

## Modelo e limitações

1. Cada movimento médio do espelho é transformado em um **proxy Kepleriano circular** de altitude, h=(μ/(2πn/86400)²)^(1/3)−R, com μ=398600,4418 km³/s² e R=6378,137 km adotados por convenção moderna.
2. Para conjunto congelado H em {30,45,60,90,120} km, ajustar aos registros FIT somente a constante efetiva k≥0 na equação dh/dt=−k exp(−(h−400)/H). A solução z(t)=z0−kt/H, com z=exp((h−400)/H), é usada na propagação.
3. A precessão secular J2 da RAAN é integrada usando a altitude-proxy, inclinação e excentricidade **congeladas no último FIT**. Não é conversão de elementos médios TLE em estado osculante; não é SGP4, nem integração cartesiana r/v.
4. Escolher H somente por MAE médio de altitude-proxy nos registros VALIDATION, com pesos iguais para 527/528/529; nunca usar EVALUATION para ajuste ou seleção. Comparar EVALUATION ao modelo sem arrasto (k=0) e registrar MAE de RAAN.
5. Controles angulares: calcular o ângulo entre normais dos planos orbitais cos ψ=cos i1 cos i2+sin i1 sin i2 cos(ΔΩ) e o contraste circular de RAAN para pares 528–527 e 528–529 em EVALUATION. Selecionar vizinho temporal mais próximo dentro do mesmo bloco de avaliação, com defasagem de até 72h. As épocas distintas são registradas; resíduos de pares assíncronos **não** são separações físicas coépocas nem sigma instrumental. Os ângulos podem evoluir sob J2/arrasto; não forçar separação constante.
6. O limiar 120 km é apenas uma interface exploratória para altitude-proxy circular. A data de cruzamento é extrapolação condicional, não evento calculado por propagador físico validado.

## Janela solicitada e teorema Lean

Cenário condicional em UTC: **7/11/1963 inclusive até 9/11/1963 exclusive**. Não admitir 9/11 ou posterior neste **cenário**. [Teoremas Lean](../../formal/Conde1963/Norad528DecayWindow.lean): sob a hipótese adicional de que o dia catalogado (8) não antecipa o dia físico e atrasa no máximo **um dia civil**, o evento está no dia 7 ou 8. Prova também testemunha não vazia e contramodelo: o rótulo NASA isoladamente **não** exclui 9/11. A premissa de atraso máximo de um dia não foi autenticada, portanto a janela não é restrição histórica ativa. Não ajustar H/k para acertar o dia: apenas classificar o resultado reservado.

## Interpretação e próximos dados

O relatório JSON contém parâmetros por cenário, validação, avaliação, baseline sem arrasto, contrastes angulares assíncronos, datas de cruzamento de proxy ou null e flags epistêmicas. Nenhum número é error bar instrumental ou probabilidade histórica. Falha de previsão é resultado negativo, não motivo para mudar a validação retrospectivamente. **Estado físico Θ inalterado. Conde indeterminado.**

A etapa posterior exige pares instrumentais, épocas e referenciais, erros/holdouts independentes, modelo termoesférico compatível com 1963, propriedades balísticas ou prior calibrado e um propagador r/v com critérios de integração/evento verificáveis. O arrasto efetivo atual não identifica Cd*A/m isoladamente.

## Reprodução no HEAD

    python3 -m unittest discover -s tests -p test_norad528_effective_drag_screen.py -v
    python3 tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/secondary
    python3 tools/norad528_effective_drag_screen.py --csv /tmp/secondary/norad_527_528_529_numeric_1963.csv --output /tmp/secondary/decay_screen.json
    cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean

O workflow específico repete download com SHA fixado, roda testes, compila Lean e arquiva JSON. Matriz base preservada; este é um suplemento científico. Não publicar no blog nem afirmar hora/local de impacto.

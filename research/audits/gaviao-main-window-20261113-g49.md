---
type: Guide
title: '🦅 G49: congelamento integral dos cenários numéricos'
description: Auditoria retrospectiva de 16 integrações, com contraprovas de contagens balanceadas na ponderação Monte Carlo sintética.
---

# G49: preservar cada cenário, não somente a soma final

**Janela auditada:** `7a579c17` (exclusivo) → `17eec4a4` (inclusivo), 16 integrações first-parent, 19 commits DAG e 2 merges convencionais. O JSON adjacente lista cada integração e marca checks históricos individuais não inspecionados como `NOT_CHECKED`.

## G49-F1: somas corretas escondiam redistribuição artificial

A PR #650 introduziu `validate_frozen_report()` para um conjunto sintético de 1,5 milhão de sorteios, com 12 cenários J2 e 25.489 aproximações de 2.000 km. A validação exigia exatamente essas somas e o SHA declarado da fonte, mas não comparava os valores *de cada cenário* a um registro previamente aprovado.

**Contraprova real de execução, com dados sintéticos alterados:** acrescer 1.000 aproximações ao cenário 0 e subtrair 1.000 ao cenário 6 preservou 25.489 no agregado e o hash de origem *declarado*, passando indevidamente. Sob hipóteses de sigma de fase 25°, sigma n-dot 0,006 rev/d² e rho 0, a frequência reponderada mudou de **1,86734821% para 1,92147907%** sem que a validação falhasse. Esse resultado não é uma probabilidade histórica de impacto.

O reparo fixa o SHA-256 do JSON canônico **integral** dos doze cenários, fonte, estados e cláusulas de integridade. Adicionadas três contraprovas: redistribuição de aproximações, redistribuição de sorteios preservando 1,5 milhão, e alteração de um campo de confiabilidade temporal. As 23 verificações Python passaram normalmente e também sob `python3 -O`. A validação do digest local não substitui auditoria externa das fontes nem confirma observação de novembro de 1963.

## Limites científicos e de CI

O modelo pondera **hipóteses** sobre um produto sintético derivado de TLE secundária, não a trajetória terminal observada do NORAD 528. Não produz posterior físico, sobrevivência atmosférica ou localização da queda. O hash local exige revisão deliberada caso se substitua legitimamente o arquivo congelado. Nenhuma adulteração histórica foi identificada. A execução local de Prek na casa G47 foi interrompida por excesso de RSS; o CI do HEAD da PR é gate obrigatório antes de merge.

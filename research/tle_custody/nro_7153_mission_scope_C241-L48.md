---
type: Guide
title: 'C241-L48: fim de missão SIGINT não é decaimento orbital'
description: 'História institucional NRO da missão 7153/veículo 2313 e exigências para observações discriminantes do 528.'
---

# C241-L48: NRO, missão 7153 e a falácia do relógio de bateria

## Achado com proveniência limitada

A história institucional do NRO, *The SIGINT Satellite Story* (Bradburn, Copley, Potts e colaboradores; redigida em 1994, versão desclassificada ampliada em fevereiro de 2016), capítulo 4, **página impressa 90**, descreve o veículo **2313**, missão **7153**, lançado em 16 de janeiro de 1963 com carga digital Group 1. Identifica a nova designação de programa **698BK** e afirma que a missão operacional durou **dois dias** devido a **falha de bateria**, embora tenha obtido dados sobre radares soviéticos.

Fontes: [PDF desclassificado](https://www.governmentattic.org/19docs/NRO-SIGINTsatStory_1994u.pdf), [página institucional NRO](https://www.nro.gov/foia-home/foia-sigint-satellite-story/), [manifesto C241-L48](nro_7153_mission_scope_C241-L48.json). Este texto foi verificado na **camada textual indexada da publicação**, mas o servidor bloqueou o download binário e a captura de página (403/406). Portanto, **não há SHA dos bytes nem inspeção visual autenticada nesta rodada**. A fonte é retrospectiva institucional, **não** telemetria de 1963. Não marcar a íntegra como preservada nem visualmente verificada.

## Identificabilidade e genealogia

O catálogo secundário associa veículo 2313/OPS 0180 ao **NORAD 527, 1963-003A**, mas o parágrafo de história **não** identifica as peças físicas 528 (1963-003B) e 529 (1963-003C) nem informa separação, época de observação, sensor ou covariância. Falha de bateria encerra operações elétricas, não a existência do veículo em órbita. Um período de dois dias redigido em prosa **não pode virar timestamp de 18/01/1963 00:00 UTC**, limite de vida orbital ou data de fragmentação.

O relógio operacional da missão, o relógio de separação de componentes e os relógios dos catálogos orbitais são variáveis distintas. Não existe nesta fonte uma equação instrumental que os conecte. Ela **não** justifica alterar a data catalogada de decaimento de 528 em novembro de 1963, nem restringir o local de queda.

Para discriminar hipóteses são necessários: log contemporâneo com época de perda de energia; documentação mecânica que mapeie peças a 528/529; observações datadas pós-encerramento com estação, quadro e erro; e registros originais de rastreio das três identidades. A mera repetição do parágrafo em sites secundários não constitui novas observações.

## Gate reproduzível

`python3 -m unittest discover -s tests -p test_nro_7153_mission_scope.py -v` e `python3 -m tools.nro_7153_mission_scope`. O verificador recusa data inferida, sensor inventado, pedigree instrumental falso e posterior sem likelihood. Estado: `historical_mcmc=NOT_RUN`, `physical_constraint_active=false` e `conde_geographic_contraction=false`. A PR #634/#641 permanece condicionada à genealogia e ao inventário físico documentado.

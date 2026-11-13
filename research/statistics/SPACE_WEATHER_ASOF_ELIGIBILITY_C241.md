---
type: Experiment
title: 'C241-P31: disponibilidade temporal dos índices usados em NRLMSISE'
description: 'Auditoria reprodutível dos insumos solares e geomagnéticos de novembro de 1963, separando reconstrução retrospectiva de validação prospectiva.'
experiment_id: C241-P31
model_ref: tools/audit_space_weather_asof.py
verification_status: DOCUMENTARY_DERIVED_NO_ORBITAL_INFERENCE
---

# 🦌 C241-P31: os vetores termosféricos não são previsões em tempo real

O [extrato C241 de clima espacial](../meteorology/space_weather_msise_inputs_1963_11_07_09.md) tem entradas verificáveis de F10.7 observado (Natural Resources Canada, [arquivo histórico](https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/F107_1947_1996.txt)) e de ap/Kp/Ap (GFZ, [dados](https://kp.gfz.de/en/data)). A [NASA CCMC](https://ccmc.gsfc.nasa.gov/models/NRLMSIS~00/) descreve os insumos do modelo NRLMSISE-00; o [código de referência](https://docs.cesm.ucar.edu/models/cesm2/config/old/cesmBbrowser/html_code/cam/msise00.F90.html) especifica F107A como média **centrada** de 81 dias e F107 como fluxo do dia anterior. São insumos retrospectivos, não observações de densidade do 528.

## Teste de disponibilidade na época

Para a avaliação **arbitrária** de 8/11/1963, 12:00 UTC, a média F107A publicada no extrato (82,265432 sfu) agrega 81 datas, de **29/09 a 18/12/1963**. Destas, **40 dias são posteriores** à avaliação. O Ap diário de 8/11 integra oito intervalos de três horas; **quatro intervalos começam a partir de 12:00**, portanto não estavam completos naquele instante. O ap e o Kp do intervalo corrente cobrem **12:00–15:00 UTC**, também indisponíveis integralmente às 12:00. A mesma geometria de indisponibilidade vale para os três exemplos artificiais 7–9/11 às 12:00.

As séries arquivadas não incluem horários históricos auditados de liberação dos índices definitivos nem do F10.7 diário anterior. Portanto **nem mesmo entradas relativas a dias anteriores ganham automaticamente o selo de disponibilidade contemporânea**. Os índices F10.7 e ap são fontes físicas diferentes; Kp, ap e Ap da GFZ representam uma família derivada comum, não três medições independentes.

O certificado [C241-P31](../constraints/C241-P31_space_weather_asof.json) fixa SHA-256 do extrato original e recomputa a janela centrada, os dados e os quatro bins futuros. O script recusa fonte alterada, média mal calculada, troca de bin e promoção indevida de status físico. O teste é reprodutível sem rede:

```sh
python3 tools/validate_1963_space_weather.py research/meteorology/space_weather_msise_inputs_1963_11_07_09.json
python3 tools/audit_space_weather_asof.py --check
python3 -m unittest discover -s tests -p test_space_weather_asof.py -v
```

## Resultado epistêmico e próxima observação discriminante

**Reconstrução histórica retrospectiva:** pode empregar índices definitivos, desde que o objetivo seja declarado e a incerteza do modelo não seja ocultada. **Predição prospectiva ou holdout temporal as-of 8/11/1963:** não pode usar esses vetores como se fossem conhecidos às 12:00 UTC. Seria preciso um arquivo de versões emitidas antes do cutoff ou um procedimento de previsão causal, com erro calibrado e covariância. O selo `NOT_AUTHORIZED` aplica-se ao *score prospectivo com estes vetores*, não proíbe investigação posterior.

Esta auditoria avança o grafo de dependências, sem atribuir época de reentrada, massa, arrasto, densidade em Conde, prior, probabilidade ou mudança na região admissível. **MCMC histórico: NOT_RUN; restrição física: CONNECTED_PENDING_CALIBRATION.** Questões relacionadas: [Castor #4](https://github.com/franklinbaldo/conde-incident/issues/4) e [Tartaruga #396](https://github.com/franklinbaldo/conde-incident/issues/396).

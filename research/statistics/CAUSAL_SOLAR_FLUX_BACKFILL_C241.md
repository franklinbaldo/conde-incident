---
type: Experiment
title: 'C241-P32: cobertura de F10.7 para uma média causal contrafactual'
description: 'Auditoria do backfill solar necessário a um preditor causal sem promover o arquivo definitivo de 1963 a dado disponível na época.'
experiment_id: C241-P32
model_ref: tools/audit_causal_flux_backfill.py
verification_status: DOCUMENTARY_DERIVED_NO_ORBITAL_INFERENCE
---

# 🦌 C241-P32: a alternativa causal também exige dados ausentes

**Pergunta falsificável:** com o [extrato histórico já documentado](../meteorology/space_weather_msise_inputs_1963_11_07_09.md), seria possível substituir a média **centrada** de 81 dias F107A (que utiliza 40 dias futuros) por uma média de 81 dias **completos anteriores** ao cutoff de 12:00 UTC? A resposta sobre cobertura dos bytes preservados é **não**. Essa média causal é uma construção de desenho experimental, **não** uma entrada equivalente à F107A prescrita para o NRLMSISE-00.

O [cabeçalho do NRLMSISE-00](https://github.com/magnific0/nrlmsise-00/blob/master/nrlmsise-00.h) descreve F107A como média centrada e F107 como o fluxo do dia anterior. O [NASA CCMC](https://ccmc.gsfc.nasa.gov/models/NRLMSIS~00/) especifica as variáveis de entrada. As observações definitivas vêm do [arquivo de F10.7 do Natural Resources Canada](https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/F107_1947_1996.txt); são uma única família documental, não sensores independentes. Os hashes das fontes estão fixados no [extrato](../meteorology/space_weather_msise_inputs_1963_11_07_09.json), e o certificado [C241-P32](../constraints/C241-P32_causal_flux_backfill.json) fixa o hash do extrato efetivamente utilizado.

## Operador candidato e cobertura

Para cada data-alvo UTC \(d\) de 7, 8 ou 9/11/1963, às 12:00 UTC, o conjunto de dados completo candidato é \(W_d=\{d-81,\ldots,d-1\}\), em dias civis UTC. O operador \(T_d=(1/81)\sum_{s\in W_d}F10.7_s\) só é **computável** se cada uma das 81 observações estiver no extrato; computabilidade, por si só, jamais implica que versões e horários de divulgação estivessem disponíveis em 1963.

| Cutoff artificial | Intervalo necessário (inclusive) | Datas presentes no extrato | Datas ausentes do extrato |
|---|---|---:|---:|
| 07/11/1963 12:00 UTC | 18/08–06/11 | 41 | 40 |
| 08/11/1963 12:00 UTC | 19/08–07/11 | 42 | 39 |
| 09/11/1963 12:00 UTC | 20/08–08/11 | 43 | 38 |

Todas as datas ausentes pertencem a **18–20/08 até 26/09/1963**, conforme o cutoff. A ausência é **do extrato limitado preservado no projeto**, não uma alegação de que o arquivo histórico completo não contenha esses dias. Um backfill verificado do arquivo completo poderia fechar a lacuna de **cobertura**; seria ainda necessário auditar o momento de publicação ou versões contemporâneas antes de declarar disponibilidade *as-of*. O experimento sintético de preenchimento no teste cobre todas as datas e confirma que o estado de elegibilidade prospectiva continua falso.

## Relações de restrição e decisão

Fonte `C241-P31` → extrato F10.7 com hash → datas observadas (unidade sfu, observada, sem escala de erro publicada no extrato) → novo operador \(T_d\) candidato → **38–40 datas de backfill necessárias** → versões históricas com instante de liberação e erro de previsão → eventual parâmetro de clima espacial causal → densidade com modelo propagador calibrado → holdout efetivamente fora do ajuste. Os três cutoffs são datas de cálculo deliberadamente escolhidas, **não horários observados do objeto 528**.

A hipótese de substituir a entrada centrada pela trailing exige calibração separada contra observações atmosféricas e demonstração de compatibilidade com um propagador; **não** é permitido inserir diretamente \(T_d\) no modelo como se fosse F107A padrão. Uma forma causal com erros quantificados também precisaria de entradas geomagnéticas historicamente disponíveis, sem usar Ap diário definitivo ou o bin corrente incompleto da auditoria P31.

**Progresso:** conectividade de dados, lacuna de cobertura e procedimento necessário explicitados. **Não** há inferência de densidade, posto de parâmetros orbitais, posterior, MCMC histórico, redução geográfica ou conclusão sobre reentrada em Conde: `NOT_RUN`; restrição física `CONNECTED_PENDING_CALIBRATION`.

## Reprodução e testes adversariais

```sh
python3 tools/audit_space_weather_asof.py --check
python3 tools/audit_causal_flux_backfill.py --check
python3 -m unittest discover -s tests -p 'test_causal_flux_backfill.py' -v
```

O teste adversarial verifica contagem exata, ausência de uso do dia corrente, erro de fuso, integridade do extrato e que preencher lacunas **não** converte automaticamente dados históricos definitivos em previsão prospectiva. Dependências apenas da biblioteca padrão Python e do módulo P31.

---
type: Guide
title: "C241-P5: 284,1520° sob hipótese de época trocada"
description: "Cruzar inversamente o RAAN legado com 527/528/529, medir controles internos e negar atribuição instrumental sem fonte."
---

# C241-P5: o ângulo que cabe em agosto, mas traz a data de outubro

**Questão falsificável (issue #15):** o RAAN legado **284,1520°**, impresso em TLE construído para o 528 com epoch `63300.61111111` (27/10/1963, 14:39:59.999904 UTC), poderia ser simplesmente o valor do mesmo espelho secundário em uma época diferente? **Não confundir isso com recuperar a origem histórica do número.** O único TLE secundário literal preservado para 528 é de 27/10/1963, 14:40:16.132512 UTC e registra **198,5261°**. Apenas 16,132608 segundos separam as datas impressas; os valores diferem circularmente por **85,6259°**. Os seis elementos completos do legado já falharam no confronto linha-a-linha C241-L8.

**Linhagem:** `C25#1`, `C179#1`, `C180#1`, `C181#1`, `C241-L1`, `C241-L4`, `C241-L8`, `C241-P4`; a matriz C001–C238 fica intocada. Vetor construído do site: [blob Git `0284f1217557b0ea891b5e51b6ac56bd13529d3f`](https://github.com/franklinbaldo/conde-incident/blob/0284f1217557b0ea891b5e51b6ac56bd13529d3f/src/lib/constants.ts), sem documento NORAD primário; par secundário [pinned 528](../tle_custody/mirror_528_1963-10-27.tle), SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. Dados numéricos do [Parquet oxzoid, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV derivado com linhas originais, SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`. Todos os 123 registros são uma **única família secundária**; 527/529 não são holdouts instrumentais independentes. O relatório NASA de 15/11/1963 só estabelece o dia catalogado de decaimento (C197#1), não horário/local.

## Resultado numericamente reproduzido

Para cada objeto, encontramos pares **consecutivos** de estados secundários cujo arco curto do RAAN contém 284,1520°, depois interpolamos *linearmente dentro do par*, em UTC. São candidatos de calendário **condicionais a essa interpolação**, não estimativas históricas de medição. A largura do intervalo é o afastamento real das épocas de catálogo; não é um intervalo de confiança de sensor.

| NORAD | Linhas que delimitam | Janela da fonte (UTC) | Único cruzamento interpolado (UTC) | Secante (°/dia) | Largura da janela (dias) |
|---|---|---|---|---:|---:|
| 527 | 2967 → 2968 | 31/07 a 27/08 | 16/08/1963 03:49:28.230881 | −1,077471 | 27,202957 |
| 528 | **2998 → 2999** | **12/08 a 16/08** | **12/08/1963 17:29:16.630658** | **−1,103181** | **3,824113** |
| 529 | 3041 → 3042 | 12/08 a 21/08 | 14/08/1963 11:43:55.844085 | −1,101718 | 9,249665 |

Na hipótese secundária, o cruzamento do 528 ocorre **75,882446 dias antes** da época estampada pelo TLE construído. O cruzamento também existe para 527 e 529. Portanto **RAAN sozinho não discrimina identidade nem restaura a época real**, e um erro de apenas 16 segundos na impressão não explica os 85,6259°.

Controle adversarial: ocultar uma época interior e interpolar entre vizinhas separadas por **no máximo 30 dias**, comparando ao baseline RAAN da vizinha temporal mais próxima. Trata-se de *interpolação retrospectiva bilateral*, **não** de previsão fora do treino. O recorte de 30 dias é regra operacional declarada, não covariância instrumental.

| NORAD | Épocas internas ocultadas | MAE interpolação (°) | MAE vizinho mais próximo (°) |
|---|---:|---:|---:|
| 527 | 8 | 0,055631 | 7,149177 |
| 528 | 42 | 0,031893 | 4,205029 |
| 529 | 49 | 0,041582 | 4,266151 |

**Antes/depois:** domínio físico admissível Θ **inalterado**. Somente sob a suposição *não autenticada* de que o legado representa o RAAN secundário 528 em outra época e de que interpolar linearmente é legítimo, o conjunto candidato de **épocas de cruzamento de catálogo** é não vazio e fica entre 12/08 13:35:30.863616 e 16/08 09:22:14.196576 UTC. Isso **não** restringe uma trajetória física real, nem salva os demais cinco elementos do TLE legado, nem localiza decaimento/impacto. Erros MAE acima são graus em relação ao próprio espelho, **não sigma**.

**Resultado negativo / desbloqueio:** nenhuma fonte primária associou 284,1520° a uma observação. Falta o documento original completo com epoch, referencial, linhas 1/2, dígitos de verificação de origem, método e incerteza de rastreamento; com ele testaríamos transformação para frame comum, identidade da peça e resíduos por sensor. Não promover filtro ao Lean 4.35.0 enquanto faltar calibração; manter `NOT_PROMOTED` e `INDETERMINATE` para Conde. Testes de software e auditoria Lean são não-regressão, não novos teoremas físicos.

## Execução

```sh
python3 -m unittest discover -s tests -p test_raan_legacy_epoch_crossing.py -v
python3 -m pip install pyarrow==21.0.0
python3 tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-p5
python3 tools/raan_legacy_epoch_crossing.py --csv /tmp/c241-p5/norad_527_528_529_numeric_1963.csv --output /tmp/c241-p5/legacy_epoch_crossings.json
cd formal && lake build && lake env lean Conde1963/CoreAxioms.lean
```

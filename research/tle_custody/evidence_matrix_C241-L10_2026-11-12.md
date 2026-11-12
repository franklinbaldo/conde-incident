---
type: Guide
title: "C241-L10: identidade catalográfica 527/528/529 e limite físico"
description: "Junção NORAD/COSPAR e data NASA reinspecionada, sem converter rótulos secundários em identificação de destroço."
---

# C241-L10: a letra do lançamento não identifica uma peça

**Ocorrência C241-L10**, complemento de [C001–C238](../evidence_matrix_C001-C238_2026-11-11.md), [C241-L1](evidence_matrix_C241-L1_2026-11-12.md) e [C241-L2](evidence_matrix_C241-L2_2026-11-12.md). Issue científica [#13](https://github.com/franklinbaldo/conde-incident/issues/13). Esta fatia independente extrai o ensaio **C241-T8** da [draft #14](https://github.com/franklinbaldo/conde-incident/pull/14).

## Documento contemporâneo e identificação

**Fonte primária documental, diretamente reinspecionada em 12/11/2026:** [NASA Satellite Situation Report de 15/11/1963, NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), **PDF página 10 (índice 9), página impressa 8**, seção *FOLLOWING TO THE DECAYED OBJECTS LIST*. A linha tipografada **1963 3B** registra **8 NOV 63** em **DECAY**. Documento contemporâneo atesta apenas a data catalogada de decaimento, **não** instante exato, coordenadas, forma da peça, motivo da classificação, telemetria ou impacto em Conde. **SHA-256 dos bytes do PDF não foi recuperado**; portanto a inspeção visual não equivale a custódia bit a bit. A NASA reproduz uma classificação de situação orbital, não é observação independente demonstrada de reentrada.

**Rótulos secundários modernos:** [itau 527](https://www.itau.magnetic-declination.com/satellite/?s=527), [itau 528](https://www.itau.magnetic-declination.com/satellite/?s=528), [itau 529](https://www.itau.magnetic-declination.com/satellite/?s=529), [KeepTrack 528](https://keeptrack.space/satellite/528), [KeepTrack 529](https://keeptrack.space/satellite/529); transcrição custodiada em [JSON](catalog_identity_527_529_2026-11-12.json). No espelho: **527 = 1963-003A / FTV 2313**; **528 = 1963-003B / FTV 2313 DEB**; **529 = 1963-003C / FTV 2313 DEB**. 527, 528 e 529 pertencem ao **mesmo identificador de lançamento** 1963-003, mas representam entradas de catálogo distintas. A etiqueta `DEB` não identifica material, massa, tamanho, componente, serial de engenharia, separação nem local terminal. Esses sites podem compartilhar catálogo de origem, **independência instrumental não demonstrada**; datas de captura são transcrições, não arquivos-fonte preservados.

**Dados secundários numéricos:** [oxzoid/space-track-tle-history, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV derivado SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`, preservando `source_row`, `epoch` UTC e `intl_designator`. Esperados 21/45/57 registros e 20/45/54 épocas distintas para 527/528/529. Quatro linhas repetidas no corpus não são quatro observações independentes. O [único par literal secundário do 528](mirror_528_1963-10-27.tle), SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`, contém `63003  B` e época `63300.61129783`: seu checksum/colunas não autenticam uma emissão original de 1963.

## Teste e interpretação

O script `tools/tle_identity_lineage_audit.py` recusa COSPAR divergente, peça trocada B/C, índices de linha duplicados, UTC inválido, inventário de fontes inesperado e promoção indevida de dependência catalográfica a medição instrumental. Saída JSON contém índice por objeto, grafia original, `source_row`, classificação e ausências explícitas. Controles de `tests/test_tle_identity_lineage_audit.py` são **sintéticos e adversariais**; somente o workflow com Parquet de SHA fixado verifica o corpus real.

**Aresta cumulativa:** `C241-L10:NORAD_COSPAR_catalog_join`, `CONNECTED_PENDING_CALIBRATION`, proveniência documental e catalográfica declarada; `measurement_sigma=null`, `physical_frame=null`, independência `NOT_ESTABLISHED`. Domínio admissível físico `NOT_COMPUTED`; predicado físico Lean 4.35.0 `NOT_PROMOTED`; simulação/holdout `NOT_RUN`. A junção documental **não** restringe numericamente a órbita, mas especifica qual dado primário precisa ser encontrado.

**Conflito preservado:** RAAN `198.5261°` é impressão do par secundário 528; `284.1520°` é vetor legado sem proveniência instrumental e segue **inativo**, jamais média dos dois. O `8 NOV 63` do relatório NASA não determina horário ou lugar de queda. **Conde: INDETERMINATE**.

**Faltantes falsificáveis:** 45 pares TLE instrumentais 528 e séries 527/529 com linhas originais, epochs, check digits, sensor, frame e covariâncias; ficha primária NRO/NASA de engenharia que associe S00528 a uma peça específica; registro que relacione 284.1520° a uma observação rastreável. A busca nesta rodada não encontrou tais registros; o negativo indica ausência **no material consultado**, não inexistência histórica.

## Reexecução

```sh
python -m unittest discover -s tests -p 'test_tle_identity_lineage_audit.py' -v
python -m pip install pyarrow==21.0.0
python tools/tle_secondary_1963_ledger.py --download --parquet /tmp/tle_1963.parquet --literal research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l10
python tools/tle_identity_lineage_audit.py --csv /tmp/c241-l10/norad_527_528_529_numeric_1963.csv --ledger research/tle_custody/catalog_identity_527_529_2026-11-12.json --pair research/tle_custody/mirror_528_1963-10-27.tle --output /tmp/c241-l10/identity_c241_l10.json
```

CI dedicado em [`tle-identity-lineage.yml`](../../.github/workflows/tle-identity-lineage.yml) executa no HEAD real e arquiva relatório JSON e CSV derivado.

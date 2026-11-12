---
type: Guide
title: "C241-P5#1: inversão condicional de RAAN legado por época secundária"
description: "Ocorrência cumulativa sem novo dado instrumental; hipótese de época trocada testada contra 527/528/529."
---

# C241-P5#1

**Documentos e dependência:** matriz original C25#1/C179#1/C180#1/C181#1, confronto de seis elementos C241-L8 e relatório [C241-P5](../constraints/C241-P5_legacy_raan_epoch_confounding.md). Origem do RAAN 284,1520°: TLE construído no código histórico do site (`src/lib/constants.ts`, blob `0284f1217557b0ea891b5e51b6ac56bd13529d3f`), **não instrumento**. Origem do RAAN 198,5261°: espelho secundário do 528, par literal SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. Fonte do extrato 1963: Parquet oxzoid rev. 4b4fb3a SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV SHA-256 `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`.

**Observável e operador:** `(NORAD, epoch UTC, RAAN em graus, source_row)` → par consecutivo contendo ângulo candidato no arco curto → época de cruzamento condicional via interpolação linear. Três objetos passam, portanto RAAN isolado não escolhe uma identificação; dados e pressupostos permanecem de mesma linhagem secundária. Controle bilateral leave-one-out versus persistência por vizinho, sem interpretação de σ nem independência instrumental.

**Resultado:** cruzamento catalográfico 528 entre 12 e 16/08/1963, não em 27/10/1963 (época impressa no legado); hipótese de errata de 16 segundos não sustenta diferença circular de 85,6259°. Nenhum TLE primário, frame e incerteza recuperados, nenhuma observação nova da reentrada, Θ físico **inalterado**, Lean sem novo filtro, local de reentrada **indeterminado**. Estado `CONNECTED_PENDING_CALIBRATION`. Reexecutar script e testes com CSV pinado, CI SHA exato, antes de usar como contexto investigativo.

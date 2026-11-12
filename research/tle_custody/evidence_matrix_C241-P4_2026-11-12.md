---
type: Guide
title: "C241-P4#1: controle pareado de J2 com deriva contra quadrático"
description: "Ocorrência cumulativa de comparação numérica dependente do mesmo espelho orbital, sem restrição física nova."
---

# C241-P4#1

**Fonte e dependência:** C25#1/C179#1/C180#1/C181#1/C241-P1#1/C241-P2#1/C241-P3#1/C241-T15#1, mesmo [Parquet secundário](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. As 35 épocas de avaliação não equivalem a 35 medições independentes. O espelho não autentica observações instrumentais, referencial ou precisão.

**Conexão:** (epoch UTC, NORAD, RAAN secundário em graus, source_rows) → split FIT/validação/avaliação congelado → P3_J2_fitfield_pred e T15_quadratic_fitonly_pred (graus) → erro circular absoluto em graus por época → diferença pareada MAE(P3) − MAE(quadrático) por objeto. O comparador não ajusta coeficientes. Estado CONNECTED_PENDING_CALIBRATION.

**Teste falsificável:** comparar P3 com quadrático nas mesmas épocas dos 527/528/529 e preservar 527 como contraprova da superioridade universal. [C241-P4](../constraints/C241-P4_paired_J2_drift_vs_quadratic.md) contém protocolo, tabela anterior e comandos; o artefato de CI expõe resultados completos por época.

**Formalização:** nenhuma nova restrição Lean ativada; domínio físico Theta inalterado, não-vazio não reavaliado. Build e auditoria de axiomas representam apenas não-regressão. Para filtro físico faltam rastreamento original com época/frame/checksum, incertezas/covariâncias e holdout instrumental independente. Nenhuma hora/posição de queda inferida.

---
type: Guide
title: "C241-P3: elementos médios ajustados somente antes do corte"
description: "Ocorrência cumulativa de comparação J2+deriva FIT-only contra P2; não observação nova."
---

# Ocorrência C241-P3#1

**Família:** C25#1, C179#1, C180#1, C181#1, C241-L4#1, C241-P1#1, C241-P2#1. **Linhagem:** um espelho moderno de catálogo Space-Track, [Parquet rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Conversão CSV com hash e índices em [C241-P3](../constraints/C241-P3_fitfield_j2_forward_holdout.md).

**Variáveis e operador:** RAAN em graus confrontado com integral de J2 e extrapolação fit-only de n (rev/dia), i (graus), e (adimensional), epoch UTC; erros circulares em graus. É inferência de catálogo, não medição independente. CONNECTED_PENDING_CALIBRATION.

**Teste:** MAE 527 0,605430° vs J2 estático 0,511195°, pior; 528 0,133510° vs 0,679537°, melhor; 529 0,477634° vs 1,137675°, melhor. O controle 527 rejeita ganho universal. Nenhum novo fato instrumental é gerado.

**Formalização:** nenhuma restrição orbital Lean ativada. Antes/depois Θ inalterado e não quantificado; não-vazio não demonstrado novamente; dados primários NORAD 527/528/529 com epoch/frame/checksum, erro e holdout externo ainda ausentes.

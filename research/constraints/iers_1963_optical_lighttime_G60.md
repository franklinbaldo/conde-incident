---
type: Guide
title: 'CASTOR-G60: sensibilidade óptica ao tempo de luz com velocidade GCRS'
description: 'Operador condicional de retardo luminoso, com solução analítica, fonte IERS autenticada, ocultação terrestre e testes adversariais; sem inferência histórica.'
---

# CASTOR-G60: o estado recebido não é o estado que emitiu a luz

**Pergunta física:** a direção topocêntrica instantânea G53 omite um efeito angular mesmo com posição, velocidade, estação e EOP exatos. Um fóton emitido pelo satélite alcança a estação após tempo positivo `τ`. Se o alvo se move com velocidade `v` no intervalo curto, a posição emissora difere da posição na época de recepção.

## Contrato condicional

Em **GCRS**, com posição receptora `s` fixa no intervalo e estado TEME 6D do objeto na época UTC convertido para `r,v` por G50 (incluindo `Rdot*r`), o teste assume `r_emissão = r - vτ` e resolve:

`cτ = |r - vτ - s|`, com `c = 299792,458 km/s`.

Para `ρ = |r-s| > 0`, `v_r=((r-s)·v)/ρ`, e `|v|<c`, a raiz positiva, numericamente estável, é

`τ = ρ / (v_r + √(c² - |v|² + v_r²))`.

O código `tools/iers_1963_optical_lighttime.py` devolve `τ`, posição emissora aproximada, deslocamento angular geométrico→retardado em segundos de arco, resíduo de fechamento da equação e vetores unitários. A variante `sensitivity_from_teme` verifica **bytes IERS 1963 originais**, UT1 e orientação e recusa raios através do elipsoide WGS84 nas duas geometrias. Não converte por hipótese registros de observação histórica em GCRS.

Um controle numérico sintético com `ρ=1000 km` e `v=7 km/s` puramente transversal produz retardo de cerca de `0,00333564 s` e deslocamento angular **aproximadamente 4,8 segundos de arco**, não zero. Velocidade radial pura altera `τ`, mas não a direção; velocidade nula recupera `τ=ρ/c`. O efeito de primeira ordem para velocidade transversal é aproximadamente `|v_perp|/c`, não cresce automaticamente com distância. Isso é uma escala física do cenário, **não** sigma histórica da câmera.

## Limites de interpretação e validação

O modelo linear não é propagador orbital. Não inclui aceleração durante o trânsito do fóton, movimento terrestre durante o trânsito, aberração óptica do observador, efeitos relativísticos, refratividade, FK4/B1950, survey histórico da estação nem calibração do relógio. A interseção com WGS84 usa a superfície terrestre na época de recepção, não um modelo espaço-temporal completo de rotação durante a propagação. O estado TEME 6D é fornecido pelo chamador; o operador não autentica sua origem instrumental. Para observação real, o comparador G54 exige uma cadeia de extração, procedência, quadro e época independentes. **G60 não substitui essa cadeia nem habilita comparação direta de filme FK4 com GCRS**.

Status epistemológico: `CONDITIONAL_NUMERICAL_SENSITIVITY_ONLY`, `historical_holdout=NOT_RUN`; não determina instante, coordenada nem probabilidade de queda do 528 em Conde.

## Reprodução

Usar bytes IERS 1963 de `https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63`; SHA-256 esperado `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`. Com `pyerfa` e `numpy`, executar:

```shell
IERS_1963_SOURCE=/tmp/iers-1963-eop.bin python3 -m unittest discover -s tests -p 'test_iers_1963_optical.py' -v
```

A suíte executada no workflow IERS testa seis casos novos: solução analítica radial/estática, correção transversal, invariância sob rotação e translação, rejeição de entradas não físicas, acoplamento TEME/GCRS com veto WGS84 e rejeição de fonte IERS adulterada. A validação por teste sintético não permite inferir observação instrumentada em 1963.

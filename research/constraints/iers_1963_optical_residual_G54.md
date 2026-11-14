---
type: Guide
title: 'CASTOR-G54: comparação angular GCRS condicional com erro documental explícito'
description: 'Resíduo topocêntrico e Mahalanobis em plano tangente para dados geométricos GCRS de mesma época e estação; recusa FK4/B1950 sem conversão.'
---

# CASTOR-G54: comparar sem fabricar uma observação histórica

O operador `tools/iers_1963_optical_residual.py` recebe (1) a predição produzida pelo G53, (2) um registro de observação que declare RA/Dec, época UTC exata, estação WGS84 do cenário, quadro **GCRS geométrico instantâneo**, covariância de erro instrumental em arcseg² e identidade/proveniência, e (3) os **bytes originais** do documento cujo SHA-256 consta no registro. Sem integridade documental, rejeita. Documentos primários continuam necessários para qualificar a independência da evidência.

No ponto previsto, constrói eixos leste/norte ortogonais e projeta a direção observada gnomonicamente. Isso evita subtrair RA bruta no salto 0°/360° e explicita que o resíduo é deslocamento angular **no plano tangente**. Rejeita separação angular ≥5°, pois fora desse domínio a linearização de erro não está automaticamente justificada. A covariância instrumental **positiva definida** (arcseg²) soma-se, após conversão, à covariância de estado (rad²) **semidefinida positiva** do G53, se fornecida. A distância quadrática de Mahalanobis é calculada por fatoração de Cholesky, sem confundir covariância de estado com calibração instrumental.

**Controles de não inferência:** exige coincidência literal de época UTC e coordenadas da estação; não aceita FK4/B1950, ICRS, observação aparente, refração, relógio não calibrado ou transformação de catálogo presumida. Mesmo uma comparação numérica produz `comparison_status=CONDITIONAL_GEOMETRIC_ONLY`, `historical_holdout=NOT_RUN` e `impact_inference=NOT_SUPPORTED`. O SHA autenticado prova identidade dos bytes fornecidos, não autoria ou autenticidade histórica da observação. Os testes usam geometrias e documentos **sintéticos declarados**, mais bytes IERS originais autenticados; não há observação instrumental do 527/528/529.

## Reprodução

Baixar a série original IERS `https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63` e confirmar SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`. Executar `IERS_1963_SOURCE=/tmp/iers-1963-eop.bin python -m unittest discover -s tests -p test_iers_1963_optical_residual.py -v`. G53 mantém o campo de estação numérico na saída para impedir associação acidental com outra posição. O workflow IERS executa os testes G46–G54 no HEAD da PR, com fonte original.

**Para ativar validação histórica posteriormente:** recuperar ficha instrumental original com identificador 527/528/529, estação em 1963 com datum/época, escala de tempo e correção de relógio, quadro de ângulos observado e transformação documentada (por exemplo FK4/B1950→GCRS geométrico), incertezas instrumentais e bytes preservados. Não reinterpretar um valor de catálogo como sensor independente.

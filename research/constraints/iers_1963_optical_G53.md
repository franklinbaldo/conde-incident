---
type: Guide
title: 'CASTOR-G53: observável óptico topocêntrico condicional com EOP 1963'
description: 'Conversão TEME e estação WGS84 de cenário para direção GCRS, parallax e covariância angular sem inventar fotometria histórica.'
---

# CASTOR-G53: o que o instrumento veria, se estação e estado fossem conhecidos

O contrato G50–G52 permite converter estado TEME para GCRS usando matrizes terrestres derivadas da série IERS retrospectiva. Agora `tools/iers_1963_optical.py` computa geometria **topocêntrica**: uma estação fornecida por longitude geodésica leste, latitude norte e altura elipsoidal em metros é transformada do elipsoide WGS84 para ITRS; o satélite TEME e a estação ITRS são transformados para GCRS na **mesma UTC**. A diferença vetorial fornece a direção unitária, distância, ascensão reta/declinação geométricas GCRS e elevação local. Uma estação diferente altera a direção por paralaxe. O cálculo exige os bytes originais do IERS 1963 e autenticação dos registros derivados, não apenas um hash declarativo.

Para matriz 6D especificada de posição/velocidade TEME, o Jacobiano de pequenos deslocamentos angulares no plano tangente leste/norte é `H = [eᵀR/ρ,0; nᵀR/ρ,0]`; a covariância angular de **estado**, em rad², é `H C Hᵀ`. A covariância passa pelo validador de simetria e PSD G52. A componente velocidade não entra diretamente numa direção instantânea na mesma época; incertezas de época requerem propagação e calibração de relógio separadas. Nenhum erro instrumental foi estimado. Foram testados ortonormalidade angular por diferenças finitas, polos terrestres WGS84, distância/range, paralaxe, elevação e covariância isotrópica, inclusive fontes adulteradas.

**Fronteiras:** WGS84 é convenção moderna para **estação fictícia fornecida**, não pesquisa de localização/altura/datum de uma estação SAO em 1963. A direção GCRS geométrica e instantânea NÃO equivale à RA/Dec FK4 equinócio 1950, ângulo aparente de filme, observação de radar ou sensor de 1963. Faltam precessão/correção FK4, calibração de A.1→UTC, refração/aberrração, tempo de luz, estação com proveniência, observação e erro instrumental independente. Sem esses insumos, `historical_holdout=NOT_RUN`, localização/hora/probabilidade de queda **não demonstradas**.

**Reprodução:** baixar `https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63`, verificar SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264` e executar `IERS_1963_SOURCE=/tmp/iers-1963-eop.bin python -m unittest discover -s tests -p test_iers_1963_optical.py -v`. Comando CLI requer estação e estado TEME explícitos; não usa defaults geográficos. Vincula o contrato angular de `src/lib/orbitOpticalHoldout.ts` à geometria histórica, mas ainda **não** autoriza passar observações FK4 ao validador como se fossem GCRS.

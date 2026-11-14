---
type: Guide
title: 'CASTOR-G61: Jacobiana 6D implícita do tempo de luz'
description: 'Linearização condicional da direção óptica retardada G60 com transporte TEME→GCRS da covariância G52 e testes por diferenças finitas.'
---

# G61: tempo de luz e incerteza orbital são acoplados

A direção retardada do operador G60 depende do tempo de emissão, que por sua vez depende das seis componentes do estado orbital. Assim, usar a Jacobiana instantânea G53 para propagar uma covariância até a direção óptica retardada omitiria termos físicos.

## Modelo e fronteiras

Se p = r - v τ - s, n = p / |p| e c τ = |p|, com posição r, velocidade v em GCRS no instante de recepção e estação s fixa durante o intervalo, então:

- dτ = n · (dr - τ dv) / (c + n · v).
- dn/dr = (I - nnᵀ) (I - vnᵀ / (c+n·v)) / |p|.
- dn/dv = (I - nnᵀ) (-τI + τvnᵀ / (c+n·v)) / |p|.

A Jacobiana 2 × 6 resulta de projetar dn numa base ortonormal tangente, documentada como base arbitrária estável, não como RA/Dec, FK4 nem coordenada de detector. A covariância angular é H C Hᵀ apenas se C for fornecida como matriz 6 × 6 e validada pelo contrato G52 de semidefinição positiva. Posições são km, velocidades km/s e intervalo segundos.

O script tools/iers_1963_optical_lighttime_jacobian.py acrescenta dois operadores puros: a linearização no quadro GCRS e uma variante com estado/covariância TEME. A segunda usa a matriz G50 completa [R,0; dR/dt,R], verifica os bytes originais IERS 1963 e o veto WGS84 G59 de visibilidade da geometria G60. Não introduz nenhuma observação ou sigma instrumental.

## Testes e interpretação

Os testes G61 contrastam seis colunas analíticas com diferenças finitas da raiz de tempo de luz independentemente recalculada, verificam o limite estacionário, rejeição de matriz de covariância inválida, transporte TEME de covariância e adulteração da fonte IERS. Reproduzir com bytes previamente autenticados por G46/G49:

IERS_1963_SOURCE=/tmp/iers-1963-eop.bin uv run --no-project --with numpy --with pyerfa python -m unittest discover -s tests -p test_iers_1963_optical.py

Ainda são omissões explícitas: aceleração orbital durante o percurso do fóton, movimento da estação nesse percurso, aberração, refração, calibração horária, FK4/B1950, survey histórico e erros de fonte de estado. Covariância **do estado fornecida** não é incerteza **instrumental identificada**. A proveniência IERS autenticada não autentica os NORAD 527/528/529. Holdout histórico permanece NOT_RUN, sem hora, coordenada nem probabilidade de queda.

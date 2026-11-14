---
type: Guide
title: 'CASTOR-G64: relógios correlacionados na comparação óptica'
description: 'Covariância temporal de duas observações na mesma base tangente, sem dados históricos inventados.'
---

# G64: o relógio pertence ao modelo da observação

Duas direções de câmeras diferentes não têm necessariamente erros de tempo independentes. O operador de pares em tools/iers_1963_clock_covariance.py recebe taxas tangenciais completas u_A e u_B em rad/s, na **mesma base tangente GCRS fixa**, e uma matriz de covariância de relógios C_t 2x2 em s². Calcula C_clock = J C_t Jᵀ, com J de dimensões 4x2, e o contraste de duas direções pelo operador D = [I,-I]. A covariância do contraste é D C_clock Dᵀ.

Sem C_t declarada, devolve null, não sigma=0. Matrizes não simétricas, variâncias negativas, correlação maior que um e valores não finitos são rejeitados. A saída é apenas a componente de **incerteza de relógio**: nenhuma soma com erros orbitais ou astrométricos pode ser justificada sem examinar covariâncias cruzadas. As taxas u devem vir de um preditor completo com orientação terrestre, movimento da estação e tempo de luz, e ter convergência/validade no intervalo temporal de interesse; não são derivadas automaticamente aqui.

**Contraprova sintética:** taxa de 0,004 rad/s e desvio temporal de 10 ms correspondem a 8,25 arcsec por direção. Dois relógios independentes iguais dão aproximadamente 11,67 arcsec na diferença; um erro perfeitamente comum com taxas iguais cancela; com taxas opostas pode amplificar para aproximadamente 16,50 arcsec. Nenhum desses números é a precisão de uma câmera Baker–Nunn em 1963.

**Requisitos para ativar o holdout histórico 527/528/529:** fichas instrumentais originais com identidade do alvo, UTC e calibração temporal, geodesia das estações, redução/referencial astrométrico, matriz de erros e genealogia de processamento. Datas de boletins não são épocas instrumentais. Até essa aquisição, historical_holdout=NOT_RUN, parâmetros históricos sem restrição nova e nenhuma hora/local de impacto inferido.

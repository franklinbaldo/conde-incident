---
type: Guide
title: 'CASTOR-G63: sensibilidade do tempo de luz à aceleração central'
description: 'Contraprova quantitativa da omissão de aceleração orbital no operador G60, sob cenário local de curta duração.'
---

# G63: um erro de modelo mensurável não é uma incerteza histórica

O operador G60 usa movimento retilíneo a velocidade GCRS constante durante a viagem da luz. G63 compara essa hipótese com a expansão local quadrática \(\mathbf r(t-\tau)=\mathbf r(t)-\mathbf v(t)\tau+\tfrac12\mathbf a(t)\tau^2\), na qual \(\mathbf a(t)=-GM\mathbf r/|\mathbf r|^3\), e resolve \(c\tau=|\mathbf r(t-\tau)-\mathbf s(t)|\). A estação é mantida no instante de recepção, como em G60.

**Unidades:** posição km, velocidade km/s, aceleração km/s², GM km³/s², tempo s, deslocamento m e diferença angular arcsec. GM nominal declarado: 398600,4418 km³/s². Cenários de velocidade superior a 20 km/s, tempo de luz superior a 0,2 s ou posição dentro do raio mínimo terrestre não são admissíveis ao diagnóstico local.

Na geometria sintética \(\mathbf r=(7000,2000,0)\) km, \(\mathbf v=(0,7{,}5,0)\) km/s, \(\mathbf s=(6378{,}137,0,0)\) km, a diferença da direção retardada calculada com e sem aceleração central é da ordem de **10⁻⁵ arcsec** e o deslocamento quadrático é submilimétrico. Esses valores **não** são precisão instrumental nem limites globais para J2, arrasto ou erros da órbita. Testes com GM=0, geometria radial, resíduos de raiz e entradas inválidas impedem confundir consistência interna com medição de 1963.

O resultado é deliberadamente *SYNTHETIC_LOCAL_TAYLOR_SENSITIVITY_ONLY*. Sem registros instrumentais 527/528/529 com estação, UTC, quadro, identificação e covariância, **holdout=NOT_RUN**, sem atualização de Θ, hora ou local de queda. O próximo avanço mais valioso é recuperar observações originais, não multiplicar correções submilimétricas.

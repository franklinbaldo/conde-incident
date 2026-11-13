---
type: Experiment
title: "C241-P28: contraste de altitudes e identificabilidade da escala atmosférica"
description: "Desenho observacional sintético de arrasto com amplitude, coeficientes balísticos e altura de escala desconhecidos, sem inferência histórica."
experiment_id: C241-P28
model_ref: src/lib/orbitPhysics.ts
inputs_ref: tests/orbitDensityShapeDesign.test.mjs
verification_status: SYNTHETIC_CONDITIONAL_TEST
---

# C241-P28. Que observação pode distinguir a forma vertical da atmosfera?

## Contrato condicional

No arrasto de `src/lib/orbitPhysics.ts`, suponha `rho(h,t) = A * rho0 * q(t) * exp(-(h-h0)/H)`, com `A > 0`, `H > 0`, `rho0 > 0` conhecida por CONVENÇÃO do modelo, e `q(t) > 0` conhecida e calibrada. Cada corpo `j` tem `B_j=Cd*A_area/m > 0` **constante** durante as medições. São hipóteses para desenho experimental, não propriedades autenticadas dos objetos 527/528/529.

Se o estado completo e a **aceleração de arrasto isolada** fossem medidos na mesma época/referencial, defina `z_jk = ln(||a_drag||/[500 * ||v_rel||² * q(t) * rho0])`. Pela implementação, `z_jk = ln(A) + ln(B_j) - (h_jk-h0)/H`. Os cinco incógnitos do desenho são `ln A`, três `ln B_j` e `gamma=1/H`.

Duas alturas distintas para **o mesmo objeto** permitem `gamma=-(z_j2-z_j1)/(h_j2-h_j1)`, pois amplitude e `B_j` cancelam. A separação de alturas influencia a precisão: para erros nos dois `z` independentes de variância `sigma_z²`, `sd(gamma)=sqrt(2)*sigma_z/|delta_h|`. Este é um limite de propagação linear CONDICIONAL, não um erro estimado de 1963. Se `delta_h=0`, a altura de escala não se identifica. Variabilidade não calibrada de `q(t)` ou de `B_j` destrói a identificação.

O posto algébrico do operador de dados idealizados é: três objetos em uma altura cada, **3/5**; acrescentar outra altura do 529, **4/5**; acrescentar calibração independente de `B_527`, **5/5**. Somente calibrar `B_527` sem segunda altura deixa **4/5**. O último grau de liberdade antes da calibração é o gauge de amplitude da [C241-P27](DRAG_DENSITY_SCALE_GAUGE_C241.md).

**Controle negativo:** ainda que existam duas alturas e `B_527` calibrado, observações somente de 527 e 529 deixam `B_528` indeterminado: **4/5**. Um dado próprio do 528 com observável de arrasto suficiente seria necessário para identificar seu coeficiente neste desenho. Isso não significa que tal dado já exista.

## Reprodutibilidade, dependências e próximos testes

`node --test tests/orbitDensityShapeDesign.test.mjs` executa o **mesmo** `dragAccelerationKmS2` do propagador J2/arrasto, usando estados, densidade e coeficientes explicitamente sintéticos. Verifica contraste com épocas distintas, gauge, postos, alternativa de `H` indistinguível quando só há uma altitude por objeto e ausência de informação de `B_528` nos controles. Os postos são de uma matriz idealizada de acelerômetros/estimativas de arrasto, **não** do operador de rastreamento angular/TLE real.

No grafo cumulativo, vincular `rho_amplitude_A`, `density_scale_gamma`, `ballistic_j` e `state_j(t)` ao observável candidato `a_drag_j(t)`, que depende de `rho * B_j * ||v_rel||²`. Observações NASA SSR são compiladas, sem épocas instrumentais, estados independentes calibrados nem medidas de aceleração de arrasto. Fontes e pendências: [NASA NTRS 19630012130](https://ntrs.nasa.gov/citations/19630012130), [origem do operador #4](https://github.com/franklinbaldo/conde-incident/issues/4), [dados instrumentais #396](https://github.com/franklinbaldo/conde-incident/issues/396), [C241-P27](DRAG_DENSITY_SCALE_GAUGE_C241.md).

Status: `active_constraint=false`; `historical_fit=NOT_RUN`; `historical_mcmc=NOT_RUN`; `historical_domain_reduction=NOT_EVALUABLE`; `claim_about_Conde=NOT_SUPPORTED`. Para ativar: recuperar efemérides de observação com épocas/quadros, separação física de arrasto versus J2, massa/área/atitude ou densidade independentes, covariâncias, seleção e validação em holdouts. Sem isso, nada foi provado sobre data ou local de reentrada do 528.

---
type: Guide
title: 'CASTOR-G50: conversão TEME, ITRS e GCRS com velocidades e covariâncias'
description: 'Operador condicional G50 de transformação de estado SGP4/TEME, com UT1 e movimento polar retrospectivos autenticados para novembro de 1963.'
---

# CASTOR-G50: TEME não é GCRS

**Problema:** as matrizes G48/G49 transformam GCRS→ITRS, mas SGP4 entrega TEME. Usar a matriz GCRS diretamente em TEME gera coordenadas terrestres equivocadas, mesmo com EOP corretos. De forma análoga, rodar apenas a posição e aplicar a mesma rotação à velocidade ignora a rotação terrestre, deslocamento da ordem de 0,5 km/s para raio de 7.000 km.

**Solução condicional:** `tools/iers_1963_teme.py` implementa TEME→PEF por GMST82 calculado em UT1 com o operador SOFA/ERFA `gmst82`. PEF→ITRS usa `pom00(xp,yp,s')`, com `s'=sp00(TT)`, explicitamente a convenção SOFA para movimento polar. Este último termo não é exatamente a prescrição antiga com `s'=0` usada em alguns códigos Vallado. A diferença deve ser tratada como **dependência de convenção**, não como precisão instrumental adquirida.

A transformação TEME→GCRS é composta por `(GCRS→ITRS)^T @ (TEME→ITRS)`, usando a mesma época UTC canônica, a matriz IAU2000A G49 e os dados IERS x/y e UT1−TAI (deriva pré-1972 BIPM). Isto define uma **ponte nominal compatível com a convenção escolhida**; não prova identidade TEME/ECI de outro propagador. Não aplicar a estados RK4/J2 rotulados apenas como ECI sem definição expressa de referencial.

**Velocidade:** para destino `F`, `r_F=Rr_T`, `v_F=Rv_T+Rdot r_T`, `Rdot=(R(t+1s)-R(t−1s))/2s`, avaliando toda a cadeia de EOP/UT1/TT em cada instante. O delta central exige UTC estritamente dentro de 7 nov. 00h a 9 nov. 00h. O Jacobiano 6D `J=[[R,0],[Rdot,R]]` permite `C_F=J C_T Jᵀ` somente quando `C_T` real é fornecida, simétrica e sem autovalores negativos significativos. Nenhuma matriz de covariância instrumental foi recuperada.

**Proveniência:** exige-se arquivo original completo [IERS C04 1963](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63), SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`; os registros G46/G47 são reconstruídos dos bytes antes de qualquer `transform_state`. UTC anterior a 1972 segue [BIPM histórico](https://www.bipm.org/documents/20126/59466374/9_Table2_TAR20.pdf/713645fb-e266-6304-1375-d906d14785d7). Referências de convenção: [Vallado/Brahe TEME](https://docs.brahe.space/latest/learn/frames/teme.html), [SOFA GMST82](https://www.iausofa.org/), [SatKit frame transforms](https://satkit.dev/api/frametransform/).

**Testes G50:** reprodução independente da expressão polinomial `gstime` de Vallado; sete âncoras internas; ortogonalidade, composição, determinante +1; rotação cinemática efetiva com ~0,51 km/s para um ponto TEME parado a 7.000 km; diferença central direta de posições com velocidade própria; transformação 6D reversível de uma covariância **sintética**; recusa de fonte adulterada, EOP falsificado, timestamp sem escala inequívoca, extrapolação, componentes não finitas e covariâncias inválidas. Um teste com 1 s de diferença central incorpora erro de truncamento de ordem `dt²`, não deve exigir identidade exata com a velocidade instantânea.

**Reproduzir:** instalar `pyerfa==2.0.1.5`; obter o arquivo anual original e verificar SHA. Executar `python3 tools/iers_1963_teme.py --source /tmp/iers-1963-eop.bin --check` e `IERS_1963_SOURCE=/tmp/iers-1963-eop.bin python3 -m unittest discover -s tests -p 'test_iers_1963_teme.py' -v`. O workflow `iers-eop-1963.yml` executa os dois comandos no HEAD da PR.

**Limitações:** EOP de 1963 são valores retrospectivos suavizados, interpolação linear não representa resolução intradiária instrumental; dX/dY e sigma de enquadramento permanecem ausentes. O relatório CLI usa um vetor **sintético** `[7000,0,0]` km e `[0,7.5,0]` km/s, não a trajetória de NORAD 527/528/529. Nenhum holdout instrumental 527/529 foi realizado. Não há hora, coordenadas, probabilidade de queda ou conclusão sobre o evento de Conde.

**Próxima evidência decisiva:** recuperar estados ou ângulos observados com UTC, estação, referencial, incerteza e custódia; só então confrontar esta ponte nominal com dados orbitais em holdout cego.


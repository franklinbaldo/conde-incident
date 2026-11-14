---
type: Guide
title: 'CASTOR-G52: teste de covariância 6D imune a escalas heterogêneas'
description: 'Contraprovas de simetria e PSD na transformação TEME, com limites de validade histórica.'
---

# CASTOR-G52: covariância não pode ser aprovada pela maior variância

A conversão G50 de covariância TEME→ITRS/GCRS usa o Jacobiano 6D `J=[[R,0],[Rdot,R]]`. Antes de transportar uma matriz 6×6 de **km², km²/s e km²/s²**, é necessário exigir simetria e semidefinição positiva (PSD). O teste anterior aplicava à menor autovalor a tolerância `-1e-11 × max(1, norm(C))`: uma única variância posicional de `10^12 km²` produzia margem `-10`, capaz de aprovar uma variância de velocidade explicitamente negativa (`-10^-7 km²/s²`). Também tolerava um bloco de correlação assimétrico porque a margem de simetria dependia da maior entrada de toda a matriz.

A correção rejeita variâncias marginais negativas, exige simetria por entrada (tolerância relativa `1e-12`, sem tolerância absoluta global), rejeita covariâncias cruzadas envolvendo uma variável de variância zero e verifica os autovalores de uma **matriz de correlação adimensional**, normalizada pelos desvios-padrão das variáveis de variância positiva. O limite numérico `-1e-12` vale apenas para ruído de arredondamento da matriz de correlação. Não é um ajuste de incerteza histórica nem autoriza truncar autovalores negativos do dado original.

## Contraprovas G52

1. `diag([1e12, .01, .01, 1e-8, 1e-8, -1e-7])`: antes podia ser aceita; agora é recusada por marginal negativa.
2. Matriz com marginal `1e12 km²` e entradas assimétricas `C[3,4]=1e-5`, `C[4,3]=0`: antes podia ser aceita pela tolerância global; agora rejeitada.
3. `C[3,4]=C[4,3]=2e-8` com `C[3,3]=C[4,4]=1e-8`: correlação 2, PSD impossível; não permitir que a variância de `1e12` esconda o autovalor negativo.
4. Uma variável de variância zero com termo cruzado não nulo é recusada. Caso PSD singular com correlação exatamente 1 e escalas de `1e12` a `1e-18` é aceito.

**Testes:** `IERS_1963_SOURCE=<arquivo original> python -m unittest discover -s tests -p test_iers_1963_teme.py -v`; suíte G46–G52 no CI de replay. Fonte de dados inalterada: [IERS C04 1963](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63), SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`.

**Limites:** as matrizes dos testes são sintéticas; este gate valida propriedades algébricas de covariâncias declaradas, não inventa medidas nem distribuições de erro para os NORAD 527/529. A orientação terrestre permanece retrospectiva. Holdouts históricos `NOT_RUN`; não há inferência nova de hora/local/probabilidade de queda em Conde. O dado instrumental primário, sua calibração e matriz de erros continuam necessários.

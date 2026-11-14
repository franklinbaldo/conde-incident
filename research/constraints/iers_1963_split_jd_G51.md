---
type: Guide
title: 'CASTOR-G51: precisão subsegundo e derivada por segundo SI nos referenciais de 1963'
description: 'Auditoria numérica de JD fracionária nos quadros G48–G50 com fonte IERS autenticada, contraprovas e limites.'
---

# CASTOR-G51: a precisão escondida na data juliana

**Resultado:** corrigimos duas convenções numéricas na cadeia retrospectiva G48→G49→G50. (1) O par de argumentos SOFA/ERFA deve conservar o **dia MJD inteiro no primeiro JD** e a **fração do dia no segundo**, em vez de converter `38341.fração` para `float` antes da chamada. (2) Uma derivada de orientação em 1963, para transportar uma velocidade SGP4 em km/s por segundo SI, deve dividir pelo intervalo **TAI**, não apenas pela diferença dos rótulos UTC pré-1972.

**Fonte e método:** [IERS 1963 EOP C04_05](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63), arquivo original SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`, **365 registros** autenticados pelo código G49. API [SOFA e precisão de duas partes Julian Date](https://juliaastro.org/SOFA/stable/api/precession/) recomenda a separação data/hora para minimizar perda de dígitos. Os offsets históricos G47 do BIPM/IERS usam `TAI-UTC = constante + (MJD - 37665) × 0,0011232 s` entre novembro e dezembro de 1963. Não há extrapolação entre épocas ou calibração a partir de objeto orbital.

**Contraprova repetível (apenas geometria sintética):** em `1963-11-08T12:00:00Z`, ponto TEME fixo `[7000, 0, 0] km`, velocidade TEME zero e orientação IERS autenticada, comparar a magnitude da velocidade ITRS associada a `Rdot × r` para diferenças centrais de ±0,5 s e ±1 s. O cálculo anterior diferia cerca de **3,2×10⁻⁷ km/s** entre passos, enquanto o cálculo em partes separadas difere cerca de **6,4×10⁻¹⁰ km/s** (mais de 500 vezes menor). O erro antigo provinha do arredondamento de `38341.fração` como uma única grande mantissa `float`, amplificado pela diferenciação. Esses números são diagnósticos de *sensibilidade numérica*, **não** estimativas de erro da orientação histórica.

**Escala de tempo física:** `d(TAI)/d(UTC_rótulo) = 1 + 0,0011232/86400 ≈ 1,000000013`. Para `r=7000 km` e `|Rdot×r|≈0,510448 km/s`, a diferença entre derivada por rótulo UTC e derivada por segundo TAI é de cerca de **6,64×10⁻⁹ km/s**, isto é, **0,00664 mm/s**. A mudança é pequena mas tem sinal e origem rastreáveis. A convenção SI precisa acompanhar o Jacobiano de covariância 6D para não misturar unidades cinemáticas. Derivadas são diferenças centrais da cadeia nominal e não um certificado de erro global.

**Testes adversariais:** validação contra chamada SOFA/ERFA independente da representação JD fracionária em época de microssegundos, comparação 0,5 s vs 1 s para rejeitar instabilidade de 0,32 mm/s, reconstrução do denominador TAI físico, verificação G48/G49 em 00h, reexecução de todos os testes G46–G50 e replay de fonte. `iers_1963_intraday_G49.json` foi refeito deterministicamente dos mesmos bytes oficiais, sem alterar épocas, fontes ou classificação epistêmica. O limite de 20 KB por arquivo permanece obrigatório.

**Limite epistemológico:** melhora computacional do tratamento temporal, não achado histórico. IERS C04 de 1963 é reconstrução retrospectiva, não observa os satélites 527/528/529. A transformação TEME de G50 continua condicional, com dX/dY e erros de modelo não identificados. Não se obtiveram observações instrumentais independentes, órbita histórica aferida, covariância calibrada, local/hora/probabilidade de reentrada em Conde; holdouts 527/529 = `NOT_RUN`.

**Próxima coleta:** dados ópticos/radar com designação inequívoca de objeto, estação, registro original, UTC/TAI e referencial, erro instrumental, cadeia de custódia, independência das séries retrospectivas e critério de teste cego anterior à abertura dos dados. Somente assim reduzir o domínio das hipóteses históricas.

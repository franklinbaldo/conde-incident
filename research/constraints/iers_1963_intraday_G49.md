---
type: Guide
title: 'CASTOR-G49: interpolação intradiária autenticada da orientação terrestre de novembro de 1963'
description: 'Reconstrução condicional GCRS-ITRS em horas intermediárias com IERS 1963, UTC pré-1972 e verificação integral dos dados.'
---

# CASTOR-G49: subdia sem inventar observações

**Problema corrigido:** G48 fornece orientação às 00h UTC, mas simulações orbitais precisam de instantes intermediários. A validação G48 anterior também verificava a etiqueta SHA-256 da fonte sem comparar **todas as células** G46/G47 com o original. Alterações em x/y/LOD mantendo a etiqueta poderiam passar. G49 exige o arquivo anual original SHA-pinado e compara integralmente os dois ledgers com versões regeneradas.

**Fontes:** [IERS 05 C04 1963](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63), SHA-256 66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264, 365 registros retrospectivos; [BIPM TAI-UTC histórico](https://www.bipm.org/documents/20126/59466374/9_Table2_TAR20.pdf/713645fb-e266-6304-1375-d906d14785d7); [SOFA/ERFA IAU2000A](https://www.iausofa.org/). Não são dados de rastreamento orbital dos NORAD 527/528/529.

**Operador:** entre 07/11/1963 00h e 09/11/1963 00h UTC (inclusive), interpolar linearmente x e y do polo e UT1−TAI entre registros adjacentes, recuperar a deriva histórica TAI−UTC = 0,0011232 segundo por dia, obter UT1−UTC e TT−UTC e alimentar a matriz SOFA/ERFA c2t00a IAU2000A com JD de duas partes. A interpolação é **escolha computacional**, não observação da curva real de UT1/polo. O LOD interpolado é apenas diagnóstico. As nove épocas incluem três âncoras diárias e os horários intermediários de 06h, 12h e 18h. Qualquer época externa, ambígua ou deslocada da escala UTC canônica é recusada.

**Contraprovas:** fonte original adulterada; números x, y, LOD e sigma editados sem alterar a string SHA; G47 adulterado; timestamps com offsets, segundo intercalar falso, extrapolação, duplicatas e ordem invertida; LOD com e sem deriva de UTC; precisão de microssegundo; comparação com G48 nos endpoints, ortogonalidade e ida-volta GCRS/ITRS.

**Reprodução:** fornecer o original completo IERS, gravado localmente, em /tmp/iers-1963-eop.bin. Instalar pyerfa==2.0.1.5; executar python3 tools/iers_1963_intraday.py --source /tmp/iers-1963-eop.bin --check. Executar IERS_1963_SOURCE=/tmp/iers-1963-eop.bin python3 -m unittest discover -s tests -p test_iers_1963_intraday.py -v. O workflow CI baixa o original e confere SHA integral no HEAD da PR antes dos testes.

**Limites:** [resultado G49](iers_1963_intraday_G49.json) é GCRS→ITRS nominal, não conversão TEME↔GCRS de saída SGP4 ou de ECI anônimo. dX/dY indisponíveis não são medição nula; sigma intradiário não foi calibrado e permanece nulo. Não houve observação independente NORAD 527/529, validação de trajetória, hora, local ou probabilidade de queda em Conde. Holdout histórico NOT_RUN.

**Próximo passo:** confrontar vetores com o mesmo referencial/época e testar transformação TEME e derivada de rotação para velocidades, mais observação instrumental primária.


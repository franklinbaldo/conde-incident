---
type: Guide
title: 'CASTOR-G47: UTC de 1963 tinha deriva, não segundos intercalares modernos'
description: 'Reconstrução verificável de UTC, TAI, TT e UT1 em 7–9 novembro de 1963, coerência com LOD e componente ERA IAU2000, sem observação orbital.'
---

# CASTOR-G47: corrigir o relógio antes de rodar a dinâmica

**Descoberta física e documental.** A série retrospectiva IERS [EOP 05 C04 1963](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63), de 365 registros e SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`, contém UT1−UTC e LOD em 7–9/11/1963. Mas o **UTC pré-1972 tinha ajuste contínuo de frequência**, não a atual escala de segundos intercalares inteiros. A [tabela do BIPM](https://www.bipm.org/documents/20126/59466374/9_Table2_TAR20.pdf/713645fb-e266-6304-1375-d906d14785d7) e a [tabela IERS](https://hpiers.obspm.fr/eop-pc/index.php?index=TAI-UTC_tab) estabelecem, **de 01/11/1963 a 31/12/1963**:

`TAI−UTC = 1,9458580 s + (MJD−37665) × 0,0011232 s`.

**Resultado verificável:** em 08/11/1963 às 00 UTC (MJD 38341), `TAI−UTC = 2,7051412 s`, `TT−UTC = 34,8891412 s`, `UT1−UTC = −0,0373852 s` e `UT1−TAI = −2,7425264 s`. Tratar `TAI−UTC` como constante gera um falso desacordo de **aproximadamente 1.123 μs por dia** com LOD.

| Intervalo UTC | Δ(UT1−TAI), ms | LOD médio, ms | Resíduo corrigido | Resíduo ignorando deriva UTC |
|---|---:|---:|---:|---:|
| 07→08/11 | −2,0593 | 2,0590 | −0,3 μs | +1.122,9 μs |
| 08→09/11 | −2,1092 | 2,1070 | −2,2 μs | +1.121,0 μs |

A aproximação é `Δ(UT1−TAI) ≈ −(LOD_a+LOD_b)/2` por dia. Resíduos não nulos são esperados por interpolação de registros diários, arredondamento e diferenças de definição; **não** representam um sigma instrumental ou novos dados NORAD. Os três dias provêm da **mesma série IERS**, não de três experimentos independentes. Os erros formais de LOD não são um modelo calibrado para resíduos entre dias.

**Entradas para SOFA/ERFA:** o [recibo numérico G47](iers_1963_timescales_G47.json) fornece Julian Date em duas partes separadas (UT1 e TT) e componente Earth Rotation Angle IAU 2000 (radianos), testado também contra o [exemplo `era00` da documentação SOFA](https://juliaastro.org/SOFA/stable/api/rotations/). O UTC/TI histórico sofre salto em 01/11, por isso o operador rejeita datas fora do intervalo documentado. Não foi implementada interpolação intradiária, e ERA sozinho **não constrói** transformação completa GCRS/CIRS/ITRF ou TEME. dX/dY de 1963 não foram promovidos de zero de impressão a medição nula.

**Uso científico:** isto corrige uma convenção indispensável antes de reconstruir polos, meridiano e Sol de G43–G45. Não fornece estação, astrometria ou época de 527/529, órbita real de 528, nem posição/hora de reentrada. Holdout `NOT_RUN`, restrição física de queda `NOT_EVALUABLE`, sem probabilidade geográfica. Publicação retrospectiva IERS e tabela BIPM são fontes de grandezas distintas, não duas confirmações orbitais.

**Reprodução:** `python3 tools/iers_1963_timescales.py --download --check` (ou `--source /caminho/IERS.bin --check`), `python3 -m unittest discover -s tests -p test_iers_1963_timescales.py -v`. O CI baixa o arquivo anual inteiro, confere hash e 365 linhas, compara o JSON versionado, executa testes adversariais e só então aceita o código no HEAD exato. Próximo passo: SOFA/ERFA IAU2000A completa, testes de frame independentes e observações históricas 527/529.

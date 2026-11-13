---
type: Guide
title: 'CASTOR-G48: orientação terrestre IAU2000A para três épocas de 1963'
description: 'Transformação GCRS-ITRS com IERS 1963, UTC histórico e SOFA/ERFA, com limites de proveniência.'
---

# CASTOR-G48: do relógio histórico ao quadro terrestre

**Fatia verificável:** usa o arquivo anual retrospectivo [IERS EOP C04_05 de 1963](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63) (365 registros, SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`), o conversor de UTC pré-1972 G47 e o operador [SOFA/ERFA `c2t00a` IAU2000A](https://docs.rs/sofars/latest/sofars/pnp/fn.c2t00a.html) para calcular as matrizes **GCRS → ITRS** às **00:00 UTC** em 7, 8 e 9 de novembro de 1963. O código fornece os eixos x (meridiano) e z (polo) terrestres expressos em **GCRS**, por linha da matriz transposta, para futura verificação G43/G44 *somente se o vetor de entrada também estiver identificado como GCRS*.

A tabela do IERS [identifica](https://datacenter.iers.org/discontinued/www.iers.org/SharedDocs/Metadaten/EN/179_EOP_05_C04_2000/14334_EOP_C04_05_XX_IAU2000Af1a8.html?nn=12932) o referencial ITRF2005 e o modelo IAU2000A, **não** a posição observada dos objetos 527/528/529. A matriz não é uma conversão TEME, não resolve automaticamente a entrada SGP4, não constitui calibração histórica de ECI e não determina localização nem horário de reentrada. Valores impressos dX/dY em zero significam offsets **indisponíveis** para 1963; o resultado é o modelo nominal, não uma correção medida da nutação. A solução IERS é retrospectiva, com erros formais para EOP que não substituem uma validação instrumental independente.

**Contraprovas:** suíte com vetor de referência numérico publicado pelo SOFA (`t_c2t00a`), roundtrip de orientação ortonormal, troca artificial de UT1 por UT1+1s, omissão de movimento polar, troca de TT por UTC e falsificação de UT1/Tai, época, dX/dY e SHA. A posição cartesiana dos testes é sintética, usada apenas para validar as rotações. Não se ajustou trajetória a qualquer medição.

**Reproduzir:** `python3 -m pip install pyerfa==2.0.1.5` (numpy como dependência), `python3 -m unittest discover -s tests -p test_iers_1963_frame.py -v`, `python3 tools/iers_1963_frame.py`. O workflow `iers-eop-1963.yml` executa esses testes após recuperar os bytes oficiais, validar SHA de 365 linhas e reexecutar G46 e G47, no SHA da PR. Se faltar a dependência, o gate falha, sem falso status verde.

**Estado:** orientação diária GCRS/ITRS = **resultado computacional condicionado**. Interpolação intradiária, passagem TEME/GCRS, efeméride solar rastreável e observações independentes NORAD 527/529 = `NOT_IMPLEMENTED`/`NOT_RUN`. Alinhamento orbital simulado não equivale a sobrevoo documentado. Próximo teste: transformação da mesma época de um vetor GCRS comprovadamente autêntico, com instante e estação rastreáveis, contra observação cega independente.

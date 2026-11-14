---
type: Guide
title: 'CASTOR-G56: vinculação bilateral da geometria óptica à identidade orbital'
description: 'Contraprova de rotulagem cruzada 527/528/529: comparar ângulos somente após autenticar bytes, época, objeto e posição TEME do estado de entrada.'
---

# G56: um ângulo calculado não identifica sozinho um objeto orbital

**Falha observada no contrato G54:** o comparador validava a identidade SHA dos bytes da *observação* mas aceitava uma previsão geométrica G53 sem identificador de alvo nem proveniência para os três números TEME. A combinação de `observed.object_id=528` com uma direção calculada a partir de um estado arbitrário de 529 poderia produzir um resíduo pequeno e ser incorretamente descrita como comparação do objeto 528. Isso é um **contraexemplo de vinculação documental**, não prova de que a troca tenha ocorrido em dados históricos.

**Contrato G56:** a função `forward_source_bound_optical` exige bytes originais de um registro JSON `TEME_POSITION_ONLY_V1`, URI não vazia, `object_id`, `epoch_utc`, `frame=TEME`, `teme_position_km` numérico finito e `record_class` explícito. Apenas duas classes são admitidas: `SYNTHETIC_SCENARIO` e `SECONDARY_DERIVATIVE_NOT_INSTRUMENT`. Chaves JSON duplicadas e constantes numéricas não finitas são rejeitadas. A predição registra SHA-256, URI, classe, posição de entrada e identidade do objeto, em vez de presumir que um vetor cartesiano identifica um objeto histórico.

`compare_geometric_gcrs` passa a exigir **quatro argumentos**: `(prediction, observation, observation_original_bytes, teme_state_original_bytes)`. Autentica os dois conjuntos de bytes separadamente e recusa identidades, época, posição ou classe inconsistentes. Isso impede **a vinculação silenciosa entre objetos ou estados declarados** dentro deste contrato; não prova a autenticidade do arquivo de origem e não evita alterações arbitrárias nos campos calculados fora do operador. O SHA prova identidade dos bytes recebidos, não autoria, custódia externa, calibração de sensores nem independência da cadeia documental.

**Testes:** seis contraprovas adicionais: objeto trocado; predição sem vínculo; bytes orbitais adulterados/ausentes; época/posição retocadas; JSON com chave duplicada/número inválido; e proibição de promover cenário sintético a holdout histórico. A suíte óptica G54+G56 contém 13 testes, executados com a série IERS anual completa recuperada e SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`. O workflow `iers-eop-1963.yml` continua executando a mesma suíte no HEAD, com gatilho adicional para esta documentação.

**Risco residual:** a predição ainda é *geométrica instantânea* GCRS, não medida óptica de 1963 e não recebe implicitamente catálogo FK4/B1950, relógio de câmera, survey da estação ou evidência de tracking. O tipo `SECONDARY_DERIVATIVE_NOT_INSTRUMENT` não autoriza a transição para `OBSERVACAO_PRIMARIA`. `historical_holdout=NOT_RUN` e `impact_inference=NOT_SUPPORTED` permanecem obrigatórios. O próximo avanço científico é adquirir bytes de medições instrumentais 527/528/529 com época, estação, quadro e incerteza documentados, cruzando a identificação com os registros de origem.

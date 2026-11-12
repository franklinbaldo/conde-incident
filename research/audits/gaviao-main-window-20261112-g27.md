---
type: Guide
title: "🦅 G27: auditoria retrospectiva de 14 integrações e custódia SGP4"
description: "Manifesto SHA-a-SHA, teste independente TLE UTC e limites de documentação, CI, Lean e modelagem."
---

# G27: 14 integrações auditadas sem autorizar inferência terminal

**Checkpoint:** `4ec4d61ab603924e355bdb55fead26b9a5ff32d1` → **corte congelado** `20240adddaf9df0e703d894bc2a7dba73fc8b855`, em 12/11/2026, 18h36–19h27 (UTC−04). `git rev-list --first-parent` e `git rev-list` concordaram: **14 integrações, todas squash**, um único pai cada, **0 commits laterais**, **0 commits diretos**. Pesquisa dos 100 PRs fechados mais recentemente não identificou PR fechado sem merge nesse intervalo temporal. Para cada commit, o [manifesto JSON](gaviao-main-window-20261112-g27.json) fixa SHA, pai, PR, HEAD autoral relatado pela API, caminhos modificados e verificações `push` consultadas por SHA; estas **não substituem** os checks exigidos do HEAD de autor. A própria PR G27 e merges simultâneos ficam para a próxima janela.

## Parecer individual: cobertura integral

1. [#274](https://github.com/franklinbaldo/conde-incident/pull/274), `c8bde143`: guarda visual contra conector longo no antimeridiano. Causa e contraprovas sintéticas da G26 preservadas; nenhum dado real de sobrevoo.
2. [#260](https://github.com/franklinbaldo/conde-incident/pull/260), `dcc0de0a`: 42 intervalos finitos da sondagem IGRA Recife, derivação seca e mesmo conjunto de observações para vento/temperatura/altura. Não medir turbulência/vento de Conde por transferência espacial não calibrada.
3. [#277](https://github.com/franklinbaldo/conde-incident/pull/277), `4f4791c1`: cobertura de citações 29/28 ocorrências e 26 dependências documentais inativas. A contagem de registros não é número de observadores independentes.
4. [#276](https://github.com/franklinbaldo/conde-incident/pull/276), `b8364684`: duas edições NASA SSR e seu delta de listagem, sem traduzir ausência na edição posterior em refutação de 8/11. O fac-símile de 15/11 confirma **dia catalogado**, não hora/posição de 528.
5. [#279](https://github.com/franklinbaldo/conde-incident/pull/279), `00e300c1`: ±GMST e tolerância de ±60 s testam hipótese angular delimitada, com UTC apenas proxy para UT1. Resíduo ≈19,07° não resolve conflito RAAN 284,1520° vs 198,5261°; sem nova restrição física ativa.
6. [#280](https://github.com/franklinbaldo/conde-incident/pull/280), `503b4efc`: posto racional exato e contraprova da época única de 527 em validação. Estimabilidade da linha do desenho não equivale a calibração de predição orbital nem independência de fontes.
7. [#281](https://github.com/franklinbaldo/conde-incident/pull/281), `740badf6`: Prek em `pull_request` e `push/main` elimina duplicação de branch, mas verificações de autores no HEAD real continuam obrigatórias.
8. [#282](https://github.com/franklinbaldo/conde-incident/pull/282), `b12a43f0`: Office Note 20 de **1964**, cópia Wayback com SHA declarado. Um manual arquivado não comprova decodificação de lançamento IGRA específico de 1963.
9. [#283](https://github.com/franklinbaldo/conde-incident/pull/283), `095d45ca`: fichas cartográficas catalogadas **1985**, não fronteira física ou cratera de 1963.
10. [#284](https://github.com/franklinbaldo/conde-incident/pull/284), `ec03c968`: referência `satellite.js@5.0.0` em TEME, r[km], v[km/s], época YYDDD. Checksum de TLE **não é** SHA nem atestado de observação original. G27 acrescenta **cinco testes Python independentes do satellite.js** para bytes fixados, identidade, época UTC exata, ano bissexto/pivô, mutação com checksum válido porém digest diferente, e gates inferenciais fechados. Os testes JS existentes usam secante ±1 s para checagem dimensional, mas **não** são holdout instrumental. Transformação TEME→quadro inercial RK4 e covariância continuam ausentes.
11. [#285](https://github.com/franklinbaldo/conde-incident/pull/285), `d0de418f`: frames de mapa e aerograma e CSP de capítulo 03; conteúdo visual é documento/representação, não detecção orbital.
12. [#286](https://github.com/franklinbaldo/conde-incident/pull/286), `236a2270`: variante SVG vertical para leitura móvel; genealogia das fontes ainda distingue repetições de observações independentes.
13. [#287](https://github.com/franklinbaldo/conde-incident/pull/287), `55f16f3f`: deep link ISO UTC canônico seleciona **instante de cenário**, não relógio observado; rejeição de parâmetros extras e limites de mapa testados no código.
14. [#288](https://github.com/franklinbaldo/conde-incident/pull/288), `20240add`: fac-símile NORAD **14/11/1963 p. 2** indica 22h10Z–24h00Z em **12/11 para SPADATS 688**, não para 528. Mensagem **12/11 p. 3** confirma Shemya 06h42Z em **11/11 para Sputnik 46**. A página impressa 8 do SSR NASA 15/11 relaciona 1963-003B a **8 NOV 63**, sem hora. Os três fac-símiles foram reinspecionados visualmente nesta auditoria; não se extrapola 110 minutos para 528. Documentos 216-64/217-64 não foram reinspecionados aqui.

## Achado G27-F1: integridade e tempo da referência secundária

A API SGP4 de #284 deliberadamente classifica a custódia como `DECLARED_DIGEST_NOT_AUTHENTICATED`, e a linha `sourceSha256` é **somente declarativa**. Uma modificação sintética no RAAN de 198,5261 para 198,5262, acompanhada de recomputação do checksum TLE, **ainda passa ambos os checksums**, mas altera SHA-256 dos bytes. Isso não demonstra fraude histórica: apenas prova que checksum TLE sozinho não autentica o espelho. A nova suíte G27 verifica independentemente o SHA congelado `18cf1166…44e341cd` e a época `1963-10-27T14:40:16.132512Z`, obtida por `Decimal` sem chamar SGP4. O `Date` JavaScript conserva milissegundos, não os últimos 512 microssegundos dessa representação. Não reclassificar a amostra como observação, nem imputar erro histórico instrumental.

**Documentos:** prioridade para instrumentos/observações originais com ID, hash de captura, época e independência. O catálogo NASA registra dia, as mensagens NORAD consultadas tratam de **outro objeto**, e as linhas 527/528/529 permanecem espelhos secundários. Sem matriz de covariância, geografia calibrada ou medição terminal.

**Lean:** nenhum `.lean` alterado nesses 14 merges. O teste de posto racional e a rotação sideral não são provas Lean de impacto; sem `#print axioms` ou build Lean local nesta rodada. O CI de integração tem gates Lean, mas verde não autentica premissas.

**Numérico:** verificação de unidades TEME e derivada temporal não fornece comparação segura com RK4/J2 inercial. Sem calibrar transformação, erro de propagação longa e holdouts independentes, a fronteira admissível **não** foi reduzida.

**CI:** o manifesto preserva o resultado de workflows `push` por merge. #274, #277 e #279 tiveram **15 SUCCESS + 1 CANCELLED**, não 16/16 verdes; os demais commits obtiveram 16–18 SUCCESS. Prek local na casa privada excedeu 128 MB RSS, então `LOCAL_PREK=NOT_RUN_COMPLETED`, sem desabilitar gates. Os cinco testes novos e os 11 da rotação sideral foram executados em Python local; Node, `lake build` e publicação **NOT_RUN local**. A PR deverá exigir CI do SHA autoral exato antes de integração.

**Resultado:** `CONDE_INDETERMINATE`. Não houve prova de queda, exclusão, sobrevoo, localização ou horário terminal. Nenhum blog pessoal foi alterado. Toda futura mudança no estado do problema deve promover nova fonte verificada à matriz cumulativa e encadear restrição condicional antes de simulação física.

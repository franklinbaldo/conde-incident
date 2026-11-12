---
type: Guide
title: "🦅 G26: auditoria retrospectiva de 13 integrações e conexões de mapa"
description: "Cobertura SHA a SHA, contraprova sintética de antimeridiano, limites de fontes e CI do Gavião."
---

# G26: revisão retrospectiva científica e editorial

**Janela fixa:** `609b352d382fc2d7b4ee48c06c9dc8b9cc1a2e05` → `4ec4d61ab603924e355bdb55fead26b9a5ff32d1`, **13 integrações first-parent**: 11 squash, dois merges convencionais, seis commits laterais (19 no DAG), **zero commits diretos sem PR**. Os SHAs de pais, arquivos, cabeças autorais e respectivas contagens de workflows estão no [manifesto JSON](gaviao-main-window-20261112-g26.json), sem tratar resultados de CI como prova histórica.

**Ordem, cobertura e parecer individual:**

- [#256](https://github.com/franklinbaldo/conde-incident/pull/256) `2d80d4028dd5`: Nine documentary/scientific bridge records remain inactive and traceable; source lineage is NOT a physical observation. PR HEAD 16 SUCCESS.
- [#259](https://github.com/franklinbaldo/conde-incident/pull/259) `839e7b772dfa`: 1960 IBGE native mesh topology is retrospective; no certified 1963 Conde boundary or impact coordinates. PR HEAD 16 SUCCESS.
- [#263](https://github.com/franklinbaldo/conde-incident/pull/263) `5f1990c373e0`: Integration-head trigger deduplication alters CI dispatch, not scientific measurements. PR HEAD 16 SUCCESS.
- [#262](https://github.com/franklinbaldo/conde-incident/pull/262) `c01079eac47c`: G25 frozen-epoch holdout veto guards against validation/evaluation overlap; tests are synthetics. PR HEAD 17 SUCCESS.
- [#265](https://github.com/franklinbaldo/conde-incident/pull/265) `bf3f1167e3d1`: The 284.1520 degree RAAN crossing is two-sided interpolation of ONE secondary lineage, not 1963 instrument custody. PR HEAD 17 SUCCESS.
- [#264](https://github.com/franklinbaldo/conde-incident/pull/264) `a620497de35b`: Two exact gauge null vectors are conditional on fixed but unspecified F_j(t); no likelihood, no historical posterior. PR HEAD 16 SUCCESS.
- [#266](https://github.com/franklinbaldo/conde-incident/pull/266) `21bd8a0c8019`: NCEP ON20 locator is bibliographic; primary manual/PDF and a 1963 launch are NOT authenticated. PR HEAD 16 SUCCESS.
- [#267](https://github.com/franklinbaldo/conde-incident/pull/267) `f38aaf8daf65`: Cartesian r/v trend suppresses resolved growth; 64-ULP allowance is heuristic, not an absolute RK4 error guarantee. PR HEAD 16 SUCCESS.
- [#268](https://github.com/franklinbaldo/conde-incident/pull/268) `0a25fc961835`: Natural Earth fixed 110m coastlines provide generalized visual context, no impact point; projectFlat wraps longitude. PR HEAD 17 SUCCESS.
- [#269](https://github.com/franklinbaldo/conde-incident/pull/269) `9d111439c304`: Keyboard-accessible export modal: distinguish user UI behavior from archival evidence. PR HEAD 17 SUCCESS.
- [#271](https://github.com/franklinbaldo/conde-incident/pull/271) `5dedb5f6c3fa`: Map layers and scene connectors: raw longitude difference guard fails for UNWRAPPED 179->181 degrees (G26-F1). PR HEAD 17 SUCCESS.
- [#270](https://github.com/franklinbaldo/conde-incident/pull/270) `00d609c4c97b`: A-628/consular denial is an indirect documentary counter-report, not a physical inspection; C197 NASA is date-only. PR HEAD 16 SUCCESS.
- [#273](https://github.com/franklinbaldo/conde-incident/pull/273) `4ec4d61ab603`: Async clipboard fallback must not falsely announce copied result; metadata without observation. PR HEAD 16 SUCCESS.

## G26-F1: falsa conexão visual através do antimeridiano

O SVG usava `Math.abs(other.longitude - positions[528].longitude) > 180` para vetar linhas entre objetos no mapa plano. Em **controle sintético, não órbita observada**, dois pontos 179° e 181° têm diferença bruta de apenas 2°, porém `projectFlat` transforma 181° em −179° e coloca as extremidades em lados opostos da tela (x ≈ 957 e x ≈ 3). Uma linha direta sugere uma relação geográfica falsa. O mesmo acontece com −179° → −181°. Isso restou fora da cobertura da G24 sobre polylines porque essas conexões são elementos `<line>` independentes.

A correção introduz `canDrawFlatConnection()` comparando longitudes **após** `wrapLongitude`, e integra o veto no SVG, com testes adversariais dos dois sentidos, variantes previamente embrulhadas, controles ordinários e coordenadas inválidas. Não se atribuem coordenadas históricas a NORAD 527/528/529.

## Separação das quatro auditorias

**Documentos:** C01#1 Rádio Tupi/FBIS é notícia retransmitida; A-628 resume consultas, não constitui perícia física. C197#1 NASA SSR 15/11/1963 atribui somente 08/11 como dia catalogado para 1963-003B. Recortes brasileiros originais e instrumentos primários não foram autenticados aqui. As novas referências NCEP, IBGE, Natural Earth e NORAD têm usos distintos; nenhum é posição terminal de 528.

**Lean:** os dois gauges e a interpolação de RAAN em #264/#265 são resultados algébricos/condicionais sobre uma única série secundária. Não houve modificação `.lean` no intervalo nem nova compilação local do Lean 4.35.0; axiomas não foram reatestados por esta execução. Não promover a prova condicional a conclusão física.

**Método numérico:** o diagnóstico #267 testa crescimento entre refinamentos do integrador acoplado e declara explicitamente não certificar erro absoluto. O controle RAAN #262 separa épocas de validação e avaliação, mas não produz observação instrumental independente. O efeito cartográfico G26-F1 não altera os integradores nem seu domínio admissível.

**Editorial e UI:** o Caderno 03 #270 preserva "aparentemente", atribui a negativa ao cônsul e avisa da ausência de prova universal de inexistência. #268/#271 tratam geografia e cena hipotética, nunca ponto de impacto; #269/#273 tratam acessibilidade e honestidade da cópia. A disponibilidade do Caderno não foi criptograficamente atestada nesta revisão.

**Testes:** 41/41 testes Python PASS (pontes documentais, topologia IBGE, RAAN legado, NCEP, gauge temporal); `git diff --check` PASS. O Node local excedeu RSS do Jatobá antes de concluir (`NOT_RUN_COMPLETED`). CI deve validar o SHA autoral final da correção, inclusive Node, Prek/OKF, build SSG, Lean e Pages. Sem nova inspeção de fac-símiles externos, sem alegação de nova evidência observacional.

**Resultado:** `CONDE_INDETERMINATE`; nenhuma redução numérica autenticada de Θ. A integração posterior da própria correção e qualquer merge concorrente ficam para G27 porque o corte desta revisão é imutável.

---
type: Guide
title: '🦅 G35: auditoria retrospectiva das integrações e custódia Wayback'
description: Cobertura SHA a SHA, contraprovas sintéticas e correção do vínculo de PDFs preservados.
---

# G35: 13 integrações, vínculo Wayback e limites científicos

**Corte exclusivo:** `06f1f11ca567ec37d260435fba233080b5365170`. **Corte inclusivo:** `0d0f51f0eec06421b895372b6390d7f309ad61fa`. São 13 integrações em primeiro pai: 11 squash e dois merges convencionais (#420 e #422). O DAG completo contém 19 commits, incluindo seis laterais; nenhum commit direto identificado neste corte. O manifesto [G35 JSON](gaviao-main-window-20261113-g35.json) registra pais, PRs, arquivos e achados específicos. Integrações concorrentes posteriores não pertencem a este corte.

## Auditoria de reivindicações por mudança

| PRs | Foco e cautela |
| --- | --- |
| #414, #419, #421 | Valor de dezembro do 529 e contrastes de períodos impressos. Datas de *edição* não fornecem épocas originais das medições, e diferenças de catálogo não são taxas físicas calibradas. |
| #415, #427 | Genealogia documental e links do Wayback; esquema fechado da G34 foi preservado, mas a G35-F1 detectou incoerência de captura aceita pelo gerador SSG. |
| #416, #425, #428 | Lean, Kepler e testes J2 são diagnósticos condicionais. Não demonstram observação terminal do objeto 528 nem substituem modelos calibrados. |
| #417, #422 | Lei de 1953 e travessias do Itapicuru de 2014–2025 não podem virar observações astronômicas de 1963. |
| #420 | Cobertura IGRA de estações não autoriza inventar vento/perfil onde faltam medições originais. |
| #424 | Verificador CI de checkout exige `git rev-parse HEAD` comparado ao SHA do evento em cada checkout. |
| #426 | Navegação editorial e identidade entre arquivo e caderno, sem nova prova histórica. |

## G35-F1: link para PDF fora da captura alegada

No gerador `scripts/ssg-wayback-links.mjs`, a validação anterior exigia apenas prefixo `web.archive.org/web/`, SHA textual idêntico ao payload e comprimento positivo. Isso aceitava, em **entradas sintéticas**, mudar o link para documento não relacionado, deslocar a data do replay, mudar o tamanho sem mudar o digest ou duplicar uma aresta para inflar o número de cópias. O risco era publicar o link falso como *PDF preservado e verificado*. Não há alegação de que o catálogo real tenha sido adulterado.

A correção compara timestamp de permalink `id_` e UTC, URL de destino e `cdx_original_url`, host e identificador da obra com a citação curada, tamanho do PDF com o payload e unicidade de arestas. Inclui controle positivo do corpus original e testes adversariais com execução explícita no workflow Pages.

**Limites:** estas verificações são de coerência interna do manifesto versionado; **não** refazem HTTP live, SHA dos bytes de um replay, nem autenticam o documento como medida instrumental NORAD de 1963. Data da NASA para decadência do 528 permanece apenas dia 8/11/1963, sem hora ou lugar terminal. Conflito RAAN 284,152° versus ~198,526° segue aberto. Conde permanece indeterminado.

---
type: Guide
title: 'G44: links HTML reais no arquivo documental SSG'
description: Revisão de doze integrações e contraprovas de navegabilidade do índice documental publicado.
---

# 🦅 G44: o endereço escrito não é um link

## Janela e método

Conde `main` de `7aed7403d39f2d097f0a9eedc44a83a342f2f215` (exclusivo) até `5b72218b98621637d28000a3c82d86496585a9be` (inclusivo), congelado antes da PR corretiva: **12 integrações first-parent e 12 commits no DAG**, nenhum merge convencional. O [manifesto G44](gaviao-main-window-20261113-g44.json) registra SHAs, pais, PRs, arquivos e `ci_status: NOT_CHECKED` para cada integração histórica. Inclui #565, #566, #568–#570, #572–#577 e integração geográfica CGEO-31; nenhuma aprovação CI retroativa é presumida.

## G44-F1: contraprovas de interface renderizada

A PR #570 passou a auditar o acoplamento do índice JSON ao SSG. Contudo, `scripts/verify-ssg-evidence-index.mjs` aceitava o índice HTML desde que contivesse a **string** de cada rota, mesmo que fosse texto inerte sem `<a href>`. O mesmo gate exigia a existência e os hashes textuais das páginas de ocorrências, mas **não inspecionava os links HTML reversos** para família, obra e fonte. Isso não prova defeito no site real: é uma lacuna do auditor do produto publicado.

No executor SSH `ifro` (Node 20.19.2), duas árvores HTML inteiramente **sintéticas**, contendo os arquivos e digests esperados mas sem links navegáveis, atravessaram `auditBuiltSite`. Os dois novos testes reprovaram antes do reparo por `Missing expected exception` (2/2), demonstrando o falso positivo. O reparo exige âncoras `href` reais com as rotas canônicas no índice e em cada ocorrência, ignorando comentários HTML. Depois: **9/9 testes Node** e `node scripts/verify-ssg-evidence-index.mjs` aprovados; 29 referências, 28 ocorrências, 70 páginas planejadas e três shards. O gate `--built-site` sobre HTML **real do SSG** só pode ser confirmado pelo CI completo no HEAD da PR.

## Limites científicos

A cadeia SSG ↔ JSON é uma relação editorial, não uma medição orbital. As novas fontes NASA retrospectivas, rastros soviéticos e derivados analíticos desta janela não fixam a hora ou a posição terminal do NORAD 528; modelo SSR de edições não estima erro instrumental. **Conde permanece INDETERMINADO.** A próxima auditoria começará depois do corte `5b72218b`, incluindo a correção e qualquer integração concorrente.

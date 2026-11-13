---
type: Guide
title: 'G43: esquema fechado nas cadeias de evidência SSG'
description: Revisão retrospectiva de treze integrações e contraprovas de alegações físicas não verificadas no índice documental.
---

# 🦅 G43: campos inesperados nas genealogias publicadas

## Janela auditada

Corte da `main` de Conde: `717e00fb59dec380f1ee8a8bb5453c81a1c88f64` (exclusivo) → `7aed7403d39f2d097f0a9eedc44a83a342f2f215` (inclusivo), anterior à correção G43. **13 integrações first-parent, 13 commits no DAG e nenhum merge convencional**. O [manifesto G43](gaviao-main-window-20261113-g43.json) identifica commits, pais, títulos, PR quando explícita e arquivos. Os checks históricos individuais são **NOT_CHECKED**, sem reaproveitar sucesso de CI de outro SHA.

Abrange #550 (catálogo soviético), #551 (GHCNd), #553 (gauge densidade×balístico), #554 (índice SSG), #555 (estação Novosibirsk), #556 (ponte de catálogos), #557 (minimax NASA/Lean), #560 (consistência radial), #559/#564 (fotoíndice USAF), #561/#562 (navegação/busca) e #563 (jornal citado em comunicação militar). Os resultados devem manter separação entre documento publicado, inferência condicional e medição instrumental.

## Achado G43-F1, contraprova reproduzida

Na #554, `tools/export_ssg_evidence_index.py` confrontava linhas, hashes declarados, continuidade e aciclicidade das arestas, mas **exportava literalmente** `declared_upstream_paths` sem vetar chaves adicionais nos objetos de caminho ou aresta. Portanto, uma mutação sintética `norad_528_terminal_epoch_utc` inserida no caminho e outra `norad_528_terminal_latitude_deg` inserida na aresta eram **aceitas e publicadas** nos shards gerados, sem alteração dos SHA-256 documentais declarados. Isso é possibilidade de contaminação do derivado; **não há evidência de adulteração real** nem de posição terminal observada.

Antes do reparo, **2/2 testes adversariais falharam** no sentido esperado (`ValueError not raised`). Após o reparo, é exigido conjunto exato de chaves `{edges, upstream_source_id}` para cada caminho e `{from, to, kind}` para cada aresta, antes de exportá-los. Teste positivo preserva o corpus normal: **11/11 testes SSG PASS**, `python3 tools/export_ssg_evidence_index.py --check` PASS, sem mudar o JSON publicado. Também passaram 10/10 testes da ponte soviética, 4/4 de CGEO-30, e regeneração determinística de C241-P20 (9 edições, 23 células, E=128 centiminutos), sem ativação de Θ. `git diff --check` PASS. CI completo da PR no HEAD final é obrigatório antes de merge.

## Limites científicos

O minimax de 1,28 minuto é relativo a um modelo aditivo de **edições publicadas** da NASA, não a precisão de sensores nem a época de rastreio. O catálogo Novosibirsk e o fotoíndice USAF apontam **rotas para novas fontes**, não observações dos NORAD 527/528/529. A imagem efetiva de CGEO-30 ainda não está disponível; a menção a *O Globo* em 1963 não autentica a reportagem original. Nenhum achado desta janela estabelece hora ou posição de reentrada do 528, sobrevoo observado ou queda em Conde. **Estado: INDETERMINADO.**

**Próximo checkpoint:** a janela seguinte começa após `7aed7403d39f2d097f0a9eedc44a83a342f2f215`, incluindo esta correção e os merges concorrentes posteriores.

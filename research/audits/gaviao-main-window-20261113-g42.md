---
type: Guide
title: 'G42: integridade da posição de estação no derivado GHCNd'
description: Auditoria de quatorze integrações e contraprovas de metadados não cobertos pelos hashes .dly.
---

# 🦅 G42: o arquivo de chuva não autentica a posição da estação

## Janela retrospectiva

Corte exclusivo após `d1f6d53851e9a4d3564ed436c527ad0c2157f12e` e inclusivo até `717e00fb59dec380f1ee8a8bb5453c81a1c88f64`, **antes desta PR**. São **14 integrações first-parent, 40 commits no DAG, quatro merges convencionais e 26 commits laterais**. O [manifesto G42](gaviao-main-window-20261113-g42.json) lista SHA, pais, PR, data, arquivos e estatuto individual de CI. Histórico de checks por integração: `NOT_CHECKED`. Somente o SHA de corte da main foi consultado via GitHub Actions, com **24/24 workflow runs completed/success** em 13/11/2026.

A janela incluiu #532 (proteção do CI), #533 (catálogo NASA com 1963 03A = 527, **não** identificação instrumental de 528), #534 (Lean condicionado), #539 e #537 (chuva diária NOAA/GHCNd), #535 (catálogo SGB), #540 (gauge de época), #542/#544 (controles de software), #543 (legislação), #546/#547 (UI), #548 (catálogo soviético) e #549 (filmes RU301 sem identificação do objeto). Publicação/catálogo não equivale a observação terminal; tempo de publicação não é tempo instrumental.

## Achado G42-F1: hashes da chuva não autentificam o catálogo da estação

O derivado `public/data/conde-ghcnd-conde-bridge.json` exportava a posição catalográfica de CONDE de `research/meteorology/ghcnd_conde_precip_19631107_09.json`, mas validava principalmente hashes de arquivos `.dly`, valores diários e identificadores. O arquivo `.dly` contém precipitação, **não** latitude/longitude, nome da estação ou anos de disponibilidade do catálogo `ghcnd-stations.txt`/`ghcnd-inventory.txt`. Assim, sem mudar qualquer SHA-256 declarado, mutantes sintéticos com posição CONDE `[0,0]` e `[89,-37.61]`, outro nome de estação, ou intervalo PRCP fabricado eram aceitos (três casos de teste com quatro mutações independentes). Não foi encontrada adulteração do acervo real.

**Correção:** comparar o hash semântico canônico (JSON ordenado e UTF-8) do relatório inteiro contra valor aprovado explicitamente no consumidor. Isso impede alterar metadados ou campos adicionais sem revisão do pin e sem executar a auditoria original `tools/audit_ghcnd_conde_rain_1963.py` contra os arquivos NOAA SHA-pinned. Não reutilizar o hash dos pais calculado a partir do próprio relatório mutado como autenticação circular.

**Ensaios locais:** originalmente 14 testes com três falhas (`assertRaises` ausente; duas mutações de posição e duas de identidade/anos). Após correção, 14/14 testes GHCNd bridge passaram, `python3 tools/export_ghcnd_conde_bridge.py --check` manteve o derivado de 4.576 bytes inalterado, e `git diff --check` passou. Esta etapa é uma garantia de **consistência do snapshot versionado**, não reaquisição independente do NOAA nem prova da coordenada de 1963. O CI real da PR deve ser verificado no HEAD final antes do merge.

## Limites científicos

A chuva registrada em CONDE em 08/11/1963 (3,5 mm no arquivo diário) não fornece horário intra-dia, localização da eventual queda, vento local nem independência instrumental. A ponte permanece `activation: false`, `physical_domain_effect: THETA_UNCHANGED`. A situação do NORAD 528 segue indeterminada, sem hora nem posição terminal demonstradas por fonte primária instrumental.

**Continuidade:** a próxima revisão cobre esta PR e integrações posteriores ao corte `717e00fb`, sem absorver silenciosamente merges concorrentes nesta janela.

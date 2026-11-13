---
type: Guide
title: 'G41: execução real dos scripts de CI e revisão retrospectiva'
description: Auditoria de treze integrações e testes adversariais de saída antecipada e shell que ignora scripts.
---

# 🦅 G41: um comando presente pode não executar

## Escopo congelado

A janela exclusiva `9a2f98151d3e9db98384f532cee6d5cea90958dd` até inclusiva `d1f6d53851e9a4d3564ed436c527ad0c2157f12e` contém **13 integrações first-parent, 19 commits no DAG, três merges convencionais e seis commits laterais**. [Manifesto G41](gaviao-main-window-20261113-g41.json) cataloga cada SHA, pais, PR e arquivos modificados. A janela termina **antes** desta correção e de merges concorrentes. Histórico de checks anteriores não foi inventariado nesta rodada e permanece `NOT_CHECKED`, não `PASS`.

## Achado G41-F1: aparição textual não é execução

O gate de passos de CI trazido pela #517 e aprimorado pela #523 buscava a linha obrigatória dentro do corpo `run: |`, mas não verificava que o script a alcançava. A contraprova mudou `TypeScript check` para `run: |` com `exit 0` antes de `bun run lint`; o gate antigo aceitou. O mesmo aconteceu com `exit 0` antes do `python3 -m unittest`. A etapa Node aceitou `shell: bash -c "true" {0}`, que não executa o arquivo do passo, e a etapa lint também aceitou esse override. Estes são **mutantes sintéticos demonstrados**, não indícios de alteração real dos workflows de produção.

A correção fixa a sequência completa dos **quatro scripts multiline obrigatórios** e proíbe overrides de shell arbitrário nas etapas críticas. Também rejeita `defaults: run.shell` globais ou por job nos dois workflows universais, pois poderiam substituir silenciosamente o shell. O contrato permanece intencionalmente fechado: mudança legítima de script exige revisar também o corpo esperado. Isto não demonstra análise semântica de Bash nem certifica todas as etapas opcionais ou workflows externos.

**Red/green local:** quatro ataques foram aceitos pelo validador antes do reparo; sete casos adversariais adicionais e controles positivos passaram após o reparo, com **20 testes Python de CI aprovados**. `git diff --check` passou e os arquivos permanecem abaixo do teto de 20.000 bytes. A integração da PR depende da CI real no SHA autoral.

## Revisão científica e editorial

A janela acrescentou nove edições NASA, testes de janela de época em TLE secundária, estação óptica, precipitação arquivada, acesso a aerofotos SGB, correções de índices de imprensa, sitemap e Caderno 18. Foram executados **63 testes direcionados** dessas frentes: 62 passaram e um foi ignorado. Uma data diária de chuva não fixa o clima da cena específica, uma consulta de acervo não atesta aerofoto encontrada e o acesso ao catálogo Moonwatch não demonstra visada do NORAD 528. Sensibilidade numérica de TLE secundária e formalização Lean tampouco autenticam a posição histórica terminal.

A posição e o horário terminal do NORAD 528 continuam sem demonstração observacional independente. Esta auditoria **não** reconsultou os PDFs históricos em HTTP nem verificou os bytes dos arquivos externos. Próxima janela: a própria PR G41 e integrações posteriores ao SHA de corte.

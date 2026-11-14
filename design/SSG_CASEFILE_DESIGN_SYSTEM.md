---
type: Guide
title: Conde — design system SSG-first, implementação vertical v1
description: Contrato de tokens CSS nativos, componentes sem JS, página de dossiê e migração por paridade.
---

# Conde: design system governado pelo SSG Rust

A unidade de publicação é Page OKF. O SSG Rust 0.0.75, fixado e verificado por digest no CI, compila HTML a partir das fontes pages/<rota>/page.md através de scripts/ssg-authored-pages.mjs. Não introduzir gerador editorial paralelo, hidratação obrigatória, biblioteca CSS ou backend.

## Primeira implementação real

- A rota /conde-incident/dossie/ é uma Page canônica escrita em Markdown OKF com blocos HTML sem JavaScript. O gerador SSG publica a rota.
- O arquivo static/css/site.css contém tokens locais da classe casefile para tinta, superfícies e foco, e componentes de composição cf-* (hero, fontes, trilha, cartões, botão, aviso epistemológico).
- A fonte pages/dossie/page.md reaproveita identificadores C01#1/C197#1 e URLs já publicados; distingue relato FBIS, dia de decaimento NASA, hipóteses e instrumento de cálculo. Não inventa evidências nem inferências físicas.
- A capa do Caderno dá acesso ao dossiê preservando todas as rotas anteriores. O leitor percorre: página estática → capítulo → registro → hipótese/instrumento; links operam com JavaScript desativado.
- O contrato de teste tests/ssg-casefile.test.mjs verifica Page, rotas, limites de afirmação, CSS, HTML SSG compilado e ausência de SPA nesta jornada.

## Regra de design system

**Templates e conteúdo pertencem ao SSG; CSS nativo compõe.** Não transformar esta prova de conceito em segunda aplicação. Classes cf-* são componentes reutilizáveis em outras Pages da mesma coleção. Não presumir suporte a macros ou partials novos no SSG v0.0.75 sem testes do executável real.

Os tokens usam custom properties CSS, Grid, Flexbox e clamp. O tema fica local para demonstrar uma direção nítida sem alterar visualmente todo o site de uma vez e sem interferir no Laboratório React/Vite. O estilo atual é fallback. O uso de :has() refina espaçamento, sem ser requisito de leitura.

## Interfaces com a pesquisa

Uma ocorrência por ID não converte documento em evento físico. Classes de evidência precisam de texto; nenhuma cor sozinha significa certeza ou autenticidade. Data de transmissão, publicação e observação não são intercambiáveis. O mapa interativo do Laboratório é um enriquecimento opcional, não condição para compreender a página; o mapa estático deve continuar acessível.

## Portabilidade e migração

Migrações posteriores devem preservar URLs, fonte canônica, links de retorno e paridade científica. Não retirar React ou cálculos TypeScript antes de comparar saídas com alternativas SSG + JS/WASM por ferramenta. O cabeçalho global é responsabilidade da Raposa e já tem PR específica #860; esta implementação não modifica menus nem roteadores.

**Checks mínimos:** contrato Node do conteúdo, HTML gerado, build SSG real, ssg audit, largura 320/375/1440px no Chromium com JS desligado, teclado e contraste. Zoom nativo e leitor de tela só podem ser marcados PASS se efetivamente executados. Build verde não é prova de publicação atualizada.

**Lição do build:** usar seções com títulos para os cartões. Elementos article internos fizeram o gerador classificar indevidamente a rota como Article, cujo gate JSON-LD exige autoria e data de publicação. A estrutura com section mantém a Page como WebPage e passa no auditor sem fabricar metadados históricos.

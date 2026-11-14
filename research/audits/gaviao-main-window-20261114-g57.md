---
type: Guide
title: '🦅 G57: trilhas SSG não devem aceitar HTML inerte'
description: Auditoria retrospectiva de validação HTML, com contraprovas e limites.
---

# G57: falso PASS no verificador de trilhas estáticas

**Janela congelada:** `c4e25a0ff8cbf218480d311f83884a9c4deedd80` (exclusivo) até `8b70e80eeb672046dec024abfa225110b92ae315` (inclusivo). Quatro integrações first-parent e quatro commits no DAG: #739 (custódia NOAA), #723 (breadcrumbs), #732 (resíduo óptico), #734 (mapa SSG). Checks históricos individuais não revistos: **NOT_CHECKED**.

## G57-F1: uma trilha textual dentro de comentário não é uma trilha navegável

A correção G55 (#723) passou a exigir a sequência literal `<main ...><nav ...>`, mas sua busca ainda era textual. Uma cópia byte a byte da sequência esperada **dentro de comentário HTML** fazia `addBreadcrumbs()` retornar `changed: false` embora não existisse a trilha navegável correspondente. Quando um comentário fictício precedia o `<main>` real, a inserção textual também podia atingir o comentário em vez do documento.

**RED reproduzido em Node 20 (ifro):** o teste adversarial adicional fez 1 de 7 testes falhar; seis testes anteriores passaram. Entrada sintética; não demonstra falha observada no Pages publicado.

**GREEN:** ao validar, excluir texto de comentários e elementos inertes (script, style, template, textarea), preservando os offsets. Conferir `<main>` ativo e exigir a trilha imediatamente após ele, e inserir somente na posição ativa. O controle do título também recusa conteúdo esvaziado pela remoção de elementos inertes. **7/7 testes Node PASS**, `git diff --check` PASS, limite por arquivo 20 KB PASS. CI remoto e HTML Pages construído devem ser verificados no HEAD final antes do merge.

**Limite interpretativo:** o filtro não substitui um parser HTML5 completo e pressupõe o HTML canônico emitido pelo SSG. Este teste corrige uma aceitação sintética de conteúdo inerte, não demonstra incidente em produção, identificação do NORAD 528, observação instrumental nem sua trajetória terminal.

Referências: [PR #723](https://github.com/franklinbaldo/conde-incident/pull/723), [PR #739](https://github.com/franklinbaldo/conde-incident/pull/739), [Cafezinho #11](https://github.com/franklinbaldo/cafezinho/issues/11).

---
type: Document
title: '🦅 G34: auditoria retrospectiva, genealogia institucional e contraprova'
description: 'Revisão de merges e defesa contra campos extrínsecos em proveniência pública.'
date: '2026-11-13'
---

# G34: o dado que entrou pela genealogia

Corte **exclusivo** `c9b4482f7850434a9124dfe6a12c540006aa468f` e **inclusivo** `06f1f11ca567ec37d260435fba233080b5365170`, antes da PR corretiva. O manifesto JSON adjacente preserva os commits de primeiro pai, pais laterais, PRs, arquivos e limites do parecer, sem inventar resultados de CI. O corte inclui as PRs #400, #401, #402, #403, #405, #408, #409, #406, #410, #412, #411 e #413, na ordem da `main`.

## Achado G34-F1: campo arbitrário em relação documental

O validador `validate_institutional_chain()` verificava apenas `(from, to, relation, printed_page)`, mas devolvia os objetos originais completos em `institutional_links`. Uma contraprova **sintética**, adicionando `norad_528_terminal_epoch_utc: 1963-11-08T12:00:00Z` à primeira relação, passou pela validação e apareceu no JSON público derivado. Um segundo mutante duplicou `C179#1` em `relevant_occurrences` e também passou, apesar de representar contagem documental enganosa.

A correção exige exatamente os quatro campos autorizados em cada relação e quatro IDs únicos na ancestralidade. Dois testes novos falharam antes da correção e passaram depois; os 13 testes anteriores e `--check-site` passaram sem modificar os fatos, dados ou artefatos publicados. **Nenhuma medição terminal real estava no corpus:** a falha dizia respeito à integridade do consumidor, não a fraude comprovada nos originais.

## Restrições científicas e editoriais

- #401 e #409 associam valores impressos SSR e um relatório institucional de 1965 (sobre acordo de 1961), sem recuperar proveniência instrumental por objeto; não atribuir medições de 527/529 a 528.
- #402 liga origem meteorológica a recortes de catálogo sem comprovar radiossonda no local do evento.
- #403 usa um contraexemplo algébrico declarado hipotético: ausência de identificabilidade não é prova de impacto ou de impossibilidade física.
- #405 e #406 usam geografia/lei publicadas em 2017/2020, sem demonstrar limites urbanos de 1963.
- #410 testa 72 direções sintéticas do envelope STM, sem cobertura probabilística nem validação instrumental; #411 exibe TLE **secundário** com hash, não fonte original.
- #412 é responsividade editorial e #413 narrativa baseada nos documentos da família NASA, sem observação terminal adicional. #408 protege eventos de CI, não autentica fontes.

**Resultado:** nenhuma hora, posição de reentrada ou queda em Conde é demonstrada. Reproduzir fonte primária com data, página, hash e incerteza continua prioritário. A PR G34 preserva o grafo histórico, restringe o contrato de validação e não publica no blog pessoal.

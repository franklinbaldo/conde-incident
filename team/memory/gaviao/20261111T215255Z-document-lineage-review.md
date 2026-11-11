---
type: AgentMemory
title: "Gavião: CI Zola revisado e raízes documentais, não testemunhas independentes"
description: "PR #23 empilhada na #18; NASA e FBIS reinspecionadas; #3 corrigida/CI verde, integração com #1/#10 pendente; 11 contraprovas documentais"
agent: gaviao
timestamp: "2026-11-11T21:52:55Z"
tags: [conde, gaviao, proveniencia, zola, fbis, nasa, falsificacao, editorial]
---

## Retomada e mudança

**Issue exclusiva [#16](https://github.com/franklinbaldo/conde-incident/issues/16)**; [PR anterior #18](https://github.com/franklinbaldo/conde-incident/pull/18) mantém o ledger. Abri a [PR empilhada #23](https://github.com/franklinbaldo/conde-incident/pull/23) sobre a branch da #18, sem conflito com arquivos da Coruja, com [grafo](https://github.com/franklinbaldo/conde-incident/blob/gaviao/document-lineage-falsification-16/research/gaviao_document_genealogy_2026-11-11.json), auditor verificável, 11 contraprovas, relatório e workflow de CI no HEAD exato. Código antes desta memória: commit `961b3fbaac1c358ae29421d9c6d59750e414c79a`; a própria memória muda o HEAD, portanto revalidar **somente no SHA final**. Não afirmar PASS antes dos logs.

## Verificações de fontes / independência

Reabri imagens do [NASA 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), impressa 8/PDF index 9: `1963 3B / 8 NOV 63`, **sem hora/local**; e [FBIS 03](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), com esfera/cratera/corpo/inscrições no único relato Tupi→FBIS. **Grau:** fac-símiles contemporâneos visualmente reinspecionados; FBIS é transcrição, não áudio/corpo físico. Hashes de PDF **NOT_COMPUTED** (download binário falhou). C111/C117 da matriz já registram TV Tupi SP, sem nova leitura integral minha; Blue Book C232 é texto anteriormente extraído, **sem fac-símile/dossiê verificado**. Dependência A-628→Blue Book e NASA↔NORAD continua hipotética, não comprovada.

## Revisões e limites

[PR #3](https://github.com/franklinbaldo/conde-incident/pull/3), HEAD `c84cce85e51252f9e589a851950385aea008e951`, corrigiu fonte FBIS/falsa cronologia e migrou site para Zola 0.22.1. [Run #43105157197](https://github.com/franklinbaldo/conde-incident/actions/runs/43105157197) **SUCCESS build**, deploy **SKIPPED**. Parecer favorável em comentário de revisão `5865713080`; tentativa de APPROVE formal rejeitada pelo GitHub (422, autor da própria conta). Condicionar integração à #1 (ResearchLedger e avisos científicos) e #10 (evitar leitor React duplicado), com CI no SHA reconciliado. [PR #12](https://github.com/franklinbaldo/conde-incident/pull/12) continua empilhada/mergeability falsa e CI sem PASS; [#21](https://github.com/franklinbaldo/conde-incident/pull/21) não confirma GMT em FBIS de 1963.

## Próxima dúvida

A Coruja/Elefante reconciliou Zola com a base científica sem expor horários de passagem arbitrários como medições? Conseguiu fonte primária específica de 1963 para decodificar `W` e indicar a genealogia da notícia? Verificar CI da #23 no **HEAD final**, e não confundir PASS de estrutura com constatação de queda/HOAX, massa, longitude, satélite real ou informação live.

Sem blog pessoal, merge, deploy, contato externo, rebase ou force-push.

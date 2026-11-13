---
type: Guide
title: "G31: 15 integrações e corte cronológico do holdout"
description: "Auditoria retrospectiva SHA-a-SHA, genealogia, checks e contraprova de vazamento cronológico em #354."
---

# G31: auditoria retrospectiva independente

**Janela congelada:** `d73e66678dbaf0583064f88da7e4702baeb7d5b0..4863347fba222da572827cf38bb867e7d5cc6336`, corte 13/11/2026 03:38:29Z. O [manifesto tipado](gaviao-main-window-20261112-g31.json) registra todos os 15 SHAs, pais, PRs, HEADs autorais, arquivos, checks e parecer de cada integração: #343, #344, #346, #347, #349, #350, #352, #353, #354, #355, #356, #335, #357, #358 e #360. `git rev-list --first-parent` e DAG completo concordam: **15 squash, zero commits laterais, diretos ou merges convencionais**. Busca delimitada de PRs fechadas sem merge não identificou fechamentos nesse intervalo; não é prova de ausência em todo o histórico.

**G31-F1, confirmado por contraprova sintética:** a PR #354 introduziu um gate de elegibilidade de fontes para inferência estatística que só verificava disjunção e contagem dos membros do holdout, sem verificar os cortes calendáricos declarados. Trocar um epoch de **528** em validação de `1963-08-03T16:23:49.393248Z` por outro em avaliação de `1963-10-02T16:35:51.689472Z`, preservando os mesmos 119 instantes e contagens de blocos 61/23/35, **passava** pelo `build()`. Isso contaminaria a interpretação do desenho retrospectivo, **não prova que o corpus original tenha sido adulterado**. Dois testes adversariais reproduziram o erro antes do reparo. A correção fixa os limites `fit < 01/08`, `01/08 <= validation < 01/10`, `evaluation >= 01/10`, em UTC de 1963, e rejeita alteração do contrato de limites. Nenhum número orbital ou data histórica foi inventado.

**Autenticidade documental:** #346/#347 usam um volume IBGE de 1958 e oito fotografias da mesma família editorial, sem época de cada câmera nem geocodificação de Conde em 1963; #349/#344/#356 tratam três replays Wayback NASA como cópias de **um** boletim e C197/C198 como duas ocorrências de uma obra, não sensores; #355 identifica prefixo PDF ON20 de julho de 2008 e dois arquivos completos posteriores. #350 impede confundir WMO 82899/82900. #352 impede ler o designador de grupo `1963-3` de NASA SP-4004 como o componente 528. A integridade dos bytes HTTP originais não foi reatestada nesta auditoria.

**Lean e física:** #356 inclui condições tipadas de proveniência no Lean 4.35.0, sem novo evento orbital, com `eventTimeUtc = none`; #335 transfere covariância 6D com `Rdot` apenas quando há estado/erros condicionais, sem medições reais de 528 nem incerteza de frame calibrada. Inspeção de `sorry`/`axiom` no arquivo novo: sem ocorrências; `#print axioms` independente **NOT_RUN**, e CI Lean não autentica premissas. #354 registra elegibilidade **zero nos insumos examinados**, não inexistência histórica de sensor. Nenhum domínio θ demonstravelmente encolhido.

**Software/editorial:** #343/#357 melhoram a navegação SSG mas build não é comprovação de deployment; #353 corrige lista YAML multilinha de CI. #358 retira a falsa hora terminal 19:48 UTC da comparação com objetos irmãos. #360 preserva manchete do *Jornal do Brasil* de 9/11/1963 como documentação **de uma explicação atribuída**, usa transcrição derivada para parte do texto e não declara balão recuperado; crônica de Stanislaw de 14/11 é posterior. Nenhum PDF secundário cria testemunho independente.

**CI observado por SHA:** o manifesto distingue SUCCESS, SKIPPED e CANCELLED por HEAD autoral e SHA de merge. Pós-merge #349, #350 e #354 registraram Pages CANCELLED com 18 SUCCESS, em vez de afirmar tudo verde. A consulta não autenticou registros históricos. Testes locais da correção: 14/14 focados + `--check` PASS; demais suites/CI devem ser verificados no HEAD final da PR. Nenhuma alteração do blog pessoal.

**Resultado:** CONDE INDETERMINADO. NASA 8/11/1963 é dia de catálogo do componente B, não instante/posição terminal; divergência RAAN 284,152° versus TLE secundário ~198,526° ainda sem cadeia instrumental primária. A próxima auditoria começa após `4863347f`, incluindo esta PR quando integrada e merges concorrentes.

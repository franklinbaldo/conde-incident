---
type: Guide
title: "G30: 11 integrações e verificação independente do PDF NASA atual"
description: "Auditoria SHA-a-SHA dos merges após G29, fontes, CI e contraprova do replay da API NASA."
---

# G30: revisão retrospectiva do Conde

**Intervalo fechado:** `b3a632d6da60c9b054473b89211579cbb488d525..d73e66678dbaf0583064f88da7e4702baeb7d5b0`, corte observado em 13/11/2026 02:26:14Z. O [manifesto tipado](gaviao-main-window-20261112-g30.json) contém SHA, first-parent, PR, HEAD autoral, arquivos e estados CI **para cada integração**. A comparação GitHub contou **11 commits**, todos squash de #326, #328, #329, #330, #331, #332, #333, #334, #337, #338 e #340; zero merges convencionais, laterais ou commits diretos. A consulta de PRs fechadas sem merge retornou apenas casos antigos, sem novo fechamento identificado nesta janela.

**Auditoria de CI:** na consulta `GET /commits/<sha>/check-runs`, cada um dos 11 SHAs integrados apresentava **19 SUCCESS / 19 checks**. Cada HEAD autoral apresentou **18 SUCCESS + 1 SKIPPED / 19 checks** (exceto #337, **19 SUCCESS + 1 SKIPPED / 20 checks**). `SKIPPED` é preservado como estado distinto; CI verde não autentica documentos. Os SHA de autor foram conferidos com metadados individuais de PR. A execução local do clone e do Prek não atesta esses SHAs.

## Quatro dimensões científicas

**Autenticidade documental:** #326 preserva origem de imagem municipal de 2021 sem bytes integrais, data da fotografia ou coordenada; #334 agrega oito fotografias de uma **única obra IBGE de 1958**, páginas PDF 180–183 e impressas 185–188, sem atribuir época das fotos. A verificação programática de hashes externos e a inspeção visual independente do PDF são **NOT_RUN** nesta auditoria. #329 examina presença/ausência de estação no WWR NOAA de superfície, que não fornece vento alto no dia; #330 e #340 tratam replays Wayback como cópias de um documento, não testemunhas instrumentais independentes.

**Lean e dependências:** #333 registra identidades MOR NORAD 687/688/943 e datas 1961/1963/1964 como **contexto** sem aresta de medição do 528; a geração tipada e o CI Lean não certificam premissas físicas. Revisão independente de `#print axioms` e reexecução local Lean 4.35.0: **NOT_RUN**. #328 impede transformar lacunas de linhas de TLE secundário em não detecção instrumental ou verossimilhança de sobrevivência.

**Software, CI e representação:** #331 impõe testes da política universal de eventos; #332 corrige a autoria de negativos Wayback. #337 oferece links diretos aos PDFs antes dos iframes. #338 distingue no PT/EN o TLE secundário C179#1 do 528 dos vetores **ilustrativos** do 527/529, mantendo o boletim NASA 1964 apenas como contexto do 527.

**Conclusão física e jornalística:** o dia NASA 08/11/1963 para 1963-003B não equivale a instante terminal nem prova impacto. A matriz, as restrições Lean e os cenários não estabeleceram um domínio físico calibrado, não vazio e reduzido com holdouts externos. Conde permanece **INDETERMINADO**. Nenhum conteúdo pessoal publicado.

## Achado G30-F1: verificador não consulta a API NASA corrente

Em #340, `tools/verify_nasa_ssr_legacy_wayback.py --fetch` afirmava comparar as três capturas históricas com a versão **atual** da API NASA, mas iterava apenas sobre os três `archived_url`. A igualdade dos hashes arquivados com um campo JSON da API é apenas coerência do manifesto; não é replay independente da versão corrente.

**Contraprova sintética (sem alegação histórica):** mock das três respostas Wayback preserva sucesso; quarta resposta, da API NASA, retorna bytes alterados. No código anterior eram feitas somente três requisições, com saída 0. A correção exige quarto request e reprova byte count, SHA-256, HTTP, MIME e delimitadores PDF. Testes adversariais em `tests/test_nasa_ssr_legacy_wayback.py`; `--fetch` é opcional por depender da rede, portanto **nenhum replay ao vivo deve ser declarado PASS apenas com CI offline**. O resultado original de 2026 permanece como observação da autora, não foi refutado por bytes externos nesta rodada.

**Próximo passo:** conferir o CI no HEAD exato da PR de correção, depois no commit da main; autenticar externamente, quando houver acesso, os bytes PDF NASA corrente e IBGE 1958. A próxima janela começa em `d73e6667`, incluindo a integração da própria correção e qualquer merge concorrente.

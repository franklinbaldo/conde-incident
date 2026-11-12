---
type: Guide
title: "G20 · retrospectiva integral de 14 merges e contraprova de ancestralidade documental"
description: "Janela first-parent G19→G20, auditoria de fontes, TLE, Lean, CI e correção da validação de caminhos declarados."
---

# G20 · Auditoria científica/editorial retrospectiva

**Corte anterior confirmado no OKF privado G19:** `9e6596c679985b2cc886e31d88969fd9eab16b18`. **HEAD congelado da main:** `5c2f610d624a79dab9b4b181851d8fe2883868f5`. A comparação do GitHub retornou **ahead 14, behind 0**, 14 squashes e **nenhum commit direto**. O [manifesto JSON](gaviao-main-window-20261112-1244.json) preserva cada SHA principal, pai, PR, HEAD de autor, caminhos e contagem de workflows. São **62 alterações de caminho, em 60 arquivos distintos**. A PR **#22** foi fechada sem merge durante a janela (15:26:02 UTC); não é commit de main.

**Ordem cronológica confirmada:** #150 → #151 → #152 → #153 → #154 → #155 → #160 → #157 → #159 → #161 → #163 → #162 → #164 → #166. Os 14 HEADs de autores tiveram todos os runs `pull_request` retornados como SUCCESS: respectivamente 10, 11, 10, 10, 10, 11, 10, 11, 12, 12, 12, 12, 13 e 13. Isto certifica execução de software, não autenticidade histórica de fontes.

## Achado G20-F1: um caminho documental que não começa na fonte citada

**Introdução #163 / dependência #155.** O novo painel React mostrava caminhos ancestrais declarados por `conde-declared-dependence.json`. A validação verificava apenas que cada aresta tinha três strings, sem garantir que a primeira `from` fosse a fonte do registro, que os nós seguintes se encadeassem até `upstream_source_id`, que não houvesse ciclos ou que `snapshot_ref` fosse único. Assim, uma cópia do feed com `FBIS_EOP_UAP_D001` apontando para uma aresta que começa em `NASA_SSR_19631115` satisfazia a validação estrutural antiga e podia aparecer na interface como ancestralidade declarada, sem sustentação do grafo.

**Contraprova e correção:** `scripts/gaviao-retrospective-g20.test.mjs` tenta (i) origem alheia, (ii) passo desconectado, (iii) destino falso, (iv) ciclo, (v) linha duplicada, (vi) snapshot diferente e (vii) ocorrência sem `#n`. A nova verificação em `src/lib/sourceCitationAudit.ts` falha fechada antes de renderizar. O feed original continua aceito, inclusive fontes sem arestas declaradas: **ausência de aresta não implica independência**. Testes sintéticos não autenticam a fonte externa.

## Auditoria em quatro eixos

**Autenticidade e dependência:** #153 reforça que URLs NASA com query/fragment não criam fontes independentes. #155 exporta genealogia, #163 a exibe; ambos descrevem relações documentais, não sensores. #160 acrescenta cartografia de Aracaju datada de 1954 com atualizações até 1961, sem confirmar um limite municipal de Conde em 1963. #164 registra indexação Smithsonian RU478 e história da estação SC-8 (Shiraz), mas não recupera medição angular original NORAD 528, dados de filme nem custódia de relógio de 1963. O fac-símile NASA C197 já custodiado indica somente **8 NOV 63** como dia de decaimento. Esta rodada **não reabriu independentemente** os bytes originais externos NASA, RU478, IGRA ou Parquet; distingue leitura de arquivos versionados de autenticação primária.

**Restrições Lean:** #157 transporta custódia do binário NMC Y20175 a nove consultas **latentes**, não nove perfis observados. Não há novo teorema que ligue medida instrumental autenticada à posição terminal. Prova formal continua condicional; sem testemunha de domínio físico não vazio e reduzido.

**Método numérico:** #151 valida n-dot/2 e BSTAR na **representação TLE secundária**, não arrasto físico; #166 computa secantes de `n` em pares de épocas do mesmo espelho, sem estimar derivada física instantânea. #159 extrai um perfil NOAA IGRA de Recife (26 níveis, 15 ventos relatados), mas `HOUR=12` é nominal e `RELTIME=9999` significa **hora real ausente**. #161 introduz gate para posição cartesiana com data instrumental, frame, incerteza e calibração declaradas; devolve explicitamente `historicalHoldoutValidated=false`. Nada disso reduz numericamente, com holdout físico, o domínio terminal de 528.

**Editorial e CI:** #150 introduz Prek OKF e 20 KB com hashes congelados para legado; *incremental* não equivale à migração completa. #154 separa reprodução GIS offline da consulta IBGE live; evita tomar instabilidade de rede por falsificação científica. #162 testa a geração do bootstrap privado, não verifica todo o provisionamento real. #152 corrige identidade de tentativas/status Pages, mas **não prova publicação**. Nenhum arquivo `stories/*.md` entrou na main desta janela. Cadernos em PRs draft continuam fora da main e não foram publicados por esta auditoria.

## Resultado e próxima dúvida

**INDETERMINADO para Conde.** Nenhuma hora, coordenada, trajetória de queda, probabilidade ou exclusão geográfica foi derivada. Próximo passo verificável: localizar observações primárias com época e incertezas instrumentais para 527/528/529; apenas então formular predicados físicos Lean e simulação calibrada com holdouts. A análise editorial da Coruja permanece independente de aprovação prévia; autores podem integrar PRs verdes. Nenhum blog pessoal foi tocado, não houve contato externo nem reescrita de histórico.

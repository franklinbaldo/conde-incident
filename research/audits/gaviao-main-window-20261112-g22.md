---
type: Guide
title: "G22: 13 integrações first-parent, duas ancestrais laterais e contraprova de HTML"
description: "Auditoria retrospectiva SHA-a-SHA de C241, meteorologia, A-628, Lean/numérico, CI e publicação HTML, sem inferência de impacto."
---

# 🦅 G22: revisão retrospectiva, sem inventar observações

**Janela fechada:** `86cf4e2cec271532b95a134623150539a0926b07` → `c9523ba0e65dd0002323d3ede1bbb60bc762a618`, [comparação GitHub](https://github.com/franklinbaldo/conde-incident/compare/86cf4e2cec271532b95a134623150539a0926b07...c9523ba0e65dd0002323d3ede1bbb60bc762a618). O manifesto [G22 JSON](./gaviao-main-window-20261112-g22.json) preserva os SHAs completos, pais, arquivos, heads autorais e checks.

**Reconciliação do DAG:** são **13 integrações na linha first-parent** da main: #184, #185, #186, #190, #193, #192, #189, #194, #195, #196, #197, #199, #187. Destas, **12 são squash e #185 é merge de dois pais**. O resultado `compare` soma **15 commits**, incluindo `a7fbbc41` e `51b244cc` no segundo ramo da #185. Esses dois commits não são edições diretas da main. Nenhuma outra alteração direta ou PR fechada sem integração apareceu no intervalo. Conferidos `parents` e pertença GitHub de #185.

## Auditoria por domínio

**Documentos e dependência:** #197 separou data datilografada de A-628 (20/11/1963), carimbos 24/26/11 e ano conflitante no assunto (1964), sem atribuir função de protocolo ou acontecimento físico aos carimbos. #194 corrigiu o período nodal da linha NASA 1963 3A no boletim de 30/11 para 94,6 min, contra 94,8 no grafo derivado anterior; sem época instrumental, não é derivada temporal. #186 custodiou 80 JPEG IIIF de mapa UWM, não o JP2 original nem uma divisa de Conde autenticada em 1963. #189 ajustou OKF da Abelha sem provar provisionamento universal. A autenticidade de todos os originais não foi reinspecionada por download nesta rodada; a revisão cotejou arquivos versionados, referências e testes.

**TLE / inferência:** #199 preserva o conflito do vetor legado RAAN 284,1520° com o espelho secundário ~198,5261°, comparando seis elementos por registro e tolerâncias **somente de serialização**, não de sensores. #192 congelou ajuste de RAAN em dados secundários 527/528/529, com validação cronológica dependente da mesma linhagem e sem cegamento histórico. #193 testou diagnósticos MCMC em cadeias sintéticas, **não** gerou posterior para Conde. #195 mede resolução numérica relativa ao sigma declarado apenas no caso cartesiano condicional, não produz prova de precisão instrumental. Não surgiram época, frame, incerteza e rastreio original simultâneos suficientes para reduzir `Θ` nem validar holdout físico.

**Meteorologia / equações:** #184 calculou 42 diferenças vetoriais de ventos observados nas 3 sondagens nominais de Recife (7–9/11/1963), com tempo real de soltura desconhecido, sem transferência a Conde nem extrapolação à termosfera. A restrição permanece `CONNECTED_PENDING_SPATIOTEMPORAL_TRANSFER`. Nada nas novas relações demonstra queda ou exclusão de Conde.

**Editorial / integração:** #196 removeu da síntese UI hora, porcentagem e conclusões consulares sem respaldo. #185 introduziu workflow de Pages; #190 corrigiu a base de assets após falha de gate; #187 corrigiu pseudo-elementos em comentários/template/script. Nenhum desses registros CI prova publicação efetiva ou autenticidade histórica. **G22-F1:** uma string de pseudo-elementos dentro de `data-snapshot='...'` ainda passava nas expressões regulares da #187. Corrigimos com leitura de tags respeitando aspas, testes contra `a`, `link`, `article` e `script` falsos e controle positivo. Gate metadata permanece obrigatório.

**CI real:** todos os heads de PR acima foram consultados; #193, #194 e #195 tiveram **13/14** workflows `SUCCESS` e uma execução `Publish Conde site` `CANCELLED`. Não apresentamos isso como 14/14. As outras dez PRs tiveram 13/13, 14/14, 15/15 ou 16/16 conforme manifesto. Esses estados não dispensam testes da correção G22 no SHA final nem autorizam revisão de fatos sem originais. Sem PR fechada sem merge na janela após `86cf4e2c` (a #171 foi anterior).

## Quatro portas científicas

Autenticidade: alguns fac-símiles foram reinspecionados pelos autores, mas não houve nova verificação independente de bytes originais nesta rodada. Lean 4.35: teoremas e predicados continuam condicionais, sem autenticação de fontes ou nova proposição que determine posição terminal. Simulação: melhorias numéricas são condicionais, sem holdout físico medido. Exclusão/identificação: a data de decaimento catalogada de 8/11/1963 não informa hora e lugar, e o boletim de 110 minutos refere-se ao **NORAD 688, não 528**. Status **INDETERMINATE** para Conde.

**Próxima pergunta:** recuperar pares instrumentais originais de 527/528/529 (UTC, referencial, covariância, estação/linhagem) e testar holdouts sem reciclagem de observações. As novas conexões documentais permanecem rastreáveis, mas não foram promovidas a restrição física ativa. Esta auditoria não alterou blog pessoal, não realizou publicação nem contato com arquivos/pessoas.

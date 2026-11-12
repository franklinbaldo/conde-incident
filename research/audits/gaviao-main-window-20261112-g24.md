---
type: Guide
title: "G24: dezessete integrações, seis commits laterais e falsificador do antimeridiano"
description: "Auditoria retrospectiva do Conde no intervalo 07e9a820..a52b4e7, com revisão científica, editorial, CI e correção cartográfica reproduzível."
---

# 🦅 G24: auditoria retrospectiva e contraprova de geometria

**Corte imutável:** [`07e9a820...a52b4e7`](https://github.com/franklinbaldo/conde-incident/compare/07e9a820aa769c2e5fc643511badb9c9449f8271...a52b4e757198d24a3a29a058438abe891d74c54c), do checkpoint privado G23 até a `main` observada às 16:44:14 de 12/11/2026, horário America/Porto_Velho. [Manifesto JSON SHA por SHA](gaviao-main-window-20261112-g24.json). **17 integrações first-parent:** 15 squash, **dois merges convencionais** (#225 e #228) trazendo **seis commits laterais**; `git rev-list` encontrou 23 commits no DAG e nenhum commit direto adicional na linha principal. Os 17 HEADs autorais foram relacionados aos PRs integrados; a consulta GitHub às PRs fechadas no intervalo encontrou estas 17 e a #198 no instante da borda inferior, já pertencente a G23. Não foram encontradas PRs fechadas sem merge nessa janela de consulta; a conclusão limita-se à consulta.

## Cobertura sem saltos

| PR | Merge abreviado | Revisão científica/editorial e resultado |
|---|---|---|
| #221 | `0cf640f` | Correção G23 de falsos atributos HTML: preservada, sem prova criptográfica dos bytes HTTPS. |
| #222 | `f529b4b` | 22 níveis úmidos calculáveis no IGRA Recife, mesma linhagem; sem transporte calibrado a Conde. |
| #224 | `9f692dc` | MCMC de fase RAAN sintético versus quadratura; o gauge sem âncora permanece não identificável. |
| #225 | `1afb606` | Merge convencional: documentos NORAD 687/688/943 não são observações do 528. |
| #226 | `e02ab16` | Estrutura COS/CRAY Y20175; 43.521 palavras de controle, mas ON20/estação/data não decodificados. |
| #228 | `86ab5e7` | Merge convencional: mapa IBGE nominal 1960, polígonos nativos projetados, não limites legais de 1963. |
| #229 | `97d13b6` | Covariância 3N declarada pode alterar ordenação de holdout r/v; nenhum sensor autenticado. |
| #230 | `805cbb1` | J2 com deriva FIT-only: piora 527, melhora 528/529 no catálogo secundário. |
| #231 | `d26bd41` | Controle quadrático FIT-only: melhora no 527 contra J2, não comprova lei orbital. |
| #114 | `ac07799` | Localizadores SAO de 1963; Natal Baker–Nunn somente após 1966 segundo cronologia institucional. |
| #232 | `8cce69e` | Restabeleceu frontmatter OKF do documento SAO integrado. |
| #235 | `84150d8` | Coruja Caderno 02 remete a códigos/testes históricos com SHA; não inventa impacto. |
| #233 | `424516e` | SVG local sem Google Maps; defeito G24-F1 no corte do antimeridiano de longitudes não normalizadas. |
| #236 | `d9a6e59` | Retirou interceptação global obsoleta de quota Google; cenário continua não observado. |
| #218 | `9dabab1` | C241-L9: altitude_km pode derivar de n,e em 119 épocas; sem ETL original e sem observação adicional. |
| #237 | `97df80d` | Link de salto preserva `#/map` e foca landmark, sem alterar hipótese científica. |
| #238 | `a52b4e7` | Smoke Chromium desktop/móvel e teclado; check de navegação visual, não medição histórica. |

**Fontes/independência:** as referências NOAA IGRA, IBGE, NASA NTRS, Smithsonian e espelho Space-Track foram confrontadas com IDs, hashes e escopos *declarados nos arquivos*, e os testes locais de custódia e adulteração escolhidos foram executados. Não houve novo download/autenticação independente de fac-símiles primários, ZIP IBGE, binário NCAR ou Parquet TLE nesta revisão. A cadeia NASA/NORAD e as notícias Tupi/FBIS continuam sem independência física demonstrada; inventários SAO não são leituras óticas. O mapa IBGE em coordenadas World_Polyconic/SIRGAS2000 não substitui fronteira administrativa comprovada em 1963.

**Lean, simulação e estatística:** a validação Lean no CI valida implicações *condicionais* e axiomas do projeto, não reentrada observada. Os ensaios #224, #229, #230 e #231 incluem falsificadores sintéticos/retrospectivos: gauge angular livre sem âncora, covariância declarada não calibrada, controle 527 com piora do J2 derivativo e quadrático competitivo. Os proxies de movimento médio e altitude #218 dependem do mesmo registro secundário, não criam novo sensor. Nenhum dos quatro eixos (autenticidade instrumental, coerência Lean, integração numérica, limite da inferência) demonstrou `Θ` não vazio e **estritamente reduzido** por observação física autêntica; preservar as arestas como `CONNECTED_PENDING_CALIBRATION`.

## G24-F1: a projeção pode desenhar uma linha continental fictícia

No código da PR #233, `projectFlat()` normaliza longitude, mas `splitDateline()` testava a diferença **antes** de normalizar. Com entradas sintéticas `(179°, 0°) → (181°, 1°)`, ele retornava um único segmento. A projeção passava de `x=957,33` a `x=2,67` no viewBox de largura 960, gerando um traço falso atravessando quase todo o mapa. O contrário ocorria com −179° → −181°. É um problema de representação, **não evidência de sobrevoo ou coordenada histórica**.

**Correção isolada:** normalizar cada longitude em `splitDateline`, preservando demais campos, antes de decidir corte; adicionar dois contraexemplos e o controle de segmento que não cruza a costura em `tests/quota-free-map.test.mjs`. Teste adversarial do código original: **FAIL esperado**, com saída explícita de `x=957,33→2,67` em um segmento; nova implementação: **PASS**. Esse controle impede um risco de visualização convincente e geograficamente falsa, sem modificar TLE ou simulação física.

## Execução e limites

- **Python no clone `a52b4e7`: 71/71 PASS** em oito suítes: COS 7, altitude 14, J2 P3 6, quadrático 6, crosswalk NORAD 6, IBGE 14, IGRA 8, MCMC 10. Todos são controles de software/documentação, não autenticação física.
- **Node em arquivo único com correção G24: 8/8 PASS**, executando `node tests/quota-free-map.test.mjs`; `git diff --check` PASS. `node --test` e os testes de covariância TS em Jatobá não foram concluídos por limite RSS do executor, registrados **NOT_RUN** e delegados ao CI real no HEAD da PR.
- **CI autoral das integrações da janela:** a API GitHub retornou 16 sucessos cada para #221/#222/#224/#225/#226/#228/#229/#232/#235/#233/#236/#237; 17 cada para #230/#231/#218/#238; a #114 teve oito sucessos retornados. Esses são runs `pull_request` associados ao SHA autoral, não substituem validação pós-merge. O workflow Lean não foi executado de forma independente em Jatobá nesta rodada.
- **Prek pessoal:** hook `pre-push` instalado no snapshot privado local, mas `prek run --all-files` consumiu mais memória que o limite Jatobá e foi interrompido; não se declarou PASS nem se enfraqueceu o gate. A validação obrigatória da casa deve vir do workflow `OKF all Markdown` no SHA final da memória.

**Veredicto:** `CONDE_INDETERMINATE`. Não existem, nesta revisão, tempo/posição terminal demonstrados, coordenadas de queda ou probabilidade sustentada. Próximos testes: obter rastreio original de 527/528/529 com época, referencial, estação e erro; realizar holdout fisicamente independente; só então considerar restrição Lean e redução numérica de domínio. O blog pessoal não foi alterado e nenhuma pessoa/arquivo foi contatada.

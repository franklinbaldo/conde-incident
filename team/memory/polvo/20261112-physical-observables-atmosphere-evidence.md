---
type: AgentMemory
title: "Parâmetros livres → observáveis físicos → evidência meteorológica"
agent: polvo
date: "2026-11-12"
repo: "franklinbaldo/conde-incident"
status: "crosswalk-model-validated; no historical geographic restriction"
tags: [conde, observables, C179, C151, NOAA, wind, physical-constraints, mcmc]
---

# O que mudou de fato

O proprietário definiu que os parâmetros livres devem ser transformados por fórmulas físicas em novas grandezas com unidades, épocas e localizações, para confrontar fontes independentes e restringir a inferência. A reação ideal a dados de tempestade não é assumir incompatibilidade com uma reentrada: testar em que **etapa física** o vento age (deriva de balão ou fragmento após desaceleração), com massa/área/arrasto e incertezas.

## Fontes e linhagens

- C179#1, linha 839 da matriz cumulativa PR #1, blob `a7978c3a75a153b16ab70118a92c434bba674cb7`: 528 época `1963-10-27T14:40:16.132512Z`, RAAN 198,5261°, i 81,8615°, e 0,0017147, n 15,74901460 rev/dia. Espelho https://www.itau.magnetic-declination.com/satellite/?s=528, par literal SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9b7b6330b9c44e341cd` (**ATENÇÃO**: em registros de contrato e custódia o SHA-256 correto é `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`; esta linha única deve ser conferida com o arquivo da PR #14). Deriva de mesma cadeia oxzoid/AFSPC; não instrumento primário.
- C151#1, linha 606, fonte histórica instrumental NOAA/NCEI IGRA Recife `BRM00082900`: https://www.ncei.noaa.gov/pub/data/igra/data/data-por/BRM00082900-data.txt.zip; transcrição na matriz dos 5 níveis de 08/11/1963 (850/700/500/300/250 hPa, 4/4/6/15/17 m/s). Horário `12 UTC` nominal; `RELTIME=9999`, hora real do lançamento não informada. Dados novos para **Recife**, não Conde; cinco níveis da mesma observação/arquivo, não cinco fontes. O pacote original NOAA foi baixado e examinado pela pesquisa anterior, **não relido nesta fatia**.
- C144#1/C145#1/C146#1: Marinha do Brasil DHN/CHM cartas sinóticas 8–9/11/1963 https://idem.marinha.mil.br/geonetwork/srv/api/records/9ea5e9a4-199d-4d14-8b55-682eb4daa211/attachments/Nov_1963.pdf ; arquivo documental independente da notícia, não vento local em altitude.
- C131#1/C197#1: **uma fonte** NASA/Goddard *Satellite Situation Report* 15/11/1963 p.8, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf, dia de decaimento catalogado, não hora/local do impacto.

## Entrega e testes

- `formal/scripts/physical_observable_bridge.py` [commit `0904e28b`](https://github.com/franklinbaldo/conde-incident/commit/0904e28b2190193361fb637c0f6852ac1f93fe97): extrai ventos diretamente da ocorrência C151 da matriz **SHA fixo**; testa fonte/níveis; transforma `p[hPa]→p[Pa]`, vento meteorológico “from”→velocidade `u_leste,v_norte`. Para a referência secundária 528, calcula `n[rev/day]→rad/s`, `a≈6723,05 km`, `h_p≈333,38 km`, `dotΩ_J2≈−1,173124071°/dia`; todos números derivados, sem erro/custódia instrumental novos.
- `formal/tests/test_physical_observable_bridge.py` e CI `.github/workflows/science.yml`: six explicit additional tests, including prova de que velocidade de descida dobrada reduz pela metade a deriva sob **mesmo perfil** e de que não há transferência direta Recife→Conde. Documento `formal/physical_observable_crosswalk.md`, commit `ac5d5495c6b476db25758a2f71e89e5328185ef6`, expõe todas hipóteses e limites.
- **Fatia reproduzível:** sob velocidade descendente **assumida** de 50 m/s entre níveis aproximados 11 km e 1,56 km do perfil de Recife de 08/11: `dt=188,8 s`, `ΔE≈−871 m`, `ΔN≈+1000 m`, módulo ≈1.326 m. Não cobre a altura até o solo nem faz previsão de um fragmento 528. Uma alteração de rapidez de descida 50→100 m/s divide esse deslocamento condicional pela metade, isolando a sensibilidade.
- [Scientific checks #43200838234](https://github.com/franklinbaldo/conde-incident/actions/runs/43200838234), SHA `04534c79966c396ff6fd5d0fd5bd42fe0a5d8ba2`: **SUCCESS 2/2** Web+Lean; `lake build`/axiom audit, **59 testes Python PASS**, export JSON `conde-physical-observables.json` com `physical_domain_reduction=NOT_RUN,weather_at_conde=NOT_VERIFIED`. O CI do commit final pós-documentação/memória precisa ser consultado separadamente, sem herdar status antigo.
- Na [PR #28](https://github.com/franklinbaldo/conde-incident/pull/28), `AGENTS.md` e `team/polvo.md` foram atualizados com grafos de observáveis e gates geográficos (commits `861296d61844bc9419a714c273b2bc24c28602f7`, `716ef7e4f94c56a3d985b8fd44192fbb9c5b117d`). A [issue #15](https://github.com/franklinbaldo/conde-incident/issues/15) recebeu nova fronteira científica. Handoff ao Castor [PR #5](https://github.com/franklinbaldo/conde-incident/pull/5#issuecomment-6821223470) para consumir o JSON e só aplicar restrições geográficas após validar fonte, transferência, massa/área/Cd e erros.

## Negativos, lacunas e próximo teste

**REDUCAO_DOMINIO_528=NOT_RUN. TEMP/MASSA/ARRASTO=NAO_CALIBRADOS. PERFIL_LOCAL_CONDE_1963=NAO_RECUPERADO. TRANSFERENCIA_RECIFE_CONDE=NOT_VERIFIED. MCMC_HISTORICA=NOT_RUN. EVENTO_TERMINAL=INDETERMINADO. ORIGINAL_ZIP_154_151=NOT_RUN.**

O próximo teste útil exige vento e temperatura por altura, localização e hora da Bahia com erros de representatividade (ou reconstrução regional validada); massa/Cd/área e velocidade terminal do objeto hipotético; e estado orbital 528 admissível. Transformar esses dados em resíduos observáveis e limites, comparar contra baseline e holdout e mostrar domínio não-vazio antes/depois. Não contar unidade nova como nova evidência nem o vento Recife como restrição dura de Conde. Nenhuma pesquisa geral de arquivo, blog, publicação, merge, contato externo, rebase ou force-push nesta rodada.

🦅 Gavião revisa; 🐘 Elefante integra após CI do HEAD e revisão.

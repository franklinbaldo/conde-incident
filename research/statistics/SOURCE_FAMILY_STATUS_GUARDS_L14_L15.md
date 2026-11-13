---
type: Guide
title: 'C241-L14/L15: elegibilidade estatística de catálogos derivados e grupo anual NASA'
description: 'Auditoria fail-closed do vínculo 1963-3 versus 1963-003B e da independência instrumental, sem posterior histórica.'
---

# C241-L14/L15: grupo de lançamento não é objeto individual

**Pergunta discriminante:** o registro anual NASA SP-4004 com designação agregada `1963-3`, estado impresso *Still in orbit.* e perigeu impresso de **286 milhas terrestres** contradiz o dia de decaimento catalogado `1963 3B` (NORAD 528)? **Não é possível inferir isso**: a linha da compilação é do **grupo**, sem filho A/B/C e sem época de medição. Não transferir estado ou perigeu ao 528. A leitura do PDF na ocorrência C241-L15 foi extraída de texto oficial, **não confirmada visualmente** na página impressa 501; sua transcrição ainda é provisória.

**Linhas e custódia:** [C241-L15, NASA SP-4004](../tle_custody/nasa_sp4004_1963_group_custody_C241-L15.json), documento [NASA SP-4004 (1964)](https://www.nasa.gov/wp-content/uploads/2023/04/sp-4004-1963.pdf), SHA-256 registrado no JSON de custódia; [C241-L14, GCAT](../tle_custody/gcat_full_catalog_lineage_C241-L14.json), compilação contemporânea de `currentcat` e `satcat` sob uma linhagem; [C197/C198, NASA SSR 15/11/1963](../tle_custody/catalog_identity_527_529_2026-11-12.json), NTRS 19640001198, p. impressa 8, que registra **apenas** o dia de decaimento para a designação B. A concordância ou discordância de dois produtos compilados não é uma observação independente de radar. A custódia/atribuição instrumental cabe à Tartaruga/Morcego; este trabalho audita consequências estatísticas.

**Contribuição mensurável:** `tools/raan_source_likelihood_readiness.py` lê os dois JSONs adicionais, fixa seus SHA-256 no relatório e acrescenta grupos de elegibilidade com `child_528_status_from_this_row=null`, `child_528_perigee_from_this_row=null` e `independent_likelihood_factor=NOT_AUTHORIZED`. Mudança de identidade, época, flag de independência, visualização ou estado falha em testes adversariais e exige reavaliação documental, em vez de ativar uma likelihood sem revisão. Esses valores agregados são variáveis de proveniência conectadas à matriz, não equações físicas ativas.

**Replay:** `python3 tools/raan_source_likelihood_readiness.py --check` e `python3 -m unittest discover -s tests -p 'test_raan_source_likelihood_readiness.py' -v`. Holdout temporal 61/23/35 continua retrospectivo e de uma linhagem secundária; nenhuma nova observação, priori histórica, modelo de erro ou probabilidade foi recuperada. `active_constraint=false`; MCMC, posterior de reentrada, discriminação geográfica e tempos terminais continuam `NOT_RUN`/`NOT_IDENTIFIED`.

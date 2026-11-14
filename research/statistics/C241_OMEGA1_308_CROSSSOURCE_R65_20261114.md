---
type: Experiment
title: C241 R65 comparação numérica OMEGA 1 e catálogo secundário NORAD 308
description: Diagnóstico temporal de identificabilidade, sem equiparar séries NASA/TLE
---

# R65: impressão OMEGA 1 versus elementos secundários 308

**Questão discriminante:** a linha NASA SSR de 15/10/1963 (C241-L68, PDF p. 5, as-of editorial 12:00Z) fornece um *fingerprint* numérico que identifica univocamente o NORAD 308? **Não**. A linha não imprime número NORAD, e o espelho histórico TLE não é uma linhagem instrumental independente comprovada. A seleção de 308 vem da correspondência retrospectiva NASA de 1977 C241-L66/L67, não de busca cega.

**Fontes congeladas:** C241-L68, NASA NTRS 19640000428, SHA-256 `fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2`; Parquet `tle_1963.parquet` (oxzoid/space-track-tle-history, commit `4b4fb3a`), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. As 52 linhas do NORAD 308, das quais 44 anteriores a 12:00Z em 15/10, são produtos do **mesmo espelho secundário**, não 52 sensores.

| Grandeza | NASA impresso | Último elemento pré-corte do 308 | Diferença 308 − NASA |
| --- | ---: | ---: | ---: |
| Período (min) | 89,7 nodal | 89,635116 proxy por 1440/n | −0,064884 |
| Inclinação (graus) | 82,15 | 82,146004 | −0,003996 |
| Apogeu (km) | 263 | 261,699526 proxy kepleriano | −1,300474 |
| Perigeu (km) | 254 | 251,151898 proxy kepleriano | −2,848102 |

Época TLE escolhida: **14/10/1963 23:23:55,702464Z**, anterior ao *as-of* editorial de 15/10 12:00Z por cerca de 12,60 horas. O período proxy do TLE arredonda para 89,6 min, não 89,7 min, sob arredondamento decimal convencional a uma casa. Isso **não** demonstra objetos distintos: período nodal não é necessariamente 1440/n TLE, os elementos não têm mesma época de observação nem modelo de gravidade, e apogeu/perigeu keplerianos não equivalem automaticamente aos valores SSR. A precisão de impressão tampouco mede sigma instrumental.

**Teste falsificável:** obter tabela contemporânea com designação NORAD impressa e seus elementos/época de sensor, além da definição do período nodal SSR e incerteza; então testar alternativas, incluindo identidades não cobertas pelo Parquet. Até lá: `active_constraint_528=false`, `terminal_sigma_hours=null`, `historical_mcmc=NOT_RUN`, `identity_probability=null`, sem probabilidade de impacto e sem redução do domínio de Conde. Comparação é descritiva e não autoriza atribuição física.

Reprodução: `python tools/c241_omega1_308_crosssource_r65.py --ssr research/tle_custody/nasa_ssr_omega1_oct15_C241-L68.json --parquet tle_1963.parquet --output /tmp/c241-r65.json`. O CI verifica SHA, 15 testes adversariais normais/otimizados e contraprova de arquivo corrompido.

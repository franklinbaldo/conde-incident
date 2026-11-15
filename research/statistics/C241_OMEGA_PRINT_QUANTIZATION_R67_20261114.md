---
type: Experiment
title: C241 R67 células decimais NASA versus proxy TLE, somente sob hipótese contrafactual
description: Certificado de incompatibilidade de arredondamento sem promover identidade orbital ou precisão instrumental
---

# R67: quantização não equivale a covariância nem a identidade

**Pergunta nova e falsificável:** sob a hipótese **contrafactual** de que a linha `OMEGA 1` do NASA SSR (15/10/1963, C241-L68) e o último proxy TLE pré-corte do NORAD 308 (14/10/1963 23:23:55,702464Z) representassem o **mesmo observável físico, a mesma época e a mesma definição**, todos os quatro valores seriam explicáveis apenas por arredondamento a casas impressas? **Não: três dos quatro falham.**

| Grandeza | Célula decimal NASA, com arredondamento half-up | Proxy TLE R65 | Distância mínima à célula |
| --- | --- | --- | --- |
| Período (min) | [89,65; 89,75) | 89,635116114 | 0,014883886 min |
| Inclinação (graus) | [82,145; 82,155) | 82,146003723 | 0 |
| Apogeu (km) | [262,5; 263,5) | 261,699525861 | 0,800474139 km |
| Perigeu (km) | [253,5; 254,5) | 251,151898073 | 2,348101927 km |

O modelo operacional de célula é **round-half-up**; a convenção real de arredondamento editorial de 1963 não foi estabelecida. O resultado é estável fora dos empates, inclusive se fossem usadas células fechadas nos dois extremos. As distâncias positivas são apenas **pontes mínimas condicionais de definição/época/observável**, não erros físicos, erro de instrumento ou tolerâncias calibradas. As unidades distintas proíbem somar as quatro distâncias ou transformar o resultado em score estatístico.

Os dados e a seleção do NORAD 308 são os mesmos de [R65](C241_OMEGA1_308_CROSSSOURCE_R65_20261114.md): NASA NTRS 19640000428, SHA-256 `fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2`; Parquet secundário 1963 do dataset oxzoid/space-track-tle-history, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. O trecho NASA é uma tabela catalográfica sem NORAD impresso, sem época instrumental nem erro individual. A origem do candidato é retrospectiva, não uma seleção cega. **Nenhuma observação independente nova foi introduzida.**

**Identificabilidade:** o teste rejeita apenas o submodelo artificial `mesma época + mesmas definições + diferenças limitadas ao arredondamento`. Não rejeita a identidade física 308/OMEGA 1, não a confirma, não atribui um `sigma`, nem identifica momento terminal, massa, latitude ou longitude. Células de impressão diferentes de valores de um modelo TLE não são resíduos observados de rastreamento. Pode haver deslocamento temporal, período nodal diferente do período `1440/n`, conversões de elementos médios e diferenças de convenção de altitude.

**Observação que discrimina:** documento primário com número NORAD, época da solução NASA, definição de período nodal, convenção de apogeu/perigeu e ao menos uma medida comparável coepocal. Para calibração de reentrada, continuam faltando horário terminal, relógio, sensor, erro e independência. Até lá `historical_mcmc=NOT_RUN`, `identity_probability=null`, `active_constraint_528=false` e nenhuma contração do domínio geográfico de Conde.

**Reprodução no CI:** a ferramenta `tools/c241_omega_print_quantization_r67.py` consome **exclusivamente a saída R65 reexecutada sobre o Parquet autenticado**, não uma tabela reescrita por esta nota. O workflow existente executa 12 testes adversariais em Python normal e otimizado, R65 original, R67, e contraprova de fonte alterada. Valida o SHA exato da PR e não cria novo trigger. Fixtures dos testes são explicitamente sintéticas.

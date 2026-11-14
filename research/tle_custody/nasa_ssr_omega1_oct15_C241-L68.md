---
type: Guide
title: "C241-L68: Omega 1 consta em órbita no boletim NASA de 15/10/1963"
description: "Nova leitura de linha orbital impressa no SSR 20, sem promover 308, época instrumental ou instante terminal."
---

# C241-L68 | Uma linha anterior à retirada de Omega 1

O [*Satellite Situation Report*, vol. 3, nº 20, de 15/10/1963](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf#page=5) inclui **OMEGA 1** entre os **OBJECTS IN ORBIT**, sob **1962 LAUNCHES**, na **página impressa 3 (página PDF 5)**. A capa interna diz que o relatório reflete dados compilados **até 1200Z de 15/10/1963** (página PDF 2).

| Campo impresso | Valor |
|---|---|
| Nome | OMEGA 1 |
| País | US |
| Lançamento | 18 JUN (seção de 1962) |
| Período nodal | 89,7 minutos |
| Inclinação | 82,15 graus |
| Apogeu | 263 km |
| Perigeu | 254 km |
| Número NORAD | **Não impresso** |

**Custódia:** NTRS **19640000428**, 286.417 bytes, **9 páginas**, SHA-256 `fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2`. O PDF já era conhecido em **C241-L12**, que examinou outra linha, relativa a 1963-37A/668. Esta é **nova extração da mesma fonte**, não um relatório ou sensor independente. As páginas PDF 2 e 5 foram examinadas visualmente, incluindo coluna e linhas adjacentes. A linha está em tabela girada, exigindo conferir o alinhamento por coluna.

**Comparação condicionada:** a edição NASA de **15/12/1963** ([NTRS 19640003479, PDF 17](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=17)) imprime **OMEGA 1** como decaído **29–30 OCT 63**. A tabela retrospectiva de 1977 ([NTRS 19780009188, PDF 46](https://ntrs.nasa.gov/api/citations/19780009188/downloads/19780009188.pdf#page=46)) associa **OMEGA 2 / NORAD 308** ao mesmo par de datas (C241-L66/L67). O **número 308 não está nesta linha de outubro de 1963**; não tratar correspondência de datas/nome como identidade instrumental provada nem corrigir silenciosamente os rótulos.

**Limite científico:** o corte **1200Z** é administrativo/editorial, **não é a época de uma observação óptica/radar individual**, nem o instante real em que um objeto foi visto vivo. Período, inclinação e altitudes são números publicados de catálogo, sem época instrumental, estação, método ou covariância recuperados aqui. A lista não certifica sobrevivência física exatamente ao corte. Nenhum `terminal_event_utc`, `sigma`, sensor ou local de impacto resulta desta linha. Não criar likelihood ou restrição ativa sobre o **528**.

**Reprodução:** `python3 tools/tle_ssr_omega1_oct15_c241_l68.py --self-test --pdf /caminho/para/19640000428.pdf`. O auditor valida contrato e SHA dos bytes; os mutantes adversariais rejeitam identificação 308 direta, data editorial como época instrumental, ativação da restrição 528, alteração de linha e PDF adulterado. Os testes não substituem a verificação da imagem da tabela original.

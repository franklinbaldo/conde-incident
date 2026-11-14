---
type: Guide
title: 'C241: massas em épocas distintas e falsa conservação do complexo'
description: 'Contraprovas exatas para impedir que campos GCAT de OPS/Agena sejam convertidos em inventário fechado de 527/528/529 ou consumo de propelente.'
---

# Contraste documental C241: massa em que instante?

**Fonte secundária preservada:** C241-L40, [GCAT, definições de Mass, DryMass e TotMass](https://planet4589.org/space/gcat/web/cat/cols.html), manifesto em `research/tle_custody/gcat_mass_semantics_C241-L40.json` com URL e SHA-256 dos seis extratos. Não é uma folha de engenharia ou pesagem na separação de fragmentos em 1963. Uma única família de catálogo, não seis instrumentos independentes.

## Duas histórias compatíveis com os mesmos quatro números

Os campos catalogados são OPS 0180/S00527 `Mass=306 kg`, `TotMass=1176 kg` e estágio Agena B A00324 `Mass=900 kg`, `DryMass=870 kg`. As identidades nominais `306+870=1176` e `306+900=1206` são exatas. A diferença `900−870=30 kg` entre as **definições de catálogo** não informa quanto combustível foi consumido antes de um determinado evento nem quando ocorreu uma separação. Não inferir massa operacional instantânea de `DryMass` sem saber inventário de consumíveis, adições e perdas.

Em cenário expressamente contrafactual, assumindo estágio seco invariável, sem perdas/adicionais, e propelente retido `f∈[0,30] kg`, as escolhas `f=0` e `f=30` geram massas de estágio no evento de 870 e 900 kg. Ambas são compatíveis com os mesmos campos GCAT, porque o catálogo não reporta `f` nem a época do evento. **Esses limites não são históricos**: eles desaparecem se as hipóteses de cenário forem retiradas.

Uma segunda contraprova: atribuir simultaneamente os 1.176 kg ao corpo 527 inteiro *na mesma época* e a um inventário fechado `m527+m528+m529+X=1176 kg`, com `m528>0`, `m529>0` e `X≥0`, resulta em contradição algébrica. Ela falsifica a **conjunção dessas hipóteses**, não a existência dos fragmentos nem a confiabilidade isolada do catálogo. Os zeros de S00528/S00529 são valores de catálogo sem massa física conhecida.

## Desenho discriminante e holdout

Para identificar a massa operacional na separação, procurar um relatório de engenharia datado com estado de propelente e convenção wet/dry, o inventário de componentes e a correspondência física entre Agena, OPS e os três NORAD. Um segundo documento que simplesmente copie GCAT não constitui observação independente. Um holdout útil seria uma medição de massa/arrasto calibrada, de outra linhagem instrumental, obtida numa época declarada e mantida fora do ajuste. O coeficiente balístico `Cd*A/m` isolado não mede massa quando área e Cd são desconhecidos.

**Status cumulativo:** C241-L39/C241-L40 `CONNECTED_PENDING_CALIBRATION`. Evidência conectada à massa operacional de estágio, ao estado de propelente no instante e à partição 527/528/529/X; todos permanecem latentes. `historical_constraint_active=false`, `historical_mcmc=NOT_RUN`, `historical_domain_reduction=false`. Não reduz domínio geográfico da reentrada do 528 nem resolve RAAN, data ou horário de queda.

Reproduzir: `python3 -m unittest discover -s tests -p test_c241_stage_epoch_ambiguity.py -v` e `python3 -m tools.c241_stage_epoch_ambiguity`. Este diagnóstico é uma fatia nova e independente, não autoriza merge das PRs antigas [#634](https://github.com/franklinbaldo/conde-incident/pull/634) ou [#641](https://github.com/franklinbaldo/conde-incident/pull/641) sem reconciliação com G48/G49/G50 e CI atual.

---
type: Guide
title: 'C241: identificabilidade de 528 com perdas, residual e erro de catálogo'
description: 'Posto racional de observações discriminantes quando a contabilidade de massa admite perdas e viés; nenhuma posterior histórica.'
---

# C241: medir 528 não equivale a fechar o inventário

O [registro GCAT C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json) contém `Mass=306 kg` e `TotMass=1176 kg` na linha S00527, `Mass=900 kg` e `DryMass=870 kg` na linha do Agena A00324. Não registra massa física dos 528/529. As diferenças nominais são aritmética de campos documentais, não evidência de combustível consumido, resíduo ou erro de pesagem.

## Nova pergunta identificável, distinta da massa total

No *cenário hipotético* de um inventário fechado e conciliado à mesma época, represente seis incógnitas: `(m527,m528,m529,X,L,epsilon)`, onde `X` é resíduo não atribuído, `L` é massa perdida e `epsilon` é erro de reconciliação assinado. A equação condicional seria `T = m527+m528+m529+X+L+epsilon`. O GCAT **não** autoriza aplicá-la a `T=1176 kg`: falta demonstrar genealogia, época, convenção e inventário. Sem esse documento, o posto histórico dessas seis coordenadas é **0/6**.

A ferramenta `python3 -m tools.mass_observation_design_C241` calcula posto exato e estimabilidade da coordenada `m528` independentemente de identificar todos os componentes. Todos os canais são observações **propostas**, não obtidas. Resultados condicionais:

| Conjunto de hipóteses ou medições **não observado** | Posto/nulidade | `m528` estimável? |
| --- | --- | --- |
| Apenas GCAT como está | 0/6 | Não |
| Total fechado validado, isolado | 1/5 | Não |
| Total + massas externas de 527 e 529 | 3/3 | Não |
| Total + três massas externas dos objetos | 4/2 | Sim, mas X/L/epsilon continuam confundidos |
| Total + três massas + X | 5/1 | Sim, L/epsilon permanecem confundidos |
| Massa direta calibrada do 528, sem total | 1/5 | Sim, mas o inventário não |
| Total + 527, 529, X, L, epsilon calibrados | 6/0 | Sim, apenas dentro do cenário |

Mesmo no cenário, `X` e `L` podem mudar de `(300,76)` para `(290,86)` kg preservando todas as outras massas, o total fictício de 1.176 kg e `epsilon=0`. Analogamente, `m528` pode passar de 200 para 210 kg se `X` cair de 300 para 290 kg. São testemunhas racionais de não-identificação, **não estimativas**.

## Observações discriminantes e critérios de custódia

A primeira aquisição útil é ficha primária do voo 2313 com inventário e data da separação, correspondência componente/NORAD e definições wet/dry. Medição instrumental de massa do 528 na mesma época, ou restrição externa calibrada equivalente, identifica diretamente a coordenada de interesse mesmo sem fechar o livro contábil inteiro. Se depender exclusivamente da soma, é preciso adicionalmente limitar ou medir perdas, resíduo e viés, com erros e independência documentados. Inferir `m` de `B=CdA/m` exige `Cd`, área e densidade calibrados, além de dinâmica e sensor. Cópias do GCAT não constituem canais independentes.

Esta extensão da [inbox Cervo #2](https://github.com/franklinbaldo/cervo/issues/2) prepara a avaliação das drafts [#634](https://github.com/franklinbaldo/conde-incident/pull/634) e [#641](https://github.com/franklinbaldo/conde-incident/pull/641), mas não as libera. Não há likelihood calibrada, prior histórica, observação instrumental nova, posterior ou redução geográfica de Conde. Estados: `historical_mcmc=NOT_RUN`, `historical_constraint_active=false`.

Reproduzir no SHA: `python3 -m unittest discover -s tests -p test_mass_observation_design_C241.py -v` e `python3 -m tools.mass_observation_design_C241`.

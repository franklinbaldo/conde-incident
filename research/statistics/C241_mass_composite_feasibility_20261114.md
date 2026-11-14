---
type: Guide
title: 'C241: exclusão condicional do inventário fechado com composto inteiro'
description: 'Provas Lean de compatibilidade de componentes; sem atribuir 1176 kg à soma dos fragmentos.'
---

# Massa do composto 527 e limites de um inventário hipotético

A fonte secundária [GCAT C241-L40](../tle_custody/gcat_mass_semantics_C241-L40.json) transcreve `Mass=306 kg` e `TotMass=1176 kg` na linha S00527, e `Mass=900 kg`, `DryMass=870 kg` para a etapa A00324. As igualdades **306+870=1176** e **306+900=1206** são aritmética de campos catalográficos: não provam que essas massas sejam simultâneas nem que `TotMass` seja um inventário fechado de 527+528+529+X.

Reaproveitamos exclusivamente as provas condicionais `MassComponent306.lean` da [draft #634](https://github.com/franklinbaldo/conde-incident/pull/634). O arquivo distingue massas dos componentes da massa do objeto orbital 527. A conclusão discriminante é uma **incompatibilidade de premissas**: suponha, *contrafactualmente*, que 1176 kg seja exatamente o total fechado, que toda a carga útil catalogada de 306 kg e toda a etapa seca catalogada de 870 kg ainda estejam integralmente no corpo 527 nesse mesmo instante, e que 528 e 529 possuam massas estritamente positivas. Não existe solução não negativa. O fato de duas descrições poderem se ajustar numericamente não identifica qual dessas premissas históricas falha.

O mesmo arquivo prova que, **somente** supondo a retenção integral dos 306 kg no 527 e inventário fechado de 1176 kg, `m528+m529+X ≤ 870 kg`. Isso não é um limite empírico para 528: não conhecemos a massa retida no 527, o material separado, a validade do total ou a época física comum. O valor de 30 kg não constitui medição de combustível gasto. Nenhuma nova medição independente de massa, arrasto ou área foi adicionada.

Reproduzir: `cd formal && lake build`, incluindo o módulo importado por `Conde1963.lean`; no CI, conferir `Lean 4.35 core proof audit` no HEAD da PR. O módulo é álgebra de inteiros naturais e hipóteses explícitas, não simulação MCMC. Esta fatia deixa o sampler e os cenários da draft #634 em quarentena; a [draft #641](https://github.com/franklinbaldo/conde-incident/pull/641) continua dependente de genealogia, época, fonte física e contratos G48/G49/G50. Estado: `historical_mcmc=NOT_RUN`, `historical_mass_posterior=null`, `active_constraint=false`, sem estreitar o domínio geográfico de reentrada.

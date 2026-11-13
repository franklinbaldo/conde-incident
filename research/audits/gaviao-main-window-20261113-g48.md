---
type: Guide
title: '🦅 G48: campos semânticos GCAT precisam ser validados'
description: Auditoria de cinco integrações e teste de oito mutações dos campos interpretativos do catálogo de massas 527–529.
---

# G48: hash íntegro não torna verdadeira uma conclusão alterada

**Janela auditada:** `9c884f7a` (exclusivo) → `7a579c17` (inclusivo): cinco integrações first-parent, seis commits DAG, um merge convencional. As integrações #622, #621, #624, #629 e #623 estão no manifesto JSON adjacente, com caminhos e SHAs. Checks históricos individuais não consultados = `NOT_CHECKED`.

## Achado G48-F1: interpretação derivada atravessava o validador

A PR #629 introduziu uma inspeção boa das colunas originais GCAT, mas o verificador `tools/gcat_mass_semantics_C241_L40.py` só checava parte dos campos *interpretativos* de `derived_checks` e `conclusion`. Assim, mudar `parent_launch_mass_balance_proven` para `true`, inventar uma observação instrumental do 528, negar que zero de catálogo é placeholder, ou atribuir a diferença de 30 kg a perda comprovada de combustível **não era rejeitado**, ainda que os mesmos hashes GCAT permanecessem. Esses mutantes são artificiais; não foi encontrada adulteração histórica.

Além disso, condições críticas usavam `assert`, desabilitado com `python -O`. Uma contraprova com `historical_mass_constraint_active=true` retornava sucesso no modo otimizado, mesmo com a fonte simulada intacta.

**RED → GREEN:** adicionados controles de transporte sintético pequeno com verificação de fingerprint deliberadamente mockada, de modo a isolar a validação semântica da custódia real dos seis arquivos. Antes: seis conclusões adulteradas aceitas e `python -O` exit 0. Depois: campos de conclusão fechados, contas derivadas coerentes, `OrbPay`/`OrbMass` preservados e guardas runtime explícitos. Oito variantes semânticas e a variante com intérprete otimizado são rejeitadas; controle positivo continua válido. O replay de 47,5 MB do catálogo original é obrigação separada do CI especializado.

## Limites epistemológicos

A PR #622 propõe partição condicional com residual X; #621 fornece equações e demonstrações Lean condicionais; #629 corrige que 1.176 kg é `TotMass` da linha S00527, não medição das massas exclusivas de 527/528/529; #624 conecta estação soviética 1078 a buscas pendentes, não a observação demonstrada; #623 corrige caminhos que disparam o replay J2. Nenhuma dessas linhas autoriza restringir parâmetros históricos sem observações ou premissas autenticadas. A diferença de 30 kg não tem mecanismo provado. Conde permanece indeterminado.

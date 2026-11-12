---
type: Skill
title: "Skill do Conde: cervo"
name: conde-cervo
description: Inferência MCMC, priors, likelihoods e identificabilidade no caso Conde, com trabalho independente e proveniência verificável.
---

# 🦌 Skill do cervo

Repositório de produto: `franklinbaldo/conde-incident`. **Workspace pessoal privado confirmado:** `franklinbaldo/cervo`; CI OKF/prek e push direto na casa. Siga `AGENTS.md` e `docs/AGENT_WORKSPACES.md`.

## Trabalho especializado
Formalizar probabilidades condicionais apenas com prior, verossimilhança, covariâncias, convergência e holdout; controlar identificabilidade de parâmetros livres.

## Em cada rodada
1. Ler o cartão próprio e a matriz/questões existentes. Quando houver workspace privado acessível, examinar suas issues de entrada, memórias e skills anteriores. Enquanto estiver indisponível, registrar a limitação sem transferir memórias privadas para o repositório público.
2. Formular pergunta falsificável e registrar proveniência, unidades, localização/época e incerteza. Não confundir cópia com observação independente.
3. Executar investigação ou código mínimo, com teste reproduzível; relatar resultados negativos e o próximo experimento.
4. Entregar código compartilhado somente por PR pequena no projeto, CI verde no HEAD, merge próprio quando seguro. Na casa pessoal privada, **push direto sem revisão obrigatória**.
5. Para colaboração, abrir uma issue no **repositório privado do destinatário** quando estiver criado e acessível; manter cruzamento com a issue/PR do projeto. Fechar com memória OKF no espaço pessoal quando possível.

## Fatia 8: experimento MCMC sintético, não posterior histórico

A interface de inferência angular mantém previsões H congeladas: o motor do Castor é a fonte futura de H físico. Para testar um sampler no círculo, use quatro cadeias realmente inicializadas separadamente, proposta simétrica de normal enrolada + salto global e compare E[exp(i theta)] com quadratura periódica sem MCMC. Sem âncora de viés de linhagem, um deslocamento de fase comum fica não identificado. Valores sintéticos nunca são prior histórico; exija fonte primária, frame, escala de erro, independência e holdouts antes de promover o modelo. Referências: tools/raan_synthetic_phase_mcmc.py e issue #219.

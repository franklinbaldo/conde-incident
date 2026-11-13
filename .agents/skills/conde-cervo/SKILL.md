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

## C241-P31: separar reconstrução retrospectiva de score prospectivo

- Ao validar um holdout *as-of* histórico, auditar **o intervalo de suporte e a hora efetiva de liberação de cada driver**, não apenas a data do registro. NRLMSISE F107A é média **centrada** de 81 dias e contém 40 dias após a data-alvo; Ap diário usa o dia UTC completo, e o bin ap/Kp corrente exige seu fim. Não classificar índices definitivos como disponíveis em tempo real sem versões publicadas com timestamp.
- Usar `tools/audit_space_weather_asof.py --check` e o certificado `research/constraints/C241-P31_space_weather_asof.json` para rejeitar avaliação prospectiva silenciosamente contaminada; séries definitivas seguem utilizáveis para reconstrução retrospectiva, com limitações físicas. Isso não é densidade nem posterior de 528. [Issue #607](https://github.com/franklinbaldo/conde-incident/issues/607).

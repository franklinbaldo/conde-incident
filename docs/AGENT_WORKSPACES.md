---
type: AgentContract
title: "Casas, equipe e projetos"
description: "Separação entre animais permanentes e trabalho do Conde."
---

# Organização dos animais

- **Casa**: `franklinbaldo/<animal>`, privada. Skills, ferramentas, issues recebidas e memória pessoal. Push direto. Memória quando necessária.
- **Equipe**: `franklinbaldo/cafezinho`, privada e permanente. Cadastro em `team/roster.json`, perfis em `team/<animal>.md`, arquivo histórico em `team/archive/conde/`, café nas issues.
- **Projeto atual**: `franklinbaldo/conde-incident`. Código, dados científicos, testes, issues e PRs. PR pequena, CI, merge seguro.

## Comunicação

Pedido a um animal: issue na casa do destinatário, com `De:`, `Para:`, contexto e solicitação. Café: issues de `cafezinho`. Trabalho técnico: issue/PR do projeto.

## Histórico

A antiga pasta `conde-incident/team/`, o cadastro duplicado e os testes administrativos foram retirados. O conteúdo histórico está em `franklinbaldo/cafezinho/team/archive/conde/` e no Git. As skills específicas do Conde permanecem em `.agents/skills/conde-*/SKILL.md` e apontam à equipe permanente.

## Qualidade

Cada casa segue suas skills e validações. Markdown pessoal utiliza OKF. No Conde, `prek`, limite de 20.000 bytes por arquivo, testes científicos, Lean e CI permanecem conforme `AGENTS.md`.

---
type: AgentMemory
title: "Zola definido como motor editorial do Conde"
description: "Decisão do proprietário: Coruja migra Caderno de histórias da PR #3 para Zola, preservando React científico."
agent: elefante
timestamp: "2026-11-11T21:16:00Z"
tags: [conde, zola, editorial, coruja, arquitetura]
---

# Continuidade

O proprietário determinou que o blog/Caderno de histórias do Conde use **Zola**. Inspecionada a PR #3: ainda publica o site pelo Vite/Bun e apresenta histórias via componentes React; portanto a implementação atual não corresponde à decisão. A main não continha workflow de Pages inspecionável na consulta. Referências: [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3), [PR #1](https://github.com/franklinbaldo/conde-incident/pull/1).

Na PR #3, foi registrada orientação à Coruja para corrigir em seu próprio branch: conteúdo em Markdown nativo de Zola, templates e configuração, GitHub Actions, subpath e reconciliação com React científico, preservando a distinção Evidências/Caderno. Esta branch de documentação atualiza AGENTS.md e a ficha da Coruja. Sem alteração do código editorial da PR #3, nenhum CI/deploy comprovado nesta sessão.

Próxima pergunta: qual arquitetura de integração minimiza sobreposição com React/Vite e preserva os simuladores sem duplicar navegação? Validar a proposta da Coruja e pedir revisão independente do Gavião no SHA final.

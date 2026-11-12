---
type: AgentMemory
title: "SSG substitui Zola no Caderno de histórias"
description: "Decisão do proprietário revoga Zola; PR #22 e instruções da Coruja passam a exigir SSG Rust."
agent: elefante
timestamp: "2026-11-12T01:39:00Z"
tags: [conde, ssg, rust, editorial, coruja, migracao]
---

# Decisão e retomada

O proprietário escolheu expressamente **SSG** (https://docs.rs/ssg/latest/ssg/), revogando a escolha anterior do Zola. Manter a memória anterior sobre Zola como histórico, não como instrução vigente. A ficha da Coruja e AGENTS.md foram corrigidos na branch da PR #22 (https://github.com/franklinbaldo/conde-incident/pull/22), com contrato de migração em `docs/ssg-editorial-acceptance.md`.

**Observado no repositório:** a PR #3 continua aberta e Draft, com workflow e templates Zola; a main ainda contém projeto React/Vite, sem workflows Pages localizados no diretório raiz consultado. Não fiz merge, não alterei branch da Coruja, não publiquei nada. Fonte técnica: docs.rs SSG 0.0.75 na consulta, documentação relata entrada Markdown + YAML + MiniJinja e instabilidade permitida entre versões 0.0.x.

**Verificação:** apenas leitura de fonte e revisão documental; migração do SSG, build, CI do head final, verificação Pages e deploy real ainda NÃO EXECUTADOS. Não há nova evidência sobre NORAD 528 ou reentrada.

**Próxima dúvida:** a Coruja conseguirá preservar os capítulos, a listagem, os URLs `/conde-incident/` e o laboratório React ao trocar o pipeline Zola por SSG? Cobrar CLI real no workflow GitHub Actions e auditoria de todas as páginas, com Gavião independente.

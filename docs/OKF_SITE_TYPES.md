---
type: Guide
title: Tipos OKF das páginas do Conde
description: Contratos para páginas e ocorrências geradas pelo SSG Rust.
---

# Páginas tipadas em OKF

Os tipos do site são `Page`, `Story`, `Source`, `Evidence`, `Hypothesis`, `Constraint` e `Experiment`; as specs normativas residem em `.okf/specs/`. Uma página tem URL e metadados próprios em vez de ser apenas painel.

**Aplicação nesta fatia:** `Page` nos índices/editoriais, `Story` nos capítulos canônicos de `stories/*.md`, `Evidence` nas 28 ocorrências curadas do arquivo SSG. O gerador preserva o conteúdo original da Coruja. `content/` é gerado, não é fonte primária.

Os tipos `Source`, `Hypothesis`, `Constraint` e `Experiment` estão prontos para receber documentos verificáveis futuros, sem preencher automaticamente dados ausentes. Uma hipótese não é observação, uma prova Lean depende de suas premissas e uma simulação não autentica impacto.

Os IDs documentais têm forma `Cxxx#n` e snapshots com hash Git. As 28 ocorrências curadas não representam todas as 241 da matriz. Múltiplas fontes sobre o mesmo registro não são necessariamente testemunhos independentes.

Validação: `node scripts/prepare-ssg.mjs`, `node scripts/check-ssg-okf.mjs`, `ssg check/build/audit`, testes Node e prek/OKF dos arquivos versionados. Build aprovado não equivale a site publicado.

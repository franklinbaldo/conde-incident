---
type: Spec
title: Ensaio
description: "Comando reproduzivel e resultados de teste associados a SHA e run, sem forjar PASS."
---

# Ensaio

Comando reproduzivel e resultados de teste associados a SHA e run, sem forjar PASS.

## Required fields

| Field | Meaning |
| --- | --- |
| `id` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `title` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `verification` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `source_url` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `rodada` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `comando` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `head_sha` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `run_url` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `resultado` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `escopo` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |

## Regra epistemologica

Este tipo registra somente seu proprio significado, nao autoriza inferir observacoes ou autenticidade fisica. `verification` distingue VERIfIED_REPO, REPORTED_REPO, HYPOTHESIS e NOT_RUN. O corpo deve apontar para os outros conceitos com links Markdown quando houver dependencia. Nenhum resultado de PR ou CI vira fato historico sem confronto original.

## Fonte do scaffold

Scaffold original criado por `okf-parser init --infer-schema --write`; descricao e obrigatoriedade de campos acrescentadas apos a geracao.

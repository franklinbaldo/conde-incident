---
type: Spec
title: Rodada
description: "Registro totalizante de uma sessao: cada nova informacao deve ter um conceito tipado vinculado."
---

# Rodada

Registro totalizante de uma sessao: cada nova informacao deve ter um conceito tipado vinculado.

## Required fields

| Field | Meaning |
| --- | --- |
| `id` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `title` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `verification` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `source_url` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `data` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `agente` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `escopo` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `proxima_duvida` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |

## Regra epistemologica

Este tipo registra somente seu proprio significado, nao autoriza inferir observacoes ou autenticidade fisica. `verification` distingue VERIfIED_REPO, REPORTED_REPO, HYPOTHESIS e NOT_RUN. O corpo deve apontar para os outros conceitos com links Markdown quando houver dependencia. Nenhum resultado de PR ou CI vira fato historico sem confronto original.

## Fonte do scaffold

Scaffold original criado por `okf-parser init --infer-schema --write`; descricao e obrigatoriedade de campos acrescentadas apos a geracao.

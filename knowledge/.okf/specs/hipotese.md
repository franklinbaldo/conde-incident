---
type: Spec
title: Hipotese
description: "Proposicao ainda nao demonstrada com teste capaz de refuta-la."
---

# Hipotese

Proposicao ainda nao demonstrada com teste capaz de refuta-la.

## Required fields

| Field | Meaning |
| --- | --- |
| `id` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `title` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `verification` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `source_url` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `rodada` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `enunciado` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `predicao_testavel` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `criterio_refutacao` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |

## Regra epistemologica

Este tipo registra somente seu proprio significado, nao autoriza inferir observacoes ou autenticidade fisica. `verification` distingue VERIfIED_REPO, REPORTED_REPO, HYPOTHESIS e NOT_RUN. O corpo deve apontar para os outros conceitos com links Markdown quando houver dependencia. Nenhum resultado de PR ou CI vira fato historico sem confronto original.

## Fonte do scaffold

Scaffold original criado por `okf-parser init --infer-schema --write`; descricao e obrigatoriedade de campos acrescentadas apos a geracao.

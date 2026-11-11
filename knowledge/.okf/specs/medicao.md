---
type: Spec
title: Medicao
description: "Valor numerico e unidade, com origem e incerteza documentadas."
---

# Medicao

Valor numerico e unidade, com origem e incerteza documentadas.

## Required fields

| Field | Meaning |
| --- | --- |
| `id` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `title` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `verification` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `source_url` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `rodada` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `grandeza` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `valor` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `unidade` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `origem` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |
| `incerteza` | Identificador/estado/fonte ou atributo obrigatorio deste tipo |

## Regra epistemologica

Este tipo registra somente seu proprio significado, nao autoriza inferir observacoes ou autenticidade fisica. `verification` distingue VERIfIED_REPO, REPORTED_REPO, HYPOTHESIS e NOT_RUN. O corpo deve apontar para os outros conceitos com links Markdown quando houver dependencia. Nenhum resultado de PR ou CI vira fato historico sem confronto original.

## Fonte do scaffold

Scaffold original criado por `okf-parser init --infer-schema --write`; descricao e obrigatoriedade de campos acrescentadas apos a geracao.

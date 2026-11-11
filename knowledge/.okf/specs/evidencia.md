---
type: Spec
title: Evidencia
description: "Relacao explicita de suporte, refutacao ou contexto entre fonte e afirmacao."
---

# Evidencia

Relacao explicita de suporte, refutacao ou contexto entre fonte e afirmacao.

## Required fields

| Field | Meaning |
| --- | --- |
| `id` | Identificador unico e estavel deste conceito; nao substituir ID Cxxx da matriz |
| `title` | Titulo legivel |
| `verification` | Grau: VERIFIED_REPO, REPORTED_REPO, HYPOTHESIS ou NOT_RUN |
| `source_url` | URL exata da origem com SHA, pagina ou data quando conhecida |
| `rodada` | ID da Rodada que catalogou a informacao |
| `afirmacao` | Referencia a afirmacao suportada ou contestada |
| `fonte` | Fonte ou artefato de que o trecho deriva |
| `relacao` | Apoia, refuta ou contextualiza, sem duplicar testemunhas |
| `limite` | Conclusao que a fonte nao permite |

## Limites epistemicos

- Este conceito nao comprova autenticidade fisica, independencia documental ou causalidade por si mesmo.
- O grau `verification` nao deve ser elevado sem nova inspecao. Fonte citada em PR nao equivale a original consultado.
- Manter no corpo links para outros conceitos e o limite de inferencia; conservar resultados negativos e conflitos.

## Proveniencia do scaffold

`okf-parser init --infer-schema --write` v0.48.2 gerou o esqueleto; descricao dos campos foi enriquecida para o caso Conde.

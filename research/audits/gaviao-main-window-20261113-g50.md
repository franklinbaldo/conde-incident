---
type: Guide
title: '🦅 G50: dependências reais no disparo do replay C241'
description: Auditoria retrospectiva de doze integrações e contraprova de cobertura de gatilhos no cenário bilateral NASA.
---

# G50: o replay só protege os insumos que o acionam

**Janela congelada:** `17eec4a4` (exclusivo) → `e26d0db8` (inclusivo), 12 integrações first-parent, 12 commits no DAG, nenhum merge convencional. O manifesto JSON adjacente enumera cada SHA, suas mudanças e mantém checks históricos individuais não consultados como `NOT_CHECKED`.

## G50-F1: cinco dependências fora dos filtros do workflow temporal

A nova família C241 de cenários bilaterais para o dia 8 de novembro de 1963 tem testes específicos e um workflow que roda auditoria do documento C197, ensaios Python, testes TypeScript e a integração Monte Carlo. Contudo, os filtros `pull_request.paths` e `push.paths` omitiram **cinco insumos efetivamente consumidos**: `research/constraints/nasa_528_decay_precision_C197_20261113.json`, `src/lib/constants.ts`, `src/lib/astrodynamics.ts`, `src/types/astrodynamics.ts` e `package.json`.

**RED reproduzido:** um novo teste de regressão executado sobre o workflow da `main` encontrou os cinco caminhos ausentes e falhou. Uma alteração que toque somente um deles não dispara o workflow especializado, mesmo se houver outros gates genéricos. Não há evidência de que alguém tenha usado essa lacuna ou que qualquer resultado histórico tenha sido falsificado.

**Correção proposta:** incluir os cinco caminhos em **ambos** os eventos, manter os filtros seletivos e conferir a paridade com o teste existente de auditoria Python. **GREEN local:** 13/13 testes `test_nov8_two_sided_day.py` passaram; `git diff --check` limpo. A confirmação obrigatória permanece sendo CI do HEAD exato da PR, antes de merge. Não suprimir etapas nem relaxar a validação científica.

## Revisão científica e limites

Os commits revisados incluem genealogia ONU/soviética, nova fonte cartográfica de 1914, índices SSG, relatório Telstar 1962, EOP IERS e cenários temporais NASA. Documentos e modelos não são sensores adicionais do 528. O rótulo **8 NOV 63** não especifica hora física, convenção UTC verificada, sigma de erro nem impacto em Conde. A função de probabilidade é **condicional a um erro gaussiano hipotético**, não posterior histórica; Telstar 1962 não calibra automaticamente o 528. O reparo é de cobertura CI, não de inferência orbital.

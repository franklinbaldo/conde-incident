---
type: Guide
title: 'G55: breadcrumbs SSG devem provar a trilha real'
description: 'Auditoria retrospectiva de 13 integrações e contraprova de falso PASS na navegação estática.'
date: 2026-11-14
---

# G55: marcador não é navegação validada

**Janela congelada:** `7784cf8b` (exclusivo) → `c4e25a0f` (inclusivo), 13 integrações first-parent, 14 commits DAG, um merge convencional. O [manifesto](gaviao-main-window-20261114-g55.json) enumera os commits e conserva checks históricos não inspecionados como `NOT_CHECKED`.

**G55-F1:** a implementação de breadcrumbs introduzida na #721 tratava a presença da string `aria-label="Trilha de navegação"` em qualquer posição do HTML como prova de que a trilha já existia. Dois mutantes sintéticos demonstraram aceitação indevida: um elemento `<meta>` no `<head>` com esse atributo e um `<nav>` vazio, sem ancestral nem título. Nenhum dos dois entregava os links de retorno exigidos, embora a verificação indicasse `changed: false`. O modo `--check` poderia, portanto, considerar válida uma página sem trilha utilizável.

**Contraprova RED/GREEN:** inicialmente quatro testes Node passaram e os dois novos adversariais falharam por ausência de exceção. Depois, seis testes passaram no executor `ifro` (Node 20). A implementação agora exige um único marcador e o HTML exato da navegação esperada imediatamente depois do `<main>` canônico. O CI Pages continua responsável por validar o HTML efetivamente construído.

**Limites:** a contraprova é sobre HTML sintético, não demonstra defeito no Pages publicado nem fornece medição instrumental ou inferência de impacto do NORAD 528. O caso histórico de Conde permanece indeterminado.

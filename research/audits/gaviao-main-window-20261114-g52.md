---
type: Guide
title: '🦅 G52: custódia INTEROBS sob Python otimizado e fonte efetiva'
description: Auditoria retrospectiva das integrações desde G51 com contraprova e replay do HTML científico.
---

# G52: um texto citado precisa ser verificado, não apenas declarado

**Janela:** `cf163c58` (exclusivo) → `cae934b9` (inclusivo), **12 integrações first-parent, 12 commits DAG, zero merges convencionais**. O JSON adjacente lista SHA e alterações; checks históricos individuais não examinados recebem `NOT_CHECKED`.

## G52-F1: o gate aceitava um manifesto falso quando otimizado

Na integração #677 (INTEROBS, estação 1023, Kiev), o script `tools/verify_konkoly_interobs_1963.py` possuía 28 verificações `assert`. O Python com `-O` elimina todas elas. Uma contraprova no HEAD da main anterior à correção manteve a função retornando `True` após três mutações independentes: SHA da página adulterado, alvo falsamente identificado como série 1963-003 e uma restrição orbital ativada sem observação. **Não existe prova de que essas falsificações ocorreram historicamente.**

O workflow especializado também executava apenas a leitura do manifesto, sem baixar a fonte HTML. Assim, um `source.sha256` declarado corretamente não representava replay efetivo dos 57.146 bytes de texto transcrito. Verifiquei independentemente que o endereço declarado entregava **57.146 bytes com SHA-256 `70a0e99b...61a47ebe5`** em 14/11/2026. O replay completo no Jatobá foi PASS.

**Reparo proposto:** converter as 28 guardas em `require` com `ValueError` incondicional, adequar os testes negativos e adicionar subprocessos reais `python -O` com controles positivos e três mutações; fazer o job especializado baixar a página HTTPS e obrigatoriamente validar o SHA e as âncoras textuais contra o snapshot obtido. Testes locais: 9/9 normais e 9/9 sob `-O`, além de replay do arquivo completo. CI autoral e pós-merge exigem verificação separada.

## Leitura epistemológica

O artigo de 1965 documenta o Sputnik 4 (`1960 epsilon 3`), inclusive contagens da estação Kiev 1023 entre várias campanhas de 1963–1964. Isso **não** constitui observação da família NORAD 527–529 em 7–9 de novembro de 1963, nem prova de cronologia de reentrada do 528. Os volumes de cooperação citados pelo artigo ainda precisam ser inspecionados. A conclusão Conde permanece indeterminada.

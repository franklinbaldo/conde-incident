---
type: AgentMemory
title: "C241-T4: grade temporal exata, sem recuperar TLE primario"
description: "Auditoria de representabilidade dos 123 carimbos e gate de conflito de duplicatas, sem inferencia orbital."
agent: tartaruga
timestamp: "2026-11-12T01:42:00Z"
tags: [conde, norad, tle, custodia, epoch, hash, proveniencia, raannaoresolvido]
---

# 🐢 Tartaruga: issue #13, PR #14, C241-T4

Retomei a PR #14 na branch `feature/tartaruga-tle-custody-1963`
(empilhada sobre a PR #1), após ler `main/AGENTS.md`,
`main/team/tartaruga.md`, issues/PRs abertas, a PR #28 e a matriz
cumulativa C001–C238 com C240–C241-T3. Sem criar issue ou PR paralela,
sem merge, sem blog, sem contato com arquivos/pessoas, sem rebase.

## Entrega verificável

- `tools/tle_epoch_grid_audit.py`: le o CSV secundario fixado e verifica
  em inteiros os carimbos UTC contra o quantum 864 µs de 8 casas decimais
  do dia TLE; divulga residual por fonte e JSON com resultado negativo.
- `tests/test_tle_epoch_grid_audit.py`: 6 contraprovas sintéticas,
  cobrindo limites de dia, 1/432/433 µs fora da grade, fonte SHA
  divergente, fuso e objeto ausente.
- `tools/audit_norad_1963.py`: gate novo contra duplicatas de mesma
  epoca com estados orbitais divergentes; escreve CSV+JSON forenses antes
  da falha. Um teste exercita dados sintéticos conflitantes/identicos.
- `.github/workflows/tle-custody.yml`: executa o teste novo sobre o
  espelho real e arquiva `tle_epoch_grid_report.json`.
- README e matriz com C241-T4, sem promover formato a evidência fisica.
- Commits: codigo/testes/workflow culminaram em
  `e96c54871c25de56336a042778071154eaa33d06`;
  README `0f26ec1aa887d0aeffa7316a1d298fbd686a68f0`;
  matriz `f215955ee3991332d5f6cc4456b711f22feb33bc`.
  A entrega final é a branch da PR #14 após esta memoria, sujeita a
  CI especifico do novo HEAD.

## Linha de dados e verificacao

- Fonte numerica secundaria: https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet
  revision `4b4fb3a`, SHA-256
  `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`.
- CSV geral SHA-256
  `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`.
- Formato tecnicamente especificado por CelesTrak:
  https://celestrak.org/columns/v04n03/ (nao documento instrumental coevo).
- Documento primario coevo NASA:
  https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf
  p. 8 = dia de decaimento, NAO carimbo de reentrada ou observacao de Conde.
- CI sobre HEAD de codigo `e96c54871c25de56336a042778071154eaa33d06`:
  https://github.com/franklinbaldo/conde-incident/actions/runs/43136329241
  SUCCESS com **46/46 testes**, Parquet e CSV SHA validos e
  **123/123 épocas exatamente na grade** (527 21/21; 528 45/45;
  529 57/57), desvio maximo 0 µs. Verificacoes cientificas:
  https://github.com/franklinbaldo/conde-incident/actions/runs/43136329367
  SUCCESS (Lean e web).
- O CI de custodia nao detectou duplicatas conflitantes na fonte real;
  o teste de conflito e sintetico e constitui gate preventivo.

## Negativos, incertezas e proxima pergunta

**Resultado negativo para autenticidade:** representabilidade na grade
nao recupera os 45 line1/line2 nem checksums originais do 528; nem
metadados de rastreio, frame/TEME, erros, identidade fisica do 528,
observacao terminal ou cadeia primária NORAD/NRO. O conflito **RAAN
198,5261° / 284,1520° segue sem resolucao instrumental**. Nao existe
nova restricao orbital fisica Lean nem dominio fisico admissivel novo;
nao converter esse PASS de formato em prova de reentrada/impacto.
Conde permanece INDETERMINADO.

Proxima prioridade: obter publicamente **registros coevos primarios**
com pares TLE originais e metadados de emissoes, ou documentar que os
numericamente espelhados foram retrospectivamente construidos.
Somente apos isso testar restricoes orbitais em Lean 4.35.0 e integrar
simulacao calibrada com holdouts. 🦅 Gavião revisor; 🐘 Elefante integrador.

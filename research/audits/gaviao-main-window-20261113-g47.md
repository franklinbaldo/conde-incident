---
type: Guide
title: '🦅 G47: dependências invisíveis ao replay orbital'
description: Auditoria de 15 integrações em Conde e reparo da cobertura de gatilhos da triagem J2/arrasto, sem alterar modelo científico.
---

# G47: uma mudança de fonte podia saltar o replay orbital

**Janela auditada:** `00e2226d` (exclusivo) → `9c884f7a` (inclusivo), 15 integrações first-parent e 15 commits no DAG, nenhum merge convencional. Manifesto JSON na mesma pasta registra cada SHA, caminhos alterados e verificações históricas individuais não consultadas como `NOT_CHECKED`.

## Achado G47-F1: lacuna de gatilho no gate específico

A PR #619 integrou o workflow `norad528-effective-drag-screen.yml`, que reconstitui as 45 épocas secundárias do 528 a partir do Parquet fixado por SHA, ajusta H/k e executa Lean. Os eventos `pull_request` e `push` usavam `paths`, porém não incluíam a divisão temporal congelada, o modelo de precisão NASA C197, o código do conversor Parquet, a camada de normalização, o TLE literal de comparação, o conjunto RAAN usado pelos testes sintéticos ou a toolchain Lean. Uma PR mudando apenas esses insumos **não acionaria o replay específico**. O workflow Integration executa testes Python sintéticos e compilação Lean, mas **não repete o download/replay Parquet do cenário**.

**Contraprova:** foi adicionado teste na própria suíte J2 verificando exaustivamente os gatilhos `pull_request` e `push` para as dependências explícitas. Sobre a main anterior, 1/18 testes falhou e enumerou nove caminhos omitidos. Após acrescentar os caminhos a ambos os gatilhos, 18/18 passaram. Trata-se de falha de **cobertura do CI**, não de adulteração histórica nem de demonstração de que um PR passado deixou de ser testado.

**Correção proposta:** incluir os caminhos omitidos sem relaxar `paths` em outros workflows nem alterar cálculo, limiar condicional ou interpretação física. O novo teste atua como guarda de regressão dos gatilhos. A PR será integrada apenas se os checks do HEAD final forem aprovados.

## Fronteiras científicas

O espelho TLE continua sendo uma linhagem secundária compartilhada. O cenário de 7–8/11/1963 e seu limiar de 120 km permanecem condicionais; a data de decaimento NASA não é medida terminal. A auditoria também executou 17 testes J2, 12 IERS, 9 as-of meteorológicos e 9 da estação 1078, todos aprovados antes do reparo de cobertura. Nenhum dado novo resolve a posição terminal do NORAD 528 ou o caso Conde.

---
type: Skill
title: "Skill do Conde: lagarto"
name: conde-lagarto
description: Meteorologia histórica e condições atmosféricas no caso Conde, com trabalho independente e proveniência verificável.
---

# 🦎 Skill do lagarto

Repositório de produto: `franklinbaldo/conde-incident`. **Casa pessoal privada:** `franklinbaldo/lagarto` (confirmada e utilizada; memória pessoal permanece privada). Siga `AGENTS.md` e `docs/AGENT_WORKSPACES.md`.

## Trabalho especializado
Auditar GFZ/Canadá/NOAA/Marinha e relações observacionais ambiente→densidade/vento; não supor condições de Conde a partir de Recife.

## Em cada rodada
1. Ler o cartão próprio e a matriz/questões existentes. Quando houver workspace privado acessível, examinar suas issues de entrada, memórias e skills anteriores. Enquanto estiver indisponível, registrar a limitação sem transferir memórias privadas para o repositório público.
2. Formular pergunta falsificável e registrar proveniência, unidades, localização/época e incerteza. Não confundir cópia com observação independente.
3. Executar investigação ou código mínimo, com teste reproduzível; relatar resultados negativos e o próximo experimento.
4. Entregar código compartilhado somente por PR pequena no projeto, CI verde no HEAD, merge próprio quando seguro. Na casa pessoal privada, **push direto sem revisão obrigatória**.
5. Para colaboração, abrir uma issue no **repositório privado do destinatário** quando estiver criado e acessível; manter cruzamento com a issue/PR do projeto. Fechar com memória OKF no espaço pessoal quando possível.

## ISD histórico de superfície: validação por dia e hora (PR desta rodada)

Além de radiossondas IGRA, consultar NOAA/ISD por **arquivo ANUAL da estação**, não inferir observações do intervalo BEGIN/END do inventário. Preservar GZIP original, SHA-256, campos fixed-width e bytes dos dias auditados em snapshot reversível; exigir flags QA no parser, horários UTC explícitos e testes adversariais de duplicação, lacuna, sentinela e estação. `SLP` é pressão ao nível do mar; `WND` é vento de superfície, sem altura nominal do anemômetro autenticada. Um QC numérico não é tolerância instrumental. A origem de dados digitizados décadas depois pode ser diferente da origem da medição, mesmo quando o dia de observação está correto. Cada nova conexão com Conde permanece `PENDING_SPATIOTEMPORAL_CALIBRATION` até comprovação de identidade da estação, transferência horizontal/vertical, propagação de erro e trajetória compatível.

## Proveniência fixa ISD: fonte N/BRAZ (13/11/2026)

Antes de classificar independência instrumental ou geográfica dos controles de superfície, auditar **posição 28 (fonte)** e **posições 42–46 (tipo)** do ISD, conforme documentação oficial, preservando os códigos exatos da observação. Em Caravelas 1963 todos os 8.532 registros originais têm `N/BRAZ`; isso é uma indicação de **compilação de conjunto nacional**, não nome de operador original, identidade de instrumento ou `sigma`. Distinguir QC do arquivo e metadados retrospectivos de ficha contemporânea. Reproduzir com GZIP integral SHA-pin, snapshot de três dias e testes adversariais; manter arestas de procedência pendentes para controles e transferências Conde.

## Inventário ISD por presença real de arquivo anual (13/11/2026)

Para um ano específico, cruze o índice HTTP dos nomes `USAF-WBAN-YYYY.gz` com `isd-history.csv` pela **chave composta**, não pela identidade nominal da estação nem apenas por `BEGIN/END`. Preserve SHA-256 dos dois documentos e a lista ordenada de nomes; audite a distância apenas contra referência cartográfica explícita (não época histórica). `CTRY=BR` é campo literal e pode conter discrepâncias geográficas. Arquivo listado não prova presença no dia, e arquivo ausente não prova ausência de medições históricas em outros acervos. Evidência de cobertura sempre gera aresta PENDING para observáveis, nunca vento Conde ou localização de queda. Use `audit_isd_bahia_coastal_1963_archive.py` e testes com os arquivos integrais originais.

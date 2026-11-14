---
type: Guide
title: "C241-L60: pares simultâneos SAO são derivados de sequências, não novos sensores"
description: "Fac-símile SAO Special Report 266, tabela de alvos e dependência instrumental para deduplicação sem presumir observação do NORAD 528."
---

# C241-L60: simultâneo não quer dizer independente

**Fonte primária do procedimento:** A. Girnius e W. L. Joughin, Smithsonian Astrophysical Observatory, *Optical Synthetic Simultaneous Observations Between Baker-Nunn Camera Stations*, **SAO Special Report 266**, 26/01/1968, [NASA NTRS 19690000806](https://ntrs.nasa.gov/citations/19690000806). [PDF original](https://ntrs.nasa.gov/api/citations/19690000806/downloads/19690000806.pdf). Recuperado em 14/11/2026: **10.985.789 bytes, 71 páginas**, SHA-256 `287158c6a3044a1d088cb5addf4635af6921222abf21a917b08bbe81c967f9b6`.

**Leitura visual:** tabela 1, **página impressa 8, página PDF 16 (índice 15)**, vista no fac-símile original rotacionado. Lista **12 alvos** (de 1960-009-2 até 1965-034-3), entre eles 1963-030-1 e 1963-030-4, **não** 1963-003A/B/C. Isso limita apenas o conjunto publicado neste relatório, **não** a vigilância histórica Baker–Nunn nem a possível existência de filmes brutos de 527/528/529.

**Método**, p. impressas **1–2**, PDF índices 8–9: uma observação simultânea *sintética* é obtida por mínimos quadrados e interpolação de diversas observações reduzidas, feitas em **duas ou mais estações** durante intervalos sobrepostos. São usadas **4 a 10 observações originais por estação**, com 7 quadros considerados adequados. Portanto, uma linha sintética não equivale a uma captura bruta nova. Um par publicado por duas estações pode conter duas direções correlacionadas pelo mesmo alvo, instante sintetizado, método e reduções. Não contar automaticamente cada direção, transcrição, catálogo ou posterior reutilização como fonte instrumental independente.

**Referenciais e incertezas**, p. impressas **4 e 6**, PDF índices **11 e 13**: o relatório escreve o tempo em escala atômica **A.S.**, expõe direções em referencial **terrestre histórico**, estima contexto de incerteza temporal de **0,3–5 ms** e rejeita soluções sintéticas com erro longitudinal/transversal de **2 segundos de arco ou mais**. Nada disso é UTC, TEME, ITRF ou sigma orbital de 528; a precisão é dependente dos quadros e do procedimento aqui descritos, não da data de queda.

**Contrato de custódia:** anotar `raw_film -> precise_reduction -> overlapping_sequence -> synthetic_pair -> earth_direction -> later_catalogue` como cadeia de dependência, nunca como seis observações. ID alvo e par estação/filme devem vir da fonte efetiva antes de promover uma ligação ao grafo. L59/P-14 e L44/P-17 são publicações distintas, mas podem compartilhar família de reduções; sem chave de filme, presumir independência seria indevido. Nenhuma época instrumental do 528, estação, covariância ou observação individual foi obtida. **Zero restrições físicas novas e nenhuma conclusão sobre queda em Conde.**

**Reprodução:** `python -m unittest discover -s tests -p 'test_tle_sao_sr266_c241_l60.py'`; também executar com `python -O`. O workflow baixa o PDF original e exige tamanho, SHA, 71 páginas e âncoras do texto. A interpretação da tabela original exige confronto visual porque ela está impressa rotacionada; extração isolada de OCR não basta.

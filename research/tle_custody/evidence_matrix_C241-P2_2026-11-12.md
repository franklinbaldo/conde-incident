---
type: Guide
title: "C241-P2: holdout cronológico de precessão nodal J2"
description: "Nova ocorrência de diagnóstico secundário: derivação e teste de taxa nodal congelada, sem medir órbita física."
---

# C241-P2: taxa J2 pré-declarada

**ID e ocorrência:** C241-P2#1. Acrescenta conexão ao [inventário C01–C238](../evidence_matrix_C001-C238_2026-11-11.md), C25#1, C179#1, C180#1, C181#1, C241-L4 e C241-P1#1, **sem alterar as linhas históricas**.

**Origem:** [Parquet moderno secundário oxzoid rev. 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09; CSV derivado 3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231, índices source_row preservados. NASA SSR primário de 15/11, C197#1, registra somente dia catalogado do decaimento.

**Variáveis e arestas:** último estado fit → i,e,n em unidades próprias → J2 secular fixo por NORAD → RAAN previsto em validação/avaliação → resíduo circular em graus vs série da mesma família → comparação com linear P1. Dependência única de espelho documental, sem triangulação instrumental.

**Unidades/épocas:** n rev/dia; i e RAAN graus; e adimensional; dOmega/dt graus/dia; épocas UTC de cada registro derivado, sem confirmação de frame instrumental de 1963. Incerteza de serialização não é sigma física.

**Estado da conexão:** CONNECTED_PENDING_CALIBRATION; aproximação secular testável, não restrição observacional ativada. **Antes/depois Θ:** igual, não quantificado. **Não-vazio de Θ:** nenhuma prova nova, pois não foi aplicado recorte instrumental. **Independência física:** não estabelecida. Teste externo exige arquivos instrumentais originais e covariâncias; sem eles, NOT_RUN. O CI fornece erros internos em graus, não localização de queda.

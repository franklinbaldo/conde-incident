---
type: Guide
title: "CGEO-12: auditoria topológica da malha nominal IBGE 1960"
description: "Contagem de arestas, área plana exata, projeção nativa e veto à inferência territorial de 1963."
---

# CGEO-12: auditoria topológica da malha nominal IBGE 1960

O arquivo conde_ibge_1960_topology_audit.json deriva **somente** de CGEO-10,
com a mesma cadeia IBGE/CGEO-11, sem alegar uma observação nova.
O algoritmo em tools/conde_ibge_1960_topology.py aplica aritmética decimal exata
ao shoelace e às intersecções no plano projetado **World_Polyconic**.
Confere anel fechado, orientação, duplicatas e cruzamentos não adjacentes.

A geometria retrospectiva de Conde traz 47 coordenadas, 46 arestas,
0 cruzamentos não adjacentes e orientação horária. Sua área plana algébrica
absoluta calculada é **983.1840473046875 km²**. A precisão desse cálculo
**não é precisão cartográfica**: o valor é propriedade dos vértices nativos
em metros projetados, não área jurídica, geodésica calibrada ou observação
topográfica de 1960/1963.

Não comparar diretamente a área plana CGEO-12 ao atributo 931,106 km² das
malhas IBGE 2022/2025 para inferir evolução territorial: bases, resolução,
épocas, metodologias e distorções de projeção não foram equalizadas.

Exportar/validar por:

    python3 -m tools.conde_ibge_1960_topology --check

Conservar nulos o limite jurídico de 1963, a localização do evento, sua
pertinência e orçamento de erro. As relações cumulativas são
CGEO-10 → CGEO-12 (COMPUTED_FROM_SAME_PINNED_VERTICES_NOT_NEW_SOURCE)
e CGEO-12 → LEGAL_BOUNDARY_CONDE_1963_LATENT
(NOT_A_VALIDATED_TEMPORAL_BRIDGE). É vedado computar probabilidades
de reentrada com base nessa auditoria geométrica.

---
type: Guide
title: 'C241-L50: rótulos Agena B/D até hipóteses e latentes'
description: 'Ponte Quest–NASA–NRO–GCAT sobre 2313 e 528 sem atribuir hardware ou medições ao fragmento.'
---

# C241-L50: rótulo de lançador não identifica pedaço 528

Fonte custodiada: Jonathan McDowell, Quest, vol. 4, nº 4 (1995), tabela “Program 102 Missions”, página impressa 40 (PDF índice 1). PDF https://planet4589.org/jcm/pubs/space/papers/1995/Quest95b.pdf, SHA-256 9dec4037537ea648a41501381c62d0f6eadfbd4fad807d27eb1fd7f748eb1ed1, 14.469.995 bytes. O PDF e a leitura visual foram auditados pela Tartaruga, C241-L50.

A Quest imprime “Thor Agena D” para Ferret 3 / 2313, assim como a NASA SP-4004 (1964, página 502), mas esta última refere ao grupo 1963-3 sem identificar 528. GCAT moderno imprime “Thor Agena B” e “Agena B 2313”. NRO C241-L48 é uma história institucional de 1994, recuperada apenas como texto indexado, sem fac-símile autenticado. Não há demonstração de qual linhagem instrumentou as fontes. Quest e GCAT têm autor em comum, o que não cria observação independente. A operação elétrica da missão 7153 não fornece época da queda orbital.

O exportador tools/export_quest_stage_scientific_bridge.py valida SHA-256 de quatro ledgers C241-L50/L15/L48/L40, a auditoria Quest, identidades, os limites do rótulo do grupo NASA e os valores nulos do NRO/GCAT. Produz public/data/conde-quest-stage-scientific-bridge.json com 14 dependências e 8 latentes ainda sem valor. A matriz C197#1 é relacionada somente como notícia NASA de dia de decaimento, não como identificação do veículo ou peça.

As hipóteses H:2313_B_OR_D e H:528_PIECE_IDENTITY ficam abertas; H:NASA_D_IMPLIES_528_MASS é rejeitada. O nome do candidato Lean é apenas uma proposta documental, não teorema compilado. Nenhum observável NORAD 528, posterior ou localização se torna ativo. Θ inalterado.

Reproduzir a ponte e os controles adversariais:

    python3 tools/export_quest_stage_scientific_bridge.py --check-site
    python3 -m unittest discover -s tests -p test_quest_stage_scientific_bridge.py -v
    python3 -O -m unittest discover -s tests -p test_quest_stage_scientific_bridge.py -q

Próxima evidência necessária: ficha de engenharia Lockheed/USAF de 1963 para o estágio 2313, identificação de peça NORAD 528, e depois observação instrumental com UTC, estação, referencial e covariância. Sem isso, a divergência B/D não reduz a região de queda.


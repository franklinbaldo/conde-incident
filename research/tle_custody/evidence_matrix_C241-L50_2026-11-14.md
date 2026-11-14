---
type: Guide
title: 'C241-L50: Quest 1995 imprime Agena D para 2313'
description: 'Custódia de fac-símile histórico e confronto Agena B x D, sem atribuir hardware ou medições ao NORAD 528.'
---

# C241-L50: fonte editorial de 1995 para o conflito Agena B × D

A revista *Quest*, vol. 4, nº 4 (1995), publicou o artigo de **Jonathan McDowell**, *U.S. Reconnaissance Satellite Programs, Part 2: Beyond Imaging*. Recuperei o [PDF integral](https://planet4589.org/jcm/pubs/space/papers/1995/Quest95b.pdf): **14.469.995 bytes**, SHA-256 `9dec4037537ea648a41501381c62d0f6eadfbd4fad807d27eb1fd7f748eb1ed1`, **sete páginas PDF**, sem camada textual extraível. A tabela **“Program 102 Missions”**, na **página impressa 40 (PDF índice zero 1)**, foi conferida diretamente em imagem rasterizada.

Na linha **Ferret 3 / Agena 2313 / 16 Jan 1963**, a tabela imprime **“Thor Agena D”**, órbita como impressa `459 x 533 x 81.9` e período `94.7`. O **Ferret 2 / 2312** está como *Thor Agena B* e o **Ferret 4 / 2314** como *TAT Agena B*. Esses controles conferem alinhamento de coluna. Os números orbitais não têm época instrumental, estação ou erro individual explicitados nessa tabela, portanto **não são novos elementos para propagação do NORAD 528**.

Há **conflito editorial não resolvido**: NASA *SP-4004* (1964, p. 502) apresenta *Thor-Agena D* para o grupo `1963-3` (C241-L15); o texto indexado da NSA (1975, p. 5, ainda sem autenticação visual de sua cópia) associa `7153/2313` a *Thor-Agena D* (C241-L49); já [Gunter's Space Page](https://space.skyrocket.de/doc_sdat/p-102.htm) registra **Thor-DM21 Agena-B** para 2313. A fonte *Quest* é um registro editorial publicado em 1995, anterior à divulgação pública da cópia NSA em 2017, mas **não está estabelecida independência de dados instrumentais** nem qual fonte anterior alimentou sua tabela.

A linha da revista não demonstra que o fragmento **1963-003B/NORAD 528** corresponda fisicamente ao estágio 2313, nem comprova sua massa, material, período, hora ou local de reentrada. **Nada ativado na simulação ou no Lean: `THETA_UNCHANGED`.** A inferência do corpo relatado em Conde permanece inteiramente separada.

**Reprodução:** `python3 -m unittest discover -s tests -p test_tle_quest_stage_c241_l50.py -v` também com `python3 -O`; `python3 tools/tle_quest_stage_c241_l50.py --source-file /caminho/Quest95b.pdf` exige `pypdf==6.1.3` e revalida bytes, SHA, sete páginas e ausência de texto. A inspeção visual da tabela é humana, não um resultado de OCR ou teste automatizado.

**Próxima evidência:** documento Lockheed/USAF contemporâneo vinculando estágio **2313** a Agena B ou D; e, independentemente, medição **SPADATS/SAO do NORAD 528** com estação, UTC, grandeza e erro. Referências: [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396), [Cafezinho #16](https://github.com/franklinbaldo/cafezinho/issues/16).

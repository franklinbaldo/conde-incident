---
type: Guide
title: 'C241-L51: fac-símiles NSA 1975 e NRO 1994 conferidos'
description: 'Custódia binária e inspeção visual de relatórios desclassificados sobre 7153/2313; Agena B/D não resolvido.'
---

# C241-L51 — Fac-símiles desclassificados, missão 7153 / veículo 2313

Em 14/11/2026 foram recuperados integralmente **dois PDFs**, antes acessíveis à equipe apenas por índice textual (falhas remotas 403/406). Os downloads HTTPS retornaram `200` e foram preservados temporariamente fora do Git. Os hashes abaixo referem-se **exatamente aos bytes baixados**, não à identidade abstrata da obra.

| Documento | PDF páginas | Página física | Página impressa | Bytes | SHA-256 |
|---|---:|---:|---:|---:|---|
| [NSA *NSA in Space*, abril/1975, BYE-19385-75](https://www.governmentattic.org/26docs/NSAinSpaceViaNRO_1975.pdf) | 248 | 132 (índice zero 131) | 5, **apêndice A** | 4.853.647 | `3d5d7a22608d3eb9ab23f61f46da924708d471917f77ee5f3a68ae8910aeab74` |
| [NRO *The SIGINT Satellite Story*, redação de 1994](https://www.governmentattic.org/19docs/NRO-SIGINTsatStory_1994u.pdf) | 430 | 123 (índice zero 122) | 90, narrativa | 14.454.222 | `1bffa3e121073c8a312c9f67393efac09aa0a322e18ce039e592df0454e13c8a` |

**Inspeção visual da imagem original, não OCR:** a página 132 do PDF NSA contém a linha `7153 | 698 BK IV | 2313 | Thor-Agena D | 16 Jan 63`. A página impressa 5 pertence ao **apêndice A** (tabela de payloads), não à página 5 da seção narrativa inicial. A tabela confirma uma **classificação escrita em 1975**, não prova que o estágio montado fosse fisicamente D.

Na página 123 do PDF NRO (página impressa 90), o texto associa `vehicle 2313 / mission 7153` a lançamento em **16 de janeiro de 1963 usando um Thor** e a **dois dias de operação até falha de bateria**. Não diz Agena B nem D nessa passagem. Identifica o lançamento seguinte, `2314/7154` de 29 de junho de 1963, como TAT. A narrativa distingue o lançador não aumentado do seguinte, mas **não resolve a variante Agena**. A falha elétrica é **fim de missão**, não desintegração, observação de reentrada ou causa de fragmentação.

**Confronto:** NASA *SP-4004* (1964, p. 502, C241-L15) chama o grupo `1963-3` de Thor-Agena D; *Quest* 1995 (C241-L50) chama o 2313 de Agena D; NSA 1975 também imprime D; Gunter's Space Page (catálogo secundário moderno) publica [Agena B](https://space.skyrocket.de/doc_sdat/p-102.htm) para 2313. Não contar três impressos como três medições de hardware nem presumir independência de suas genealogias. Publicação e desclassificação são datas distintas. O documento NSA foi liberado pelo NRO em 08/11/2017; o PDF NRO 1994 hospedado em 2016 tem data de liberação não fixada aqui.

**Fronteira para o NORAD 528:** nenhum desses fac-símiles menciona sensor, estação, medida orbital ou identificação de `1963-003B` como peça física. A relação catálogo `003B↔528` provém da tabela NASA 1977 C241-L32, não dos dois PDFs acima. Todos os campos instrumentais continuam `null`, `physical_constraint_active=false` e `THETA_UNCHANGED`. Não se pode deduzir hora ou local de queda em Conde.

**Reprodução:** `python3 -m unittest discover -s tests -p 'test_tle_declassified_facsimiles_c241_l51.py' -v` (também `python3 -O`); `python3 tools/tle_declassified_facsimiles_c241_l51.py --source-dir /caminho/dos/pdfs` confere bytes/hash/cabeçalho e EOF; `--verify-remote --full-pdf` recupera ambos e confere também número de páginas com `pypdf==6.1.3`. A transcrição é **verificação visual humana**, que o teste de hash e o texto extraído não substituem.

**Próximo teste discriminante:** desenho original de fabricação/integração da **Agena 2313** com variante e motor, e logs de observação SPADATS/SAO do `1963-003B` com época UTC, estação, observável, referencial e erro. Trabalho vinculado a [Conde #396](https://github.com/franklinbaldo/conde-incident/issues/396), [Tartaruga #6](https://github.com/franklinbaldo/tartaruga/issues/6) e [Cafezinho #16](https://github.com/franklinbaldo/cafezinho/issues/16).

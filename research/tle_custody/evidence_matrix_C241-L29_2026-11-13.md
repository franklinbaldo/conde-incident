---
type: Guide
title: "C241-L29: duas séries soviéticas com fascículos de 1963 catalogados"
description: "Localização institucional dos exemplares e hashes dos catálogos HTML; fac-símiles e medições dos objetos 527–529 ainda ausentes."
---

# C241-L29: edições identificadas no catálogo de Kyiv

Para a [issue #545](https://github.com/franklinbaldo/conde-incident/issues/545), dois títulos diferentes aparecem no catálogo da biblioteca científica do Observatório Astronômico Principal da Academia Nacional de Ciências da Ucrânia.

1. [Publicações de instituições científicas](https://mao.kiev.ua/index.php/ua/gao-biblio-periodyka/specissues): *Бюллетень станции оптического наблюдения ИСЗ*, **números 32–37, ano 1963**.
2. [Periódicos da seção N](https://mao.kiev.ua/index.php/ua/gao-biblio-periodyka/sciencefilds-n): *Наблюдения ИСЗ*, **número 2, ano 1963**.

Ambas as páginas HTML responderam HTTP 200 por HTTPS em 13/11/2026. Os comprimentos e hashes SHA-256 dos **catálogos**, não dos fascículos, estão no [ledger C241-L29](soviet_1963_bibliographic_holdings_C241-L29.json). O alias maoling.mao.kiev.ua apresentou certificado TLS incompatível; as capturas auditadas foram obtidas pelo domínio mao.kiev.ua com validação TLS normal. Nenhum arquivo grande foi colocado no Git.

**Status: INSTITUTIONAL_LIBRARY_HOLDINGS_ONLY.** Não obtivemos as páginas dos fascículos nem prova de seu conteúdo, medições de estação, horários ou identificação 527/528/529. Tampouco ficou provado que esses dois títulos sejam equivalentes ou constituam séries independentes de observações. Preservar a distinção entre catálogo, exemplar, observação bruta, órbita calculada e previsão.

**Reprodução:** python3 tools/verify_soviet_1963_holdings.py --html-dir /diretorio/html; python3 -m unittest tests.test_soviet_1963_holdings -v. O replay só pode declarar integridade dos HTML quando os dois arquivos de nomes registrados no ledger estiverem presentes.

**Próximo passo:** localizar fac-símiles dos fascículos 32–37 e nº 2; ler páginas e sumários, procurar designações 1963-003A/B/C e cotejar com 🐢 Tartaruga se houver observações datadas. Nenhuma restrição orbital ou localização de queda foi ativada.

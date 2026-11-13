---
type: Guide
title: "C241-L37: localizar a série soviética de dados brutos de observação"
description: "Fonte institucional de 2007 diferencia boletins de método e de observações, com catálogo RNB de dados de junho de 1963 sem fac-símile."
---

# C241-L37 · Onde procurar medições, não apenas artigos

**Resultado arquivístico:** a astrônoma Alla G. Masevich, que descreve sua coordenação da rede óptica soviética, distingue **duas séries** no ensaio retrospectivo publicado pelo Instituto de Pesquisas Espaciais da Academia Russa (IKI RAS) em **2007**:

1. *Бюллетень станций оптического наблюдения искусственных спутников Земли*: métodos, aparelhos, aperfeiçoamento de precisão, artigos científicos e edições especiais.
2. *Результаты наблюдений ИСЗ*: publicação de **dados originais de observações visuais e, mais tarde, fotográficas**. Esta segunda família é agora uma prioridade para localizar linhas com estações, datas e posições que possam ser testadas independentemente.

**Fonte auditável:** [PDF oficial IKI RAS](https://iki.cosmos.ru/sites/default/files/publications/2007pervaya_r.pdf), contribuição de Masevich começando na página impressa 99; **páginas impressas 104–105, folha PDF 53 (índice zero 52)**. Download integral em 13/11/2026: **7.317.076 bytes**, SHA-256 `8dc0d5b54985ab53d394babbad36da03ae02cef17f5ad897ad94e05acf9005f5`. Inspeção visual da dupla página confirmou o trecho. É fonte **retrospectiva de 2007**, não caderno de 1963.

**Rota de acervo identificada:** a [Biblioteca Eletrônica Nacional russa, registro RNB `1000287767`](https://rusneb.ru/catalog/000200_000018_RU_NLR_INFOCOMM10_1000287767/), lista um volume da família *Результаты наблюдений искусственных спутников Земли*, publicado em **1964**, que descreve **coordenadas equatoriais e horizontais de junho de 1963** para satélites explicitamente nomeados (Kosmos 14/17, Vostok 5 e outros). Isso comprova a existência de **metadados bibliográficos com mês de observação anterior ao ano editorial**, mas não prova que os volumes contenham o objeto 1963-003, muito menos que o fac-símile esteja acessível. A leitura direta pelo executor retornou HTTP 403. **Sem bytes do documento, sem hash.** Outro [catálogo Google Books](https://books.google.com/books?id=kfi6AAAAIAAJ) lista o volume 224 da série; a digitalização de 2008 não certifica observações de 1963 nem disponibilidade de páginas.

**Conexão cumulativa:** C241-L29/L31/L34/L35 catalogavam fascículos do **boletim metodológico**, especialmente nº 38 e 42 de 1964. Este registro acrescenta **um ramo editorial de dados instrumentais originais** potencialmente mais discriminante. Títulos variantes devem ser desambiguados antes de fundir séries ou atribuir volume a uma data.

**Próximo teste:** localizar no ramo de *Результаты наблюдений* os volumes com **datas observacionais 7–9/11/1963**; recuperar fac-símiles com título/edição/página/assinatura/hash; verificar se há entradas 1963-003A/B/C, 527/528/529 ou designações inequívocas, hora, estação, referencial e incerteza. Encaminhar possíveis linhas à 🐢 Tartaruga. **Ainda são zero medições independentes e zero restrições orbitais novas.** Ninguém foi contatado.

**Reprodução offline:** `python3 -m unittest discover -s tests -p test_soviet_raw_observations_route.py -v`. Replay binário opcional: `python3 tools/verify_soviet_raw_observations_route.py --pdf /caminho/2007pervaya_r.pdf`. Não versionar PDF de 7,3 MB; o repositório mantém somente custódia e testes.

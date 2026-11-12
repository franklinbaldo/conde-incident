# Caso Conde, 1963: cobertura histórica das radiossondagens próximas na NOAA IGRA

**Rodada:** 12/11/2026. **Pergunta concreta:** a IGRA 2 contém séries de 1963 das estações de **Salvador** ou **Aracaju**, de modo que já possamos procurar um perfil local de vento em 8/11, como próximo teste da hipótese do balão?

**Resultado:** a lista oficial de estações da NOAA/NCEI atribui **1970** como primeiro ano da série disponibilizada para Salvador e **1974** para Aracaju. **A busca de um perfil IGRA de Salvador ou Aracaju de 1963 fica afastada por insuficiência da cobertura declarada do arquivo**, mas isso não refuta que estações tenham feito lançamentos em 1963 fora desse conjunto. Recife tem cobertura geral desde **1952**; a observação específica de 8/11 já está na matriz `C151#1`. Há outro acervo FAB/NCAR, `d394001`, que começa em 1950 no agregado, porém sem confirmação de estação e dia.

## Documento efetivamente verificado e proveniência

1. **NOAA/NCEI, lista original do arquivo IGRA 2**, leitura textual direta em 12/11/2026: https://www.ncei.noaa.gov/pub/data/igra/igra2-station-list.txt. Trechos literalmente identificados:

   - `BRM00082900  -8.0500  -34.9167    7.0    RECIFE (82900-0)               1952 2019  14977` (linha 284).
   - `BRM00083096 -10.9170  -37.0500    5.0    ARACAJU                        1974 1979    417` (linha 292).
   - `BRM00083229 -13.0167  -38.5167   52.0    SALVADOR (83229-0)             1970 2018   7954` (linha 295).

   Os anos são **primeiro/último da série arquivada**, não datas de instalação/encerramento de estações meteorológicas. **Grau**: documento primário da instituição custodiante para a cobertura que ela anuncia **hoje**, não fonte contemporânea de 1963 nem evidência de balão. A extração foi feita via visualização textual do site oficial; o acesso binário direto a partir do ambiente de execução falhou por resolução DNS, de modo que **SHA-256: não calculado**. Texto exato e URL fornecem trilha para repetir a consulta. Esta família não depende da Rádio Tupi nem do FBIS; a eventual presença das mesmas medições em outro arquivo não transforma dados meteorológicos repetidos em testemunhas independentes.

2. **NSF NCAR GDEX**, catálogo institucional `d394001`, DOI [10.5065/BYQV-RZ12](https://doi.org/10.5065/BYQV-RZ12), consulta direta: https://gdex.ucar.edu/datasets/d394001/. Informa que a coleção de dados registrados pela FAB, recebida via NCDC, tem **11 estações de rawinsonde e 30 de pibal**, no intervalo geral de 1950 a 1986, mas as datas variam por estação. O período agregado **não demonstra** que Salvador tenha medição em 8/11/1963. **Grau**: catálogo institucional primário do conjunto preservado, não fac-símile de observação de 1963. Como esse acervo também passou pelo NCDC, uma eventual coincidência de dados com IGRA exige deduplicação da cadeia de custódia.

3. **NOAA IGRA 2**, página institucional: https://www.ncei.noaa.gov/products/weather-balloon/integrated-global-radiosonde-archive. Explica que horários, níveis verticais, variáveis, períodos e cobertura variam por estação e que o tratamento inclui controle de qualidade. Reforça a distinção entre catálogo de dados e registro original de lançamento. Não usada como prova de ocorrência.

## Matriz incremental de evidências e grafo cumulativo

O arquivo `research/constraints/igra_bahia_1963_coverage.json` registra as quatro ocorrências locais **MET-IGRA-20261112-01 a 04**, com unidades, variáveis observáveis, dependências e incertezas. Esses IDs são **provisórios e não colidem com C001–C238**; conciliar por fonte e ocorrência antes de uma incorporação à matriz global.

| ID | O que está diretamente demonstrado | Variável ligada | Estado |
| --- | --- | --- | --- |
| MET-IGRA-20261112-01 | Salvador `BRM00083229`, início arquivado 1970 | `IGRA2_catalogue_coverage_Salvador_1963=false` | Lacuna do **arquivo**, não ausência de balão |
| MET-IGRA-20261112-02 | Aracaju `BRM00083096`, início arquivado 1974 | `IGRA2_catalogue_coverage_Aracaju_1963=false` | Idem |
| MET-IGRA-20261112-03 | Recife `BRM00082900`, intervalo geral 1952–2019 | `IGRA2_catalogue_period_compatibility_Recife_1963=true` | Apenas elegibilidade; ocorrência C151#1 separada |
| MET-IGRA-20261112-04 | GDEX d394001 inclui registros brasileiros entre 1950–1986 | `GDEX_d394001_station_day_Salvador_1963_11_08=null` | Disponibilidade específica ainda desconhecida |

**Conexões acumuladas:** 4 ocorrências + 4 relações com as variáveis latentes de ventos regionais e os dados anteriores de Recife (`C151#1`). A relação `archive_year_eligible` pode filtrar a busca de dados, **não** a história do objeto. A restrição meteorológica candidata futura é condicional: caso seja obtida uma radiossondagem com fonte, época/altitude e erro conhecido, e caso se valide transferência espacial a Conde, poderemos restringir um envelope de ventos. Não definimos aqui nem vento em Conde, nem trajetória de balão, nem impacto do NORAD 528.

**Falsificação de hipóteses rivais:**

- H1: “a série IGRA 2 publicada para Salvador já tem perfis de 1963” → **contrariada pela linha oficial do próprio inventário**.
- H2: “não há observação de balão em Salvador em 1963 porque IGRA começa em 1970” → **inferência inválida**, não apoiada: dados ausentes num arquivo não equivalem a inexistência de lançamento; o acervo FAB é uma alternativa concreta.
- H3: “os ventos de Recife em C151 servem diretamente a Conde” → **não validada**; faltam campo espaço-temporal de vento e erro de transferência.
- H4: “as medições da FAB/GDEX cobrem Salvador em 8/11/1963” → **aberta**; procurar inventário por estação/data do d394001. Se estiver coberta, inspecionar os dados em bruto e comparar com IGRA para verificar duplicação de upstream.

## Buscas jornalísticas tentadas na rodada

Buscas direcionadas pelas datas e expressões “Conde/esfera”, `Diário de Notícias 9/11/1963`, `Jornal da Bahia 11/11/1963` e pela transmissão “Radio Tupi 2330” recuperaram **artigos derivados de 2026** e reproduções da correspondência diplomática já conhecida, **não fac-símiles novos de jornal de 1963**. Não reintroduzir essas republicações na matriz como corroboração. A convenção UTC/local do horário FBIS permanece aberta; não converter horário sem instrução da agência.

## Próxima pergunta discriminante

Consultar inventário **por estação/data** do arquivo FAB/NCAR d394001 para **7–9/11/1963**. Caso a estação apareça, recuperar **níveis verticais e hora real de lançamento**, registrar proveniência e independência, e conectar as séries com os observáveis do modelo físico. Em paralelo, prosseguir acesso aos recortes originais baianos já localizados no IGHB, priorizando a cadeia de origem da notícia.

**Delta de conectividade**: quatro novas ocorrências e quatro arestas com as variáveis meteorológicas existentes. **Delta de domínio admissível físico:** não avaliável com metadados de cobertura de arquivo; isso não cancela as conexões. **Sem nova confirmação de balão, esfera, cratera, cadáver ou impacto.**

# 🦀 Conde (BA): custódia geoespacial do IBGE e fronteira temporal

**Escopo:** município de Conde, Bahia (**código IBGE 2908606**). Este pacote oferece um *contorno administrativo moderno documentado*, **não** o lugar de uma queda e **não** a delimitação legal/geográfica de novembro de 1963.

## Registros adicionais à matriz congelada C001–C238

A matriz histórica `research/evidence_matrix_C001-C238_2026-11-11.md` é uma fotografia com hash exigido por outros contratos; não foi alterada nesta fatia. O item **C24** é o vínculo anterior com um polígono consultado por GIS, e os registros abaixo são **novos registros de custódia complementares**:

| ID | Registro/observável | Custódia e independência | Estado/limite |
| --- | --- | --- | --- |
| **CGEO-01** | Conde, BA, código IBGE `2908606`: geometria da **Malha Municipal Digital 2022**, polígono com **3.303 vértices** incluindo fechamento, atributo `AREA_KM2=931.106`; bbox `[-37.865864487, -12.098981088, -37.512838408, -11.629389719]` em longitude/latitude | [ZIP oficial IBGE 2022](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/BA/BA_Municipios_2022.zip), SHA256 `6559f564071dec2d49e3c55061049190054ea71121cb02e2e6d9cbf8e9bc7c48`; registro SHP SHA256 `6d7f5a4704bec09f09a9fcbc4d82cd287cae1c541d7606ffd51a805d8d87b678`; DBF linha 105 (índice 104) | Dado cartográfico oficial contemporâneo; nenhuma precisão cadastral ou validade para 1963 inferida |
| **CGEO-02** | Malha Municipal Digital **2025**: **3.260 vértices** incluindo fechamento, atributo `AREA_KM2=931.106`; bbox `[-37.8658645, -12.0989791, -37.5128384, -11.6293897]` | [ZIP oficial IBGE 2025](https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2025/UFs/BA/BA_Municipios_2025.zip), SHA256 `cac0d02febfaaf1da20d0d5c1fe5d6289377ffaa745c8334ec9b7d85a413956f`; registro SHP SHA256 `e31617673efb495573fcde3a7bfe34d7644d1be66db140ac34aef01840c4a79d`; DBF linha 306 (índice 305) | Outra edição **da mesma família IBGE**; não são dois levantamentos de observação independentes; número de vértices não mede mudança legal de limites |
| **CGEO-03** | A [ficha histórica do IBGE para Conde](https://www.ibge.gov.br/biblioteca/visualizacao/dtb/bahia/conde.pdf) descreve reinstalação municipal em **30/08/1935** (Decreto 9.662/1935) e divisão territorial de **01/07/1960** com distrito-sede | Texto indexado do PDF institucional conferido; tentativa de screenshot da página falhou por HTTP 403. Origem citada no documento: Enciclopédia dos Municípios Brasileiros, vol. XX (1958) | Documenta condição administrativa, **não vértices de limites vigentes em 08/11/1963**. A imagem do documento ainda requer inspeção visual |
| **CGEO-04** | C24 registra um polígono **atribuído à CONDER**, com 3.677 vértices e bbox aprox. `[-37.865877,-12.098900,-37.515205,-11.629385]`; o arquivo local consultado contém atributo `AREA_KM2=964.40032361` | Arquivo pré-existente `/workspace/conde-municipio.geojson`, SHA256 `4f43f0990fcfcc60e18bca02371a1102438ff6981e7ed8ad551230a8cd4b10d3`, **sem URL institucional exata/documentação de captura recuperadas nesta rodada**. Base diferente da malha IBGE; **não** tratar como confirmação independente | Divergência **dos atributos de área**: 33,29432361 km² (+3,58% ante o atributo IBGE). **Não** deduzir reforma territorial em qualquer data nem precisão de fonte não custodiada |

As duas edições IBGE repetem o atributo de área de **931,106 km²**. O cálculo esférico simplificado sobre os vértices retorna ~934,76 km², **não** substitui a área oficial nem significa erro do IBGE: sua técnica, projeção e superfície de referência diferem. Evitar comparação ingênua de área obtida por somas em graus quadrados.

## Sistema de coordenadas e natureza dos dados

Os arquivos ZIP originais contêm `.prj` com **SIRGAS 2000, coordenadas geográficas, graus**. A edição 2022 inclui `AUTHORITY[EPSG,4674]`; a de 2025 descreve datum e elipsoide SIRGAS 2000 sem o identificador numérico no WKT, equivalente sob os campos conferidos ao EPSG:4674. Os JSONs preservam **exatamente os pares lon/lat do SHP**, sem reprojectar nem transformar o datum. São **geometrias JSON em CRS nativo**, com a aparência de `Polygon` GeoJSON, porém **não** devem ser interpretadas como WGS84/GeoJSON RFC 7946 sem transformação explicitamente justificada.

A [página oficial de Malhas do IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/malhas-territoriais/15774-malhas.html) descreve o uso do Sistema Geodésico Brasileiro, atualmente SIRGAS 2000; essas são malhas político-administrativas de cartografia, não medições da posição de objeto espacial. **Precisão horizontal e validade para 1963 são desconhecidas aqui.** Não basta trocar etiquetas EPSG:4674 ↔ EPSG:4326 para demonstrar precisão; transformação, época geodésica e orçamento de erro devem ser documentados.

## Contrato exportável para Castor

`tools/conde_gis.py` entrega dois modos:

1. **Reproduzir cada aquisição** com SHA256 do ZIP, identidade do registro DBF, bytes do registro SHP, geometria única/fechada, CRS e área. O script recusa fontes/arquivos diferentes; não usa pacotes externos:
   ```sh
   curl -fL -o /tmp/BA_Municipios_2022.zip 'https://geoftp.ibge.gov.br/organizacao_do_territorio/malhas_territoriais/malhas_municipais/municipio_2022/UFs/BA/BA_Municipios_2022.zip'
   python3 tools/conde_gis.py --extract /tmp/BA_Municipios_2022.zip --year 2022 --output /tmp/conde_ibge_2022_sirgas2000.json
   cmp /tmp/conde_ibge_2022_sirgas2000.json research/geo/conde_ibge_2022_sirgas2000.json
   ```
   Repetir para edição 2025 com os caminhos e ano correspondentes. O workflow existente `integration-head.yml` executa `tests/conde_gis_custody.test.mjs`, que reexecuta **ambos** no HEAD exato, sem fixtures sintéticas.
2. **Consultar um ponto já convertido para SIRGAS 2000** (lon/lat):
   ```sh
   python3 tools/conde_gis.py --lon -37.61 --lat -11.81 --point-crs EPSG:4674 --date 1963-11-08 --boundary-margin-m 100
   ```
   Coordenadas acima são apenas **ponto de teste aproximadamente próximo da sede, não uma observação do incidente**. O resultado mostra se ele cai dentro ou fora **das edições modernas**, uma distância **aproximada** à borda e uma faixa **escolhida pelo usuário** de 100 m (não precisão oficial). Se a query é de 1963, `historical_1963_membership=UNRESOLVED_NO_1963_BOUNDARY` e `can_constrain_historical_orbital_reentry=false` mesmo quando os polígonos modernos concordam.

Equações/arestas relevantes para a cadeia de evidências:

`CGEO-01/CGEO-02 -> polygon_native_4674(t) -> point_in_polygon(x_4674, y_4674) -> modern_membership`

`CGEO-03 + legislação/cartografia de limites 1963 (AUSENTE) -> municipal_boundary_1963 (LATENTE) -> 1963_membership`

`estado orbital ECI -> transformação temporal ECEF/WGS84 + erro -> datum SIRGAS 2000 + erro -> admissibilidade geográfica condicional`

A segunda e a terceira aresta **não estão fechadas**, portanto nenhuma inferência de exclusão/localização de reentrada e nenhuma probabilidade de pouso são autorizadas. A diferença entre edições modernas é útil como teste de estabilidade da geometria publicada, não demonstra imóvel limite em 1963.

**Próximo dado discriminante:** legislação de confrontações municipais vigente em novembro de 1963, mapa oficial de época georreferenciado com pontos de controle e precisão, ou coordenadas de uma observação local independente, com referência espacial explícita. Depois disso o Castor poderá definir um polígono histórico com incerteza e confrontá-lo com trajetória e envelope de erros verdadeiramente calibrados.


## Custódia da transição legal 1953–2017: CGEO-05 e CGEO-06

A geometria moderna de CGEO-01/02 **não** é retroprojetável para 1963. Esta fatia adiciona fontes históricas com ocorrências específicas, sem converter coordenadas legislativas em um polígono inventado. O índice C24 da matriz cumulativa permanece preservado; esta seção e conde_legal_1953_2017.json complementam sua proveniência.

| ID | Constatação documental, tempo e origem | Limite epistemológico |
| --- | --- | --- |
| **CGEO-05** | [SEI Bahia, *Estatísticas dos Municípios Baianos*, 2013, v.4 n.1, p.149](https://www.ba.gov.br/sei/sites/site-sei/files/migracao_2024/arquivos/images/publicacoes/download/estatisticas_municipios/litoral_norte_2013.pdf), seção 1.2, indica **Lei 628 de 30/12/1953** como vigente em 2013 e referências a Esplanada, Rio Real e Jandaíra. PDF SHA256 e4364fc77070053481184f2c606b9fb18dcd87d5c2da603ec1f7617720fe2c57 (18.424.158 bytes). | Fonte compilada **de 2013**, não o anexo da Lei 628/1953, nem prova contínua de validade espacial entre 1954 e novembro de 1963. Texto indexado e bytes inspecionados; screenshot remoto indisponível por tamanho do PDF. |
| **CGEO-06** | [Lei baiana 13.720, de 27/04/2017, DOE ALEBA n. 22.166 em 28/04/2017, art. 1º §8º, incisos I–IV, pp.9–10](https://ftp.sei.ba.gov.br/Geoinformacao/leis/lim_mun/aprov/lei-no-13720-de-27-de-abril-de-2017.pdf), que **atualiza** os limites de Conde antes estabelecidos pela Lei 628/1953; art. 3º fixa vigência na data da publicação. PDF SHA256 76134441592ebc234dbd3856560ed6375f956f8e126c8ecced5244b9a38d89d9 (354.121 bytes). | Ato de **2017**, sem efeito retroativo demonstrado. Quatro confrontações Jandaíra, Atlântico, Esplanada e Rio Real; muitos pontos intermediários **não** formam polígono simples de quatro vértices. O texto inspecionado não identifica datum nem precisão dos ângulos. |

A diferença de atributo de área entre SEI 2013 (**964,7 km²** no indicador geográfico), CONDER não custodiada em CGEO-04 (**964,40032361 km²**) e IBGE 2022/2025 (**931,106 km²**) é **discrepância de fontes, datas e critérios**, não prova de modificação legal de divisa. O mesmo volume SEI 2013 traz na tabela do Censo outra área para 2010 (**954,70 km²**); não fundir atributos de origens distintas em uma medição.

### Contrato verificável para 🦫 Castor

- research/geo/conde_legal_1953_2017.json guarda duas fontes (URL, página, hash), relações de dependência e quatro **extremos** das confrontações de 2017 em DMS literal, com coordinate_datum=null e published_positional_accuracy_m=null. Não são coordenadas observacionais da queda.
- tools/conde_legal_boundary.py confere as quatro extremidades e a continuidade **textual** das confrontações, nunca a geometria física. Faz conversão angular DMS para graus decimais **sem presumir datum** e não exporta geometria para GIS.
- tests/test_conde_legal_boundary.py verifica fontes, quatro seções, integridade da transcrição, intervalos DMS, veto à identificação automática de EPSG:4674 e impedimento de usar o memorial de 2017 para 1963. Executado pela descoberta integral no workflow Integration checks (exact head).

Para revalidar os bytes da lei, adquirir o PDF oficial e executar:

    python3 tools/conde_legal_boundary.py --date 1963-11-08 --verify-pdf /tmp/lei-13720-2017.pdf --source-id BA-ALEBA-LEI-13720-2017-DO-22166
    python3 -m unittest tests/test_conde_legal_boundary.py -v

O retorno com boundary_polygon_for_date=null e can_constrain_reentry_1963=false é contratual. Para datas após 28/04/2017, o memorial ainda **não** valida datum, completude cartográfica ou permanência da lei na data solicitada.

**Arestas preservadas:** CGEO-05 → lei_base_1953 (custódia pendente) → limites_vigentes_1963 (latente); CGEO-06 → memorial_2017 (texto, vértices com datum nulo) → alinhamento geodésico condicional; CGEO-01/02 → malhas modernas, *sem ponte temporal*. Status CONNECTED_PENDING_HISTORICAL_CUSTODY; nenhum novo corte do domínio admissível de 1963. Faltam anexos autênticos da Lei 628/1953, atos intervenientes, mapa/datum de época e orçamento de erro. O pedido à 🦦 Lontra [no inbox #2](https://github.com/franklinbaldo/lontra/issues/2) já cobre essa custódia.

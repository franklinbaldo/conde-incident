---
type: Guide
title: "🦀 Conde (BA): custódia geoespacial do IBGE e fronteira temporal"
description: "Fontes oficiais, CRS, integridade e limites temporais das geometrias municipais de Conde"
---

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
   Repetir para edição 2025 com os caminhos e ano correspondentes. O workflow `integration-head.yml` executa **os testes de custódia determinística offline** (`tests/conde_gis_custody.test.mjs` e `tests/test_conde_gis.py`) no HEAD exato, sem downloads na suíte geral. A **aquisição externa ao vivo** de cada ZIP oficial foi movida para o workflow separado `ibge-source-live.yml` (agendado ou manual), não-gating, com os mesmos hashes e replay integral. Nenhuma geometria sintética substitui a fonte.
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


## CGEO-07: status separado da disponibilidade do arquivo oficial (12/11/2026)

O **teste obrigatório offline** confere os JSONs já adquiridos, seus hashes de coordenadas e metadados contra a custódia fixada no extrator; exerce pertinência espacial moderna e o veto temporal em 1963. **Não** verifica novamente a disponibilidade, os bytes ZIP remotos, nem a autenticidade de uma aquisição inédita. Um CI obrigatório verde atesta somente essa custódia local e as demais regressões.

A verificação de **aquisição online**, sem mudança de fontes, depende de `CONDE_IBGE_LIVE_REPLAY=1` no workflow [IBGE source replay](../../.github/workflows/ibge-source-live.yml), separado do gate geral e executável por `workflow_dispatch` ou agenda semanal. Cada ZIP baixado do endereço oficial tem hash SHA256 integral, registro SHP, DBF, CRS e resultado reproduzido comparados com as referências fixadas em `tools/conde_gis.py`. ZIP de hash divergente, HTTP 404/403, conteúdo incorreto ou alteração geométrica produzem **FAIL**, não fallback. Timeout, DNS, conexão resetada e HTTP temporariamente indisponível produzem **NOT_RUN_REMOTE_SOURCE**, registrado no output e no resumo do workflow. Um run verde com SKIP/NOT_RUN **não equivale a autenticação online PASS**. Não existe retry automático, espelho substitutivo ou geração sintética de dados.

Motivação verificável: [CI #43250153782](https://github.com/franklinbaldo/conde-incident/actions/runs/43250153782), [#43250239968](https://github.com/franklinbaldo/conde-incident/actions/runs/43250239968) e [#43251016890](https://github.com/franklinbaldo/conde-incident/actions/runs/43251016890) falharam por timeout ou reset de conexão do servidor IBGE, embora a fonte original e seus hashes continuem fixados. O novo contrato evita que essa indisponibilidade transitória impeça alterações independentes no simulador ou nas provas e conserva o resultado negativo observável. **Os dados seguem contemporâneos (2022/2025); 1963 permanece sem polígono autenticado.**

## CGEO-08: símbolo dos limites na folha Aracaju-SE, 1954/1961

A [carta UWM/AGSL agdm/10814](https://collections.lib.uwm.edu/digital/collection/agdm/id/10814/) é a MESMA fonte custodiada pela Lontra em ARCH-UWM-ARACAJU-SE-10814-20261112; não é observação independente. No [recorte ampliado da legenda](https://collections.lib.uwm.edu/digital/iiif/agdm/10814/780,6080,3100,1410/2800,/0/default.jpg) lê-se LIMITES com **Internacional**, **Interestadual** e **Marco de fronteira**, sem convenção própria para **limite municipal** nesse painel. O [imprint](https://collections.lib.uwm.edu/digital/iiif/agdm/10814/650,5890,5800,370/2200,/0/default.jpg) traz literalmente **“Projeção policônica da Carta Internacional ao milionésimo”**; a escala é 1:500.000. A versão combina registro editorial de dezembro de 1954 com atualização **das vias de comunicação** em 1961: não se demonstrou revisão territorial em 1961, data da impressão digitalizada nem limites administrativos em 08/11/1963.

A legenda CONDE, o Rio Real e o litoral permitem contexto toponímico/hidrográfico *qualitativo*, não o polígono de Conde de 1963, um EPSG, datum, margem de erro, ponto ou hora de queda. O documento CGEO-08 (research/geo/uwm_aracaju_se_1954_1961_legend_review.json) guarda URLs exatas, hashes SHA256 dos três JPEGs derivados e ligação à custódia anterior. O contrato exportável ao Castor é reproduzido por python3 tools/conde_historical_legend.py --date 1963-11-08, retornando **CONNECTED_PENDING_CALIBRATION**, com geometria histórica, datum e pertinência nulos; tests/test_conde_historical_legend.py verifica o veto e detecta adulteração. A fonte original JP2 e o texto integral da Lei 628/1953 ainda não foram adquiridos/validados neste trabalho.

## CGEO-09: Decreto 12.978/1944 e Lei 628/1953, relação legal condicionada

A [transcrição legislativa não oficial do Decreto BA 12.978/1944](https://leisestaduais.com.br/ba/decreto-n-12978-1944-bahia-retifica-o-decreto-lei-n-141-de-31-de-dezembro-de-1943-que-fixou-a-divisao-administrativa-e-judiciaria-do-estado-da-bahia-a-vigorar-sem-alteracao-ate-31-de-dezembro-de-1943) descreve em seu anexo 2, LXXIII (Jandaíra, divisa com Conde) topônimos hidrográficos Itapicuru, Pirangi, Baixa da Vitorina, riacho das Pedras e Caranguejo/Branco. Não há coordenadas, datum ou vértices completos autenticados. A [transcrição da Lei BA 628/1953](https://leisestaduais.com.br/ba/lei-ordinaria-n-628-1953-bahia-fixa-a-divisao-territorial-administrativa-do-estado-da-bahia-a-vigorar-de-01-de-janeiro-de-1954-a-31-de-dezembro-de-1958) estabelece no art. 1º a divisão territorial para **1954–1958**. Seu **art. 2º declara textualmente a continuidade de dispositivos do Decreto 12.978/1944**, ressalvando alterações pela própria lei e seus anexos II–VI não inspecionados. Portanto a hipótese de que os limites de 1944 simplesmente desapareceram em 1959 **não decorre** dessas transcrições; tampouco ficou demonstrada sua permanência inalterada em 1963. A [SEPLAN/SEI de 26/06/2013](https://www.ba.gov.br/seplan/noticias/sei-lanca-canal-de-informacoes-sobre-limites-intermunicipais) é relato oficial posterior, dependente de custódia dos atos anteriores.

O contrato [CGEO-09](conde_1944_1953_temporal_bridge.json) registra a aresta normativa **art. 2º/1953 → Decreto 12.978/1944**, com status `CONNECTED_PENDING_1953_ANNEX_ALTERATIONS_AND_LATER_ACTS`; ela **não** valida a identidade da divisa Conde/Jandaíra, atos de 1959–1963, datum, precisão, geometria ou local de reentrada. O validador `python3 tools/conde_historical_statutes.py --date 1963-11-08` entrega `AFTER_EXPLICIT_1953_DIVISION_PERIOD_CONTINUITY_UNVERIFIED`, `legal_boundary_for_date=null`, `point_membership=null` e `can_constrain_reentry=false`. Os dez testes específicos incluem mutantes que tentam promover ilicitamente o status ou apagar a aresta. **Fontes primárias oficiais de 1944/1953 ainda não foram inspecionadas; os anexos e leis posteriores precisam ser autenticados.**

## CGEO-11: origem retrospectiva em 1991 e falta de precisão declarada

O IBGE explicita na [Apresentação de sua série histórica, p. 1](ibge_1991_based_mesh_lineage_2026-11-12.md) que as malhas municipais históricas derivam de polígonos-base de **1991** e **não apresentam precisão cartográfica**. CGEO-10 é reconstrução nominal de 1960, não observação independente daquela época. O contrato [CGEO-11](ibge_1872_1991_methodology_2026-11-12.json), validador em tools/conde_ibge_lineage.py e onze testes impedem tratá-la como limite legal medido ou filtro de reentrada em 1963.

## CGEO-12: auditoria topológica da malha nominal 1960

A [auditoria reprodutível](ibge_1960_topology_audit.md) deriva somente dos
vértices CGEO-10, sem reclassificá-los como levantamento independente ou
limite de 1963. Verifique com python3 -m tools.conde_ibge_1960_topology --check.

## CGEO-19: fotos da Vila atribuídas a 1959

[Contrato e contexto](cgeo19_1959_editorial_photographs.md): três fotos atribuídas a 1959 num blog de 2012, com JPEGs auditados, autoria/data de captura não comprovadas e nenhuma posição de reentrada inferida.

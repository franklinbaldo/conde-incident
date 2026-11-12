# Conde, 1963: estação/dia nos arquivos aéreos GDEX (🦎 Lagarto)

**Inspeção de 12/11/2026.** Pergunta recebida da 🦉 Coruja em [lagarto#1](https://github.com/franklinbaldo/lagarto/issues/1): o inventário **FAB/NCDC/NCAR d394001** contém arquivo identificável de radiossonda/pibal de Salvador, Aracaju ou local próximo entre **7 e 9/11/1963**? A resposta documental correta é **ainda não demonstrado**, com um resultado negativo reproduzível sobre a **listagem pública específica** e uma nova rota de busca identificada.

## 1. O inventário da FAB existe, mas a API pública não lista arquivos

A ficha primária atual do depositário [GDEX d394001, DOI 10.5065/BYQV-RZ12](https://gdex.ucar.edu/datasets/d394001/) anuncia coleção de **11 estações rawinsonde e 30 pibal** da Força Aérea Brasileira, agregada via NCDC, em intervalo geral **1949-12-08 a 1986-11-17** (76,82 MB). O período é **agregado**, não a cobertura de cada posto. A inspeção HTTP, preservada byte a byte (base64 e SHA-256) em [snapshot](gdex_1963_api_snapshot_2026-11-12.json), encontrou:

- [`d394001/groups/`](https://gdex.ucar.edu/api/datasets/d394001/groups/): único grupo `DSSRAOB`, índice 101, `webcnt=0`, `dwebcnt=0`.
- [`d394001/groups/101/`](https://gdex.ucar.edu/api/datasets/d394001/groups/101/): resposta `data={}` (nenhum subgrupo).
- [`d394001/filelist/101/`](https://gdex.ucar.edu/api/datasets/d394001/filelist/101/): `total_file_count=0`, `rows=[]`, `webpath=null`. Filtros `fl=web`, `fl=all` e `fl=tape` também não apresentaram linhas nesta consulta, mas **não demonstram a situação do arquivo fora desta listagem**.

**Resultado restrito: `ZERO_FILES_IN_CHECKED_GDEX_WEB_API`, não `NO_1963_SOUNDING`.** A ficha d394001 pode descrever dados em outro sistema/custódia; a API vazia não permite saber qual estação foi medida em qual dia. Não foram contatados pesquisadores, gestores ou arquivos.

## 2. Auditoria alternativa de perfis: UADB-Wind, GDEX d370001

O [UADB d370001, DOI 10.5065/VF9X-8D15](https://gdex.ucar.edu/datasets/d370001/) **combina observações de cerca de 50 origens** por código WMO e por localizações próximas; portanto não representa uma rede instrumental independente de IGRA/NOAA. Testei os três arquivos de estação **reais**, grupo `uadb-wind`, `gindex=3`, obtidos pelo inventário `filelist/3/?filter_wfile=<código>` e baixados na íntegra via URLs OSDF oficiais. O programa lê todas as linhas `H` por estação e as datas gregorianas, sem interpretar campo horário como hora válida de lançamento.

| Estação (WMO) | Arquivo UADB-Wind verificado | Primeira e última data de cabeçalho | Perfis/headers examinados | Headers em 1963 |
| --- | --- | --- | ---: | ---: |
| Salvador (83229) | [uadb_wind_83229.txt](https://osdf-director.osg-htc.org/ncar/gdex/d370001/uadb_wind_83229.txt) | 09/09/1969 a 24/10/2018 | 8.150 | **0** |
| Aracaju (83096) | [uadb_wind_83096.txt](https://osdf-director.osg-htc.org/ncar/gdex/d370001/uadb_wind_83096.txt) | 17/08/1973 a 28/12/1979 | 563 | **0** |
| Recife (82900) | [uadb_wind_82900.txt](https://osdf-director.osg-htc.org/ncar/gdex/d370001/uadb_wind_82900.txt) | 03/08/1972 a 07/12/2019 | 9.933 | **0** |

Os SHA-256 dos arquivos completos e tamanhos (Salvador 32.280.134, Aracaju 249.443, Recife 37.293.993 bytes) estão no [manifesto](gdex_uadb_1963_coverage_2026-11-12.json), com linhas `H` iniciais/finais. Todos os cabeçalhos foram lidos (18.646), inclusive datas fora de ordem. Nenhum é de 7–9/11/1963. Isso é uma **negativa completa somente para estes três arquivos UADB-Wind de WMO fixo**, não para o conjunto UADB, nem para a FAB em 1963. O UADB compositado pode ainda incorporar códigos distintos para estações próximas, que não foram inspecionados nesta fatia.

A primeira data de Salvador no UADB é **1969**, anterior ao ano inicial **1970** anunciado no índice **IGRA2** (`MET-IGRA-20261112-01`), mas nenhum contém perfil de 1963 nas séries examinadas. Aracaju tem **1973** no UADB versus **1974** no IGRA2. Para Recife, o UADB verificado começa em **1972**, enquanto o IGRA contém observações de **8/11/1963** em `C149#1`/`C151#1`. Logo, **ausência no UADB não invalida o perfil instrumental anteriormente recuperado do IGRA**. Regras de composição, cobertura e seleção diferem.

**Unidades/altitude/tempo:** cabeçalhos UADB trazem coordenadas da estação, e linhas de nível contêm pressão, altura e componentes de vento conforme formato UADB, mas **não há linhas dos três alvos em novembro de 1963** para extrair pressão hPa, altura m, vento m/s ou erro instrumental. O campo horário de alguns cabeçalhos é não interpretável como HHMM regular (p.ex., `1165` em Salvador); este relatório afirma **datas de registros**, não horário efetivo de balões. Altitude de qualquer perfil de Conde em 1963: **desconhecida**; incerteza instrumental, temporal e espacial: **não quantificada**.

## 3. Nova fonte-filtro concreta, ainda sem leitura

O [GDEX d353000, NMC B3 ADP Global Upper Air (1962–1972)](https://gdex.ucar.edu/datasets/d353000/) publica no [grupo sinótico 2](https://gdex.ucar.edu/api/datasets/d353000/filelist/2/?filter_wfile=Y20175) o arquivo **[`Y20175`](https://osdf-director.osg-htc.org/ncar-gdex/d353000/Y20175)**, identificado no próprio inventário como `non-aircraft ua, 1963`, **117.264.384 bytes**. É uma nova rota documental direta para procurar a estação e o dia. **Não foi baixado nem inspecionado**, portanto não se sabe se inclui Salvador, Aracaju, Recife ou as datas de interesse. Cabe investigar formato, estação, época e qualidade com executor externo adequado, sem atribuir observações inexistentes.

## 4. Conexão com C17–C23, C144–C151, C193 e Castor

- **C17–C19**: Ap/Kp do GFZ e F10.7 do Canadá são medidas históricas de séries globais, **não** densidades da termosfera acima de Conde. **C20**: a regressão climática testada antes melhorou 2 de 4 cortes e piorou 2, portanto não há sinal sistemático validado. **C21**: último TLE 528 do espelho em 27/10, anterior aos distúrbios subsequentes. **C23**: CelesTrak republica fontes GFZ/Canadá, não é validação independente.
- **C144–C146**: cartas sinóticas originais da Marinha (pressão de superfície às 12 HMG de 8–9/11) não fornecem ventos por altitude ou reentrada. **C147, C149–C151**: a estação Recife de IGRA é arquivo instrumental válido para os perfis nominais das datas, mas `RELTIME=9999` não informa hora real; **C151** dá cinco níveis de vento observados em Recife em 8/11, não em Conde.
- **C193**: Explorer XVII fornece densidade/temperatura em abril–junho de 1963, **não no período do evento**; não transportar valores sem modelo e erro.
- **Encadeamento factual:** nova ocorrência de inventário `MET-GDEX-20261112-05` (API d394001 vazia), `MET-UADB-20261112-06/07/08` (três arquivos reais completos), `MET-NMC-20261112-09` (candidato anual 1963). As cinco arestas conduzem a `latent_wind_profile_Bahia_1963` e `density_drag_parameters_528` com **estado PENDING**. Isso muda a prioridade de aquisição dos arquivos, **não** o domínio físico do Castor.
- **Limite científico:** nenhuma medição de vento de Conde, erro de transferência Recife→Conde, perfil de densidade termoesférica local, coeficiente balístico do fragmento, nem trajetória recuperada. `physical_constraint_status=NOT_ACTIVATED` e não há geolocalização da queda.

## Reprodutibilidade

Os dados pequenos das sete respostas HTTP GDEX foram arquivados como **bytes exatos** em [snapshot](gdex_1963_api_snapshot_2026-11-12.json) e a integridade é testada offline em CI: `python3 -m unittest discover -s tests -p 'test_upper_air_coverage.py' -v` e `python3 tools/audit_upper_air_coverage.py`. Para repetir a auditoria de todos os 18.646 cabeçalhos, baixe os três arquivos UADB-Wind do quadro para uma pasta temporária e execute `python3 tools/audit_upper_air_coverage.py --data-dir /pasta/temporaria`. A leitura completa e hashes foram executados no Jatobá; **não foram incluídos arquivos binários grandes no Git**. Alterações futuras da API não reescrevem a fotografia de 12/11/2026; nova medição exige novo registro datado.

**Conclusão:** o arquivo agregado FAB segue candidato histórico, mas sua listagem pública não permite extrair as sondagens. A busca ganhou três negativas específicas de arquivo de estação, duas pequenas diferenças de ano inicial entre UADB e IGRA, e uma rota anual concreta de 1963 a investigar. Nada disso é observação de balão, esfera ou objeto orbital em Conde.

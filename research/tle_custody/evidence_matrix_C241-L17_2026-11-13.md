---
type: Guide
title: "C241-L17: NASA agosto de 1963 entre abril e outubro"
description: "Três tabelas NASA rastreáveis para 1963 3A/B/C, com períodos e altitudes publicados sem épocas de sensor."
---

# C241-L17: três publicações, não três épocas instrumentais

**Ocorrência C241-L17**, em continuidade à [C241-L16](evidence_matrix_C241-L16_2026-11-12.md), à [C241-L12](evidence_matrix_C241-L12_2026-11-12.md), à [C241-L10](evidence_matrix_C241-L10_2026-11-12.md) e à [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13). A ligação ao grafo cumulativo está **CONNECTED_PENDING_CALIBRATION**, sem nova redução física de domínio.

## Documento e custódia

[NASA Goddard, *Satellite Situation Report*, vol. 3, nº 16, 15/08/1963, NTRS 19630012289](https://ntrs.nasa.gov/citations/19630012289), [fac-símile PDF oficial](https://ntrs.nasa.gov/api/citations/19630012289/downloads/19630012289.pdf), capa com **X-533-63-1** e NASA-TM-X-50364 na indexação. O título registrado na API NTRS contém o erro literal *Saatellite Situation Report*, preservado no ledger como metadado, não reproduzido como título histórico corrigido.

Na tabela rotacionada **OBJECTS IN ORBIT**, PDF página **7**, índice zero **6**, página impressa **5**, as três linhas `1963 3A`, `1963 3B` e `1963 3C` foram **conferidas visualmente** em 13/11/2026. A declaração editorial **1200Z em 15/08/1963** é o instante de compilação do boletim, não a época orbital atribuível a cada linha.

Captura da URL oficial: **252.639 bytes**, SHA-256 `4e5cb0205577bc1b0959088db9ca3ae7a05f8de480b5ece9b86c385437636968`. Esse hash identifica **o PDF recuperado**, não checksum de linhas TLE. O CI refaz o download e exige o par de tamanho/hash; seus testes não inspecionam novamente pixels. Alteração da CDN deve causar falha e nova auditoria, não atualização silenciosa.

## Série documental comparada

Os extremos são [NASA vol. 3 nº 9, 30/04/1963](https://ntrs.nasa.gov/citations/19630012128) e [NASA vol. 3 nº 20, 15/10/1963](https://ntrs.nasa.gov/citations/19640000428), ambos com proveniência e conferência prévias em C241-L16/C241-L12. A associação das designações a NORAD 527/528/529 **depende da C241-L10**, pois os fac-símiles não imprimem os IDs NORAD nessas linhas.

| Objeto | Abr: período, apogeu/perigeu | Ago: período, apogeu/perigeu | Out: período, apogeu/perigeu |
|---|---|---|---|
| 1963 3A / 527 | 94,6 min; 537/460 km | **94,6 min; 537/458 km** | 94,6 min; 531/462 km |
| 1963 3B / 528 | 94,1 min; 505/435 km | **93,3 min; 455/412 km** | 92,4 min; 401/376 km |
| 1963 3C / 529 | 94,3 min; 531/437 km | **93,8 min; 493/422 km** | 93,3 min; 458/408 km |

Variações de período de **abril→agosto / agosto→outubro**, em minutos publicados: **3A 0,0/0,0; 3B −0,8/−0,9; 3C −0,5/−0,5**. Inclinações (graus) publicadas em agosto: 3A **81,88**, 3B **81,87**, 3C **81,89**. A consistência do sinal para 3B/3C aumenta a resolução da **cronologia editorial**, mas não demonstra decaimento orbital medido, taxa temporal, causa dinâmica ou independência das observações: publicações não fornecem épocas de ajustes individuais, estações, sensores, quadro, variâncias ou linhas TLE originais.

## Dependências e falsificabilidade

Grafo documental: NASA nº 9 → **nº 16 (nova ocorrência)** → nº 20 → nº 22, que registra o **dia catalogado 08/11/1963** para 3B (C241-L11). A edição nº 21, imediatamente anterior à nº 22, **permanece não recuperada**; a pesquisa textual na API NTRS por *satellite situation report* não fornece prova da existência ou inexistência de um scan específico.

O [ledger C241-L17](nasa_ssr_aug15_1963_C241-L17.json), o auditor `tools/tle_nasa_ssr_aug15_audit.py`, os testes adversariais e o workflow `tle-nasa-ssr-aug15.yml` verificam origem, bytes, transcrição e conexão aos extremos sem transformar datas editoriais em observáveis físicos. O relatório do workflow contém o vetor de três publicações e dois deltas, **não uma derivada por dia**.

**Negativos explícitos:** `original_tle_pair=null`, `physical_frame=null`, `measurement_sigma=null`, `observing_station=null`, `terminal_time=null`, `terminal_location=null`, identidade material 528 desconhecida. RAAN **198,5261°** continua de espelho secundário; **284,1520°** continua valor legado sem autenticação e inativo. Nenhuma restrição Lean física promovida; resultado para **Conde INDETERMINATE**.

Para reproduzir, execute `python3 -m unittest discover -s tests -p test_tle_nasa_ssr_aug15_audit.py -v` e o workflow dedicado, que compara os bytes atuais da NASA com o PIN histórico. Se o documento oficial mudar, preservar variantes com proveniência em vez de apagar o registro original.

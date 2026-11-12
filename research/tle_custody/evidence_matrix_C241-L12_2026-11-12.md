---
type: Guide
title: "C241-L12: NASA 15 outubro 1963, 3A/3B/3C em órbita, metadados divergentes"
description: "Fac-símile original NASA, três linhas catalográficas e controle entre índice NTRS, edição e dados orbitais não instrumentais."
---

# C241-L12: o catálogo de outubro não é um TLE de novembro

**Ocorrência C241-L12**, ligada à [matriz cumulativa](../evidence_matrix_C001-C238_2026-11-11.md), à [issue #13](https://github.com/franklinbaldo/conde-incident/issues/13) e ao [suplemento C241-L11](evidence_matrix_C241-L11_2026-11-12.md). Nova publicação documental anterior ao decaimento informado em novembro, **não** novo sensor nem linha 1/2 TLE original.

## Fonte primária documental

[NASA Satellite Situation Report 15/10/1963, vol. 3, nº 20, NTRS 19640000428](https://ntrs.nasa.gov/citations/19640000428); [PDF oficial](https://ntrs.nasa.gov/api/citations/19640000428/downloads/19640000428.pdf), **duas representações binárias retornadas pela mesma URL NASA em 12/11/2026**: recuperação inicial 282.624 bytes, SHA-256 **826f260524f6a7b83695e5c01d383025ff0da884656ebcc7fb98a1408c698ce3**; nova entrega/CI 286.417 bytes, SHA-256 **fe5183940081fbbfe1e791b8cf47c1ac2c08ecad0c17f5d54d7cac83fb5992b2**. Página do PDF **7 (índice zero 6)**, página impressa **5**, tabela *OBJECTS IN ORBIT*, visualmente reinspecionada no fac-símile rotacionado. Diferença de 3.793 bytes entre respostas oficiais: são **dois artefatos de download da mesma publicação**, não novas observações. O CI exige SHA-256/bytes em uma lista fechada, sem aceitar conteúdo arbitrário. A equivalência integral de páginas entre representações **não foi demonstrada**; a tabela da nova versão foi reinspecionada visualmente no fac-símile. Transcrição em [ledger JSON](nasa_ssr_1963_oct15_C241-L12.json):

| Designação | Período nodal impresso, min | Inclinação, graus | Apogeu, km | Perigeu, km |
|---|---:|---:|---:|---:|
| 1963 3A | 94.6 | 81.89 | 531 | 462 |
| 1963 3B | 92.4 | 81.87 | 401 | 376 |
| 1963 3C | 93.3 | 81.87 | 458 | 408 |

As três linhas indicam **16 JAN**, fonte **US**, na edição de 15/10. A designação moderna NORAD/COSPAR 527/528/529 depende da correspondência secundária já documentada em C241-L10. A tabela NASA identifica **3A/3B/3C**, não fornece números NORAD, RAAN, épocas TLE, covariâncias, sensores ou estado osculador.

**Divergência editorial real:** a capa do PDF traz **X-533-63-1**, enquanto o metadado NTRS apresenta **X-583-63-1**. Não corrigimos uma fonte pela outra nem presumimos qual índice é o erro. O fac-símile diz nº 20 em 15/10; a edição nº 22 é 15/11. **A edição nº 21 ainda não foi recuperada**, portanto 15/10 não pode ser declarada edição imediatamente anterior a 15/11.

## Relações rastreáveis, sem fabricar medições

A edição de **15/10/1963** lista **1963 3B** entre *objects in orbit*. A NASA publica em **15/11/1963**, nº 22, a adição do mesmo designador à lista de decaídos, com o **dia 08/11/1963**. O encadeamento documental é **C241-L12 → C241-L11**. Uma listagem editorial não estabelece observação orbital no dia da publicação, nem fornece tempo ou lugar da reentrada.

O recíproco **1440/92,4 = 15,5844... ciclos nodais por dia** é calculável aritmeticamente do período impresso, mas **não é um mean motion TLE original**: faltam definição de período, data de estimação, quadro, processo de arredondamento, modelo, instrumentos e incerteza. Não foi comparado como se tivesse a mesma semântica dos 15,74901460 rev/dia do espelho secundário de 27/10. Três linhas de uma mesma publicação **não são três conjuntos independentes de rastreamento**.

No grafo: fonte e página → (3A/3B/3C, valores impressos, edição) → sequência editorial com C241-L11 → **CONNECTED_PENDING_CALIBRATION**. Domínio físico reduzido **NOT_ESTABLISHED**; hipótese Lean não promovida, simulação não executada. RAAN **198,5261°** permanece apenas secundária; **284,1520°** continua material forense sem fonte e inativo. Sem instante nem posição terminal, **Conde INDETERMINATE**.

## Reproduzir

Executar testes: python3 -m unittest discover -s tests -p test_tle_nasa_ssr_oct15_audit.py -v. Baixar os bytes originais da URL do ledger e executar python3 tools/tle_nasa_ssr_oct15_audit.py --ledger research/tle_custody/nasa_ssr_1963_oct15_C241-L12.json --pdf /tmp/19640000428.pdf --output /tmp/c241-l12.json.

O auditor valida **ambos os pares exatos SHA-256/tamanho retornados pela mesma URL NASA**, a paginação declarada, invariantes das três linhas e limites epistemológicos; distingue artefatos de download sem confundi-los com novas medições. Uma terceira versão inesperada faz o CI falhar. A extração visual original foi humana, não verificada pixel a pixel por CI; o código **não realiza OCR**. Resultado negativo: edição nº 21, TLEs originais 527–529, checksums históricos, observações brutas, frame, sigma e ficha física de S00528 **não recuperados**.

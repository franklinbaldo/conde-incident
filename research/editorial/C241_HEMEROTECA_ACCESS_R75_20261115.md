---
type: Guide
title: "C241-R75: segunda e última passada do censo de acesso FBN"
description: "Capas e testes HEAD verificáveis do Correio da Manhã de 12–14/11/1963, limites dos catálogos bloqueados e buscas São Paulo/Salvador sem extrapolar edição."
---

# C241-R75 | Segunda e última passada do censo FBN

**Prioridade:** [#871](https://github.com/franklinbaldo/conde-incident/issues/871).
**Delegação:** [Elefante em lagarto#3, 15/11 ~14h UTC](https://github.com/franklinbaldo/lagarto/issues/3#issuecomment-6895477078).
**Censo primário:** [pré-registro](C241_HEMEROTECA_ACCESS_PREREG_20261115.md) e [CSV atualizado](C241_HEMEROTECA_ACCESS_CENSUS_20261115.csv).
**Executor:** Ifro, via Jatobá somente para SSH/inspeção com `max_memory_mb=128`; sem Cloud Build, IAM, trigger ou recursos novos.

## Resultado da passada

A tabela original tinha 42 pares título×data. Conservam-se os oito HEAD 200
da primeira passada; esta R75 acrescentou **três HEAD 200** do *Correio da
Manhã* com **datas efetivamente verificadas na capa**, e anotou a edição de
9/11 já autenticada independentemente pela Tartaruga na [PR #1060](https://github.com/franklinbaldo/conde-incident/pull/1060).
Resultado acumulado no CSV: **11/42 testes HEAD 200**, **uma edição em custódia
anterior sem reteste R75**, **30/42 células não testadas**. As 30 células não
testadas não são 403, 404, ausências de fascículo ou negativas jornalísticas.

| Dia da capa | Coleção | Edição | HTTP HEAD R75 | Content-Length | SHA-256 do PDF integral |
|---|---|---|---|---|---|
| 12/11/1963 (terça) | 089842 | 21659 | 200, 14:56:48Z | 20.179.037 | `a744f75a91462d2246ecf905353143ffe72a9c326ab0462a1241a4db3a2bc606` |
| 13/11/1963 (quarta) | 089842 | 21660 | 200, 14:56:52Z | 20.333.897 | `497cd71b643be03f908e26c2e99100fd24908fb026ca33c8e1667d49ee897bc0` |
| 14/11/1963 (quinta) | 089842 | 21661 | 200, 14:56:55Z | 21.320.531 | `d3b6301c192f8513c8a9a53a06d18eb47fc82b76fda45b6438bc1f416e8854e0` |

As três URLs seguem o padrão `https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_<edicao>.pdf`,
com os números **confirmados nas respectivas capas**, não atribuídos por
interpolação. Houve GET integral exclusivamente das três edições necessárias
para confirmar a capa, SHA-256 dos bytes baixados e renderização local da
primeira página; **nenhuma notícia foi lida ou classificada**. O `Content-Length`
foi aferido pelo HEAD do Ifro, com intervalo de ao menos três segundos entre
as requisições desta passada. A camada textual estava parcialmente corrompida;
a data foi conferida na imagem da capa.

A edição 21659 é de **12/11**, não 11/11. Portanto **11/11 continua sem
número de edição comprovado**; isso não demonstra que o jornal deixou de
circular nesse dia. Para 9/11, **21657** foi autenticada por capa pela
Tartaruga na [PR #1060](https://github.com/franklinbaldo/conde-incident/pull/1060):
22.546.215 bytes, SHA-256
`a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0`.
Essa edição **não foi baixada ou testada de novo pela R75**.

## Catálogos com acesso bloqueado, não PDFs datados

Consultas HTTP HEAD no **Ifro**, em 15/11/2026 UTC, sem login e sem
repetição após o bloqueio:

| Coleção | Endpoint de catálogo consultado | UTC | HTTP | Efeito |
|---|---|---|---|---|
| Jornal do Brasil, 030015 | [Docmulti](https://memoria.bn.gov.br/DocReader/docmulti.aspx?bib=030015) | 14:59:30Z | 403 | não permite mapear número×dia; os 25 slots prévios em 403 do CGEO-75 não foram reexecutados |
| Última Hora RJ, 386030 | [BNDigital](https://bndigital.bn.gov.br/acervo-digital/ultima/386030) | 14:59:37Z | 403 | nenhuma edição de novembro foi autenticada |
| Tribuna da Imprensa, 154083_02 | [DocReader](https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=154083_02) | 14:59:40Z | 403 | nenhuma edição de novembro foi autenticada |
| A Noite, 348970_06 | [DocReader](https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=348970_06) | 14:59:43Z | 403 | nenhuma edição de novembro foi autenticada |

**403 de catálogo NÃO equivale a 403 do PDF de uma data**. Não houve
identificador de edição confirmado para testar as 7 células desses títulos,
e não foram geradas URLs presumidas. O 403 depende do executor. Não se
tentou contornar Cloudflare, nem fazer login ou consultar acervos pagos.

## São Paulo e Salvador: última procura restrita por código elegível

Busca de descoberta em 15/11/2026, aproximadamente 14:53–14:58 UTC,
nos resultados públicos indexados de `bndigital.bn.gov.br/acervo-digital/`
e `memoria.bn.gov.br/docreader/`. Termos por título mais `1963`,
`hemeroteca`, cidade, `bib` ou `acervo-digital`:

| Cidade | Título | Resultado restrito |
|---|---|---|
| Salvador | A Tarde | `SEM_COLECAO_ELEGIVEL_CONFIRMADA` (8–14/11/1963) |
| Salvador | Jornal da Bahia | `SEM_COLECAO_ELEGIVEL_CONFIRMADA` (8–14/11/1963) |
| Salvador | Diário de Notícias | [artigo histórico da BNDigital](https://bndigital.bn.gov.br/artigos/diario-de-noticias-salvador-1875/) encontrado, **sem código de fascículo 1963 comprovado** |
| São Paulo | O Estado de S. Paulo | `SEM_COLECAO_ELEGIVEL_CONFIRMADA` para o diário em 1963 |
| São Paulo | Folha de S. Paulo | `SEM_COLECAO_ELEGIVEL_CONFIRMADA` para o diário em 1963 |
| São Paulo | Diário Popular | `SEM_COLECAO_ELEGIVEL_CONFIRMADA` para o diário em 1963 |

Nenhum status HTTP de fascículo foi produzido nesses seis títulos,
pois nenhum **código vinculado a uma edição do intervalo** foi confirmado.
O artigo da FBN sobre *Diário de Notícias* afirma sua integração aos
**Diários Associados em 1943**: em 1963 não era fonte editorial independente.
Os outros cinco resultados são lacunas deste localizador, **não prova de
inexistência do jornal, de coleção FBN, de digitalização ou de notícia**.

## Propriedade e independência em 1963: limite de proveniência

A matriz do projeto registra *Correio da Manhã*, *Última Hora*, *A Tarde*
e *Jornal da Bahia* como **títulos de imprensa a confrontar fora dos
Diários Associados**; a [R72 da Tartaruga](c241_tartaruga_r72_correio_manha_1963_11_10.md)
documenta o *Correio* como **outro título** e deixa a origem autônoma da
matéria `UNDETERMINED`. Nenhum desses documentos identifica aqui,
por instrumento societário, o **titular legal em 1963**:
`PROPRIEDADE_NAO_VERIFICADA` para Correio, Última Hora (RJ/PE),
Tribuna, A Noite e Jornal do Brasil. Para *Diário de Notícias*
(Salvador), `DIARIOS_ASSOCIADOS_1943_PLUS` segundo a FBN.
Não inferir independência do relato a partir do nome do jornal.

## Parada e limites

Esta é **a última passada atribuída ao Lagarto**. Os 30 pares não testados
permanecem lacunas, porque não houve vínculo edição×data ou acesso ao
catálogo; a busca se encerra sem fabricar números por interpolação.
Não se atribui `LIDO_SEM_MENCAO`, hora, testemunha, órbita ou impacto ao
corpus. Os registros PDF já obtidos podem ser usados **somente por leitor
designado**, respeitando os escopos da [#871](https://github.com/franklinbaldo/conde-incident/issues/871).
A missão SSG/índices da [lagarto#3](https://github.com/franklinbaldo/lagarto/issues/3)
continua pausada.

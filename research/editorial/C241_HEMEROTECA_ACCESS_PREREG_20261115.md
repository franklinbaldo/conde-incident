---
type: Guide
title: "C241: pré-registro fechado do censo de acesso FBN, 8–14/11/1963"
description: "Universo e regras congelados antes de testar os PDFs da Hemeroteca; apoio documental à prioridade #871, sem leitura de notícias."
---

# C241: pré-registro do censo de acesso à Hemeroteca (15/11/2026)

**Escopo previamente congelado.** Uma passada por título × data de **08 a 14/11/1963** para descobrir se os arquivos de jornais diários digitalizados pela FBN são acessíveis sem login no endpoint `https://hemeroteca-pdf.bn.gov.br`. Este é um teste de acesso **não** de conteúdo, presença de notícia ou independência editorial. Delegação: [lagarto#3, Elefante](https://github.com/franklinbaldo/lagarto/issues/3#issuecomment-6894006751); prioridade [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871).

## Universo fixo de coleções com códigos rastreáveis

| ID | Título, cidade | Código FBN | Fonte do código | Papel |
|---|---|---|---|---|
| CM-RJ | Correio da Manhã (RJ) | `089842` | https://bndigital.bn.gov.br/acervo-digital/correio-manha/089842 | controle, PDF já baixado em 08 e 10/11 |
| JB-RJ | Jornal do Brasil (RJ) | `030015` | https://memoria.bn.br/DocReader/docmulti.aspx?bib=030015 | controle, 403 anterior dependente do executor |
| UH-PE | Última Hora Nordeste (Recife) | `765147` | https://bndigital.bn.gov.br/acervo-digital/ultima-hora/765147 | controle, PDFs 00472–00475 já custodiados |
| UH-RJ | Última Hora (RJ) | `386030` | https://bndigital.bn.gov.br/acervo-digital/ultima/386030 | descoberta; edição distinta da Nordeste |
| TI-RJ | Tribuna da Imprensa (RJ), 1960–1969 | `154083_02` | https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=154083_02 | descoberta |
| AN-RJ | A Noite (RJ), 1960–1964 | `348970_06` | https://memoria.bn.gov.br/docreader/DocReader.aspx?bib=348970_06 | descoberta |

**Estratos sem coleção elegível codificada identificada antes do congelamento:** São Paulo e Salvador. Não tratar isso como ausência de jornais ou de digitalização; é lacuna do localizador desta passada, a reportar explicitamente como `SEM_CODIGO_VERIFICADO`. *A Tarde* e *Jornal da Bahia* permanecem com o dono ([#884, item 2](https://github.com/franklinbaldo/conde-incident/issues/884)). *Diário de Pernambuco* (`029033`) é dos Diários Associados e está excluído por projeto. *Correio Paulistano* (SP, `090972`) foi extinto em 1963; o catálogo FBN explicitamente disponível consultado não confirmou fascículos de 8–14/11, portanto fica **fora do conjunto testado**, sem afirmar data exata de encerramento. Não inferir que a ausência de código é falha HTTP.

## Protocolo congelado antes do teste

1. A lista acima é fechada. Para cada uma das seis coleções, considerar cada uma das sete datas do intervalo, inclusive fins de semana; `SEM_EDICAO_VERIFICADA` quando não houver identificador documental confirmado, sem inventar números por interpolação.
2. Identificar a edição por catálogo FBN ou custódia já autenticada **antes** de gerar URL `https://hemeroteca-pdf.bn.gov.br/<codigo>/per<codigo>_1963_<edicao>.pdf`. Documentar como a data foi atribuída ao número; quando houver subcoleção, não apagar o sufixo `_02`/`_06` arbitrariamente. `HTTP_NOT_TESTED` para URL não mapeável, não 404 fictício.
3. Uma requisição `HEAD` por URL inequivocamente identificada; `GET` com Range curto somente se HEAD for inconclusivo. Respeitar alguns segundos de intervalo. Para 403, no máximo uma repetição a partir de segundo executor disponível, sem contornar bloqueio, login ou captcha.
4. Guardar: título, data de interesse, edição, URL, HTTP, `Content-Length` informado (ou `null`), executor, horário UTC, método e observação. Para cada título com 200, confirmar data de capa de **uma** edição com download integral, somente quando necessário e autorizado pela ausência de custódia anterior; preservar tamanho e SHA-256. `CAPA_NAO_CONFERIDA` não é `CAPA_FALSA`.
5. Não interpretar conteúdo das páginas; não procurar menções a Conde; não multiplicar acessos após a parada. Resultado sem novas URLs também é válido. Não criar inferência de hora, órbita, reentrada ou testemunho.

**Limite científico:** acesso HTTP e data de capa não provam cobertura jornalística, independência de relato nem hora do evento. A fonte FBN pode ser servida diferentemente por executor, especialmente se houver Cloudflare.

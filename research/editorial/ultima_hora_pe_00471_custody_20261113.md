---
type: Evidence
title: "Última Hora PE 00471, 8/11/1963: índice e tentativas negativas"
description: "Documento não lido; edição localizada no índice BN, PDF 403 e CDX exato sem captura 200."
---

# UH Pernambuco 00471: localizar antes de interpretar

**Objeto:** edição 00471 de *Última Hora* (PE), 8 de novembro de 1963, página impressa 8. [A Hemeroteca Digital BN lista a edição 00471 na coleção de 1963](https://memoria.bn.gov.br/DocReader/765147/5339). Isso demonstra a presença do **rótulo da edição no catálogo**, não que a página 8 tenha sido lida.

**Consulta técnica de 13/11/2026:** a URL exata `https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf` respondeu **HTTP 403** a HEAD no Jatobá. A consulta CDX exata `https://web.archive.org/cdx/search/cdx?url=hemeroteca-pdf.bn.gov.br%2F765147%2Fper765147_1963_00471.pdf&output=json&filter=statuscode%3A200&collapse=digest` devolveu `[]`. A segunda resposta é um negativo **somente para aquela URL e aquele filtro CDX**. Não exclui outros caminhos ou capturas.

A leitura semântica prévia do blog antigo atribui a notícia sobre estátuas escondidas num buraco de quatro metros à página 8, mas **não houve confronto com o fac-símile nesta rodada**. Portanto, nenhum trecho da notícia, ligação com o relato TV Tupi/FBIS, coincidência causal ou geometria física está confirmado. Bytes, hash e paginação do próprio arquivo seguem nulos. Ver [pedido da Lontra #6](https://github.com/franklinbaldo/lontra/issues/6) e [auditoria Conde #494](https://github.com/franklinbaldo/conde-incident/issues/494).

**Correção de navegação, 13/11/2026:** a URL anteriormente citada com página física `5756` selecionava **Edição 00507**, embora o menu lateral também listasse a 00471. Consultas HTTP 200 ao DocReader confirmam que os IDs físicos **5339–5346** selecionam especificamente *Edição 00471*, enquanto **5338** seleciona 00470 e **5347** seleciona 00472. [Primeira posição da edição](https://memoria.bn.gov.br/DocReader/765147/5339); [oitava posição candidata](https://memoria.bn.gov.br/DocReader/765147/5346). O número de posição no DocReader **não é uma paginação impressa verificada** e o retorno foi HTML do seletor, **não imagem da página**. Corrigir o link não equivale a ler a matéria. O erro de localização anterior é preservado para rastreabilidade.

O manifesto e os testes preservam a diferença entre **indexação**, **arquivo recuperado**, **página inspecionada** e **hipótese narrativa**. Próximo passo: obter a página original com URL e SHA-256, cotejar edição e data impressas, extrair o texto em contexto e só então comparar relatos.

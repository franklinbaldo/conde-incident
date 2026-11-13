---
type: Guide
title: 'CGEO-31: resposta AJAX do leitor SGB sem fotograma'
description: 'Painel real, custódia do delta HTTP e ausência de imagem autenticada'
---

# CGEO-31: requisição assíncrona de imagem também não entregou bytes

Em **13 de novembro de 2026**, após selecionar o nó `s679` da árvore FotoUSAF do [SGB](https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF) na **mesma sessão HTTP**, foi enviada uma requisição assíncrona ASP.NET AJAX ao controle `CarregaImagemHiddenButton`, incluindo `ScriptManager1=DocumentoUpdatePanel|CarregaImagemHiddenButton` e cabeçalho `X-MicrosoftAjax: Delta=true`.

A resposta oficial teve HTTP 200, `text/plain`, **9.024 bytes** e SHA256 `3e4d49a20fbcffef0ca57aa05bdbe23620dcfa0bb5a238a16899e9bc83938644`. Não foi um JPEG, PNG nem PDF. O conteúdo foi uma resposta AJAX delimitada por comprimento, contendo o `DocumentoUpdatePanel` com **2.752 bytes**. O [fragmento real de HTML](evidence/cgeo31_ajax_document_panel.html) tem SHA256 `23c72cf7fb3cbdb7e4c715434e0ecfd3d1d32c45deb2e82b9555443bf247f8fb` e inclui exatamente uma tag `DocumentoImg` **sem `src`**. O fragmento é derivado da mesma resposta, não outra testemunha independente.

Verificação offline: `python3 tools/cgeo31_usaf_ajax.py`; para replay de toda resposta original mantida fora do Git, `python3 tools/cgeo31_usaf_ajax.py --original-ajax caminho`. A segunda modalidade compara tamanho, SHA256 e os bytes do painel no delta AJAX, impedindo que um HTML fabricado passe por fonte oficial. Testes adversariais rejeitam contagem alterada, URL de imagem fictícia, geometria ou restrições orbitais promovidas.

**Conclusão restrita:** neste POST assíncrono também não foi entregue uma URL de imagem, mas isso **não prova ausência do fotoíndice no acervo**. Ainda cabe investigar um navegador real e possíveis handlers de mídia. O rótulo USAF 63-32 e `/1` não identificam data de captura nem pegada de voo. A referência PETROBRAS 53 D/1961 continua separada. Sem fotograma autenticado e ponte temporal, o centro de Conde em 1963 e o local alegado da queda seguem nulos. A investigação continua na [issue #558](https://github.com/franklinbaldo/conde-incident/issues/558).

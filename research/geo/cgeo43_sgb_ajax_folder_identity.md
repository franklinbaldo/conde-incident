---
type: Guide
title: 'CGEO-43: armadilha de identidade no AJAX do fotoíndice USAF'
description: 'O SGB seleciona a pasta 1850 via GET, mas o callback AJAX retorna imagem da pasta 0335; veto à falsa atribuição'
---

# CGEO-43: a imagem não pertence à pasta selecionada

Em **14/11/2026 (UTC)**, consultei o leitor público do [Serviço Geológico do Brasil](https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF&pasta=1850). O parâmetro **`pasta=1850`** fez o HTML inicial selecionar inequivocamente o nó de valor **680** e rótulo **1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI**. Isso fornece uma rota HTTP direta para selecionar a pasta, sem os postbacks Telerik de CGEO-30.

O passo seguinte é uma armadilha técnica: no *mesmo* `requests.Session`, enviei o callback `CarregaImagemHiddenButton` com `ScriptManager1=DocumentoUpdatePanel|CarregaImagemHiddenButton` e AJAX `X-MicrosoftAjax: Delta=true`. O retorno HTTP 200 carregou um `img src` real, mas também trouxe **`PastaTxt: 0335 Projeto USAF 63-32 - área A: SA.22-X-B-V` e `_selectedValue: 1`**. A seleção havia voltado para a primeira pasta. Repeti com `GET ...&pasta=1851` (nó 681) e observei **o mesmo fallback**. Em ambos os casos, os JPEGs renderizados eram binariamente iguais: **558.245 bytes, 3.767 × 3.928 pixels, SHA256 `21acae03404dae880b40c69565c841bf7a3cdf1dc392c11bfe1cbe83828a4bd0`**. Os URLs incluem IDs de cache diferentes; logo comparar apenas URL seria insuficiente. Trata-se de **derivada JPEG do documento da pasta 0335**, não imagem autenticada do fotoíndice MI-1850.

A inspeção visual do JPEG indevidamente recuperado lê **`AREA 11`, `ACGS`, `Date 1967-1969`** e notas **`Não voada pela USAF`**. **Esses dizeres não pertencem ao fotoíndice de Conde**. Rejeita-se tanto atribuir a data 1967–1969 à pasta 1850 quanto concluir que a região de Conde não foi fotografada. O código de projeto `63-32` continua sem data individual de tomada autenticada.

A matriz em [JSON](cgeo43_sgb_ajax_folder_identity.json) fixa SHA256 e tamanho das quatro respostas HTTP originais, cujos bytes integrais permaneceram fora do Git. Os quatro excertos preservados, derivados diretamente das respostas, possuem seus próprios hashes e são verificados por `python3 tools/cgeo43_sgb_ajax_identity.py`. A verificação offline autentica os excertos, **não afirma ter baixado de novo os JPEGs ou os HTMLs integrais**. Doze testes adversariais bloqueiam troca de pasta, alteração de hashes, falsificação de data, geometria e inferência orbital.

**Requisito para futura aquisição:** a resposta que expõe o `DocumentoImg src` deve confirmar **simultaneamente** `PastaTxt=1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI` e `_selectedValue=680` antes de se creditar qualquer JPEG. Idealmente inspecionar a rede de um navegador real em executor capaz de conservar integralmente o estado Telerik durante o callback. Depois, custódia dos bytes e inspeção de datas, faixas e footprints.

Os dados não autenticam foto da folha MI-1850, posição do centro urbano de Conde em novembro de 1963, local de queda, nem nova restrição orbital. Esta é uma **descoberta de integridade de evidência**, continuando [CGEO-29/30/31](cgeo31_usaf_ajax_delta.md) e a [issue #558](https://github.com/franklinbaldo/conde-incident/issues/558).

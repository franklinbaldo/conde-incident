---
type: Story
title: "A página que apontava para outro jornal"
description: "Caderno 17: a pista dos quatro metros no Última Hora de 8/11/1963 teve o endereço digital corrigido, mas a fotografia da página ainda não foi recuperada."
date: "2026-11-13"
summary: "A investigação encontrou a edição procurada no índice da Biblioteca Nacional, mas descobriu que o link anterior abria outra edição. O jornal ainda precisa ser visto."
chapter: "17"
author: "Coruja · Caderno de investigação"
status: "Edição 00471 identificada no seletor do DocReader; fac-símile da página 8 não recuperado; coincidência textual pendente de confirmação"
---

# A página que apontava para outro jornal

O capítulo anterior terminou com uma coincidência de quatro metros. Uma rádio do Rio falou de uma esfera que teria feito um buraco no centro de Conde, na Bahia. Uma pesquisa anterior, sobre um jornal do Recife, mencionava outro buraco da mesma profundidade, cavado para esconder estátuas roubadas. Para investigar se essas duas frases tinham alguma relação, faltava uma operação aparentemente banal: **abrir a página do jornal**.

O endereço que usávamos, porém, conduzia a **outra edição**.

## Um número no lugar de outro

O jornal procurado era o *Última Hora* de Pernambuco, **edição 00471, de 8 de novembro de 1963**. A notícia sobre as estátuas havia sido localizada na **página 8**, segundo uma [leitura semântica anterior](https://github.com/franklinbaldo/franklinbaldo.github.io/blob/main/docs/research/conde-ufo-semantic-reading-1963.md). Nesta investigação, a reprodução visual da folha não tinha sido recuperada.

A [primeira auditoria da Lontra, PR #497](https://github.com/franklinbaldo/conde-incident/pull/497), tentou o [PDF da edição 00471](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00471.pdf#page=8). Em 13 de novembro de 2026, o pedido técnico HEAD respondeu **HTTP 403**. A busca CDX por capturas com resposta 200 daquele endereço exato não retornou registros. Nenhum desses dois negativos demonstra que a página esteja perdida, ou que outros endereços e arquivos não tenham uma cópia.

Havia também um link para o leitor digital da Biblioteca Nacional: `/DocReader/765147/5756`. A interface desse endereço mostrava, na lista lateral, a edição 00471. Era fácil concluir que a edição tinha sido aberta.

Mas a lista lateral é apenas um menu. O **seletor da edição corrente** naquele endereço indicava **00507**, não 00471. A confusão veio à tona na [correção documental #510](https://github.com/franklinbaldo/conde-incident/pull/510). É a diferença entre ver o título de um livro numa estante e estar com esse livro nas mãos.

## Oito posições, nenhuma página lida

Os registros da auditoria corrigida mostram que os identificadores físicos **5339 a 5346** do [DocReader](https://memoria.bn.gov.br/DocReader/765147/5339) selecionam a edição 00471. A posição imediatamente anterior, 5338, seleciona 00470; a seguinte, 5347, seleciona 00472. O identificador **5346** é, assim, um [candidato à oitava posição digital](https://memoria.bn.gov.br/DocReader/765147/5346).

Isso **não** prova que o número impresso no papel seja 8. E a correção do endereço produziu apenas **HTML de navegação**, não a imagem escaneada da folha. A transcrição da notícia sobre estátuas, suas palavras e a profundidade do buraco seguem sem uma nova conferência visual.

O [manifesto de custódia DOC-UH-PE-1963-00471-LOCATOR](https://github.com/franklinbaldo/conde-incident/blob/main/research/archive/ultima_hora_pe_00471_1963_locator_20261113.json) preserva o erro anterior, o seletor correto, a tentativa de PDF e as ausências de hash e imagem. Os [testes de regressão da PR #510](https://github.com/franklinbaldo/conde-incident/blob/main/tests/test_ultima_hora_pe_00471_locator.py) rejeitam um atalho particularmente traiçoeiro: encontrar “00471” no menu lateral e declarar que a edição selecionada é 00471.

Há uma ironia burocrática. Em [23 de outubro de 2026, a Fundação Biblioteca Nacional anunciou a retomada do acesso à Hemeroteca Digital](https://www.gov.br/bn/pt-br/central-de-conteudos/noticias/aos-usuarios-da-hemeroteca-digital-brasileira-3), advertindo que a recomposição integral do acervo seria gradual. O funcionamento geral do portal, portanto, não garante que uma URL específica entregue a página procurada.

## O que a correção muda na história de Conde?

A fonte sobre a esfera é diferente: o [documento do FBIS com a transmissão atribuída à Rádio Tupi, em 8/11/1963](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) registra **o relato de quatro metros**, não uma medição independente do suposto buraco.

A frase do Recife, por outro lado, ainda depende da leitura anterior do jornal. A [ponte documental proposta pela Abelha, incorporada à PR #501](https://github.com/franklinbaldo/conde-incident/pull/501), mantém essa relação como **candidata textual não ativada**: sem página autenticada, sem roteiro ou gravação da rádio e sem cronologia de circulação, não há como estabelecer cópia entre redações, fonte comum ou fabricação. Nenhuma das possibilidades altera os parâmetros de órbita do NORAD 528.

O endereço correto é um avanço pequeno, mas real. Ele remove um erro de navegação que poderia contaminar o trabalho seguinte. **Não transforma uma edição indexada em uma notícia lida, nem dois números iguais em duas testemunhas de um mesmo acontecimento.**

O próximo teste é objetivo: recuperar os bytes da folha candidata 5346 ou do PDF original; guardar URL, tamanho e SHA-256; verificar visualmente data, edição e número de página; transcrever o trecho completo com seu contexto. Só depois confrontá-lo com o texto do FBIS e procurar uma cadeia de transmissão datada.

A investigação encontrou a porta certa. Ainda falta abrir o jornal.

## O que mudou

Desde o [Caderno 16](https://franklinbaldo.github.io/conde-incident/stories/2026-11-13-dois-buracos-de-quatro-metros/), foram verificados os limites do índice digital e corrigida a edição efetivamente selecionada no DocReader. **Não foi obtido novo testemunho sobre uma esfera, uma cratera ou uma reentrada em Conde.**

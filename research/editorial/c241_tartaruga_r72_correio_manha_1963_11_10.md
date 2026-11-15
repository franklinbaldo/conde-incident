---
type: Source
title: "C241-R72: Correio da Manhã, 10/11/1963, p. 8, negação noticiada em Conde"
description: "Leitura visual do original FBN e distinção entre desmentido divulgado, hora do evento e testemunho independente."
source_id: C241-TARTARUGA-R72-CM-19631110
locator: "Correio da Manhã (Rio de Janeiro), 10 de novembro de 1963, página impressa 8, página PDF 8, FBN 089842/21658"
provenance: "Fac-símile original FBN baixado, SHA-256 verificado e página 8 renderizada visualmente no executor Ifro"
verification_status: ORIGINAL_PAGE_VISUALLY_READ
---

# C241-R72 | *Correio da Manhã* de 10 de novembro, p. 8

**Escopo:** [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871), prioridade 1 da direção. Fonte contemporânea de **imprensa de outro título**, não uma época orbital, nem uma observação independente do evento. [Manifesto reprodutível](../archive/conde_correio_manha_1963_11_10_C241_TARTARUGA_R72.json).

## Documento original e custódia

- **Coleção:** Hemeroteca Digital da Fundação Biblioteca Nacional, `089842`, edição `21658`.
- **Documento:** [*Correio da Manhã*, domingo, 10/11/1963, PDF integral](https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21658.pdf#page=8).
- **Artefato integral observado no Ifro:** 62.742.698 bytes; 97 páginas PDF.
- **SHA-256 do PDF integral:** `75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3`.
- **Página:** impressa **8** = página **8 do PDF**. Cabeçalho da página foi visualmente conferido; o recorte foi renderizado por `pdftoppm` a 140 DPI.
- **Matéria:** `PRECIPITAÇÃO DE OBJETOS CONTINUA`, colunas superiores esquerdas da página 8, sem crédito nominal de repórter legível na matéria.

## O que a matéria realmente documenta

O texto noticia que o Serviço de Buscas e Salvamento da FAB e o governo baiano **desmentem a suposta queda em Conde**, município próximo a Salvador. Sob o intertítulo **FANTASIA**, atribui ao Observatório Nacional uma avaliação cética sobre o objeto baiano. A matéria oferece uma declaração nominal do professor **Mário Ferreira**, ex-integrante do Observatório do Valongo, **sobre fenômenos e materiais de modo geral**, não um testemunho presencial da ocorrência de Conde.

**Não há hora local de queda** no artigo lido, nem testemunha presencial identificada para Conde. A matéria também menciona acontecimentos alegados em Iguape/SP e nas proximidades da Califórnia: **não os fundir** com a ocorrência baiana. A data da edição (10/11) é **data de publicação**, não instante de reentrada ou queda. É possível que as negativas reproduzam comunicações oficiais ou outras notícias; **seus textos originários não foram obtidos** aqui.

A leitura é **`LIDO_SEM_HORA` restrita à matéria da página 8**, não certificação de todas as 97 páginas da edição. A camada de texto do PDF apresentou caracteres corrompidos; a afirmação central foi conferida na imagem renderizada, sem depender do OCR/PDF text layer. O negativo nas demais páginas **não foi certificado**.

## Independência e efeito científico

- **Outro veículo de imprensa:** sim; o fac-símile é de *Correio da Manhã*, não da edição do *Diário de Notícias* de Salvador, que pertenceu aos Diários Associados.
- **Origem autônoma da notícia e dos desmentidos:** `UNDETERMINED`. Não presumir apuração independente apenas porque o veículo é diferente.
- **Fonte primária do desmentido FAB/BA:** `NOT_RECOVERED`. Aqui temos a **atribuição jornalística** de um desmentido.
- **Testemunha ocular de Conde / instante do suposto evento:** `null`.
- **Nova restrição para NORAD 528/637:** **não**. O texto não informa hora, rastreio, sensor, trajetória, identidade de objeto nem prova física.

**Interpretação:** esta fonte contemporânea é um novo contraponto jornalístico para a genealogia das narrativas de Conde e para a hipótese nula (#887). Seu conteúdo **não demonstra a inexistência** do acontecimento, tampouco valida uma queda de satélite. Ao contrário dos documentos Blue Book analisados em [R71](conde_local_hour_bluebook_2026_11_C241_TARTARUGA_R71.md), esta é uma página jornalística original identificada; porém sua dependência informacional continua em aberto.

## Reprodução e limites

1. Baixar o PDF original acima, conferir **bytes e hash**.
2. Renderizar somente a página 8 e conferir visualmente cabeçalho, título, duas colunas e o trecho sobre Conde.
3. Executar `python3 -m unittest tests.test_correio_manha_tartaruga_r72` e `python3 -m tools.audit_correio_manha_tartaruga_r72 --pdf <caminho>`.
4. Não promover a avaliação do Observatório Nacional nem o desmentido noticiado a sensor, horário, testemunha ou probabilidade.

A prioridade operacional segue na [#871](https://github.com/franklinbaldo/conde-incident/issues/871): procurar **hora local literal**, crédito e fonte efetivamente independente; avisar [Castor #870](https://github.com/franklinbaldo/conde-incident/issues/870) **somente se houver hora útil**.

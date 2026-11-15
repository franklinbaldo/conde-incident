---
type: Source
title: "C241-R76: duas páginas integralmente lidas do Correio da Manhã de 9/11/1963"
description: "Amplia leitura de artigo isolado para páginas PDF 5 e 21 completas, com conclusão restrita àquelas páginas."
source_id: C241-TARTARUGA-R76-CM-19631109
locator: "Correio da Manhã, edição 21.657 de 9/11/1963, coleção FBN 089842, páginas PDF 5 e 21 (impressas 5 do 1.º caderno e 9 do 2.º)"
provenance: "PDF FBN original custodiado na R74, SHA-256 rechecado no Ifro; páginas visualizadas em quadrantes sobrepostos em resolução ampliada"
verification_status: TWO_ORIGINAL_PAGES_FULLY_VISUALLY_EXAMINED_EDITION_INCOMPLETE
---

# C241-R76 | Duas páginas completas do *Correio da Manhã* (9/11/1963)

**Encomenda:** [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871), com [delegação do Elefante à Tartaruga](https://github.com/franklinbaldo/tartaruga/issues/9#issuecomment-6894707313). **Entrega incremental:** leitura visual *integral das colunas, notas e anúncios* nas páginas PDF **5 e 21**, não das 28 páginas do fascículo. Registro [estruturado](../archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R76.json).

## Custódia e método

Fac-símile original [FBN 089842/21657](https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21657.pdf), autenticação de edição já documentada em [R74](c241_tartaruga_r74_correio_manha_1963_11_09.md). PDF **22.546.215 bytes**, **28 páginas**, SHA-256 `a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0`, reconferido no executor Ifro em 15/11/2026. Não houve novo download do PDF. Uma vista panorâmica de todas as 28 páginas auxiliou a seleção, mas **não** constitui leitura integral.

As duas páginas escolhidas foram examinadas em imagens ampliadas, divididas em **quatro quadrantes sobrepostos**, incluindo suas margens, títulos, colunas e anúncios. A imagem de p. 5 já existia na custódia R74 em resolução de 3.100 px de altura; a p. 21 foi renderizada do mesmo original com `pdftoppm -f 21 -l 21 -scale-to 3100`. A camada textual desse fascículo apresenta falhas concretas de extração (por exemplo, `IGUAPE` visível no original e omitido em `pdftotext -layout`), de modo que não se usa busca lexical negativa como prova de ausência.

## Páginas efetivamente examinadas

| Página PDF | Página impressa | Resultado restrito à página |
|---|---|---|
| **5** | **5, 1.º caderno** | **EXAMINADA**. Leitura completa das colunas, incluindo a notícia **OBJETO MISTERIOSO CAI EM RIO DE SP** já identificada em R74. Seu crédito é *Iguape (do enviado especial da sucursal SP)* e o local relatado é Rio Peropava, **Iguape/SP**, com testemunhas atribuídas **àquela ocorrência**, não a Conde. Também foi lida a matéria **SENSÍVEL VARIAÇÃO MAGNÉTICA NO PAÍS**, sobre estudos geomagnéticos gerais, sem menção identificada a uma hora da ocorrência em Conde. As demais colunas abordam administração, educação, ex-combatentes, comércio e anúncios. |
| **21** | **9, 2.º caderno** | **EXAMINADA**. As colunas **Notas Médicas**, **Correio Militar**, **Aviação e Astronáutica**, **Ensino** e anúncios foram examinados. Na seção **Aviação e Astronáutica**, o tópico *Novo Comandante* trata da Base Aérea do Galeão e de pessoal militar; não fornece observação ou hora de queda em Conde. |

Em **nenhuma dessas duas páginas** foi localizada hora literal atribuída ao suposto evento de Conde, testemunha presencial identificada em Conde ou medição que identifique o NORAD 528/637. **Isto não é negativo da edição.** A existência de notícia sobre objeto em Iguape não permite transferir horário, nomes, local ou mecanismo causal para o relato baiano. A matéria sobre geomagnetismo tampouco autoriza inferir causa atmosférica/orbital do relato.

## Estado da leitura e parada

**2/28 páginas completas** nesta edição (PDF 5 e 21); **26/28 continuam pendentes** de leitura integral coluna por coluna. A **capa** da página PDF 1 foi examinada antes apenas para autenticar data/número, não como página integral. Outras páginas já vistas em panorama ou em recortes não recebem `EXAMINADA`. No jornal de **10/11/1963**, edição 21658, **97 páginas**, apenas a **matéria** da p. 8 tem leitura atribuída pela [R72](c241_tartaruga_r72_correio_manha_1963_11_10.md), não a página/edição inteira.

**Conclusão:** `NO_NEW_CONDE_EVENT_HOUR_IN_TWO_FULLY_READ_PAGES`. Independência da **origem da matéria** em relação à Tupi/FBIS segue `UNDETERMINED`, embora se trate de outro título. Não foi ativada exclusão orbital, hora derivada nem atribuição de identidade física.

**Próxima fatia legítima:** continuar as 26 páginas de 9/11 e, em seguida, as 97 de 10/11, preservando o método de artigos, créditos, eventual horário literal e legibilidade. **Parada só quando ambas as edições estiverem integralmente lidas**, como pedido pelo Elefante. Não expandir 11–14/11 por inferência do catálogo.

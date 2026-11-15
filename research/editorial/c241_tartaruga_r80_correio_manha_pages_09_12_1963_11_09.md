---
type: Source
title: "C241-R80: Correio da Manhã de 9/11/1963, PDF 9–12"
description: "Leitura visual integral do fim do primeiro caderno; horários de TV, bolsa e bancos não são hora do evento de Conde."
source_id: C241-TARTARUGA-R80-CM-19631109
locator: "Correio da Manhã, Rio de Janeiro, 9/11/1963, nº 21.657, FBN 089842, páginas PDF 9–12 e limite de caderno na PDF 13"
provenance: "Original FBN 22.546.215 bytes, SHA-256 reconfirmado no Ifro; páginas 9–12 renderizadas a 150 dpi com quatro recortes sobrepostos por página; texto extraído auxiliar"
verification_status: FIRST_CADERNO_VISUALLY_COMPLETE_EDITION_INCOMPLETE
---

# C241-R80 | *Correio da Manhã*, 9 de novembro de 1963

Prioridade [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871), lote redefinido pelo Elefante em [Tartaruga #9](https://github.com/franklinbaldo/tartaruga/issues/9#issuecomment-6899629904). A unidade é **artigo e página efetivamente examinada**, não uma palavra ausente no OCR nem um fascículo inteiro presumido negativo.

## Custódia e delimitação

[PDF original FBN 089842/21657](https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21657.pdf), 9/11/1963, nº 21.657, 28 páginas PDF, 22.546.215 bytes, SHA-256 `a5aa619730df13e2a630c7d16fcfde95f58180ec3a05063038177b03fd46f7d0`. Arquivo já custodiado e hash recalculado em 15/11/2026 no Ifro; nenhum rebaixamento, substituição ou alteração do original.

As páginas **PDF 9–12** foram renderizadas a 150 dpi e vistas por inteiro, seguidas de **quatro quadrantes ampliados e sobrepostos por página**, incluindo títulos, colunas, legendas, fotografias e anúncios. A camada `pdftotext` contém caracteres corrompidos e não decide resultados negativos. Páginas PDF 9–11 trazem fólio impresso 9–11 e identificação do **1º caderno**. A página PDF **12 não exibe fólio numérico**: traz o cabeçalho completo de edição e termina a seção, como mostra a abertura inequívoca de **“2.º Caderno” na PDF 13**. Não foi inventado fólio impresso 12. A PDF 13 foi vista **somente para identificar a fronteira**, não certificada como leitura integral.

## Leitura visual por artigo e página

| PDF / fólio | Estado | Conteúdo e falsa associação evitada |
|---|---|---|
| **9 / 9** | **EXAMINADA** | Anúncio de programação da **TV-Tupi, canal 6** (12h05–22h30), escolas, SURSAN, eleição municipal gaúcha, fiscalização aduaneira, amostras marinhas do Museu Nacional, acidentes ferroviários e Petrobras. Horas da grade televisiva não são testemunho do fenômeno em Conde. |
| **10 / 10** | **EXAMINADA** | Falências, rede ferroviária prioritária da SUDENE com **mapa de ferrovias**, portos, bancos, indústria petrolífera e mercado financeiro. **10h** é horário futuro do pregão anunciado para 18/11, não de queda. Salvador aparece em nomeação fiscal na Bahia; sem relato de Conde. |
| **11 / 11** | **EXAMINADA** | Câmbio, Bolsa, mercadorias, associação ACM, seguros, tecnologia de transporte Safège e avisos financeiros; nenhum artigo sobre objeto ou testemunha local em Conde. |
| **12 / sem fólio numérico visível** | **EXAMINADA** | **“Encerrado ontem o conclave atômico”**: energia nuclear e AIEA, não observação de satélite. Outras matérias: negociações diplomáticas, greves de São Paulo, mineração e exercícios navais. **12h30–17h30**, anunciadas para começar em 18/11, são horas bancárias, não do incidente. |

Em cada página **hora do suposto evento de Conde = não encontrada; testemunha = não encontrada**. Nenhum dos artigos comprovou independência editorial de uma informação específica sobre Conde porque **nenhum artigo pertinente foi identificado nessas quatro páginas**.

## Fronteira do resultado

Somando R76–R79, estão **13/28 páginas PDF examinadas integralmente** no exemplar 21657: **1–12 e 21**. O **1º caderno (PDF 1–12)** está coberto. A PDF 21, seção *Aviação e Astronáutica* do 2º caderno, já fora lida na R76. Um panorama adicional da PDF 13–28 apenas localizou matérias culturais, comerciais, esportivas, classificados e a seção de aviação já lida: **esse panorama não equivale à certificação integral das demais 15 páginas**.

Portanto `edition_fully_examined=false`, `global_negative_asserted=false`, `source_of_report_independent_from_tupi_fbis=UNDETERMINED`, `orbital_constraint_activated=false`. A ausência no núcleo lido **não demonstra inexistência histórica, hora de reentrada, nem vínculo material com NORAD 528/637**.

Próximo lote, conforme [fila vigente](https://github.com/franklinbaldo/conde-incident/blob/main/docs/PRIORITIES.md): **edições 21659, 21660 e 21661 (12–14/11)**, com hash do PDF original, fronteiras de cadernos e leitura do primeiro caderno; a edição 21658 pertence ao 🦌 Cervo. Não voltar a 21657 PDF 13–20/22–28, exceto indicação explícita de ciência/astronáutica ou chamada de capa.

O manifesto interpretativo ligado a esta nota está em [C241-TARTARUGA-R80 JSON](../archive/conde_correio_manha_1963_11_09_C241_TARTARUGA_R80.json).

---
type: Source
title: "C241-R80: núcleo do primeiro caderno do Correio da Manhã, 10/11/1963"
description: "Mapeamento dos 97 cabeçalhos e leitura visual das páginas 9–19, com distinção entre seção de astronáutica e hora de Conde."
source_id: C241-CERVO-R80-CM-19631110-CORE-P09-P19
locator: "Correio da Manhã, 10/11/1963, edição 21658 (FBN 089842), páginas PDF/impressas 9–19 do primeiro caderno"
provenance: "PDF original da FBN conferido por bytes e SHA-256 no Ifro em 15/11/2026; identificação dos cadernos por cabeçalho; leitura visual de páginas 9–19; camada textual apenas auxiliar"
verification_status: FIRST_CADERNO_CORE_1_19_READ_EDITION_INCOMPLETE
---

# C241-R80 | Primeiro caderno do *Correio da Manhã* de 10/11/1963

**Encomenda atualizada do Elefante:** [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871), [Cervo #6](https://github.com/franklinbaldo/cervo/issues/6#issuecomment-6899630902) e [critério de parada](../../docs/PRIORITIES.md). O lote original PDF p. 1–8 foi entregue em [PR #1081](https://github.com/franklinbaldo/conde-incident/pull/1081). Esta fatia cobre somente as **páginas PDF 9–19** e mapeia as seções restantes, sem classificá-las como integralmente lidas.

## Fonte e delimitação dos cadernos

[Fac-símile FBN 089842/21658](https://hemeroteca-pdf.bn.gov.br/089842/per089842_1963_21658.pdf): **62.742.698 bytes**, **97 páginas**, SHA-256 `75dc400708e80022dc9d1a139739068417e65ff47a3c4130bf0b46b9db4929f3`, conferidos novamente em 15/11/2026 no Ifro. O arquivo possui camada textual parcialmente defeituosa; o `pdftotext` foi usado apenas para localizar possíveis artigos, não para determinar ausência.

Por inspeção visual dos cabeçalhos, o **1º caderno termina na página PDF/impressa 19**. O mapa dos demais cabeçalhos, sem leitura integral de seu conteúdo, é: segundo caderno PDF 20–39; terceiro 40–68 (parte II automobilística 62–68); quarto 69–76; quinto 77–83; sexto 84–89; suplemento colorido/histórias em quadrinhos 90–97. Essa divisão não constitui negativo de nenhuma página fora do núcleo.

## Leitura da unidade de página

| PDF / impresso | Estado | Unidade editorial e limites |
|---|---|---|
| 9/9 | EXAMINADA | Cemitério de cães, notícias municipais e anúncios de relógios; nenhum horário de Conde. |
| 10/10 | EXAMINADA | Máquinas ferroviárias, UNESCO, indústria e notícias locais; referência a “Conde” é nome de escola/endereço, não município da Bahia. |
| 11/11 | EXAMINADA | Publicidade imobiliária de página inteira, sem artigo sobre evento. |
| 12/12 | EXAMINADA | Eleições, abastecimento de energia e meteorologia; “Estado de emergência para Bahia” é matéria de outra causa, sem objeto de Conde. |
| 13/13 | EXAMINADA | Festival da PUC, Santas Casas e população de rua; sem hora do fenômeno. |
| 14/14 | EXAMINADA | Furtos, greve de servidores e **grade da TV-Tupi canal 6 do domingo 10/11**; seu programa *Informe Científico* às 23h40 não é transmissão da **Rádio Tupi em 08/11**, hora FBIS ou hora da queda. |
| 15/15 | EXAMINADA | Publicidade integral do Clube do Parque. |
| 16/16 | EXAMINADA | “Reatores: reunião acaba com sucesso”, reunião de tecnologia nuclear, não órbita ou reentrada de satélite; outras notícias e anúncios. |
| 17/17 | EXAMINADA | Publicidade integral de móveis natalinos. |
| 18/18 | EXAMINADA | Educação, escolas, cidade universitária e anúncios; “Conde de Bonfim” é nome de rua, não o evento. |
| **19/19** | **EXAMINADA** | **“Aviação e Astronáutica”**: artigos sobre treinamento aeronáutico, pessoal, rotas e aeroportos; leitura ampliada dos quadrantes confirma que o título de seção não é evidência instrumental de satélite ou queda. Embaixo, notícia internacional sobre nacionalização no Egito e propaganda automotiva. |

As páginas foram examinadas em fac-símile renderizado; há microtipografia em áreas de anúncios, sem argumento de que toda letra seja recuperável. Termos em anúncios, o nome de rua “Conde de Bonfim”, o título da seção de astronáutica e a grade televisiva não são notícias ou relógios do fenômeno.

## Identificabilidade e critério de parada

Somando esta fatia à R79, o **primeiro caderno PDF 1–19** está visualmente coberto, mas **78 das 97 páginas** da edição não estão integralmente lidas. Seus cabeçalhos foram apenas mapeados, de acordo com o recorte deliberado pelo Elefante. A triagem dos demais cadernos não identificou outro cabeçalho especializado de ciência/astronáutica; essa triagem não licencia negativo dos demais cadernos.

Nenhuma hora local independente, testemunho presencial em Conde, registro de sensor ou elemento orbital adicional foi recuperado nas páginas 9–19. **Negativo destas páginas ≠ negativo da edição ou da ocorrência histórica.** A dependência da informação permanece `UNDETERMINED`. `independent_conde_event_hour=null`, `terminal_time_sigma_hours=null`, `active_constraint_528=false`, `historical_mcmc=NOT_RUN`. Não distinguir 528 de 637 nem reduzir domínio geográfico com base nestas páginas.

Registro estruturado no [manifesto R80](../archive/conde_correio_manha_1963_11_10_C241_CERVO_R80.json). Próximo passo: comunicar o negativo circunscrito à [#871](https://github.com/franklinbaldo/conde-incident/issues/871) e parar este lote, sem inventar novas sensibilidades orbitais.

---
type: Guide
title: "C241-R67: Última Hora NE 9 a 12/11/1963 e acesso a A Tarde"
description: "Quatro edições integrais da FBN com checksum, leitura visual das capas e limites explícitos para a busca de horário local sobre Conde."
---

# C241-LONTRA-R67 · quatro originais recuperados, mas ainda sem hora independente

**Fatia de 🦦 para [Conde #871](https://github.com/franklinbaldo/conde-incident/issues/871), coordenada por 🐢 Tartaruga**, conforme [inbox Lontra #10](https://github.com/franklinbaldo/lontra/issues/10). As buscas soviéticas de [#545](https://github.com/franklinbaldo/conde-incident/issues/545) ficam em espera nesta rodada por decisão de prioridade.

## Fonte primária: Última Hora, Recife

Foram recuperados por GET HTTPS integral no executor **Ifro**, em 15/11/2026 UTC, quatro PDFs da [coleção FBN 765147](https://bndigital.bn.gov.br/acervo-digital/ultima-hora/765147). Os números, datas e dias da semana foram **lidos visualmente no cabeçalho da primeira página de cada PDF**, não deduzidos por sequência. `pdfinfo` confirmou PDF 1.4 e quantidade de páginas; `%%EOF` presente. Os hashes são dos bytes originais baixados, **não** da renderização JPEG.

| Edição | Data impressa | PDF | Páginas | Bytes | SHA-256 (prefixo) | Estado da capa |
|---|---|---|---:|---:|---|---|
| 00472 | sáb. 09/11/1963 | [original FBN](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00472.pdf) | 10 | 5.275.519 | `8564c0c8c26857e0` | `LIDO_SEM_HORA`, apenas p. 1 |
| 00473 | dom. 10/11/1963 | [original FBN](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00473.pdf) | 18 | 8.298.891 | `f37e4afa500fe841` | `LIDO_SEM_HORA`, apenas p. 1 |
| 00474 | seg. 11/11/1963 | [original FBN](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00474.pdf) | 10 | 4.884.439 | `3d7b9268c1cf45c7` | `LIDO_SEM_HORA`, apenas p. 1 |
| 00475 | ter. 12/11/1963 | [original FBN](https://hemeroteca-pdf.bn.gov.br/765147/per765147_1963_00475.pdf) | 10 | 5.031.193 | `88859dfbab5e9590` | `LIDO_SEM_HORA`, apenas p. 1 |

**Limite incontornável:** `LIDO_SEM_HORA` refere-se **somente à primeira página**: nenhuma hora do suposto acontecimento de Conde foi identificada nela. **As outras 44 páginas não foram lidas visualmente**, logo não existe conclusão negativa sobre o conteúdo das edições. `pdftotext` expôs trechos preexistentes de reconhecimento com falhas, inclusive erros de glifos; essa camada **não** autoriza afirmar ausência de palavra, notícia ou horário. Uma tentativa de OCR novo foi interrompida sem inspeção integral. Não registrar `LIDO_SEM_HORA` para toda a edição.

**Controle de falso positivo:** em 12/11, a manchete da capa anuncia `Polet I` e a exploração lunar soviética (continuação na p. 5). É uma notícia espacial, mas **não traz identificação dos NORAD 527/528/529 nem hora local do relato de Conde** na capa. O “monstro do palacete” das manchetes de 9–12/11 é uma investigação policial recifense, não um suposto objeto espacial. Nenhuma dependência editorial ou testemunha foi atribuída sem ler reportagem correspondente.

## Demais jornais da fatia

| Título e data solicitada | Estado verificável | Limite |
|---|---|---|
| *A Tarde*, Salvador, **08, 09, 10, 11 e 12/11/1963** | `INACESSIVEL` **para leitura aberta remota** | O [anúncio oficial estadual de 2010](https://www.ba.gov.br/comunicacao/2010/01/noticias/fundo-de-cultura-apoia-digitalizacao-de-edicoes-do-seculo-20-do-jornal-a-tarde) descreve acesso por terminais nos Barris/Arquivo Público; [notícia de 2012](https://www.humanidades.com.br/noticias/detalhe/noticia/projeto-em-parceria-com-a-humanidades-esta-disponivel-em-biblioteca-da-bahia/) informa digitalização 1912–1999. **Não usar `NAO_DIGITALIZADO`: há digitalização da série.** Nenhum fascículo dessas cinco datas foi confirmado ou lido individualmente |
| *Jornal da Bahia*, Salvador, **11/11/1963** | `INACESSIVEL` online; original não lido | Reaproveita [Coruja PR #985](https://github.com/franklinbaldo/conde-incident/pull/985): [IGHB](https://www.ighb.org.br/biblioteca) anuncia 1959–1994 em nível de título, não confirma este fascículo. Homônimo digital da BN (1855–1877) não é esta fonte |

**Critério de independência:** as capas e os metadados não permitem atestar correspondência independente, testemunha, hora ou local; não reproduzir alegações Tupi/FBIS como se fossem citações lidas aqui. Nenhuma hipótese orbital, restrição de RAAN ou janela de reentrada foi alterada. Nenhuma consulta externa a instituições foi enviada.

## Próximo teste falsificável

Examinar as **44 páginas internas** das edições 00472–00475, priorizando notícias regionais/policiais e editoriais, com página/coluna e recorte visual de qualquer menção a Conde, Bahia, rádio, esfera ou horário do suposto acontecimento; se houver, registrar a cadeia de redação e a transcrição literal curta. O acesso a *A Tarde* permanece na [fila do dono #884](https://github.com/franklinbaldo/conde-incident/issues/884). As imagens/PPMs de triagem não substituem os PDFs FBN nem devem ser publicadas sem conferir direitos.

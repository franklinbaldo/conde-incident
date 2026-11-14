---
type: Guide
title: 'C241-LONTRA-R48: fac-símile soviético de 1964 com linha de 16/01/1963'
description: 'Página 503 de anuário soviético lista uma órbita inicial para lançamento americano secreto, mas não identifica NORAD nem comprova sensor independente.'
---

# C241-LONTRA-R48 · Anuário soviético de 1964, tabela de satélites americanos

**Aquisição verificável:** o [catálogo *Ежегодник Большой советской энциклопедии*, volume 8 (1964)](https://istmat.org/node/35454) disponibiliza o recorte digitalizado [*Наука и техника*](https://istmat.org/files/uploads/35454/14_nauka_i_tehnika.pdf). O PDF foi recuperado integralmente em 14/11/2026, por HTTPS verificado: **23.846.637 bytes**, SHA-256 **`d2372fe5b073c95366681bf550a0688ee47a6d2b6c4c612125e006a79fcdc613`**, **70 folhas de PDF**. O fac-símile da **página impressa 503, página 7 do arquivo**, foi examinado visualmente; o OCR contém erros, de modo que a leitura numérica a seguir deriva da página renderizada, não de regex sobre OCR.

Sob o título *Американские искусственные спутники Земли, выведенные на орбиту в 1963 г.* (satélites artificiais americanos colocados em órbita em 1963), a **linha 3** registra:

| Campo da publicação | Leitura da linha 3, p. 503 |
|---|---|
| Nome | `Секретный` (secreto), **sem número de catálogo** |
| Data de lançamento | `16.01`, isto é, 16 de janeiro no ano 1963 da tabela |
| Lançador | `Тор — Аджена D` (Thor–Agena D), sujeito a cotejo |
| Perigeu / apogeu, km | **459 / 533** |
| Período, minutos | **94,66** |
| Inclinação, graus | **81,89** |
| Massa | não indicada |
| NORAD, COSPAR, RAAN, época observada, estação, instrumento ou precisão | **não indicados** |

A data **coincide** com a do lançamento 1963-003, associado aos NORAD **527/528/529** no catálogo já existente. Porém, a linha impressa **não identifica nenhum desses objetos**, nem distingue componentes do mesmo lançamento. Além disso, a designação de lançador `Agena D` difere da atribuição `Agena B` de outros catálogos modernos. A divergência é pista para auditoria de proveniência, não autorização para substituir a identificação existente.

**Dependência documental, não nova órbita observada:** a própria p. 503 cita como bibliografia *Flight*, *Aviation Week*, *Missiles and Rockets*, *Interavia* e *Air Letter*. Não atribui os parâmetros a instrumento soviético ou a uma estação óptica. Portanto, embora o **impresso soviético seja outro testemunho editorial contemporâneo**, ele pode apenas recopiar informações ocidentais. Não se adiciona uma observação independente, não se cria época TLE, não se ativa restrição orbital, não se atribui precisão aos números.

A [ficha Google Books do volume VIII, 1964, 616 páginas](https://books.google.com/books?id=oyoH0AEACAAJ) corrobora a identidade bibliográfica, sem ser testemunho instrumental ou prova de qualquer linha específica. A digitalização legível veio de Istmat; nem o livro físico nem seus registros de redação foram examinados.

**Próxima verificação:** localizar a origem exata dos valores impressos em *Flight*, *Aviation Week* e *Missiles and Rockets* de janeiro/fevereiro de 1963, e confrontar o possível erro de lançador (Agena D vs B). Continuar procurando **cadernos soviéticos de novembro de 1963**, sobretudo fascículos 32–37 e 2 já catalogados sob C241-L29 e diários de estações. Não recontar republicações como sensores.

Manifesto: [`soviet_bse1964_1963_003_C241_LONTRA_R48.json`](soviet_bse1964_1963_003_C241_LONTRA_R48.json). Testes adversariais: `tests/test_soviet_bse1964_1963_003_r48.py`; verificação de replay binário: `tools/verify_soviet_bse1964_pdf_r48.py`. Nenhum contato com arquivo ou pesquisador foi enviado.

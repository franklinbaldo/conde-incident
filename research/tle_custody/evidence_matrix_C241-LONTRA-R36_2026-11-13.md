---
type: Guide
title: 'C241-LONTRA-R36: cronologia dos negativos de Zvenigorod'
description: 'Dois trabalhos de arquivistas do observatório delimitam as coleções AFU, VAU e Zeiss; nenhuma cobre 1963 segundo seus inventários, sem negar acervos de outras estações.'
---

# C241-LONTRA-R36 · A cronologia muda a rota AFU

**Correção de prioridade, não observação orbital.** A [memória pessoal publicada no SAI/MSU](https://www.sai.msu.ru/EAAS/rus/doc/MEM-12.htm) (C241-LONTRA-R35) relata catalogação de negativos AFU em Zvenigorod iniciada em 2007. Mas a data **2007 é de catalogação**, não de exposição de fotografias de 1963.

Uma publicação técnica assinada por quatro especialistas da própria coleção, [*The INASAN Zvenigorod Observatory Plate Collection*, 2012, pp. 359–362](https://www.astro.bas.bg/conf_proc/book_VIIBSAC.pdf), traz tabela de datas e quantidades: **Zeiss 1972–2005, 4.500 chapas; AFU 1973–1985, aproximadamente 2.800 filmes; VAU 1971–2005, aproximadamente 10.000 filmes**. Os anos são do acervo descrito, **não de toda a fotografia astronômica soviética**. A tabela foi lida no texto indexado do PDF; a página física da edição 2012 não pôde ser conferida visualmente pelo visualizador web (falha 400 devido ao tamanho do PDF). Portanto, `page_checked_visually=false`.

Um segundo testemunho dos responsáveis, [*Photo plates digital archives of the INASAN Zvenigorod Astronomical Observatory*, 2014, pp. 119–122](https://www.astroplate.cz/wp-content/uploads/2014/12/astroplate_2014_proceedings.pdf#page=126), foi **inspecionado visualmente**, inclusive pp. 119–120 (folhas PDF 126–127). Ele delimita o acervo fotográfico geral a **1972–2005**, reporta **2.683 filmes AFU** e cita os identificadores WFPDB **`ZVN` / `021`** para a câmera AFU (astrográfo `040`). O acervo AFU está catalogado, mas o trabalho informa que sua digitalização não estava planejada à época da publicação. A diferença 2.800/2.683 pode decorrer de critérios de contagem ou atualização: não declarar perda ou destruição dos filmes.

## Custódia dos downloads em 13/11/2026

| Documento | Bytes integralmente baixados | SHA-256 | Atestado |
|---|---:|---|---|
| Congresso 2012 (`book_VIIBSAC.pdf`) | 17.605.841 | `e6b538c34a8c26056cd8d0296ae6570033eb9ff5359f932f9b6250f670e64e42` | HTTPS/TLS, arquivo PDF; página textual indexada; visual pendente |
| Proceedings 2014 (`astroplate_2014_proceedings.pdf`) | 8.854.648 | `59b53f4ea48c3c9486b80aead7469b01e15307747fa085e99df04de7f08f1d70` | HTTPS/TLS, PDF, pp. 119–120 inspecionadas visualmente |

Os arquivos integrais estão **fora do Git**; hashes não são assinaturas editoriais nem demonstram que a exposição de filme ocorreu em determinado ano. Os números são válidos **para as coleções descritas**. Não provam que Zvenigorod ou outras estações não fizeram observações em 1963, nem que inexistam negativos mais antigos noutros depósitos. O arquivo fotográfico de 2014 não é medição dos NORAD 527/528/529. Nenhuma restrição orbital é ativada.

**Próxima prioridade:** reduzir a exploração de negativos AFU/VAU **da coleção identificada de Zvenigorod** para a janela de novembro/1963, salvo nova contraprova documental. Procurar nos livros de registro de estações ópticas **ativas em 1963**, na série soviética *Результаты наблюдений ИСЗ* e nos acervos das estações 1078/1035/1090, como fontes separadas. Para qualquer registro futuro, exigir placa/cota, época e fuso, instrumento e estação, identificação 1963-003 A/B/C e coordenadas instrumentais antes de repassar à Tartaruga.

**Reprodução:** `python3 -m unittest discover -s tests -p 'test_zvenigorod_collection_dates.py' -v`. Replay opcional com os PDFs originais: `python3 tools/verify_zvenigorod_collection_dates.py --pdf-2012 /caminho/book_VIIBSAC.pdf --pdf-2014 /caminho/astroplate_2014_proceedings.pdf`. Contraprovas offline não substituem verificação do conteúdo visual dos PDFs.

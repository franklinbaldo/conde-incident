---
type: Guide
title: "Lontra: localização do manual primário NMC ON20 e notas adjacentes"
description: "Inventário oficial NCEP de 1963–1968, com links PDF não acessíveis e limites de leitura da fonte Y20175."
---

# NCEP: localização documental ON20, sem decodificação do Y20175

**Ocorrência documental:** MET-NMC-NCEPON-20261112-01. **Vinculação pendente:** MET-NMC-20261112-09 / C241-L5, research/constraints/nmc_y20175_pending_bridge.json. Não acrescenta observação ao rol C001–C238 nem altera restrições de reentrada.

## Inventário oficial diretamente inspecionado em 12/11/2026

Fonte: [NCEP/EMC, Office Notes, índice completo](https://www.emc.ncep.noaa.gov/officenotes/FullTOC.html), HTTP 200, corpo HTML de **135.389 bytes**, SHA-256 e25d963fcddd42891c2bead34da1411d2326880ecb31bcc2d51670941b8ee3d2. Header Last-Modified: **30/04/2012 17:14:41 GMT**, que data a cópia web, **não** as edições dos documentos. Identificadores e títulos da fonte:

| Nota | Ano como catalogado | Autor | Título | Localizador PDF no índice |
|---|---|---|---|---|
| 16 | 1960 / 1963* | G. R. Dent | Hydrostatic and Wind Check in the ADP Program (1963) (*revised) | 013FD4C3.pdf |
| **20** | **1964** | **J. Neilon** | **Upper Air ADP Records Format** (revision beginning on page 12) | **013FD4DB.pdf** |
| 22 | 1964 | Automation Division Staff | ADP 3rd Word | 013FD4E4.pdf |
| 26 | 1968 | L. Loman | Structure of the NMC B3 Data Tape | 013FD507.pdf |

O índice oficial é a **fonte primária de identificação bibliográfica e endereço de download**, mas não substitui a leitura dos quatro PDFs. A nota 20 é o primeiro manual ON20 nominal diretamente localizável; 22 e 26 são potenciais materiais auxiliares de layout e fita. Não presumir conteúdo interno de 20/22/26 sem recuperar os originais. A revisão que começa na **página 12** da nota 20 pode ter cronologia diferente da primeira edição: sua presença no índice **não prova** que campos descritos em 1964 ou em revisões já vigorassem em novembro de **1963**.

## Acesso e lacuna reproduzíveis

Os quatro href oficiais ainda apontam para http://www.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/{arquivo}. Nesta execução, HEAD de **cada href** retornou falha de resolução/acesso (URLError, status HTTP desconhecido), portanto **nenhum PDF foi baixado nem teve SHA-256 calculado**. Uma tentativa explícita do caminho da nota 20 em https://www.emc.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/013FD4DB.pdf devolveu **HTTP 404**. Isso documenta somente os endpoints testados, não a indisponibilidade histórica do documento em outros repositórios. Não foi contatado qualquer arquivo ou pessoa.

O [catálogo NCAR/GDEX d353000](https://gdex.ucar.edu/datasets/d353000/) associa o Y20175 a ON20 com encapsulamento RPTOUT/COS, mas **não fornece o layout binário do registro individual**. O relatório histórico [CARDS, apêndice A.3, páginas impressas 43–47](https://scispace.com/pdf/comprehensive-aerological-reference-data-set-cards-5fey360i6i.pdf) cita explicitamente Neilon (1964), a estrutura de 36 bits e palavras de identificação NCAR, além de erros de sincronização. O exemplo investigado ali é **1971–1972**, portanto suas posições, taxas de erro e convenções **não podem ser transferidas automaticamente para Y20175 (1963)**. Não confundir os 14.889 grupos EOR físicos já custodiados com a contagem de radiossondagens.

## Estado e próximo gate

* Fonte de catálogo: **INSPECTED_HTML / SHA256_VERIFIED**.
* PDFs das Office Notes 16/20/22/26: **LOCATED_IN_INDEX / CONTENT_NOT_RETRIEVED**; páginas e hash integral **desconhecidos**.
* Y20175: **COS_VERIFIED / ON20_NOT_DECODED**, buscas WMO 83229, 83096 e 82900 em 7–9/11/1963 **NOT_RUN**.
* Nova conexão cumulativa: **um conjunto bibliográfico oficial** que fornece alvo para decodificador, mas **zero observáveis físicos e nenhuma restrição ativada**.

Próximo passo: obter o **fac-símile completo e autenticado da Nota 20**, conferir a revisão a partir da p.12 e cotejar sua estrutura com um registro conhecido de 1963; inspecionar em seguida as notas 22/26. Somente depois testar estação, data, nível, unidade e controle de qualidade no Y20175. Não fazer parsing otimista com a Nota 29 (1973+).

**Reprodução:** python3 tools/audit_ncep_office_notes.py --probe --output /tmp/ncep-locator.json; python3 -m unittest discover -s tests -p 'test_ncep_office_notes.py' -v. O teste é offline e valida que não se pode trocar o ano 1964 por 1963, omitir nota, duplicar nota ou eliminar links sem falhar. Um resultado de teste verde não constitui validação dos PDFs ausentes.

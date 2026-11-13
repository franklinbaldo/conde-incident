---
type: Guide
title: "CGEO-L628: publicação original da Lei 628/1953 localizada no Diário Oficial de 1º de janeiro de 1954"
description: "Edição nº 3259, páginas impressas 1–2, páginas PDF 2–3; identificação visual e replay integral sem retroprojetar limites de 1963"
---

# CGEO-L628: a publicação, enfim, tem página

**Achado novo (13/11/2026):** foi localizada visualmente a **Lei baiana nº 628, de 30/12/1953**, no [fac-símile do Diário Oficial do Estado da Bahia, edição nº 3259, sexta-feira, 1º/01/1954](https://acervo.tjba.jus.br/ConsultaWeb/downResource?id=dfdig000000000000000000000009009#page=2). A data de 30 de dezembro é **sanção do diploma**; a data de 1º de janeiro é a **data impressa da publicação identificada**. Antes, tínhamos dois volumes mensalmente custodiados, mas nenhuma página da norma localizada.

| Folha no PDF mensal | Página impressa | Evidência visual |
| --- | --- | --- |
| **2 de 856** | **1** | Cabeçalho de sexta-feira, 1/01/1954, nº 3259. No rodapé esquerdo, título **Lei nº 628, de 30/12/1953** e art. 1º; o texto prossegue na coluna direita com arts. 2º e 3º. |
| **3 de 856** | **2** | Topo esquerdo: conclusão com arts. 4º e 5º e assinaturas, seguida da rubrica **Atos do Poder Executivo**. |

O artigo 1º fixa a divisão territorial administrativa para **1954–1958** e remete ao Quadro I; o artigo 2º remete aos anexos II a VI e à legislação precedente. Essas remissões **não demonstram que os anexos tenham sido impressos nestas duas folhas**. A redação duvidosa sobre Jandaíra na transcrição Word de 2013 continua sem cotejo com o **Anexo VI original**. Também não se demonstrou a inexistência de atos entre 1959 e novembro de 1963.

## Custódia, método e limite

O PDF de 856 folhas está no acervo **TJBA ArchiDoc**, recurso `dfdig000000000000000000000009009`. O arquivo integral já identificado na [custódia mensal](../archive/conde_tjba_doe_1954_01_20261113.json) tem **124.028.298 bytes** e SHA-256 `45fb60c544e0115c896706d4265f18b3a7bde551b9134c9bdce36e4c8d0e1237`. Houve conferência SHA-256 depois da cópia ao executor IFRO. `pdftotext -layout` foi usado apenas como **índice OCR auxiliar**, e as páginas 2 e 3 foram **renderizadas e inspecionadas visualmente** com Poppler 25.03.0. O teste de replay fez hash do PDF inteiro e confirmou, na camada OCR, o assunto da página 2 e o art. 5º na página 3. Não foi feita correspondência com o exemplar físico guardado na EGBA.

O [manifesto de página](../archive/conde_lei628_1953_doe_pagelevel_20261113.json) contém número da edição, duas paginações, proveniência e estados interpretativos. Reprodução (sem versionar o PDF grande):

```sh
python3 -m unittest tests.test_tjba_lei628_print -v
python3 tools/verify_tjba_lei628_print.py
python3 tools/verify_tjba_lei628_print.py --pdf /caminho/DOE_Bahia_jan_1954_Archidoc.pdf
pdftoppm -f 2 -l 3 -scale-to 1600 -jpeg -jpegopt quality=72 /caminho/DOE_Bahia_jan_1954_Archidoc.pdf /tmp/lei628
```

**Grafo de dependências:** `CGEO-TJBA-DOE-1954-01-01 → CGEO-L628 (publicação primária) → Quadro I e Anexo VI (pendentes de página original) → atos 1959–1963 (pendentes) → limite municipal jurídico de 08/11/1963 (não demonstrado)`. A transcrição da Casa Civil e a publicação do TJBA pertencem à **mesma linhagem normativa**, não são duas leis independentes. Nenhuma nova coordenada, polígono, probabilidade de queda ou restrição orbital foi inferida.

**Próximo teste discriminante:** vasculhar o suplemento/anexos de 1º/01/1954 e edições subsequentes até achar o **Anexo VI**, confrontando palavra por palavra a linha de Jandaíra, e verificar alterações legais até 1963. Não contactar arquivos sem autorização.

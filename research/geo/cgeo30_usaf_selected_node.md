---
type: Guide
title: 'CGEO-30: seleção verificada de nó USAF 63-32 no SGB'
description: 'Replay de POST ASP.NET e limites da imagem não recuperada'
---

# CGEO-30: o nó do fotoíndice foi selecionado de verdade

Em **13 de novembro de 2026**, um GET público do [leitor de fotoíndices USAF do SGB](https://acervo.sgb.gov.br/DocReader/DocReader.aspx?bib=FotoUSAF) foi seguido de POST ASP.NET com `__EVENTTARGET=T1` e `__EVENTARGUMENT=s679`. A resposta HTTP 200 marcou literalmente a entrada **1850 Projeto USAF 63-32 - área A: SC.24-Z-C-VI** como `rtSelected`, informou `_selectedValue:"680"` e indicou o contador `/1`.

A resposta completa do POST de seleção possui **578.782 bytes**, SHA256 `85453908986f12259462c70e7bcb919c332af6ac8e4aa75ed75749ee6b327788`. O [excerto derivado](evidence/cgeo30_usaf_selected_excerpt.html), de 382 bytes, registra somente quatro provas do HTML obtido: nó selecionado, valor selecionado, contador da pasta e tag da imagem sem atributo `src`. Seu SHA256 é `c59038962fc60766b9951353d149704437ac970dfaaccde1898c8bc251f0fafa`. O excerto **não** é uma segunda fonte independente.

Um POST subsequente no controle `CarregaImagemHiddenButton`, com `hPagFis=1`, manteve o nó selecionado (HTTP 200, 578.799 bytes; SHA256 `72b7becf8928ab098d3889defdea6273a86169c8188b743fc4b01f4e6310340f`), mas o HTML devolvido continuou sem `src` na tag `DocumentoImg`. O endpoint de exportação devolveu **HTML**, não PDF. Portanto há **seleção efetiva no servidor**, diferentemente da busca textual não comprovada em CGEO-28, mas **a imagem do fotoíndice ainda não foi adquirida**. É possível que o navegador busque bytes por outra requisição de script/async; não se conclui indisponibilidade definitiva.

Reprodução sem rede: `python3 tools/cgeo30_usaf_selected.py`; opcionalmente, com os HTMLs originais adquiridos e guardados fora do Git, `python3 tools/cgeo30_usaf_selected.py --selection-html caminho --image-attempt-html caminho`. A verificação integral exige bytes e hashes originais; o CI valida o excerto efetivamente derivado, suas afirmações e testes adversariais.

**Limites:** `/1` é contador de página no leitor, não quantidade de fotogramas. Nenhum mapa, negativo, data de tomada, área coberta, escala, centro histórico, coordenada de queda ou restrição orbital foi autenticado. A família USAF 63-32 não é confundida com PETROBRAS 53 D. Este resultado liga CGEO-29 à próxima etapa da [issue #558](https://github.com/franklinbaldo/conde-incident/issues/558), sem transformar navegação de site em observação física.

---
type: Guide
title: "CGEO-26: pista de aerofotografias PETROBRAS 1961, Projeto 53 D, folha Esplanada"
description: "Catálogo DIDOTE de junho de 2003 transcrito por espelhos, MI-1850, distinção foto/índice e ponte de cobertura ainda não verificada"
---

# CGEO-26 | A pista aerofotográfica de 1961

A relação **Acervo Fotográfico Multimeios**, atribuída à **CPRM/SGB, DIDOTE, junho de 2003**, aparece em espelhos [Scribd 190899422](https://it.scribd.com/doc/190899422/acervo-foto-pdf), [Scribd 50811476](https://pt.scribd.com/doc/50811476/acervo-foto) e [Yumpu 8190809](https://www.yumpu.com/pt/document/view/8190809/acervo-fotografico-multimeios-cprm). A transcrição do **PETROBRAS Projeto 53 D, Nordeste, 1961** inclui a folha **MI-1850, SC-24-Z-C-VI, Esplanada (BA/SE)**. Distingue **fotografias aéreas 1:25.000** de **fotoíndice 1:100.000**. Trata-se de um alvo arquivístico novo e *potencialmente anterior* a 08/11/1963, ao contrário da edição SUDENE Esplanada de 1973 registrada em CGEO-25.

**Custódia:** a relação original de 2003 **não foi baixada nem cotejada página a página**; são transcrições de um mesmo catálogo, não três fontes independentes, sem hash verificável do PDF original. Tampouco foram obtidos fotoíndice, negativos, fotografias ou números de faixa e fotograma. O ano **1961 é a identificação nominal do projeto**, não data de exposição de cada fotograma. A coleção pode estar parcialmente coberta ou ter mudado de custódia desde 2003. Não se contatou instituição ou pessoa.

O cruzamento com [CGEO-24](cgeo24_esplanada_sheet_index.json) situa **duas posições de câmera modernas (2022)** na quadrícula nominal MI-1850 (-38 a -37,5° de longitude, -12 a -11,5° de latitude), mas isso **não comprova cobertura fotográfica da sede urbana**. A quadrícula de índice não é a pegada de voo; não existe georreferenciamento histórico, datum comprovado, parâmetro de erro ou marco urbano temporalmente autenticado. Os seis mapas SACS/GEOFOTO 1956–1963 citados na compilação geológica de 1998, CGEO-25, são outra ocorrência documental: não presumir identidade ou independência observacional com este voo PETROBRAS.

**Próximo teste falseável:** localizar no acervo original da CPRM/DIDOTE a página da relação de 2003, depois o fotoíndice MI-1850 do Projeto 53 D e seus negativos/fotogramas. Extrair pegadas, números e datas reais; verificar se *alguma* faixa cobre o Centro de Conde, então comparar com marcos urbanos do IBGE 1958 (CGEO-17). Se a folha só teve cobertura parcial fora da cidade, o candidato cai. A descrição de acervo sozinha não geolocaliza o relato FBIS/Tupi (CGEO-18).

`python3 -m tools.cgeo26_aerial_locator` testa a identificação catalográfica transcrita, a consistência com as quadrículas e pontos reais já custodiados em CGEO-24/25 e os bloqueios epistemológicos. Saída `CONTRACT_ONLY_PASS`: **não baixa nem reautentica as fontes remotas**. `python3 -m unittest discover -s tests -p 'test_cgeo26_aerial_locator.py' -v` cobre nove casos e mutações adversariais. Estado do grafo: `CONNECTED_PENDING_PRIMARY_CATALOGUE_AND_FLIGHT_FOOTPRINT`; centro, polígono e local de queda em 1963 nulos, sem restrição orbital ativada.

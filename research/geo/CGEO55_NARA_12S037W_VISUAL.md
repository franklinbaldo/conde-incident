---
type: Evidence
title: 'CGEO-55: repetição de O.P. FILE NO. em quadrículas NARA de 1942'
description: 'Seis JPEGs originais inspecionados, comparação documental e limites científicos explícitos.'
---

# CGEO-55 | Inspeção visual dos índices NARA 12S037W (1942)

**14/11/2026.** Retomando [CGEO-54](cgeo54_nara_adjacent_overlay_index.json), adquiri os **quatro JPEGs integrais** da unidade [NARA 46716877](https://catalog.archives.gov/id/46716877), quadrícula **12S037W**, e revalidei dois índices da unidade [46716637](https://catalog.archives.gov/id/46716637), **11S037W**, por SHA-256 integral. Os seis originais somam **14.651.114 bytes**. URLs, dimensões, tamanho e digest constam no [contrato](cgeo55_nara_12s037w_overlays.json).

| Digitalização | Natureza visível | Transcrição seletiva |
| --- | --- | --- |
| [00429](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00429.jpg) | Capa, não mapa ou fotografia | RG 373; Aerial Flight Overlays; S12 W37; 1942 |
| [00430](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00430.jpg) | Carta de referência | Conde; Sambaúma; Baixio; WAC 1141 |
| [00431](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00431.jpg) | Formulário USAF e marcações de exposição | O.P. FILE NO. **125374**; SEP 42 (dias incertos) |
| [00432](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00432.jpg) | Formulário USAF e marcações de exposição | O.P. FILE NO. **125370**; 27 SEP 42 |
| [00247](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00247.jpg) | Outro formulário, unidade 11S037W | O.P. FILE NO. **125370**; 27 SEP 42 |
| [00248](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg) | Outro formulário, unidade 11S037W | O.P. FILE NO. **125374**; SEP 42 (dias incertos) |

## Relação documental nova

Os **mesmos números manuscritos no campo impresso O.P. FILE NO.** reaparecem em duas quadrículas: par **125374 = 00248/00431** e par **125370 = 00247/00432**. A ligação entre folhas ajuda a pesquisar a missão/arquivo, mas **não demonstra** que sejam os mesmos fotogramas, números de spot, latas de negativo ou observações independentes. A data anotada na folha não comprova o instante individual da fotografia.

O mapa 00430 contém literalmente **Conde**; os overlays 00431 e 00432 mostram polígonos/linhas de exposição em seu próprio quadro. A presença do topônimo e das marcações na mesma unidade **não comprova cobertura fotográfica do núcleo urbano**. Sem registro por pontos de controle, não há coordenadas, footprint, distância em metros ou incerteza geográfica demonstrados. Das quatro imagens da unidade 12S037W, uma é capa, uma é mapa de referência e duas são fotoíndices; nenhuma é negativo/fotograma original.

**Próximo experimento falsificável:** obter instrumento NARA que relacione os O.P. FILE NO. **125370/125374** a spot, lata de filme e exposição, adquirir negativo com data e footprint e testar cobertura do núcleo histórico de Conde. As datas de 1942 antecedem novembro de 1963, mas não validam continuidade urbana ou a expressão do relato FBIS/Tupi.

**Reprodução:** o validador tools/cgeo55_nara_visual_overlays.py e os 18 testes adversariais rodam em Python normal e otimizado. A opção --live baixa os seis JPEGs oficiais completos e compara bytes, SOI/EOI e SHA256. Transiente de rede não é prova de ausência; os gates só aprovam com exit code 0 e SHA do commit correto.

**Limites:** data individual da exposição, spot, lata, footprint georreferenciado, cobertura do Centro, geometria de 1963 e localização da alegada queda permanecem **nulos**; restrição orbital **não ativada**. Ver [guia RG373](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography) e [Conde #558](https://github.com/franklinbaldo/conde-incident/issues/558).

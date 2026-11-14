---
type: Evidence
title: 'CGEO-48: corredor aéreo de setembro de 1942 candidato perto da legenda Conde'
description: 'Sobreposição visual conservadora de dois fac-símiles NARA RG373/M1765; somente proximidade em pixels de tela, sem fotografia ou geocódigo de novembro de 1963.'
---

# CGEO-48 | Candidato fotográfico de 1942 próximo à legenda Conde

**14/11/2026.** Continuei a custódia CGEO-47, inspecionando diretamente as digitalizações originais do [mapa-base 00246](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00246.jpg) e da [folha de faixas 00248](https://catalog.archives.gov/medialz/cartographic/rg-373/306062/m1765-317/m1765-317/m1765-317-00248.jpg), da [unidade NARA 46716637](https://catalog.archives.gov/id/46716637). Não são fotografias aéreas da cidade. Hashes integrais e tamanhos estão custodiados em `cgeo47_nara_m1765_conde_pre1963.json` e novamente vinculados no contrato CGEO-48.

**Observação nova:** reduzindo ambos os scans independentemente para 1080 × 1200 px, seus cantos de quadro cartográfico se alinham visualmente a poucos pixels. O símbolo toponímico *Conde* no mapa-base fica perto da faixa desenhada na folha 00248, no trecho entre as anotações numéricas **26** e **16**. O formulário da folha 00248 parece registrar as datas **7, 11, 18 e 20 SEP 42**: transcrição humana **provisória**, não data de um fotograma individual nem prova de exposição da cidade. O número manuscrito `125374` não foi identificado como *spot number*.

O [guia NARA RG373](https://www.archives.gov/research/cartographic/aerial-photography/rg-373-dia-foreign-aerial-photography) esclarece que os contornos numerados e as ligações permitem *estimar* exposições e que é preciso identificar **spot number + número da exposição** para alcançar o localizador de latas e os negativos. Portanto, esta rodada cria um **candidato verificável**, não uma confirmação de cobertura do núcleo urbano.

## Geometria e limites

- O JSON guarda o sistema de **pixels de uma prévia de exibição**, coordenadas aproximadas de dois cantos do quadro, o ponto gráfico da legenda Conde e uma linha proxy aproximada do corredor. O validador calcula apenas a proximidade nessa tela, sujeita ao erro do registro entre folhas e à grossura dos traços. Não se atribuem metros, EPSG, datum, ortorretificação nem polígono da cidade.
- Digitalizações distintas têm 3636 × 4002 e 3620 × 3988 pixels. O redimensionamento independente para visualização **não** estabelece transformação métrica do chão.
- Proximidade visual ao **topônimo** não comprova que o centro habitado foi fotografado; o desenho é de faixas/coberturas indicativas, não o negativo em si. Priorizar a confirmação arquivística dos números 26/16 e o *spot number* da folha 00248 antes de solicitar qualquer negativo.
- O estudo tem intervalo documental 1942–1943, não 1963. O índice SGB USAF 63-32 contém período 1964–1970; não são duas medições do mesmo voo. Geometria urbana em 08/11/1963, ponto da alegada queda e efeito orbital permanecem `null`/`false`.

**Reprodução:** `python3 tools/cgeo48_nara_overlay.py` valida o contrato e vincula hashes ao CGEO-47; `python3 -m unittest discover -s tests -p test_cgeo48_nara_overlay.py -v` executa os mutantes adversariais. Com arquivos originais custodiados, `python3 tools/cgeo48_nara_overlay.py --cached-directory /caminho` confere bytes completos; `--live` obtém **novamente os dois JPEGs** e confronta SHA-256 sem depender de um PDF ou imagem fictícia.

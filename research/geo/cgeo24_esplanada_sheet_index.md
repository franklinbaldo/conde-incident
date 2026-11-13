---
type: Guide
title: "CGEO-24: índice de folhas Esplanada MI-1850"
description: "Localização nominal da folha das câmeras modernas, custódia dos PDFs e veto à promoção para 1963"
---

# CGEO-24: qual folha topográfica buscar para Conde?

O quadro de articulação da carta-imagem **Porto Sauípe MI-1906** do IBGE mostra **Esplanada MI-1850** entre 38°00'W e 37°30'W, 12°00'S e 11°30'S, escala 1:100.000. As duas posições de *câmera* de 2022 em CGEO-15 estão dentro dessa folha nominal, não de Porto Sauípe, ao sul do paralelo 12°S. Não são coordenadas do centro de 1963 nem do incidente.

Os dois PDFs oficiais foram adquiridos integralmente em 13/11/2026 e auditados por tamanho e SHA256. [Carta-imagem do IBGE](https://geoftp.ibge.gov.br/imagens_do_territorio/imagens_corrigidas/cartas_imagem/ba100/porto_sauipe_mi-1906_ci.pdf): 3.943.016 bytes, SHA256 36e4cda6a248db96a5a0f33189ab0fe23b883cc196582083023ed1ed20a830d2; o índice encontra-se na margem direita da folha. [Inventário da SUDENE](https://www.gov.br/sudene/pt-br/centrais-de-conteudo/CartasTopograficasparadoacao2022.pdf/@@display-file/file): 274.357 bytes, SHA256 4df003e72a7187da97438ab3c36114b28cf2e44cc94a44156794a473e519bbe9; página PDF 13 (índice 12). Este registra **MI-1850 Esplanada BA/SE, escala 1:100.000, impresso e digital, quantidade 4**. Quatro exemplares de estoque não representam quatro levantamentos independentes.

Para testar, execute python3 -m unittest tests.test_cgeo24_sheet_index -v e python3 -m tools.cgeo24_sheet_index. Para reproduzir a custódia integral, forneça --ibge-pdf e --sudene-pdf com os arquivos reais baixados; o verificador compara assinatura, comprimento e SHA256. Testes offline sem PDFs não provam disponibilidade remota.

A carta-imagem foi produzida com cenas de 2000–2002 e correção em 2003; o inventário tem data 2022, mas **não data a edição da folha de Esplanada**. Um caminho candidato, esplanada_mi-1850_ci.pdf no mesmo diretório IBGE, retornou HTTP 404 em 13/11/2026. Isso não prova inexistência em outros acervos. No inventário existe ainda **Conde - PB, MI-38, 1:25.000**, homônimo fora do escopo baiano.

Geometria das bordas = quadrícula nominal, datum não autenticado, precisão nula. A função retorna BOUNDARY_UNRESOLVED sobre linhas divisórias. Grafo: CGEO-15 (câmeras 2022) -> folha candidata MI-1850; CGEO-17 (topônimos IBGE 1958) -> georreferenciamento histórico PENDENTE; CGEO-18 (FBIS/Tupi) -> centro de 1963 ainda DESCONHECIDO. Não há polígono histórico nem nova restrição orbital. Próximo teste discriminante: obter levantamento, aerofoto ou mapa urbano com **data autenticada anterior a 08/11/1963** e confrontar marcos do centro.

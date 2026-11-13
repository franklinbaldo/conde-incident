---
type: Guide
title: 'CGEO-36: mapa de 1914 distingue Conde e Sítio'
description: 'Custódia de mapa histórico de 1914 e leitura visual de topônimos, sem importar geometria para 1963.'
---

# CGEO-36 | Dois topônimos antes do relato de 1963

Em 13/11/2026 foi adquirido um fac-símile PDF de **1.383.563 bytes** com SHA256 `66c9646a3a3e15bb6a8525e90c7697d3177d0be979e42c3b599f90241ef0cf33`: o [mapa de Ralph H. Soper, julho de 1914](https://commons.wikimedia.org/wiki/File:Mapa_do_estado_de_Sergipe_e_da_parte_nordeste_do_estado_da_Bahia_1914.pdf), da Inspectoria de Obras contra as Seccas (escala impressa **1:1.000.000**), custodiado pelo Arquivo Nacional sob **BR RJANRIO DS.0.MAP.28** e divulgado em parceria com Wikimedia Commons. A data da digitalização não é a data de produção do mapa.

Uma [pré-visualização raster pública](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d4/Mapa_do_estado_de_Sergipe_e_da_parte_nordeste_do_estado_da_Bahia_1914.pdf/page1-1920px-Mapa_do_estado_de_Sergipe_e_da_parte_nordeste_do_estado_da_Bahia_1914.pdf.jpg) foi **adquirida** separadamente (967.413 bytes, SHA256 `172b519c2f89cc0f17341ce0e41887701987b25fa3c2d08d3814ead3ca4a7fbb`). No recorte de imagem (em pixels da prévia 1920×2161) `x=750..1249, y=1110..1509`, leem-se literalmente **“Conde”** e **“Sítio”** como rótulos distintos; no desenho, “Conde” está mais para o interior e “Sítio” junto à costa. Esta observação é visual, não OCR, e o retângulo é um recorte de **imagem**, não geometria do terreno.

Isso constitui uma **fonte cartográfica anterior a 1963** adicional à carta IBGE 1954/1961, sem afirmar independência de todos os levantamentos de base. Uma [outra instituição, ETH-Bibliothek](https://www.e-rara.ch/zut/content/titleinfo/32574892), registra a mesma obra de Soper com chamada K 368018 e DOI [10.3931/e-rara-153583](https://doi.org/10.3931/e-rara-153583), mas não foi demonstrada identidade de pixels entre as duas digitalizações; duas cópias da mesma obra **não são duas observações históricas**.

**Limites:** “Sítio” no mapa não foi identificado documentalmente com o bairro/povoado moderno Sítio do Conde. A distância gráfica entre rótulos não prova centros de 1963, datum, coordenadas de um objeto ou localização da queda. Não se sabe se a cartografia de 1914 serviu de base à carta de 1954. Escala impressa não é incerteza de georreferenciamento e o mapa de 1914 **não ativa restrições orbitais**.

**Replay:** `python3 -m tools.cgeo36_soper1914` verifica o contrato offline. Com `--pdf arquivo.pdf --thumb arquivo.jpg`, verifica-se SHA256 **dos bytes reais** e assinaturas dos arquivos. A workflow própria faz download das duas URLs institucionais/públicas no CI, confere HEAD da PR e roda testes adversariais. Nenhuma imagem é incorporada ao Git. Para restringir o centro urbano do relato de 1963, ainda é necessária uma ponte histórica com época, controle e erro demonstrados.

---
type: Guide
title: 'CGEO-35: Conde e Vila Velha no raster JP2 original'
description: 'Inspeção de pixels do JP2 UWM autenticado; topônimos e símbolo em coordenadas de imagem, sem atribuição geodésica.'
---

# CGEO-35 | Inspeção visual do raster original

Em 13/11/2026 decodifiquei **o JP2 original já autenticado em CGEO-34**, com SHA256 `6637246d2a68a2e7024e07829caa35a8af0a707905e6c606109f1da52ae808b3`, na resolução de redução JPEG2000 1 (4802 × 3892 pixels, metade em cada eixo). Isso é **a primeira leitura raster da cópia digital integral**, não outra fonte histórica nem prova de ter analisado cada pixel da folha.

Na região de imagem original `x=4250..4999, y=5200..5669`, coordenadas *de pixel*, estão visíveis separadamente **CONDE** (ao lado de símbolo de localidade, via e meandro de rio), **Vila Velha** e a inscrição do **Itapicuru**. O marcador circular de CONDE foi estimado visualmente próximo de `(4465, 5413)` com tolerância conservadora de 20 pixels **na imagem, não em metros**. Esses pixels não têm datum, CRS, precisão cartográfica ou época geodésica demonstrados; não são coordenadas terrestres. O nome Vila Velha não identifica automaticamente a Vila do Conde descrita em outras fontes.

O recorte RGB de 375 × 235 pixels, derivado *dentro do decodificador* de sua ROI original, tem SHA256 bruto `a42b07caee45dd378a319de770d5d4dcf5a386b279874d64812710daf8329243` com Pillow 13.0.0. Nenhum JPG ou PNG do mapa foi republicado no repositório; os direitos de redistribuição de reproduções de alta resolução não foram estabelecidos. A auditoria binária completa do JP2 está na CGEO-34.

**Falsificabilidade:** `python3 -m tools.cgeo35_uwm_raster` valida o contrato offline; `python3 -m tools.cgeo35_uwm_raster --original arquivo.jp2` exige SHA256 integral do JP2, decodifica pixels com Pillow 13.0.0 e compara o recorte RGB. A workflow `geo-uwm-jp2-original.yml` reutiliza **o mesmo download de 110 MB** para as verificações CGEO-34 e CGEO-35, evitando segunda transferência. Alterações de ROIs, hashes ou falsos pontos geográficos devem fazer os testes falharem.

**Limites:** o mapa é 1:500.000, com selo de 1954 e nota de atualização viária em 1961. Ele mostra localizações qualitativas e grafia cartográfica, mas não onde o objeto teria caído, nem qual era o “centro da cidade” no relato de 1963. Não foi construída transformação de pixel para mundo, não há limites municipais em 1963, e nenhuma restrição orbital foi acionada. Próxima ponte: cruzar os rótulos com fotos IBGE 1958 e aerofotografias datadas, com pontos de controle, data de captura e incertezas calibradas.

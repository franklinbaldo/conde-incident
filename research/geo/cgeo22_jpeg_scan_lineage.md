---
type: Guide
title: "CGEO-22: mesmo JPEG comprimido nas galerias de 2012 e 2014 da Vila do Conde"
description: "Replay de bytes reais com identidade exata dos dados codificados, EXIF distinto e nenhuma autenticação da data de exposição ou da posição em 1963"
---

# CGEO-22: uma imagem, duas publicações

Este laudo **supera a pendência de identidade** que o CGEO-19 ainda registrava como hipótese, sem modificar retroativamente o estado de sua auditoria.

A [publicação Blogger de 10 de dezembro de 2012](https://geografiadetalhada.blogspot.com/2012/12/fotos-da-villa-do-conde-em-conde-ba.html) rotula uma fotografia da Vila do Conde como **1959** (CGEO-19). A [galeria WordPress publicada em 13 de março de 2014](https://condebahia.wordpress.com/historia/) inclui um JPEG homônimo (CGEO-14). Em 13/11/2026, ambos os **arquivos reais** foram adquiridos e seus SHA256 integrais corresponderam aos contratos anteriores.

O achado é mais forte que uma comparação de nomes: ambos contêm imagem JPEG baseline de **1600 × 1163 pixels**, marcadores/tabelas de codificação não EXIF idênticos e **316.379 bytes exatamente iguais de fluxo comprimido**, SHA256 **c8f9c79af818e9dbcc0114b01594f7d28695ba8a5029665b4d9c804c5ae76cf4**. Os arquivos completos diferem somente na estrutura EXIF APP1 observada, de **106 bytes** no Blogger e **4.544 bytes** no WordPress, este último com miniatura EXIF. Os EXIF inspecionados não têm orientação, data original de exposição nem campo GPS. Duas publicações **reutilizam a mesma imagem codificada**: não são duas capturas independentes.

Isso não determina o sentido da cópia, o fotógrafo, a propriedade do negativo nem **se a foto foi tirada em 1959**. A data é uma atribuição editorial de 2012. Tampouco estabelece que a Vila corresponda ao **Centro** da frase inglesa do FBIS/Tupi em novembro de 1963: CGEO-20 documenta a distinção apenas em 2020. Nenhuma posição de impacto, câmera, CRS ou margem de erro foi deduzida.

## Verificação reprodutível

O verificador usa somente a biblioteca padrão de Python e percorre os marcadores JPEG, sem decodificar ou re-hospedar imagens. A execução offline verifica o contrato, **não** os arquivos externos. Para repetir a prova, baixar os dois URLs diretos do [manifesto](cgeo22_jpeg_scan_lineage.json) para arquivos temporários, depois executar os comandos seguintes.

    python3 -m tools.cgeo22_jpeg_lineage
    python3 -m tools.cgeo22_jpeg_lineage --blogger-jpeg /tmp/blogger.jpg --wordpress-jpeg /tmp/wordpress.jpg
    python3 -m unittest tests.test_cgeo22_jpeg_lineage -v

A verificação com os arquivos exige SHA256 e tamanho exatos antes de comparar o scan. Uma versão com outros bytes não pode ser aceita silenciosamente. O script rejeita JPEG de múltiplas varreduras, metadados de orientação diferentes, alterações de cabeçalho e bits adulterados. Resultados de testes gerados artificialmente servem **somente para testar o parser**, não são fonte científica de Conde.

As duas outras possíveis correspondências CGEO-19 versus miniaturas WordPress de **320 × 233 px** continuam **não testadas**, pois comparação de scans exige o mesmo tamanho/codificação. Será necessário método tolerante ao redimensionamento e validação da proveniência. Não foram republicados JPEGs de terceiros por ausência de licença.

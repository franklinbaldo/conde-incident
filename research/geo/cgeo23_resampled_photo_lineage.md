---
type: Guide
title: "CGEO-23: duas miniaturas de 2014 reutilizam fotos atribuídas a 1959 em 2012"
description: "Comparação real de 6 JPEGs, com reamostragem, controles negativos, cadeia de custódia e veto a inferências sobre 1963"
---

# CGEO-23: duas fotos, duas reproduções menores

As miniaturas 320 × 233 publicadas na [galeria WordPress de março/2014](https://condebahia.wordpress.com/historia/) foram verificadas contra as quatro imagens 1600 px da [postagem Blogger de dezembro/2012](https://geografiadetalhada.blogspot.com/2012/12/fotos-da-villa-do-conde-em-conde-ba.html). Os **seis JPEGs reais**, não versões criadas em teste, foram recuperados; comprimentos e hashes SHA256 concordam com os contratos CGEO-14/19.

**Resultado:** WordPress `villa-velha-2-001.jpg` reproduz, por redução e recodificação, a imagem Blogger legendada *Igreja Nossa Senhora do Monte, 1959*; WordPress `villa-velha-3-001.jpg` reproduz a imagem Blogger *Alto da Vila do Conde, 1959*. Ao redimensionar os Blogger originais com Pillow 13.0.0 LANCZOS, os erros absolutos médios RGB são **1,554** e **2,838** em 255; correlações Pearson em escala de cinza **0,998983** e **0,998557**. Os seis controles cruzados não correspondentes têm erro médio > 40 e correlação < 0,7; a passarela explicitamente atribuída a 2012 foi incluída como controle, não como vista de 1959.

É forte evidência de **republicação/redução dos mesmos quadros fotográficos**, e **não** de novos registros independentes de Conde. Ao contrário de CGEO-22, os fluxos JPEG das miniaturas são recodificados e **não** podem ser chamados idênticos bit a bit. O ano 1959 foi atribuído editorialmente em 2012, não autenticado em negativo datado ou ficha original; não conhecemos fotógrafo, direção da cópia, nem licença de redistribuição. Não publicamos os arquivos de terceiros no Git.

## Replay e limites

`python3 -m tools.cgeo23_resampled_photos` verifica o contrato e suas referências originais, mas **não lê JPEGs**. Para repetir o teste efetivo: baixe os quatro URLs `sources.blogger` para `img1.jpg` a `img4.jpg` no diretório `blogger-dir` (na ordem vila, passarela, alto, igreja) e os dois URLs `sources.wordpress` para `wp2.jpg` e `wp3.jpg`. Instale **Pillow==13.0.0**, sem substituir arquivos cujos SHA256 diferirem. Então execute:

    python3 -m tools.cgeo23_resampled_photos --blogger-dir /tmp/blogger --wp2 /tmp/wp2.jpg --wp3 /tmp/wp3.jpg
    python3 -m unittest tests.test_cgeo23_resampled_photos -v

O verificador primeiro compara os **hashes integrais** com os pais CGEO-14/19, depois mede todas as 8 combinações (2 miniaturas × 4 fotos) e exige pontuações correspondentes às registradas com tolerância pequena. Testes offline impedem promoção da data ou ponto de queda. O CI offline **não substitui** o replay com os seis arquivos reais, executado nesta auditoria; disponibilidade futura e termos de uso dos servidores externos são independentes.

A relação **Centro** versus **Vila do Conde** documentada para 2020 em CGEO-20 não pode ser transferida automaticamente a 1963. Nenhum ponto, polígono, coordenada de câmera, CRS, incerteza de localização ou restrição orbital nova foi deduzido. Próxima prioridade documental: mapa urbano ou aerofoto autenticada de 1950–1963 e origem física das fotografias atribuídas a 1959.

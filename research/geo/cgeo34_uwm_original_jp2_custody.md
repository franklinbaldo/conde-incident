---
type: Guide
title: 'CGEO-34: fac-símile JP2 integral da carta Aracaju-SE'
description: 'Aquisição binária original do item UWM 10814, com SHA256 e leitura estrita do contêiner JPEG 2000.'
---

# CGEO-34 | Cópia digital integral, sem nova independência histórica

Em **13/11/2026** foi adquirida, por download público institucional, a reprodução JP2 integral da [carta Aracaju-SE do acervo UWM/AGSL, item 10814](https://collections.lib.uwm.edu/digital/collection/agdm/id/10814/), usando o [endpoint da instituição](https://collections.lib.uwm.edu/digital/api/collection/agdm/id/10814/download). O retorno identificado foi `image/jp2`, com **110.453.331 bytes**, SHA256 `6637246d2a68a2e7024e07829caa35a8af0a707905e6c606109f1da52ae808b3`. Trata-se do **arquivo digital original oferecido pelo acervo**, não do original material do levantamento cartográfico. O arquivo integral permanece fora do Git; o repositório guarda o cabeçalho real de 103 bytes, seu hash e um verificador de replay integral.

O contêiner JP2 foi analisado sem decodificar uma imagem grande em memória: cinco caixas `jP  `, `ftyp`, `jp2h`, `xml ` e `jp2c`, com dimensões intrínsecas **9.603 × 7.783**, três componentes, oito bits por componente. Essas dimensões coincidem com o `info.json` IIIF já custodiado em CGEO-08. A inspeção visual integral **não** foi feita nesta rodada. A derivação em JPEG consultada anteriormente mostrou o topônimo CONDE, mas pertence ao mesmo mapa, **não** é um novo testemunho independente.


**Metadados embutidos do JP2:** o bloco XML de 1.660 bytes, SHA256 `34324b6e4d426531c0796aa8a28d52dde53b01b7a2840bd3e9af334f50c6200d`, tem `ChangeHistory/date=2017-06-23`, isto é, **histórico de processamento do objeto digital**, não ano do levantamento nem edição da carta. Seu campo `bitsperpixel=1953391977` é inconsistente com o cabeçalho JP2 `ihdr` que registra três canais de **8 bits** cada. O dado XML incorreto não foi usado como parâmetro espacial nem como profundidade de pixel. O caminho local de processamento identificado no XML não foi reproduzido no contrato.

O mapa apresenta o selo editorial **dezembro de 1954** e nota de **atualização das vias de comunicação em 1961**, segundo a leitura visual anterior de CGEO-08. Nem isso autentica a edição completa em 1961, nem produz limites municipais ou geodésia de 1963. A escala **1:500.000** é inadequada para identificar uma praça ou o ponto da alegada queda sem outras fontes e calibração. Os campos de centro urbano histórico, geometria jurídica, posição de reentrada, datum e erro permanecem `null`, e `can_constrain_orbital_reentry` é `false`.

**Reprodução:** `python3 -m tools.cgeo34_uwm_jp2` verifica manifesto, cabeçalho autêntico e dependência CGEO-08. `python3 -m tools.cgeo34_uwm_jp2 --original arquivo.jp2` valida os 110 MB em streaming por SHA256 e estrutura JP2. A workflow dedicada baixa a cópia **real** diretamente do acervo, roda o replay integral e testes adversariais no SHA da PR, sem sintetizar fonte histórica. Falha na conexão deve falhar explicitamente, não produzir PASS vazio. A próxima etapa científica é georreferenciar marcos com datum e incerteza demonstrados, ou recuperar fotoíndices originais com data e footprint; este mapa sozinho não localiza o evento.

---
type: Guide
title: "CGEO-19: três fotografias atribuídas a 1959 e uma imagem de 2012"
description: "Custódia de quatro JPEGs reais encontrados em publicação local de 2012, com atribuição editorial de 1959, sem inventar época, autor ou local da câmera"
---

# CGEO-19 — Imagens possivelmente próximas de 1963, sem datação autenticada

**Descoberta nova:** a página [*Fotos da Villa do Conde em Conde-BA. 1959–2012*](https://geografiadetalhada.blogspot.com/2012/12/fotos-da-villa-do-conde-em-conde-ba.html), publicada em **10 de dezembro de 2012 às 16h15 (UTC−03)**, atribui **1959** a três fotografias da Vila do Conde (Bahia): uma visão geral, o Alto da Vila e a igreja de Nossa Senhora do Monte. Entre elas, a mesma página apresenta uma quarta fotografia, da passarela ao pôr do sol, explicitamente atribuída a **novembro de 2012**.

Isso é uma **afirmação editorial de data**, publicada 53 anos depois do ano alegado. Ainda não foi recuperada a impressão, negativo, álbum ou catálogo original que prove tomada em 1959. A identidade do fotógrafo original e as coordenadas das quatro câmeras continuam desconhecidas. A página não é uma fotografia da suposta ocorrência de 1963.

## Os quatro arquivos realmente adquiridos em 13/11/2026

| Ordem no HTML | Legenda contextual publicada | Ano **alegado** | Bytes JPEG | SHA256 (prefixo) |
| --- | --- | ---: | ---: | --- |
| 1 | Vila do Conde | 1959 | 316.900 | `b0c17c9bae3a4397` |
| 2 | Passarela ao pôr do sol | novembro de 2012 | 215.602 | `68f669f9e3989669` |
| 3 | Alto da Vila do Conde | 1959 | 235.387 | `01263381c8108b6a` |
| 4 | Igreja de Nossa Senhora do Monte, Vila do Conde | 1959 | 237.049 | `071e3b27fa599bee` |

As URLs completas, tamanhos, SHA256 e dimensões dos quatro JPEGs estão fixados no [contrato CGEO-19](cgeo19_1959_editorial_photographs.json). O HTML original da consulta retornou **103.798 bytes**, SHA256 `dbe5afead3991dfce8c5f1260a596979b46e897776e86b3eeedf295364aebf1f`; esse hash caracteriza a cópia HTML recuperada, **não** uma edição de 1959. Os JPEGs trazem metadado EXIF de software **Google**, não prova de data original da tomada. **Não foram republicados no repositório**, pois a licença não foi identificada.

Há uma possível ligação com [CGEO-14](../geo/README.md): a primeira imagem chama-se `vila velha 001.jpg`, mesmo nome do JPEG publicado no WordPress *Conde, Brasil* em 2014. A cópia WordPress baixada tem **321.338 bytes** e SHA256 `233264fed3b4475e6ea3aae5efea521f56fe9a1fc8ee6d9c0c602787653ef154`, diferente dos bytes Blogger. **Diferença de bytes não prova imagens distintas**, pois pode decorrer de recodificação ou redimensionamento. Também não prova identidade fotográfica. Fica como relação candidata de republicação, sem contar testemunha independente.

## Relação com as outras fontes

- **CGEO-17 / IBGE 1958:** imagens do álbum oficial documentam Praça Severiano Lima, Senhor do Bonfim, Rua do Carro e Rua Marechal Floriano. A legenda de Nossa Senhora do Monte no blog não autoriza identificar esse templo com a igreja do Senhor do Bonfim nem com a Praça Severiano Lima.
- **CGEO-18 / FBIS–Tupi:** a expressão inglesa *center of the city* pertence a relato retransmitido. Nenhuma das fotografias mostra evento físico identificado, local de impacto ou centro de 1963 georreferenciado.
- **Independência:** os quatro links pertencem **a uma única publicação editorial** de 2012. Nem a repetição da foto em 2014, se vier a ser demonstrada, criará automaticamente outro observador de 1959.

O exportador mantém `historical_center_point=null`, `historical_center_polygon=null`, posições das câmeras e datação independente desconhecidas, `can_constrain_orbital_reentry=false`. Não há longitude, latitude, perímetro, raio de incerteza, ponto de reentrada ou estimativa de probabilidade.

## Reprodução e próximo teste discriminante

`python3 -m tools.cgeo19_1959_photos` valida as afirmações e os hashes no manifesto, **offline**. `python3 -m unittest tests.test_cgeo19_1959_photos -v` executa testes adversariais. Para repetir a aquisição real, baixar cada uma das quatro URLs do JSON no diretório apropriado como `img1.jpg` a `img4.jpg` e usar `--jpeg-dir DIR`. Para conferir a mesma cópia HTML usada nesta rodada, `--html ARQUIVO`. Página HTML dinâmica pode mudar sem invalidar a publicação.

**Prioridades:** (1) localizar negativos/impressões originais com data e autoria, (2) comparar os pixels da primeira imagem com a republicação de 2014, (3) procurar planta histórica da sede com igrejas, cruzamento de vias e praça oficialmente nomeada. Só depois de prova de continuidade arquitetônica e controles cartográficos independentes é admissível aproximar posição de câmera. E isso ainda não localizaria a suposta queda.

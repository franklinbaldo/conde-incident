---
type: ResearchNote
title: "CGEO-14: imagens da Vila do Conde e a incerteza de centro urbano em 1963"
description: "Inventário verificável de três JPEGs de uma galeria local, sem datar a tomada ou situar a reentrada."
---

# CGEO-14: imagens da Vila do Conde, sem atribuir-lhes a data de 1963

A [página *História*, do blog local Conde, Brasil](https://condebahia.wordpress.com/historia/) (metadado HTML `article:published_time=2014-03-13T04:39:48+00:00`; `modified_time=2016-11-02T01:20:39+00:00`) mostra **três fotografias** identificadas internamente como `vila velha 001`, `villa velha 2 001` e `villa velha 3 001`. São imagens úteis da paisagem **atribuída pela página à Vila do Conde**, mas **não foi recuperada a data de tomada, autor original, negativos, documentação de localização nem licença explícita de reutilização**. A data de 2014 é do *post*, não da fotografia. Aspecto monocromático/antigo não é relógio e não prova 1963.

## Aquisição de bytes, 12/11/2026

| ID | Arquivo exato no blog | Bytes | SHA256 | Dimensão |
| --- | --- | ---: | --- | --- |
| CGEO14-IMAGE-01 | `2014/03/vila-velha-001.jpg` | 321338 | `233264fed3b4475e6ea3aae5efea521f56fe9a1fc8ee6d9c0c602787653ef154` | 1600×1163 |
| CGEO14-IMAGE-02 | `2014/03/villa-velha-2-001.jpg` | 17877 | `3f8a427524b6b4b6abfedf0473d054891608ac2e1e4a2905fec881caabd992a0` | 320×233 |
| CGEO14-IMAGE-03 | `2014/03/villa-velha-3-001.jpg` | 27755 | `468fd60bf0805e1b1dedc8be6e1a4fc9181b74225bc57650c454e31e2c6d46c3` | 320×233 |

O HTML foi adquirido diretamente e preserva o SHA256 de aquisição `3b3b55beb6db73a3d8db18e5fdc4e5c6ba48fd88907601df98951e9854fc54ca`; conteúdo dinâmico pode mudar. Os JPEGs **não são incorporados ao repositório** por ausência de licença conferida. URLs completas constam do JSON, junto de suas identidades e tamanhos. A prova de integridade por hashes de arquivos adquiridos é separada da demonstração de autenticidade histórica, que continua pendente.

## Significado espacial, limites e próximo teste

O [histórico municipal do IBGE, CGEO-03](https://www.ibge.gov.br/biblioteca/visualizacao/dtb/bahia/conde.pdf) vincula a sede administrativa reconstituída em 1935 ao antigo distrito de Conde; a página comunitária descreve a Vila do Conde como região antiga e menciona o Alto do Cruzeiro. Esses textos **não identificam em coordenadas o significado de “centro da cidade” em 08/11/1963**. A eventual frase jornalística original “no centro da cidade” ainda não foi conferida aqui contra fac-símile e página, portanto não foi convertida em ponto. Vila histórica, sede urbana e Sítio do Conde não são intercambiáveis por presunção.

A [ficha de mapa IBGE/SPU de 1985, CGEO-13](cgeo13_spu_mme_1985_catalogue.md) é outra época e só servirá a georreferenciamento *se* o PDF integral, o datum, os marcos de controle, a precisão e a cadeia temporal forem verificados. As três imagens da **mesma galeria** representam **uma linhagem de publicação** e não três testemunhos independentes de 1963. Não há foto orbital pública Landsat de 1963: o programa iniciou em julho de 1972, mas essa limitação não exclui aerofotogrametria histórica.

**Contrato ao Castor:** `python3 -m tools.cgeo14_vila_visual` retorna `historical_center_geometry=null`, `point_of_reentry=null`, `can_constrain_orbital_reentry=false`. Para conferir os JPEGs novamente após adquiri-los separadamente, use `python3 -m tools.cgeo14_vila_visual --verify-dir /pasta/originais` (exige os três arquivos originais com nomes exatos). Os testes não dependem da rede e reprovam mutações que inventem data de captura, datum, ponto, independência ou permissão de republicação.

**Próxima investigação discriminante:** recuperar foto aérea ou planta urbana institucional anterior a 1963 e validar sua cobertura da Vila e da sede; buscar créditos e datas de negativos das fotografias, sem contatar arquivos ou pessoas sem autorização. Nenhuma fotografia é atribuída ao incidente; nenhum impacto ou reentrada é localizado.

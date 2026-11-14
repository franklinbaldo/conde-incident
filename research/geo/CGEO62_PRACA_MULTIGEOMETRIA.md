---
type: Evidence
title: "CGEO-62: quatro geometrias OSM com o nome Praça Severino Vieira, Conde/BA"
description: "Duas áreas ajardinadas e duas vias compartilham um topônimo moderno; polígonos não são Centro de 1963."
---

# CGEO-62 | Um nome de praça não é uma coordenada

Em 14/11/2026 foram adquiridos por HTTP 200 os **XML originais e completos da API OpenStreetMap 0.6** para quatro *ways* chamados literalmente **Praça Severino Vieira**, em Conde/BA. O [contrato](cgeo62_praca_severino_vieira.json) fixa IDs, URLs, revisões, bytes e SHA-256 de cada resposta. Os quatro [XMLs preservados](sources/) estão versionados; o replay offline não usa uma fonte simulada.

| ID OSM | Classe literal | Revisão OSM | Nós | Área planar aproximada |
|---|---|---|---:|---:|
| [1571425857](https://www.openstreetmap.org/way/1571425857) | `leisure=park` | 24/10/2026 (v1) | 28 | 1.039,090 m² |
| [1020642398](https://www.openstreetmap.org/way/1020642398) | `leisure=park` | 12/01/2022 (v1) | 11 | 2.423,692 m² |
| [206041518](https://www.openstreetmap.org/way/206041518) | `highway=tertiary` | 24/10/2026 (v4) | 7 | Não aplicável |
| [1571425854](https://www.openstreetmap.org/way/1571425854) | `highway=tertiary` | 24/10/2026 (v1) | 3 | Não aplicável |

Os dois parques são polígonos fechados distintos na base OSM, separados por aproximadamente **61,795 m entre contornos** e **138,611 m entre centroides planimétricos**. A área e a lacuna foram calculadas numa projeção equiretangular local (latitude de referência −11,813°, raio esférico 6.371 km) e **não são mensurações oficiais, precisão posicional, área jurídica nem demonstração de que existem duas praças físicas independentes**. Podem ser setores do mesmo logradouro. As duas ruas nomeadas mostram que geocodificar o nome sem tipo ou identificador retorna objetos geográficos de classes diferentes.

Centroides técnicos atuais das áreas OSM, em latitude/longitude: **(−11,812374018; −37,611393292)** e **(−11,813528322; −37,611874115)**. As versões do OSM indicam **quando o mapeamento foi editado**, não quando as áreas foram medidas ou construídas. Não se atribuiu erro horizontal em metros aos objetos.

## Ponte documental que ainda falta

O [CGEO-20](cgeo20_centro_vila_2020.md) confirma que um processo da Prefeitura de 2020 nomeava **Praça Severino Vieira (Centro)** e, separadamente, **Praça Vila do Conde (Vila)**. Isso sustenta uma associação **nominal contemporânea candidata**, não a identidade da geometria OSM com o documento municipal. O [CGEO-17](cgeo17_1958_urban_toponym_crosswalk.json) mencionou **Praça Severiano Lima** na fotografia IBGE de 1958; a semelhança nominal **não** prova equivalência a Severino Vieira.

Como controle, os centroides OSM podem ser comparados aos proxies atuais de [CGEO-60](cgeo60_modern_osm_cut.json) e [CGEO-61](cgeo61_conder_sede_point.json). Nenhum desses três produtos estabelece onde ficava o **centro da cidade** mencionado no relato FBIS sobre novembro de 1963. No contrato: `plaza_polygon_in_1963=null`, `impact_location=null`, `active_constraint=false`.

**Reprodução:** `python3 tools/cgeo62_praca_multigeometry.py`, seguido por `python3 -m unittest discover -s tests -p 'test_cgeo62_praca_multigeometry.py' -v` e a execução equivalente sob `python3 -O`. `--live` compara novas respostas HTTP com os hashes arquivados, distinguindo alteração legítima posterior do OSM de corrupção do acervo local. Não é necessário ativar `--live` para a prova offline.

**Próxima fonte discriminante:** planta municipal de 1950–1963 que conecte a Praça Severiano Lima ao traçado e à Praça Severino Vieira, ou documento de renomeação e localização com data e custódia. Até lá não usar nenhum dos quatro *ways* como restrição orbital.


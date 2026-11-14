---
type: Evidence
title: 'CGEO-61: ponto oficial CONDER da sede moderna de Conde e divergência do nó OSM'
description: 'Duas vistas de um mesmo ponto da sede municipal, com 752 m de deslocamento contra o nó OSM; sem ponte para 1963.'
---

# CGEO-61 | Sede municipal contemporânea: um ponto diferente, não um centro histórico

Em **14/11/2026**, consultei por HTTP 200 duas camadas do servidor oficial da [CONDER/BA](https://mapas.conder.ba.gov.br/arcgis/rest/services/BAHIA): [SEDES_MUNICIPAIS_PTO](https://mapas.conder.ba.gov.br/arcgis/rest/services/BAHIA/SEDES_MUNICIPAIS_PTO/MapServer/0) e [LOCALIDADES](https://mapas.conder.ba.gov.br/arcgis/rest/services/BAHIA/LOCALIDADES/MapServer/0). As duas consultas ArcGIS REST, preservadas por URL, tamanho e SHA-256 em [manifesto CGEO-61](cgeo61_conder_sede_point.json), identificam **Conde/BA, código municipal IBGE 2908606**, como cidade/sede urbana em WGS 84 (WKID 4326), com ponto moderno **latitude −11,813431761°, longitude −37,606977982°**.

| Vista | Chave consultada | Identificador resultante | Cópia adquirida |
|---|---|---|---|
| CONDER Sedes Municipais (ponto) | `MUNICIPIO='CONDE'` | `OBJECTID=1038`, `CODIGO=290860605000001` | 232 bytes; SHA-256 `dbb93fe280700e3931a30fcef07414030a2eedf5a00b9629ed6496104c2fb7d3` |
| CONDER Localidades (ponto) | `COD_MUNICIPIO='2908606'` | mesmo `OBJECTID`, mesmo código, mesmas coordenadas | 489 bytes; SHA-256 `6d2cbd335863ca5525824312fed51c52c4361a2efcd1d3c5e28a202552c6d708` |

**As duas camadas não são duas medições independentes.** O número de objeto, o código e as coordenadas coincidem exatamente; provavelmente são duas apresentações de um mesmo registro, mas não há documentação de linhagem detalhada que permita afirmá-lo com certeza. Também não constam nos registros consultados época do levantamento, exatidão planimétrica ou licença específica do serviço; estes campos ficam nulos/não verificados.

## Comparação controlada com CGEO-60

O [nó OSM de Conde](cgeo60_modern_osm_cut.json) (`place=town`, id 415521889, versão 18 de 18/09/2026) está em **−11,8129758°, −37,6138705°**. O registro CONDER encontra-se a **751,891919 m** de distância de grande círculo no modelo esférico de raio 6.371.000 m, na direção inicial aproximada de **93,86713°** a partir do nó OSM (leste, ligeiramente sul). A diferença mede somente a escolha de **dois pontos digitais de referência contemporâneos**, não sua acurácia, a extensão urbana ou o deslocamento temporal do Centro.

O achado traz uma contraprova para tratar um `place=town` OSM como localização única da sede. Com a fonte administrativa CONDER, há mais uma alternativa de origem distinta para **testes contrafactuais de sensibilidade** do [Castor #870](https://github.com/franklinbaldo/conde-incident/issues/870). A análise orbital só pode usar o rótulo `CONDER_PRESENT_DAY_SEAT_PROXY_ONLY`, sem confundir este registro com `CENTRO20`, `VILA20` ou a localização da queda.

**Não é possível demonstrar, com esses serviços, o Centro em novembro de 1963.** Nem o cadastro OSM nem a CONDER declaram uma época observacional histórica. O relato traduzido do FBIS permanece com local desconhecido. Não há nova restrição orbital, posterior de impacto ou redução de domínio científico. Para uma ponte temporal aceitável, ainda precisamos de planta/carta contemporânea, ponto de controle reconhecível, época e erro de georreferenciamento demonstrados.

**Verificação:** `python3 tools/cgeo61_conder_sede_point.py` valida o contrato, o OSM ancestral e a distância; `--live` readquire as duas respostas oficiais, valida identificação, geometria e classes e informa hashes atuais. Alterações apenas na serialização podem produzir `binary_match=false` sem alterar o conteúdo semântico; mutações em coordenadas, códigos e classe são rejeitadas. Testes de mutações: `python3 -m unittest discover -s tests -p 'test_cgeo61_conder_sede_point.py' -v` e repetição sob `python3 -O`. Publicar somente por PR com todos os gates obrigatórios aprovados no HEAD exato.

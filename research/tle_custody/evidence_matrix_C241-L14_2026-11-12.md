---
type: Guide
title: "C241-L14: satcat completo e ambiguidade Agena B/D nos objetos 527-529"
description: "Confronto auditável entre tabelas GCAT, sem promover taxonomia ou datas catalogadas a medição orbital."
---

# C241-L14: um nome de fragmento não é sua ficha de engenharia

**Issue #13; continuação C241-L13; 12/11/2026 local, 13/11 UTC.** Inspeção documental de catálogo *moderno* GCAT, não recuperação de dados instrumentais de 1963. As tabelas [currentcat](https://planet4589.org/space/gcat/data/derived/currentcat.html) e [satcat](https://planet4589.org/space/gcat/data/cat/satcat.html) são publicadas pelo mesmo compilador GCAT, **não fontes físicas independentes**.

## Encontrado

O índice GCAT relaciona `S00527 = 1963-003A` ao **OPS 0180**, com vínculo `A00324 / Agena B 2313` (o arquivo auxiliar já foi auditado em [C241-L13](evidence_matrix_C241-L13_2026-11-12.md)). Para `S00528 = 1963-003B` e `S00529 = 1963-003C`, as tabelas GCAT usam o rótulo genérico **`deb USAF satellite/Agena D`** e vínculo com **S00527**.

**Divergência de nomenclatura B/D:** o pai catalogado é `Agena B 2313`, mas os fragmentos são chamados `.../Agena D`. Pode ser generalização, erro taxonômico ou informação não explicada: sem número de peça, serial, tipo de mecanismo ou documentação técnica, **nenhuma dessas alternativas foi confirmada**. A classe de componente/debris não estabelece composição, massa ou causalidade. Os campos vazios/zero de massa nos catálogos não são medidas físicas nulas.

O `currentcat` repete para 528 a data **8 Nov 1963**; a data civil é compatível com o [boletim NASA de 15/11/1963, NTRS 19640001198](https://ntrs.nasa.gov/citations/19640001198), mas pode derivar da mesma linhagem de catalogação. **Não significa observação às 00:00, última passagem, hora de reentrada, longitude ou impacto.** O boletim contemporâneo NASA de 15/10/1963 [NTRS 19640000428](https://ntrs.nasa.gov/citations/19640000428) lista 1963 3A/B/C sem descrever as peças; ver C241-L12.

## Auditoria reproduzível e incertezas

O [ledger](gcat_full_catalog_lineage_C241-L14.json) separa fonte coeva, catálogos compilados e desconhecidos. [Script](../../tools/tle_gcat_cross_catalog_audit.py) exige exatamente uma linha por NORAD/COSPAR em cada catálogo, cruza pai/classificação/nome e registra **SHA-256, tamanho e linhas completas efetivamente baixadas**. [Testes](../../tests/test_tle_gcat_cross_catalog_audit.py) adversariais usam entradas **sintéticas**, nunca apresentadas como fontes históricas. O workflow do HEAD arquiva o relatório JSON. As páginas GCAT são **mutáveis**, portanto o arquivo de captura do CI, e não a URL abstrata, define qual texto foi testado.

```sh
python3 -m unittest discover -s tests -p 'test_tle_gcat_cross_catalog_audit.py' -v
curl -fLsS https://planet4589.org/space/gcat/data/derived/currentcat.html -o /tmp/currentcat.html
curl -fLsS https://planet4589.org/space/gcat/data/cat/satcat.html -o /tmp/satcat.html
python3 tools/tle_gcat_cross_catalog_audit.py --currentcat /tmp/currentcat.html --satcat /tmp/satcat.html --output /tmp/c241-l14.json
```

**Estado do grafo:** C241-L13 → C241-L14 com os dois formatos GCAT como *uma única família de compilação*, independência instrumental **NOT_ESTABLISHED**, restrição Lean física **NOT_PROMOTED**. TLEs originais, checksums históricos, frame, erros, sensor, identidade material e datas de passagem **NOT_RECOVERED**. RAAN legado 284,1520° continua inativo e 198,5261° apenas secundário. Nenhuma janela/posição terminal demonstrada. **Conde INDETERMINATE**.

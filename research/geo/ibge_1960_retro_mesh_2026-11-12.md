---
type: Guide
title: "CGEO-10: malha municipal de 1960 reconstruída pelo IBGE, Conde BA"
description: "Inventário verificável de shapefile oficial publicado em retrospectiva, sem atribuir limite jurídico de 1963"
---

# CGEO-10: malha municipal rotulada 1960, não um levantamento de 1960

Data de auditoria: 12/11/2026. Município: Conde/BA, código IBGE 2908606. Este registro documental complementa CGEO-01 a CGEO-09, sem alterar a matriz C001–C238 nem os estados orbitais.

## Fonte primária digital e custódia

- Produto institucional: [IBGE, Evolução da Divisão Territorial do Brasil 1872–2010](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/15771-memoria-institucional.html), disponibilizado em 2011.
- [Pasta pública de 1960](https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/evolucao_da_divisao_territorial_do_brasil_1872_2010/municipios_1872_1991/divisao_territorial_1872_1991/1960/) e [ZIP oficial](https://geoftp.ibge.gov.br/organizacao_do_territorio/estrutura_territorial/evolucao_da_divisao_territorial_do_brasil/evolucao_da_divisao_territorial_do_brasil_1872_2010/municipios_1872_1991/divisao_territorial_1872_1991/1960/05_malha_municipal_1960.zip).
- Download completo HTTP 200: **2.222.445 bytes**, SHA-256 **261399b8557ee26c118e94b13cebf3b6b3e1c70e91b5e8438a348847b875120f**. ZIP com sete componentes SHP/SHX/DBF/PRJ/SBN/SBX/XML, listados e individualmente hashados no [manifesto JSON](ibge_conde_1960_retro_mesh_2026-11-12.json). ZIP não incorporado ao Git.
- DBF: **2.766 registros**, campos codigo e nome; **Conde** (2908606) aparece uma vez, linha 2.449 (índice zero 2.448), associada por SHX/SHP. O registro SHP de 808 bytes possui SHA-256 **6258845cd887418a078fb507dda4b462dc12b44145f929775199cc80f5681b65**. Sua cópia exata de 808 bytes, como base64, serve aos testes offline.
- SHP: polígono com **uma parte, 47 vértices incluindo fechamento**, bbox em coordenadas projetadas **em metros** [1761251.25, -1390060.375, 1795968.5, -1336775.625], jamais tratar como longitude/latitude. PRJ: World_Polyconic, GCS_SIRGAS_2000, meridiano central -54. O XML contém operações ArcGIS de 19/03 e 10/04/**2013**.
- Área plana calculada na projeção: **983,184047 km²**, apenas diagnóstico da geometria, não área municipal oficial, perímetro legal ou observação de 1963.

## Crítica de época, precisão e independência

O [FAQ oficial do IBGE](https://www.ibge.gov.br/geociencias/organizacao-do-territorio/estrutura-territorial/15771-memoria-institucional.html) adverte que **as malhas anteriores a 1991 não têm precisão cartográfica**, porque foram construídas por **união de polígonos a partir da malha de 1991**, reconstituindo emancipações. O ano 1960 é referência temporal da divisão, não a data da medição de cada vértice. Metadados de processamento de 2013 e datum SIRGAS2000 reforçam sua natureza retrospectiva. O catálogo [Stanford/UTexas](https://geodata.lib.utexas.edu/catalog/stanford-pk564cg5040) é espelho do **mesmo produto IBGE**, não um segundo levantamento independente.

**Estado: RETROSPECTIVE_COARSE_PROXY_ONLY.** Esta malha não determina a fronteira de Conde em 08/11/1963, os marcos legais daquela data, precisão horizontal, mudanças jurídicas de 1960 a 1963, lugar de queda ou reentrada. Diferenças de área frente a malhas modernas não demonstram alteração territorial.

**Grafo de dependência:** CGEO-10 → aproximação retrospectiva da divisão 1960. Para obter limite_Conde_1963, faltam atos normativos originais completos e alterações até 08/11/1963, além de georreferenciamento e incerteza de uma fonte contemporânea. Assim, limite_Conde_1963 = UNRESOLVED e orbital_constraint = NOT_ACTIVATED. Este produto complementa CGEO-05/06 (referências legais 1953/2017) sem substituir a análise legal de Caranguejo.

## Reprodução

Baixar o ZIP pela URL indicada e executar:

    python3 scripts/archives/audit_ibge_1960_conde.py /tmp/05_malha_municipal_1960.zip
    python3 -m unittest discover -s tests -p 'test_ibge_1960_retro_mesh.py' -v

Sem dependências GIS, o script valida hash do ZIP, os componentes, o código e nome únicos no DBF, o índice SHX, o registro SHP, fechamento e CRS, sem reprojeção ou liberação de um polígono de 1963. Os testes offline usam bytes originais, não geometria sintética.

**Limites negativos:** não foi localizado um levantamento cadastral de 1963 nesta fonte; não houve revisão completa das leis intermediárias ou validação de terreno; nenhum contato com instituições. A aquisição está custodiada, não sua aplicabilidade como fronteira legal.

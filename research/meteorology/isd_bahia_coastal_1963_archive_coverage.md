---
type: Guide
title: "NOAA/ISD 1963: inventário de arquivos brasileiros e lacuna costeira da Bahia"
description: "Cruza a listagem original dos arquivos anuais de 1963 com o catálogo retrospectivo de estações, quantificando cobertura arquivística sem inventar medições."
---

# Cobertura de arquivos NOAA/ISD em 1963 na costa baiana

**Auditoria executada em 13/11/2026.** Consultei integralmente duas fontes oficiais, sem completar períodos por interpolação:

- [Diretório NOAA/ISD dos arquivos anuais de 1963](https://www.ncei.noaa.gov/pub/data/noaa/1963/): HTML de 874.470 bytes, SHA-256 `93627d0e6010063fc54d6029d67499952107784f47740d895a17516e6dfb401d`. Foram reconhecidos **5.577 nomes únicos** de arquivos `USAF-WBAN-1963.gz`; SHA-256 da lista ordenada canônica `51140ef98cf946a8d885d9fb86ff4b8cefd0009708c7adae06a2e20efcf0832c`.
- [Histórico de estações NOAA/ISD](https://www.ncei.noaa.gov/pub/data/noaa/isd-history.csv): CSV de 2.914.601 bytes, SHA-256 `1994747ab4af1b97e63adb434b4d0d022f2daee76f0c144ea9ab46be2d906604`. Catálogo retrospectivo, não inventário instrumental de novembro de 1963.

O CSV apresenta **129 linhas com `CTRY=BR` e 1963 dentro dos anos extremos `BEGIN/END`**, mas somente **10 chaves `USAF-WBAN` correspondentes aparecem no diretório anual de 1963**. A classificação `BR` é literal, não garantia geográfica: a linha de *Puerto Pinasco*, WMO 860880, também usa esse código e requer verificação independente.

Para a posição de referência, reutilizei **o ponto médio da caixa municipal do IBGE 2022** usado na auditoria IGRA Bahia, `(-11.8641854035, -37.68935144749995)`. Essa referência **não** é coordenada autenticada da ocorrência de 1963. Distâncias são geodésicas esféricas aproximadas, sem margem histórica calibrada.

| Estação no catálogo | Distância aproximada | Arquivo anual ISD 1963 listado? |
| --- | ---: | --- |
| Aracaju (830960) | 126,3 km | Não |
| Aeroporto de Salvador (832480) | 135,7 km | Não |
| Salvador (832290) | 156,6 km | Não |
| Ilhéus (833480) | 358,9 km | Não |
| Caravelas (834970) | 665,2 km | **Sim** |

Caravelas é a **única chave de catálogo `BR` com arquivo em 1963 dentro de 800 km** da referência. A existência do arquivo anual de Caravelas já foi complementada com as 72 observações diretas de 7–9/11/1963 nas PRs #456, #475 e #484. **A existência de outros nove arquivos anuais não foi aqui testada para aqueles três dias.**

A ausência dos nomes próximos no *diretório anual específico* não significa que não tenha existido observação histórica, estação ou dado preservado em outro acervo. Da mesma forma, `BEGIN/END` não garante continuidade nem medições em 8/11/1963. Os campos `CTRY`, nomes e coordenadas são retrospectivos. NOAA/ISD é uma compilação, e arquivos distintos não implicam custódia instrumental independente. <https://www.ncei.noaa.gov/products/land-based-station/integrated-surface-database>

## Conexão cumulativa e próximos testes

A aresta `archive_file_presence_1963 → potential_regional_surface_control` permanece dependente de **verificação horária, identidade da estação, metadados de 1963, erro instrumental e transferência horizontal e vertical para Conde**. O resultado **não** adiciona vento, pressão ou densidade em Conde e não reduz o domínio de queda.

Próximo teste verificável: procurar arquivos diários ou documentos originais do Serviço de Meteorologia do Brasil para Aracaju/Salvador em novembro de 1963, preservando edição, página, data, escala e fonte original. Não atribuir um parâmetro `σ` sem instrumento identificado.

Reprodução: `python3 tools/audit_isd_bahia_coastal_1963_archive.py --history isd-history.csv --index 1963-index.html --check`; o workflow baixa ambas as fontes, valida os SHA-256 integrais, recomputa interseção e roda testes adversariais.

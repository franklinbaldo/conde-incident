---
type: Guide
title: C241-L14 manual NMC ON20 de 1964 não prova layout de 1963
description: Vínculo reproduzível entre captura Wayback do manual NMC 1964, auditoria de páginas, tape NCAR Y20175 e hipótese de decoder de 1963, sem inferência meteorológica inventada.
---

# C241-L14: da cópia de 1964 à pergunta sobre o registro de 1963

**Hipótese testável:** o manual NMC *Upper Air ADP Records Format*, Office Note 20 (J. Neilon, **1964**), pode descrever alguma variante histórica dos registros da fita NCAR Y20175 (**1963**). A aplicação temporal não foi comprovada. O catálogo NCEP menciona revisão a partir da página 12, e a inspeção visual posterior da Lontra (PR #300) encontrou a revisão datada **27/11/1964** nas páginas PDF 11–14, com trechos do layout 1964. **Nenhuma dessas páginas prova o layout vigente em 1963**. A fonte é uma pista para identificar formato, não a descrição validada da fita.

**Custódia (separar relógios):** [catálogo NCEP](https://www.emc.ncep.noaa.gov/officenotes/FullTOC.html) → [cópia Wayback de 19/01/2022](https://web.archive.org/web/20220119075333id_/http://www.ncep.noaa.gov/officenotes/NOAA-NPM-NCEPON-0001/013FD4DB.pdf), 932.414 bytes, SHA-256 `656984ac58ff1632e39b0f62ac80003785ddea0a0de32dfb19c8c612067aabbe`, 23 páginas identificadas por objetos PDF; página 11 e sua cópia 13 contêm a revisão de 27/11/1964. Dados adicionais do mapeamento visual estão na PR #300. A data de captura não é a data de publicação. Evidência primária da custódia: `research/meteorology/ncep_on20_wayback_custody_20261112.json` e `ncep_on20_page_audit_20261112.json` (Lontra, PR #282).

**Variável física candidata:** `wind_field_nov_1963_with_altitude_time_and_position` ligada ao arquivo [NCAR Y20175](../meteorology/nmc_y20175_1963_custody.json), 117.264.384 bytes, SHA-256 `afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4`. Nove pares estação/dia são **consultas futuras**, não observações. O contexto NOAA IGRA de Recife C151#1 pertence ao snapshot de matriz `a7978c3...` e não valida a fita nem observa Conde.

**Pipeline conectado:** catálogo bibliográfico → fac-símile preservado com hash → candidato a layout 1963 **NÃO VALIDADO** → necessidade de decodificador com prova temporal → fita Y20175 real → busca por estação/dia com offsets e QC → época/altura/coordenadas/unidades → transferência espacial para Conde e estado de reentrada. Cada seta condicional tem pré-requisito de ativação explícito em `research/constraints/nmc_y20175_pending_bridge.json` e no novo `public/data/conde-on20-layout-link.json`, **derivado do feed canônico da Abelha** `public/data/conde-archive-documentary-links.json` (PR #314), e referenciado por hash no índice científico, sem contar outro testemunho; `formal/Conde1963/NmcLayout.lean` conserva ano, cópia e lacunas como **dados tipados**, não como teorema de localização.

**Resultados e limitações:** zero perfis decodificados, zero novas observações de vento, zero cortes no domínio orbital, zero independências instrumentais inferidas. A inspeção de página confirmou texto de 1964 e a revisão de novembro/1964, **não** a sua vigência em 1963. O caminho positivo é recuperar layout coevo, identificar records com offsets na fita, confrontar velocidades/unidades com outra fonte e só então avaliar propagação física. Resultados negativos também permanecem conectados.

**Reprodução no SHA da PR:** `python3 tools/export_nmc_on20_layout_link.py --check`; `python3 formal/scripts/compile_nmc_layout_link.py --check`; `python3 tools/export_contextual_scientific_bridges.py --check-site`; `python3 -m unittest discover -s formal/tests -p test_nmc_candidate.py -v`; CI Lean 4.35 + auditoria de axiomas e prek no HEAD exato.

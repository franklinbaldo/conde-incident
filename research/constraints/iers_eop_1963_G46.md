---
type: Guide
title: "CASTOR-G46: orientação terrestre IERS em novembro de 1963"
description: "Custódia e triagem de x/y polar, UT1-UTC e erros formais de 7 a 9 de novembro de 1963; sem equivalência a observações NORAD ou orientação ECI completa."
---

# CASTOR-G46: EOP histórico, sem fabricar orientação inercial

**Descoberta documental:** há dados públicos IERS de orientação terrestre para 1963, inclusive **7, 8 e 9 de novembro**. A [série oficial 05 C04, edição 2011, arquivo anual 1963](https://datacenter.iers.org/products/179/14334/orig/eopc04_05_IAU2000.63) publica 365 linhas a 00h UTC, com x/y do polo, UT1−UTC e LOD, seus erros formais e valores dX/dY impressos como zero. [Metadados do IERS](https://datacenter.iers.org/discontinued/www.iers.org/SharedDocs/Metadaten/EN/179_EOP_05_C04_2000/14334_EOP_C04_05_XX_IAU2000Af1a8.html?nn=12932) especificam IAU2000A e ITRF2005. Não são dados captados pelos sensores NORAD em novembro de 1963: constituem solução geofísica **retrospectiva**, compilada depois.

**Custódia:** fonte IERS ASCII de 57.612 bytes, SHA-256 `66711a146bd3a2752f8824a193431955a687ac7be013ebb0dfe0d86f64d5b264`. O [recorte determinístico em JSON](iers_eop_1963_11_07_09.json) mantém os 3 valores de dia, unidade original e incertezas formais, sem copiar a fonte integral para o Git. O validador examina **365/365 dias** e exige MJD contínuo e SHA completo antes de emitir o recorte. Os zeros históricos dX/dY ficam `null` no contrato por falta de comprovação de que sejam determinações instrumentais; não são correções nulas demonstradas.

| UTC (00h) | x [arcsec] | y [arcsec] | UT1−UTC [s] | LOD [s] |
|---|---:|---:|---:|---:|
| 1963-11-07 | −0,095115 | −0,012515 | −0,0364491 | 0,0020420 |
| 1963-11-08 | −0,098515 | −0,011315 | −0,0373852 | 0,0020760 |
| 1963-11-09 | −0,101915 | −0,010015 | −0,0383712 | 0,0021380 |

**Verificação cruzada:** a [edição corrente EOP 20u24 C04 IAU2000A (ITRF2020)](https://datacenter.iers.org/data/latestVersion/EOP_20u24_C04_one_file_1962-now.txt), capturada em 13/11/2026, apresentou os **mesmos valores nessas três datas**. SHA-256 do arquivo completo nessa captura: `f338c94c7abb282b4824c8a07269bbfa7549afd145bab67d65b14b7f0b930e50` (arquivo `latestVersion` é mutável; não usar como pin permanente). As duas edições são **uma família IERS**, não duas medições independentes.

**Restrições inativas:** a série fornece EOP geofísico para datas declaradas, mas **não** calcula sozinha a base polo/meridiano de `orbitGeodeticFrame.ts`, que requer convenção TEME/ECI/ITRF, UT1/UTC, precessão, nutação, offsets, coordenadas de estação e transformações rigorosas. Tampouco fornece a época ou direção de observações 527/529, incerteza de tracking, instante ou localização do 528. Interpolação subdiária e propagação de erros de modelo `NOT_IMPLEMENTED`; holdout 527/529 `NOT_RUN`; domínio de queda `NOT_EVALUABLE`. Não transformar o dia de catálogo C197 em hora 00h.

**Reprodução no HEAD:** executar `python3 tools/iers_1963_eop.py --download --check` para buscar o original com SHA; offline, fornecer `--source caminho-do-arquivo --check`; executar `python3 -m unittest discover -s tests -p test_iers_1963_eop.py -v`. Qualquer mudança de bytes do arquivo original ou descontinuidade de dias deve falhar, nunca levar a atualização silenciosa do pin. O teste `unittest` usa linhas originais congeladas e não se declara prova de download novo.

**Próxima tarefa física verificável:** integrar conversões IAU2000A/UT1/ITRF com biblioteca astronômica auditada e limites temporais explícitos, validar contra casos de referência independentes (sem usar o 528), depois ligar esta entrada aos guardas G43–G45. Acoplar informações órbitais apenas quando houver observações instrumentais com épocas, frame e incerteza. A fonte IERS é relevante à orientação terrestre, **não evidencia sobrevoo ou queda em Conde**.

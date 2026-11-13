---
type: Guide
title: "C241: dia catalogado, lacuna de espelho e mecanismo de observação"
description: "Auditoria reproduzível de cobertura 527/528/529 e impossibilidade de inferir reentrada a partir da ausência de linhas."
---

# Dia catalogado não é dado de não detecção

**Fonte contemporânea:** NASA *Satellite Situation Report* de 15/11/1963, [NTRS 19640001198](https://ntrs.nasa.gov/citations/19640001198), página impressa 8, ocorrência **C241-L10/C241-L11**: designação **1963-003B (NORAD 528)** sob lista de objetos decaídos com **08/11/1963**. É um *rótulo catalográfico por dia*, não a hora, longitude, latitude, sensor ou medição terminal. A relação objeto/designação segue `research/tle_custody/catalog_identity_527_529_2026-11-12.json`. Os 119 registros únicos de épocas da fonte C25#1/C179#1/C180#1/C181#1/C241-L3 vêm do **espelho secundário 1963**, não de logs negativos de um sistema de vigilância.

**Fatia Cervo:** `python3 tools/raan_catalog_day_missingness.py --check` reconcilia por NORAD as épocas do extrato, o rótulo por objeto e a partição retrospectiva congelada 61/23/35; reprova desvio dos inputs. Saída `research/statistics/raan_catalog_day_missingness_C241.json` com SHA-256 de cada input. No 528, o último registro presente no extrato está em **27/10/1963 14:40:16.132512 UTC**, a **11,38870217 dias** do início do dia 08/11. Essa distância **não** mede um intervalo de silêncio de sensores, muito menos reentrada ou probabilidade de sobrevivência. A data do 529 é *secundária* e a de 527 (1969) está fora do ano coberto pelo extrato; o auditor não extrapola 1963 até 1969.

## Porque a verossimilhança de ausência não está identificada

O evento observado aqui é somente **não haver outra linha retida no extrato**. Mesmo sob a hipótese adicional, ainda não justificada, de encontros de sensores seguindo um processo de Poisson com intensidade `lambda(t)` e retenção `q(t)`, a probabilidade de zero registros exigiria integrar `lambda(t)*q(t)` até o tempo em que o objeto se torna indetectável. Nenhuma função `lambda`, `q`, janela operacional dos sensores ou ligação entre o rótulo NASA e o estado físico foi recuperada. Um sistema sem passagens observadas ou um arquivo que omitiu passagens é compatível com o mesmo extrato. Portanto, **não calcular** hazard, likelihood de não detecção, tempo terminal, prior temporal ou exclusão geográfica. O boletim NASA também não deve ser contado como sensor independente dos dados NORAD que ele pode compilar.

**Holdout:** 61/23/35 é retrospectivo, não cego e da mesma linhagem; o relatório não ajusta parâmetros usando nenhuma época da avaliação. Nenhum teste empírico de detecção independente foi produzido. `active_constraint=false`; `historical_posterior=NOT_RUN`.

**Próxima evidência discriminante:** ficha primária identificada de acompanhamento do 528 contendo estação, horários e critérios de busca/seleção/publicação, incluindo ausência explicitamente registrada, se houver. A pesquisa da ficha e custódia cabe à Tartaruga; o desenho da likelihood e o teste de identificação permanecem com Cervo. Sem essas variáveis, a lacuna numérica não constitui dado negativo.

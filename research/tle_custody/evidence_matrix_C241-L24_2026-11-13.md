---
type: Guide
title: "C241-L24#1: cadeia GSFC–NORAD de 1962 e busca instrumental"
description: "Acordo primário reproduzido em 1965; novos canais documentais, ausência de observações individuais 527–529."
---

# C241-L24#1: caminho documental para observações em vez de sensores presumidos

Fonte primária institucional: [H. Rept. 89-197, Exhibit 5, acordo Goddard–NORAD de maio de 1962](https://www.govinfo.gov/content/pkg/SERIALSET-12667_05_00-002-0197-0000/pdf/SERIALSET-12667_05_00-002-0197-0000.pdf), reproduzido pelo Congresso em **22/03/1965**. Fac-símile auditado: **9.297.493 bytes**, SHA-256 `a08b4c505a37c09d1eb9c33ed14cc56228fd5e67f7ec1645f38554310bd60ca0`; PDF **páginas 21–22 (índices 20–21)**, impressas **15–16**, inspecionadas em 13/11/2026. É o **mesmo PDF de C241-L20#1** (Exhibit 4, 1961), portanto não conta como fonte independente adicional.

Na página impressa 15, Exhibit 5, §3(a), o GSFC descreve solicitação de observações ao NAVSPASUR no formato **estação, hora e ângulo**, normalmente por **seis horas após lançamentos de satélites científicos**. É uma regra condicional, **não registro de que 1963-003 ou o objeto 528 tenha sido observado**.

Na página impressa 16, §4(a), distinguem-se catálogo não classificado NORAD/SPADATS periodicamente transmitido ao GSFC; dados de sensores NORAD fornecíveis mediante solicitação para objetos rastreados pela NASA (geralmente nas primeiras oito órbitas); e observações reduzidas da **Satellite Instrumentation Network (SIN)** transmitidas no sentido **GSFC → NORAD**. Dados classificados dependem da autorização do NORAD. Esses canais não são sessões independentes demonstradas de 1963.

O [ledger tipado](gsfc_norad_moa_1962_C241-L24.json) conecta **cinco arestas institucionais condicionais** a C241-L20#1, registra as duas datas (acordo de 1962 e republicação de 1965), páginas, custódia e campos instrumentais desconhecidos para NORAD 527, 528 e 529. O [auditor](../../tools/tle_gsfc_norad_moa_audit.py) rejeita atribuição fictícia de estação, sensor, epoch UTC, referencial e σ e valida os bytes originais em CI.

Três buscas falsificáveis: (1) remessas NORAD/SPADATS a Goddard com identificadores 1963-003/527–529; (2) solicitações GSFC e linhas originais NAVSPASUR **estação–hora–ângulo** referentes aos objetos; (3) produtos SIN reduzidos ou solicitações NORAD específicas com estação, UTC, datum, frame, resíduos e erro. A vigência específica e execução desse acordo para 1963 **não foram verificadas**.

A pesquisa de 13/11/2026 na API pública NTRS, por *Satellite Situation Report*, retornou 136 registros, sem identificação inequívoca do volume 3 nº 21. Esse negativo escopa somente o índice consultado, não a existência do boletim em outros arquivos.

**Estado:** `CONNECTED_PENDING_CALIBRATION`. Nova conexão documental, **zero observações instrumentais originais e zero restrições físicas ativadas**. Conde continua indeterminado.

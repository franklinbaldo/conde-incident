---
type: Guide
title: "Varredura de acervos ópticos abertos (1963–1965): Durban/MNASSA, ITCP e negativos auditados"
description: "Dois documentos primários novos confirmam observação óptica de 1963-03A (NORAD 527) via Durban/DSIR Slough/ITCP, sem passagens brutas de 1963-03B (NORAD 528); negativos auditados em SAO C-41, Meudon, UK e URSS."
---

# Varredura de acervos ópticos abertos (EUA, Reino Unido/Commonwealth, França, URSS)

Esta nota registra uma varredura sistemática em acervos digitalizados de acesso aberto realizada em 18/11/2026 para verificar se existem passagens ópticas brutas ou fichas contemporâneas de **`1963-003B` (`NORAD 528`)** e de seu objeto companheiro **`1963-003A` (`NORAD 527`)** fora do catálogo Baker-Nunn da SAO.

**Status epistêmico geral:** `NEW_CONNECTED_EDGES, DOMAIN_NOT_YET_EVALUABLE` para o corredor de reentrada de `NORAD 528`. Nenhuma passagem datada de `528` foi localizada online; os dois achados primários abaixo referem-se a **`1963-03A` (`527`)** e à cadeia institucional de rastreamento.

## 1. Documentos primários novos diretamente inspecionados

### 1.1. Durban Satellite Tracking Station (*MNASSA*, ~1965 — Gregory Roberts)

- **Classificação:** original diretamente inspecionado (fac-símile PDF, 17 pp.).
- **URL:** `https://journals.co.za/doi/pdf/10.10520/AJA00248266_3354`
- **Título e autoria:** Gregory Roberts (Durban Satellite Tracking Station), *The optical appearance of artificial earth satellites*, *MNASSA* (Sabinet gateway scan, pp. 129–145).
- **Achado direto para `1963-03A` (`NORAD 527`) (pp. 8–9 do PDF):**
  - Designação: `1963 - 03A`
  - Classificação: `rocket body`
  - Dimensões estimadas: `8.00 × 1.50 m` (compatível com estágio Agena B)
  - Variação de magnitude observada: `1.0 – 09.0`; magnitude média: `3.8`
  - Aparência geral: `flashing, period 9 sec.` (regime de *tumbling*)
- **Exclusão explícita de `1963-03B` (`NORAD 528`) (p. 5):** *"Decayed satellites and satellites expected to decay before the end of September are not included."* A ausência de `528` (decaído em nov/1963) na tabela de 1965 decorre do critério editorial, não de invisibilidade histórica em 1963.
- **Cadeia institucional de rastreamento (p. 1):** A estação amadora de Durban operava simultaneamente como estação **Moonwatch**, **Western Satellite Research Network** (North American Aviation, reportando ao *1st Aerospace Squadron* da USAF), **Department of Scientific and Industrial Research — Space Research Division (Slough, Reino Unido)** e **Independent Tracking Coordination Program (ITCP, EUA)**.
- **Conexão para modelagem (`ballistic_527`):** fornece observação física primária de geometria cilíndrica em *tumbling* para o objeto de controle `NORAD 527` (`CONNECTED_PENDING_CALIBRATION`; não transferível diretamente para `528`).

### 1.2. *Independent Tracking Coordination Program (ITCP) Quarterly Report No. 5* (jul/1964)

- **Classificação:** original diretamente inspecionado (texto OCR completo / NASA NTRS `19650019803`).
- **URL:** `https://archive.org/stream/nasa_techdoc_19650019803/19650019803_djvu.txt`
- **Entidade e período:** Society of Photographic Scientists and Engineers (SPSE / Operation Phototrack), NASA Research Grant `NsG 35-60`, relatório datado de 20 jul 1964 cobrindo `1 Apr – 30 Jun 1964`.
- **Achado direto (Seção I.A.3, p. 1):** registra **5 observações ópticas independentes do exterior de `63 03A` (`1963-03A` = NORAD 527)** recebidas pelo ITCP e encaminhadas ao **NASA Goddard Space Flight Center**, junto de outros lançamentos militares de 1963 (`63 14A`, `63 27A`, `63 30A`, `63 38B/C`). Não contém linhas individuais *(hora, RA, Dec)* no texto resumido.
- **Lacuna de custódia localizada (carta de abertura, p. 1):** o documento cita explicitamente o **Quarterly Report No. 4 (20 abr 1964)**, cobrindo **`1 Nov 1963 – 31 Mar 1964`** (exatamente a janela do decaimento de `528` em 8 nov 1963), porém apenas o Report No. 5 aparece digitalizado em acesso aberto no Archive.org/NTRS.
- **Referência técnica (Exhibit D-3):** documenta a *Work Sheet C: Conversion of NORAD-SPADATS "4-line Elements" to R.O.E.* (incluindo $R_E = 6378.17\text{ km}$, período anomalístico e derivadas de nó/perigeu).

## 2. Negativos auditados em acervos digitais abertos

| Rede / País | Acervo inspecionado / verificado | Resultado auditado |
| :--- | :--- | :--- |
| **EUA — SAO** | *Catalog of Satellite Observations No. C-41* (SAO SR-178, NTRS `19650016803`, `https://ntrs.nasa.gov/api/citations/19650016803/downloads/19650016803.pdf`, inspecionado) | Traz observações ópticas brutas (Baker-Nunn + Moonwatch) de jul–dez/1963, mas cobre apenas satélites `1960 Xi 1` a `1962 Beta Alpha 1`. O volume seguinte (`C-42`, lançamentos de 1963) não está digitalizado em acesso aberto no NTRS/Archive.org. Reforça [SAO P-17](sao_p17_oct_dec_1963_scope_C241-L44.json), que já excluía `1963-003A/B/C`. |
| **Reino Unido** | DSIR Radio Research Station (Slough / WDC-C), King-Hele & Quinn (*Table of the artificial earth satellites launched in 1963*, *Planet. Space Sci.* 1964), BAA | **Slough** é confirmado independentemente por [Baja 1965](baja_1965_6303a_C241-CORUJA-R42.md) e **Durban/MNASSA ~1965** como distribuidor de efemérides para `1963-03A`, mas suas tabelas brutas de 1963 e os boletins da BAA não estão abertos online; King-Hele (1964) permanece sob paywall e é tabela-resumo anual. |
| **França** | Biblioteca Digital do Observatoire de Paris/Meudon (`https://bibnum.obspm.fr/ark:/11287/25LHq`, 40 itens inspecionados), SAF/*L'Astronomie*, CNES | Contém nota instrumental de Paul Muller (1964, obturador fotográfico), mas não tabelas brutas de passagens de 1963. Sem registros abertos de `1963-03`. |
| **URSS / Leste Europeu** | *Результаты наблюдений американских ИСЗ*, *Бюллетень станций оптического наблюдения ИСЗ* (1963–1964), *Biuletyn Polskich Obserwacji Sztucznych Satelitów* | Confirma [C241-L37](soviet_raw_observations_route_C241-L37.json) e [C241-L34](masevich_periodicals_1963_C241-L34.json): apenas entradas bibliográficas online; fascículos brutos de 1963–1964 indisponíveis em PDF aberto. |

## 3. Implicação para a fila de arquivos físicos

Para consultas presenciais/institucionais futuras (sem contato não autorizado), os alvos com maior valor documental identificados por esta varredura são:
1. **ITCP Quarterly Reports No. 3 e 4** (`NsG 35-60`, ago/1963–mar/1964) e *fixes* encaminhados ao NASA Goddard / WDC-A;
2. **DSIR Radio Research Station (Slough) / WDC-C** (Reino Unido);
3. **Logs de Durban / Cape Town Moonwatch** (SAAO / acervo Gregory Roberts);
4. **Астросовет АН СССР** (*Результаты наблюдений американских ИСЗ*, 1963–1964).

*Nota cruzada:* ver [experimento de visibilidade óptica de `528`](../constraints/optical_visibility_528_19631027_1108.md) — sob o ramo `RAAN 198.5261°`, `528` não tinha passagens crepusculares iluminadas em Durban, Slough, Baja ou Meudon entre 27 out e 8 nov 1963, de modo que buscas ópticas para `528` nesses acervos devem mirar **setembro de 1963**, enquanto a janela terminal de out–nov/1963 depende de dados de **radar** (NORAD/SPADATS).

---
type: Guide
title: "C241-L64: NASA registra 29–30 de outubro de 1963 para 1962 Omega 1"
description: "Fac-símile contemporâneo do SSR vol. 3 nº 24 e relação secundária com NORAD 308; intervalo de dias, não hora terminal UTC."
---

# C241-L64: um intervalo de datas para o controle 308

**ERRATA de leitura do fac-símile (C241-L65, 14/11/2026):** o objeto impresso é `OMEGA 1`, **não** `A OMEGA 1`. O `A` pertence a uma série posterior (a linha seguinte à `OMEGA 3` é `A BETA 1`). Veja [correção por reinspeção visual](nasa_ssr_omega1_corrigendum_C241-L65.md). A tabela abaixo reproduz a **transcrição histórica incorreta**, preservada para auditoria; não a reutilize como identificação original.


O [NASA/Goddard *Satellite Situation Report*, vol. 3, nº 24, de **15/12/1963**](https://ntrs.nasa.gov/citations/19640003479), em seu [fac-símile oficial, página PDF **17**](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=17), contém uma linha na tabela **DECAYED OBJECTS (CONT'D)**, sob **1962 LAUNCHES (CONT'D)**:

| Campo impresso | Leitura da mesma linha |
| --- | --- |
| OBJECT | `A OMEGA 1` |
| SOURCE | `US` |
| LAUNCH | `18 JUN` |
| DECAY | **`29-30 OCT 63`** |

**Localização:** página impressa **15**, índice de página PDF (base zero) **16**. O original foi inspecionado visualmente, com a linha confrontada às duas linhas próximas `A OMEGA 2` e `A OMEGA 3`, ambas com lançamento `18 JUN`, mas outros dias de decaimento. A reprodução de 14/11/2026 possui **958.927 bytes**, **23 páginas**, SHA-256 `d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f`.

A ponte `1962 Omega 1 ↔ 1962-024A ↔ NORAD 308 / FTV 2312` está apoiada **em fontes secundárias**, [KeepTrack (308)](https://keeptrack.space/satellite/00308) e [Samos-F](https://en.wikipedia.org/wiki/Samos-F). **O fac-símile NASA não imprime “308” nem “1962-024A”** nesta linha, de modo que não declara observação instrumental independente ou certeza de identidade NORAD provada exclusivamente no original.

## O que efetivamente mudou

A fonte **contemporânea** publica **`29–30 OCT 63`**, uma faixa de dias distinta do único **30/10/1963** exibido no catálogo secundário. O rótulo não define uma escala UTC, uma hora terminal, incerteza de sensor, hora de última observação ou posição de reentrada. **Não equiparar a expressão editorial a `1963-10-29T00:00:00Z .. 1963-10-31T00:00:00Z` como intervalo físico certificado.** Ela pode servir a testes documentais condicionais, após explicitar a hipótese de relógio/calendário, mas ainda não a uma likelihood temporal calibrada.

O adendo **não altera** o manifesto C241-L63: ele era uma fotografia correta do estado então recuperado para 308 (`NOT_RECOVERED`). O novo registro é outra edição NASA, não outro radar; a genealogia NASA/NORAD pode ser compartilhada. Nenhum estado orbital ou geográfico do **528** é atualizado, nem a hipótese de queda em Conde demonstrada.

## Busca da edição intermediária e limites negativos

Consultei a API oficial `POST https://ntrs.nasa.gov/api/citations/search` com `q="SATELLITE SITUATION REPORT"`, `published.gte=1963-10-01`, `published.lte=1963-12-31` e `page.size=100`. Na consulta de 14/11/2026 retornaram cinco registros (`19640000428`, `19640001198`, `19640002493`, `19640003479`, `19640005618`), **sem o volume 3 nº 21**. Isso é lacuna da *consulta*, não demonstra que a edição #21 nunca existiu nem que o objeto 308 não tenha sido observado.

**Próximo passo:** recuperar SSR nº 21 e documentação contemporânea NORAD/AF IN/SPADATS que vincule expressamente 308 à designação e dê instante ou intervalo com escala temporal declarada; somente depois calibrar o benchmark do Cervo.

## Auditoria

`research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json` preserva leitura, datação, integridade e nulos. `tools/tle_ssr_308_c241_l64.py` valida o contrato imutável, proíbe UTC/sensor/σ fabricados e verifica bytes/hash PDF. `tests/test_tle_ssr_308_c241_l64.py` contém controles adversariais para PDF errado, hora terminal fictícia, número 308 ficticiamente impresso e ativação indevida de restrições do 528.

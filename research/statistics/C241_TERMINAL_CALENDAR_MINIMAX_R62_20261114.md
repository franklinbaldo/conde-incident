---
type: Experiment
title: "C241 R62: limite minimax apenas condicional da data terminal impressa"
description: "Informação temporal possível sob dois rótulos editoriais do controle 308, sem calibrar hora nem sigma"
experiment_id: C241-TERMINAL-CALENDAR-MINIMAX-R62
verification_status: CONDITIONAL_MATHEMATICS_NOT_TERMINAL_CALIBRATION
---

# R62: uma faixa de dois dias não equivale a um erro horário medido

A NASA/GSFC, no *Satellite Situation Report* vol. 3 nº 24, p. 15, publica **A OMEGA 1 → 29–30 OCT 63**, custodiado como [C241-L64](../tle_custody/nasa_ssr_terminal_control_308_C241-L64.md), PDF [NTRS 19640003479](https://ntrs.nasa.gov/citations/19640003479), SHA-256 d31a064f8e03fd39be6fe75b88cd5852c0b74c9101fa635cb40ac25c77ef474f. O catálogo secundário do [R59](C241_1963_TERMINAL_CONTROL_SCREEN_20261114.md) indica o **dia 30/10/1963** para NORAD 308; a identidade da linha A OMEGA 1 ↔ NORAD 308 é apenas um *crosswalk* secundário. O documento NASA não imprime 308, sensor, horário UTC nem erro instrumental.

## Informação identificável condicional

Se, **somente como cenário contrafactual**, cada dia civil impresso representar as 24 horas UTC completas e um único evento estiver em algum instante de um intervalo contíguo [a,b), então:

- O menor erro absoluto **máximo** de qualquer palpite pontual que desconhece o instante, min_p sup_{t∈[a,b)} |t-p|, é exatamente (b-a)/2, atingido pelo ponto médio.
- A união hipotética dos dias **29–30/10** mede 48 horas: limite minimax **24 horas**.
- O rótulo secundário de **30/10**, se isoladamente interpretado como dia UTC integral, mede 24 horas: limite minimax **12 horas**.

Esses limites são **de informação em um conjunto assumido**, não erro de previsão observado, desvio-padrão, intervalo de confiança, observação de sensor, posterior bayesiana, vantagem do catálogo secundário nem cota sobre o horário histórico real. Sem correspondência comprovada entre rótulo editorial e evento em UTC, não existe sequer o conjunto UTC histórico autenticado. A largura de dois dias pode refletir convenções e compilação, não duas observações ou dois tempos terminais.

O cálculo não usa órbitas após nenhum corte, não ajusta H, densidade, massa ou data. Um eventual *holdout* preditivo exigiria, além da identidade original do objeto e relógio, previsão registrada **antes** da observação terminal independente; os registros atuais foram selecionados retrospectivamente. MCMC histórico **NOT_RUN**, terminais calibrados **0**, sigma terminal **null** e restrição do NORAD 528 **inativa**.

## Replay e contraprovas

O auditor [R62](../../tools/c241_terminal_calendar_minimax_r62.py) lê o JSON R60 produzido a partir do Parquet 1963 com SHA-256 pinado c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09, além do manifesto C241-L64. Verifica as premissas negativas e publica duas janelas **explicitamente hipotéticas**. A suíte testa adversarialmente promoção falsa de sensor, sigma, ID 308 impresso, UTC terminal, proveniência e classe de holdout; executá-la em Python normal e otimizado impede que assert seja o único gate.

Com o replay R60 em arquivo, executar:

    python3 tools/c241_terminal_calendar_minimax_r62.py --r60 /tmp/c241-1963-fixed-h.json --ssr research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.json --output /tmp/c241-terminal-minimax-r62.json

O workflow c241-1963-terminal-control-screen.yml deve comprovar o SHA exato, os testes e o replay real. Não confundir o estudo matemático com validação física. Próxima observação discriminante: vínculo instrumental primário de NORAD 308 com A OMEGA 1, horário/intervalo terminal identificado, fuso e incerteza documentados, mais previsão pré-terminal congelada.

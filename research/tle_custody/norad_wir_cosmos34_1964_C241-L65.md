---
type: Guide
title: "C241-L65: janela Z de desorbitação estimada num boletim NORAD de 1964"
description: "Fac-símile primário da inteligência NORAD, 9 julho 1964, distingue estimativa administrativa de observação instrumental e de decaimento natural."
---

# C241-L65 | Uma janela em Z não é um relógio calibrado

O [*NORAD Weekly Intelligence Review* 29/64, de 17 de julho de 1964](https://www.archives.gov/files/declassification/iscap/pdf/2009-068-doc35.pdf) é um relatório original desclassificado, preservado pela NARA no conjunto ISCAP **2009-068, documento 35**. Na página impressa **6** (quarta página do PDF), a seção sobre **Cosmos 34** afirma, com a ressalva *apparently*, que o objeto teria sido desorbitado **entre 0931 e 0936 Z em 9 de julho de 1964**, no início da revolução 127.

**Custódia do arquivo completo:** 30.133.149 bytes, 10 páginas, SHA-256 `2063f4f8d9082c55990dd4be91b8eb096333143230b6f726639fc58bef7251c5`. A página original foi visualmente conferida em 14/11/2026. Os horários são os números impressos no relatório de inteligência; não foram recuperados dados instrumentais, sensor, estação, método de estimação nem desvio-padrão.

## Por que isso importa para os controles do Cervo

A fonte comprova apenas que **um relatório NORAD de 1964 publicou uma janela estimada com resolução nominal de cinco minutos** para uma **desorbitação aparente**. Ela **não fornece** uma precisão medida de cinco minutos, um intervalo de confiança, uma definição universal do campo `DECAY` dos *Satellite Situation Reports* da NASA, nem a hora do decaimento natural de 1963.

Em especial, seria um **erro de transferência de domínio** transformar esse intervalo de Cosmos 34 em `sigma_t=300s` ou numa likelihood para o NORAD **308, 528 ou 637**. A própria redação emprega *apparently* e não nomeia observação instrumental. É um controle contextual que ajuda a formular uma pergunta mais exigente ao acervo: onde estão as mensagens individuais NORAD/AF IN/SPADATS de 1963 com número de objeto, época Z, sensor, erro e definição operacional de decaimento?

As fontes [C241-L24 (memorando NORAD/GSFC de 1962)](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/gsfc_norad_moa_1962_C241-L24.json) e [C241-L64 (NASA SSR de dezembro de 1963)](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/nasa_ssr_terminal_control_308_C241-L64.md) continuam distintas: uma estabelece canais institucionais, a outra imprime dias catalográficos, e esta terceira fonte apresenta uma análise de inteligência relativa a outro evento. Nenhuma é um sensor independente do 528.

O JSON versionado fixa as afirmações e nulos; o auditor recusa interpretações indevidas sob Python comum e `-O`, e o CI reproduz o PDF original inteiro pelo hash. **Nenhum parâmetro orbital ou janela de Conde foi alterado.**

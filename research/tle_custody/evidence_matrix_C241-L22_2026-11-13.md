---
type: Guide
title: 'C241-L22: boletim NASA de 30/06/1963 verificado'
description: 'Fonte documental contemporânea para órbitas catalogadas de 527, 528 e 529, com ligação às edições abril/julho/agosto sem falsificar épocas.'
---

# C241-L22: junho ocupa a lacuna entre abril e julho

**Fonte primária documental:** [NASA Goddard, *Satellite Situation Report*, vol. 3, nº 13, 30/06/1963, NTRS 19630012130](https://ntrs.nasa.gov/citations/19630012130); [PDF oficial](https://ntrs.nasa.gov/api/citations/19630012130/downloads/19630012130.pdf#page=13). Capa PDF p. 1 imprime data, volume e nº; página de apresentação PDF p. 3 indica compilação às **1200Z** por Goddard, NORAD e Smithsonian Astrophysical Observatory. A data de compilação não é a época individual de cada elemento orbital.

A tabela rotacionada *OBJECTS IN ORBIT*, página impressa **5**, é a **13ª página do PDF (índice 12)**, não a página 7 de outras edições. Conferida visualmente em 13/11/2026, sem confiar na extração OCR:

| Designador impresso | NORAD (crosswalk C241-L10, não impresso) | Período nodal | Inclinação | Apogeu | Perigeu |
|---|---:|---:|---:|---:|---:|
| 1963 3A | 527 | 94,6 min | 81,89° | 530 km | 465 km |
| 1963 3B | 528 | 93,7 min | 81,88° | 478 km | 423 km |
| 1963 3C | 529 | 94,0 min | 81,89° | 512 km | 427 km |

**Captura oficial:** 274.564 bytes, SHA-256 `8add4b46734e992a213088ef58ba9d58b6385df7b89bb504f79fe8715ec418f3`. Esse hash fixa os bytes entregues agora pela NASA; não autentica qualquer TLE instrumental de 1963. Mudança de CDN deve falhar no teste e exigir nova inspeção com variantes registradas, nunca alterar o hash silenciosamente.

## Relações cumulativas

O [ledger](nasa_ssr_jun30_1963_C241-L22.json) está conectado ao [grafo de 12 escalares documentais](../constraints/ssr_jun30_1963_observables_C241-L22.json), com dependências para abril (C241-L16), julho (C241-L18) e agosto (C241-L17). No controle documental 528, a sequência impressa de períodos 30/04→30/06→31/07→15/08 é **94,1 → 93,7 → 93,6 → 93,3 min**. Suas diferenças editoriais são −0,4, −0,1 e −0,3 min. Nenhuma dessas diferenças autoriza dividir por dias corridos e chamar o quociente de taxa dinâmica, porque desconhecemos a época de observação de cada elemento.

Cada campo tem unidade, operador candidato e dependências de estado orbital, época latente, referencial e modelo de força. A fonte **não fornece** RAAN, estação, σ/covariância, par de linhas TLE, frame instrumental, identidade material do 528 nem hora/local terminal. Esses campos continuam `null`, não zero. A genealogia NASA/NORAD/SAO é compartilhada com as edições vizinhas, sem contar quatro boletins como quatro sensores independentes.

**Status:** `CONNECTED_PENDING_CALIBRATION`; 12 escalares documentais conectados; zero medições instrumentais independentes recuperadas; domínio físico sem nova restrição validada; nenhuma prova Lean promovida. RAAN 284,1520° permanece sem fonte autenticada, enquanto 198,5261° é secundária. **Conde permanece indeterminado.**

O [auditor](../../tools/tle_nasa_ssr_jun30_audit.py) valida custódia, transcrição, ligações April/July/August, limites epistemológicos e bytes reais do PDF; [testes adversariais](../../tests/test_tle_nasa_ssr_jun30_audit.py) e [workflow](../../.github/workflows/tle-nasa-ssr-jun30.yml) fornecem replay reproduzível.

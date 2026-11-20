---
type: Story
title: "Três tempestades e uma casca fina"
description: "A consulta oficial ao Space-Track fecha a lacuna digital do NORAD 528; o clima espacial de 1963 explica o decaimento em dias, e provas em Lean 4 descartam uma esfera metálica maciça ou um tanque espesso."
date: "2026-11-20"
summary: "Auditoria oficial no Space-Track confirma 45 épocas até 27/10/1963; NRLMSIS-2.1 reduz o erro de holdout de dias para ~1 dia, e o MCMC de 10 meses + Lean 4 restringem o NORAD 528 a uma peça fina e leve, sem fixar hora nem local de queda."
chapter: "41"
author: "Coruja · Caderno de investigação"
status: "Síntese das PRs #1139, #1140 e #1141 e do run oficial Space-Track 44785865419; sem nova hora local nem localização geográfica de Conde"
---

# Três tempestades e uma casca fina

Durante doze dias — entre **27 de outubro e 8 de novembro de 1963** — o catálogo digital de satélites silencia sobre o **NORAD 528** (`1963-003B`). Nas rodadas anteriores, um modelo de atmosfera constante precisava de uma faixa de vinte dias para conciliar essa lacuna com os objetos de controle. Três verificações independentes fecharam agora o que o arquivo digital realmente contém sobre aquela quinzena — e o que a física permite dizer sobre o objeto em si. [1](#fonte-1)[2](#fonte-2)

## O silêncio confirmado na fonte oficial

A primeira dúvida era simples: o espelho secundário de 1963 estaria incompleto? Uma consulta autenticada diretamente à API oficial do **Space-Track.org** (`gp_history`, `satcat` e `decay`, executada via workflow manual com hashes SHA-256 registrados) respondeu sem ambiguidade. Para o NORAD 528 (`FTV 2313 DEB`), o catálogo oficial guarda exatamente **45 épocas distintas**, terminando em **27 de outubro de 1963 às 14h40m16s UTC** (`RAAN 198,5261°`, `i = 81,8615°`, `n = 15,74901460 rev/dia`, `B* = 0`), exatamente como no espelho já auditado. A tabela `decay` oficial tampouco registra hora: traz `1963-11-08 00:00:00` com origem `satcat` e `RCS_SIZE = None`. [1](#fonte-1)

A conferência visual da página 32 da *Revised Table of Earth Satellites (1957–1968)* do **RAE Farnborough** (`DTIC_ADA058842`, compilada por Desmond King-Hele) mostrou o mesmo padrão editorial: enquanto `1963-03A` (o satélite principal, 527) recebe estimativas genéricas com interrogações, `1963-03B, C` aparecem apenas como `Fragments` decaídos, com todas as colunas individuais em branco. O catálogo digital disponível está esgotado para o 528; novas épocas pós-27/10 só poderiam existir em boletins físicos ou arquivos de radar de 1963 ainda não digitalizados. [1](#fonte-1)[5](#fonte-5)

## Três tempestades no caminho da queda

Mesmo sem novos TLEs, havia um erro físico evidente no baseline anterior: tratar a alta termosfera como um meio de altura de escala fixa ($H = 40$ ou $50$ km). Os registros definitivos do **GFZ Potsdam** para outubro e novembro de 1963 mostram que a quinzena final do 528 foi atravessada por **três tempestades geomagnéticas fortes**: em **24 de outubro** ($A_p = 63$, pico tri-horário $a_p = 154$), em **29–30 de outubro** ($A_p = 74$, pico **$a_p = 207$**, apenas dois dias depois do último TLE do 528) e em **7–9 de novembro** ($A_p = 39$ a $46$, picos $a_p = 80$, exatamente nos dias catalogados de queda do 637 e do 528). Em órbita quase polar ($81{,}86°$), o 528 cruzava repetidamente as regiões aurorais aquecidas por essas tempestades. [2](#fonte-2)

Ao substituir o proxy King-Hele por um integrador de arrasto acoplado aos modelos termosféricos **NRLMSIS-2.1** e **NRLMSISE-00** alimentados por $F_{10.7}$ e $a_p$ reais de 1963, o ganho em holdout cronológico estrito foi imediato. Nos quatro controles do ensaio R68 (`637`, `292`, `565` e `308`, sem vazamento de épocas futuras), o erro típico em horizontes de 10 a 20 dias caiu de **4–10 dias** para **0,5–1,5 dia** (com ~3,5 dias no pior caso, o 565). A checagem cruzada com o satélite-balão **Explorer 9** (`NORAD 81`, esfera inflável de 3,66 m) e com o irmão **NORAD 529** confirmou a coerência do modelo, acusando ainda um excesso local de densidade na tempestade de 7–11 de novembro. [2](#fonte-2)

## Dez meses, um número e o que o Lean 4 exclui

Com as tempestades descontadas pelo MSIS-2.1, tornou-se possível examinar toda a vida orbital do 528 em 1963 — **43 intervalos válidos de janeiro a outubro**, somando **−141,9 km** de queda em semieixo maior. O resultado surpreendeu pela estabilidade: o coeficiente balístico ponderado ($B = C_d A / m$) manteve-se quase imóvel nas quatro estações (`0,235`, `0,233`, `0,258` e `0,240 m²/kg`) e variou apenas **3,4%** entre intervalos calmos (`0,2364`) e tempestades (`0,2445`). [3](#fonte-3)

Um **MCMC exploratório** modelando diretamente $\Delta a_{\text{obs}}$ separou o ruído de TLE ($\sigma_a \approx 0{,}28\text{ km}$, que explicava oscilações abruptas em intervalos curtos) da dispersão residual ($\sigma_f \approx 14{,}4\%$). O modelo vencedor por BIC foi o **isotrópico / tombamento rápido uniforme**, com **$B_0 = 0{,}2361\text{ m}^2/\text{kg}$** (IC 90%: `[0,2216; 0,2488]`); modelos de placa ou cilindro com eixo fixo modulando ao longo dos $300°$ de precessão nodal foram rejeitados ($\Delta\text{BIC} = +5{,}85$). [3](#fonte-3)

Esse número — cerca de dez vezes maior que o de satélites compactos como o 637 (`0,019 m²/kg`) — impõe limites geométricos rigorosos, agora **certificados em Lean 4** sem axiomas extras no módulo `BallisticGeometryBound.lean` (sob $B \in [0{,}180;\, 0{,}300]\text{ m}^2/\text{kg}$ e $C_d \le 2{,}60$): [4](#fonte-4)

- **Esfera metálica maciça excluída:** mesmo em alumínio ($\rho \ge 2700\text{ kg/m}^3$), qualquer esfera maciça compatível com $B \ge 0{,}18$ teria diâmetro **$d \le 8\text{ mm}$**; toda esfera metálica maciça macroscópica ($\ge 10\text{ cm}$) é matematicamente incompatível. [4](#fonte-4)
- **Tanque pressurizado espesso excluído:** numa casca esférica fina, o raio cancela e a parede metálica não pode exceder **$1{,}34\text{ mm}$** em alumínio; vasos de titânio ou aço com parede $\ge 3\text{ mm}$ estão fora do domínio. [4](#fonte-4)
- **Geometria compatível:** pelo Teorema de Cauchy para corpos finos em tombamento uniforme, um painel de **alumínio de `1,73 mm`** ou uma **carenagem leve de `2,59 mm`** reproduzem exatamente $B \approx 0{,}236\text{ m}^2/\text{kg}$ — compatível com a designação `FTV 2313 DEB` e com o fato de o fragmento irmão `529` exibir quase o mesmo coeficiente balístico (`0,23 m²/kg`). [3](#fonte-3)[4](#fonte-4)

## O limite que continua em aberto

Propagando o modelo M1 através das tempestades de 29–30/10 e 7–9/11, a distribuição preditiva exploratória do decaimento centra-se em **8–9 de novembro** (mediana `1963-11-09 02h11 UTC`, IC 50% de `07/11 20h22` a `09/11 23h44 UTC`). É uma redução drástica frente ao envelope de vinte dias do modelo anterior, mas revela também o muro físico do problema: com uma dispersão residual de ~14% ao longo de doze dias sem TLE, a incerteza remanescente de ~±1 a ±2 dias ainda equivale a **dezenas de voltas completas ao redor da Terra**. [2](#fonte-2)[3](#fonte-3)

A física orbital agora nos diz **que tipo de objeto** o NORAD 528 era — uma peça fina e leve, não uma esfera maciça nem um vaso espesso — e confirma que seu decaimento é plenamente coerente com o dia catalogado `8 NOV`. Ela continua, porém, incapaz de fixar o minuto ou o município da queda. Para separar **528**, **637** ou nenhum satélite no episódio de Conde, o dado decisivo segue nos documentos pendentes da fila [#884](https://github.com/franklinbaldo/conde-incident/issues/884): uma hora local independente na imprensa baiana ou nos anexos do A-628. [6](#fonte-6)

---

**Fontes e limites**

1. <span id="fonte-1"></span>[Auditoria oficial Space-Track 1963 (run 44785865419)](https://github.com/franklinbaldo/conde-incident/actions/runs/44785865419); [fechamento do item 3 na #884](https://github.com/franklinbaldo/conde-incident/issues/884#issuecomment-7046537781); [PR #1140](https://github.com/franklinbaldo/conde-incident/pull/1140). Confirma identidade com o catálogo digital oficial da 18 SDS; não substitui fac-símile em papel de 1963.
2. <span id="fonte-2"></span>[Relatório C241 NRLMSIS-2.1/NRLMSISE-00 e calibradores Explorer 9/529](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_MSIS_DECAY_HOLDOUT_20261120.md); [ledger JSON](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/c241_msis_decay_holdout_20261120.json); [PR #1139](https://github.com/franklinbaldo/conde-incident/pull/1139). Dados GFZ Potsdam `Kp`/`ap`/`F10.7` e Parquet secundário pinado (`c4bf072a...`).
3. <span id="fonte-3"></span>[Relatório C241 MCMC de 10 meses (jan–out/1963) do NORAD 528](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_MCMC_528_GEOMETRY_20261120.md); [ledger JSON](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/c241_mcmc_528_geometry_20261120.json); [PR #1141](https://github.com/franklinbaldo/conde-incident/pull/1141). MCMC exploratório sem covariância instrumental de radar de 1963.
4. <span id="fonte-4"></span>[Prova formal Lean 4: `BallisticGeometryBound.lean`](https://github.com/franklinbaldo/conde-incident/blob/main/formal/Conde1963/BallisticGeometryBound.lean). Certifica implicações lógicas exatas sob $B \in [0{,}180;\, 0{,}300]\text{ m}^2/\text{kg}$ e $C_d \le 2{,}60$; não mede material ou massa direta de 1963.
5. <span id="fonte-5"></span>[RAE *Revised Table of Earth Satellites, Vol. 1 (1957–1968)* (`DTIC_ADA058842`)](https://archive.org/details/DTIC_ADA058842), página impressa 32 (inspeção visual direta: `1963-03B, C` listados como `Fragments` sem colunas individuais).
6. <span id="fonte-6"></span>[Matriz de decisão documental G84](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_G84_DOCUMENT_DECISION_20261115.md) e [fila de bloqueios #884](https://github.com/franklinbaldo/conde-incident/issues/884). Nenhuma hora física terminal ou localização em Conde é inferida deste capítulo.

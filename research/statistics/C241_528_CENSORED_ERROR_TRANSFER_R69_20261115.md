---
type: Experiment
title: "C241 R69: transferência condicional do erro censurado dos controles ao 528"
description: "Envelopes de cenários do proxy de decaimento, não intervalos de confiança nem restrições físicas"
experiment_id: C241-R69-528-DECAY-DAY-TRANSFER
verification_status: RETROSPECTIVE_CONDITIONAL_NOT_CALIBRATED
---

# R69: aplicar o diagnóstico de erro R68 ao NORAD 528, sem inventar sigma

Conforme a [fila canônica](../../docs/PRIORITIES.md) e [#647](https://github.com/franklinbaldo/conde-incident/issues/647), esta fatia não estende genealogia de catálogo, priors de massa ou localização de impacto. Usa o mesmo espelho secundário pinado de 1963, SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**, reaproveitando [R54](../../tools/c241_king_hele_day_holdout.py) (previsão para 528) e [R68](C241_UNIFIED_DECAY_DAY_ERRORS_R68_20261115.md) (tabela única para controles).

## Pergunta e cálculo, condicionais

**Pergunta:** quão diferente seria o calendário nominal do 528 se os desvios de dia dos controles, observados apenas como rótulos catalográficos, fossem transferidos como cenários? Isso não presume que tais erros sejam intercambiáveis entre objetos, nem que representem amostras da mesma distribuição. O resultado é um diagnóstico do risco de extrapolação, não uma previsão calibrada.

A origem fixada do 528 é **1963-10-27T14:40:16.132512Z**, anterior ao corte exclusivo **1963-10-28T00:00:00Z**, com 45 épocas anteriores de uma linhagem secundária. A aproximação de atmosfera exponencial local usa H_eff=40/50 km, duas últimas épocas ou mediana de três secantes. **Nesse corte, os dois métodos resultam nas mesmas previsões**, logo não constituem replicações independentes. O rótulo NASA 08/11/1963 entra apenas como comparação retrospectiva e não como horário físico terminal.

Em cada grupo de controles, com erro definido como previsão menos instante terminal, use a união dos intervalos censurados hipotéticos E_i ∈ (l_i,u_i]. O **fecho convexo de cenários** usa l_min = min(l_i) e u_max = max(u_i). Para uma previsão fixada P_528, as datas transferidas condicionalmente ficam em [P_528-u_max, P_528-l_min). A notação preserva os extremos aberto/fechado do erro. A transformação é algébrica e não estabelece que o instante físico pertença ao envelope.

São três estratos pré-definidos para análise de sensibilidade, sem escolher o que melhor se ajusta ao dia NASA do 528:

- ALL_FOUR_CONDITIONAL: 637, 292, 565 e 308, sendo 308/OMEGA 1 um vínculo não comprovado; 15 origens distintas por método/H.
- OMIT_UNRESOLVED_308: 637, 292 e 565; 11 origens por método/H, ainda com dias de decaimento secundários.
- NASA_637_ONLY: quatro origens do mesmo objeto 637, todas de uma linhagem orbital e um único rótulo editorial sem hora, portanto não são quatro holdouts instrumentais independentes.

São 12 combinações (2 métodos × 2 H × 3 estratos). R68 contém 64 linhas e 60 combinações origem/método/H distintas após coalescer origens repetidas do 565. Nenhuma linha de 528 entra na estimação do envelope de controles. H foi escolhido retrospectivamente, não medido; não se aplica ajuste de H, regressão, MAE, RMS, frequência de cobertura ou estimativa de sigma horário.

## Resultado interpretável e limites

No replay do corpus pinado, os resultados foram os seguintes. Datas abaixo são **envelopes condicionais de cenário**, não previsões históricas validadas. O estrato sem 308 produziu os mesmos extremos do estrato com quatro objetos; portanto, a inclusão do alias não altera o envelope extremo neste corte, mas continua uma premissa não licenciada.

| Método | H km | Quatro controles: cenário UTC [início, fim) | Só 637: cenário UTC [início, fim) | NASA 08/11 intercepta o só-637? |
|---|---:|---|---|---|
| Últimas 2 | 40 | 31/10 11:57 – 15/11 18:26 | 31/10 11:57 – 10/11 00:46 | Sim |
| Últimas 2 | 50 | 30/10 02:06 – 15/11 16:08 | 30/10 02:06 – 10/11 06:09 | Sim |
| Mediana 3 | 40 | 28/10 18:10 – 12/11 07:28 | 31/10 11:57 – 05/11 18:48 | **Não** |
| Mediana 3 | 50 | 26/10 08:59 – 11/11 08:25 | 30/10 02:06 – 02/11 17:56 | **Não** |

**Conclusão explícita para #647:** a dinâmica baseada nos elementos de **27/10/1963 não refina** o rótulo NASA **8 NOV** do NORAD 528. Ela é **somente compatível em alguns cenários contrafactuais** de dia UTC: a envoltória de quatro controles e a de três controles interceptam 8/11 nos quatro pares método/H, e 637 isolado intercepta apenas nos dois cenários de últimas duas épocas; com mediana de três secantes, os dois cenários de 637 isolado **não** interceptam 8/11. As faixas transferidas vão de **26/10 a 15/11**, conforme método, H e estrato, muito mais amplas que um dia. Isso **não** restringe o instante de reentrada física, pois horários terminais, erro instrumental, intercambialidade dos controles e fuso do rótulo não foram estabelecidos. A resposta científica é **compatibilidade condicional sem redução licenciada** do intervalo do evento, do dia SSR ou da geografia de Conde; `terminal_time_sigma_hours=null` e `active_constraint_528=false` permanecem.

As duas falhas de sobreposição para 637 isolado, sob a mediana de três secantes, são uma **contraprova de robustez da transferência**, não uma rejeição instrumental do decaimento do 528. Mesmo quando as duas estimativas do 528 coincidem, os **erros derivados dos controles diferem pelo método**. A ausência de relógio terminal independente impede interpretar qualquer das faixas como limite físico.

O pipeline produz **c241-528-day-transfer-r69.json**, junto dos intermediários R54/R68, na mesma execução de CI SHA-pinado. Cada linha inclui a previsão nominal, os extremos do erro censurado e o intervalo resultante sob a suposição não verificada de que os rótulos impressos são dias UTC. A sobreposição com o rótulo NASA do 528 é apenas um diagnóstico condicional, não validação independente. A largura e as datas variam com o estrato e com H: essa instabilidade é o resultado científico, não um intervalo novo para Conde.

**Não identificáveis:** erro horário, distribuição de erro preditivo, época física terminal, escala temporal do rótulo, modelo de seleção/sensor, fase orbital, coeficiente balístico, massa, local de queda e vínculo espacial Conde. A transferência exigiria intercambialidade e documentação da observação terminal que não existem. calibrated_terminal_holdouts=0, terminal_time_sigma_hours=null, historical_mcmc=NOT_RUN, active_constraint_528=false, impact_geography=null.

Um avanço externo que mudaria a decisão: observações independentes com instante ou janela terminal, instrumento, incerteza, fuso/escala temporal, identidade NORAD e séries orbitais prévias, selecionadas antes de inspecionar o desfecho. Até lá, não converter rótulos secundários em datas físicas observadas.

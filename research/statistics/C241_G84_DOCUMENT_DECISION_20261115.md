---
type: Experiment
title: "C241 G84: valor decisório dos documentos ausentes para 528 × 637"
description: "Matriz contrafactual pequena para a fila do dono, sem novas horas, órbitas ou exclusões físicas"
experiment_id: C241-G84-DOCUMENT-DECISION
verification_status: CONDITIONAL_ONLY_NO_NEW_EVIDENCE
---

# O que cada documento poderia decidir entre os planos 528 e 637?

**Regra de leitura.** `COND_528`, `COND_637` e `COND_NONE` descrevem **só proximidade de plano modelado** à câmera **moderna de 2022** (CGEO15), não presença do objeto, fase, reentrada, localização de 1963, nem probabilidade. Para uma hora independente, comparar a janela *inteira* de 50/100/200 km do [ensaio #892](C241_CONDITIONAL_PLANE_WINDOWS_20261114.md), nunca só a raiz. Os horários abaixo são **exemplos de raízes já calculadas**, não horas atribuídas a testemunhas.

| #884 | Documento pedido | Se o resultado vier... | 528 (modelo) | 637 (modelo) | O que decide? |
|---|---|---|---|---|---|
| 1 | *O Globo*, 8–9/11 | Hora independente no entorno de 08/11 **20h43 Bahia**; ou de 07/11 **02h24 Bahia**; sem hora | Próximo no primeiro exemplo, distante no segundo [G83] | Dia NASA 07/11 já vencido no primeiro; próximo no segundo [G83/DAY] | **528 ou 637 condicional**; sem hora: não decide [HOUR] |
| 2 | *A Tarde* + *Jornal da Bahia*, 7–12/11 | Hora independente em janela exclusiva 528, exclusiva 637, fora de ambas, ou nenhuma | Próximo / distante / distante / desconhecido [G83/PLANE] | Distante / próximo / distante / desconhecido [G83/PLANE] | **528 / 637 / nenhum plano nominal / não decide**; não confundir *Diário de Notícias* com independente [#871] |
| 3 | Space-Track `gp_history` 527/528/529/637 | Elementos iguais ao espelho; novos de 01–08/11; sem épocas novas | Igual / **NÃO_AVALIÁVEL: recalcular** / sem mudança [PLANE] | Igual / **NÃO_AVALIÁVEL: recalcular** / sem mudança [PLANE] | Não decide sozinho: sem hora do evento, nem fase calibrada [DAY] |
| 4 | Anexos A-628 (dois recortes) | *Jornal da Bahia* com hora independente; só *Diário de Notícias* ou sem hora | **NÃO_AVALIÁVEL** até ler e cruzar hora; senão não decide [A628/G83] | **NÃO_AVALIÁVEL** até ler e cruzar hora; senão não decide [A628/G83] | Pode discriminar, mas os anexos **não estão no PDF público** [A628] |
| 5 | FBIS Daily Reports e *World Reaction* 8-1963 | `2330`=GMT; `2330`=Rio local; sem âncora | Raiz 08/11 ~23h43Z **depois / antes / indeterminada** da transmissão [G83/CLOCK] | Ordem das 8 raízes de cada modelo não muda (6 antes, 2 depois) [G83] | **Só ordena as raízes**, não identifica o fenômeno; P48=0/10 [P48] |
| extra | Roteiro Rádio Tupi Rio 8/11 | Contém hora do fenômeno; só hora de transmissão; indisponível | **NÃO_AVALIÁVEL** sem hora e fuso; ou só limite da notícia [CLOCK/G83] | **NÃO_AVALIÁVEL** sem hora e fuso; ou só limite da notícia [CLOCK/G83] | Hora do programa **não é** hora do evento [#886] |

**Dois contrastes reproduzíveis:** no [G83](c241_fbis_plane_ledger_g83.json), 528 cruza o plano em **08/11 23:43:35Z** (ou 23:42:58Z no ramo com decaimento). Isso fica **13–14 min depois** do ramo FBIS GMT (23h30Z), mas **~107 min antes** do ramo Rio local (09/11 01h30Z). Para 637, as raízes de 08–09/11 estão depois do **dia** NASA 07/11 sob ambos os cortes civis hipotéticos. O dia NASA **não fornece hora terminal**. O relatório R68 e a [PR #1019](https://github.com/franklinbaldo/conde-incident/pull/1019) não fornecem sigma de hora do 528.

**Contagem lógica, não estatística:** 1: 2/3; 2: 3/4; 3: 0/3; 4: 0/3; 5: 0/3; 6: 0/3 cenários ilustrativos com seleção geométrica condicional (não são frequência de resultados em arquivos, nem chance de obter informação). Uma fonte com **hora independente e localização autenticada** (#884 itens **1, 2 ou 4**) pode discriminar mais diretamente. O item **5** pode resolver primeiro a convenção de transmissão; **3** melhora os estados orbitais, mas sozinho não fornece a hora. O roteiro extra não tem acervo identificado. A [matriz JSON detalhada](c241_document_decision_g84.json) traz, por cenário, duas células e seus IDs de fonte.

**Contrato negativo:** `historical_event_time_utc=null`; `verified_fbis_clock=null`; `orbit_exclusion_licensed=false`; `physical_compatibility_licensed=false`; `active_constraint=false`; `posterior=false`; `impact_probability=null`. Os 34 registros do G83 não mudaram e nenhuma nova simulação foi feita. **Nenhuma das seis fontes ainda ausentes permite agora declarar 528, 637 ou nenhum objeto fisicamente compatível.** Fontes: [#884](https://github.com/franklinbaldo/conde-incident/issues/884), [#871](https://github.com/franklinbaldo/conde-incident/issues/871), [#886](https://github.com/franklinbaldo/conde-incident/issues/886), [#870](https://github.com/franklinbaldo/conde-incident/issues/870); matriz de fontes detalhadas no JSON.

---
title: "O número sem testemunha saiu da simulação"
date: "2026-11-12"
summary: "A equipe já sabia que dois ângulos orbitais entravam em conflito. A novidade é que o simulador finalmente deixou de usar como referência o valor sem proveniência. A troca melhora a rastreabilidade, mas ainda não revela onde o objeto caiu."
chapter: "15"
author: "Coruja · Caderno de investigação"
status: "Correção operacional auditada nas PRs #83–84; TLE secundário, trajetória terminal e impacto não demonstrados"
---

# O número sem testemunha saiu da simulação

**O que acontece quando uma simulação começa com um número que ninguém consegue atribuir a uma observação?** Um mapa pode continuar parecendo convincente. As contas podem produzir decimais, horários e distâncias. Mas o problema está antes do primeiro cálculo: qual dado autorizou o programa a escolher aquela órbita?

O [capítulo 12](https://github.com/franklinbaldo/conde-incident/pull/62) apresentou a contradição: dois vetores atribuídos ao NORAD 528 traziam ascensões retas do nó ascendente (RAANs) separadas por **85,6259°**, embora suas épocas diferissem por apenas **16,132608 segundos**. Sob as premissas então testadas, deslocar o relógio não explicava a divergência. **Não se descobriu qual vetor foi medido em 1963.** Nos capítulos seguintes, o Caderno acompanhou testes de previsão sobre um espelho orbital. Agora houve outra mudança, concreta e diferente: **o próprio programa deixou de empregar o ângulo sem fonte como entrada operacional do 528**.

## Primeiro, o número que estava dirigindo o cálculo

O arquivo histórico do projeto continha **RAAN 284,1520°** no vetor legado do objeto 528. Esse valor não vinha acompanhado de um par original de elementos com custódia instrumental, época e referencial autenticados. A crítica documental não dependia de provar que o ângulo era fisicamente impossível: bastava reconhecer que **não havia documentação suficiente para tratá-lo como observação histórica**.

A 🐢 [Tartaruga isolou o par TLE literal na PR #83](https://github.com/franklinbaldo/conde-incident/pull/83), integrando-o ao repositório como [arquivo preservado de duas linhas](https://github.com/franklinbaldo/conde-incident/blob/main/research/tle_custody/mirror_528_1963-10-27.tle). O par corresponde ao **NORAD 00528**, com época **27 de outubro de 1963, 14:40:16,132512 UTC**, inclinação **81,8615°**, excentricidade **0,0017147**, RAAN **198,5261°** e movimento médio **15,74901460 revoluções/dia**. O SHA-256 do conteúdo preservado é `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`.

Esses campos não surgiram de um radar consultado agora. O par foi recuperado de um [**espelho secundário atual**](https://www.itau.magnetic-declination.com/satellite/?s=528), e valores da mesma linhagem aparecem no [espelho numérico oxzoid, revisão fixa `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet). A [matriz cumulativa, C179 e C181](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md), já advertia que **um checksum válido verifica o formato, não a autenticidade de uma estação de rastreamento em 1963**. E o formato retrospectivo TLE não transforma a linha em fac-símile contemporâneo.

Era uma escolha entre dois graus de rastreabilidade desiguais: um vetor legado sem origem demonstrada e outro que ao menos podia ser **reproduzido, confrontado e citado**. Nenhum dos dois, por esse motivo isolado, oferece um estado físico certificado com incerteza conhecida.

## A mudança ocorreu no código, não no céu

A novidade da [**PR #84, agora integrada à `main`**](https://github.com/franklinbaldo/conde-incident/pull/84) é verificável em três lugares: as [constantes TypeScript](https://github.com/franklinbaldo/conde-incident/blob/main/src/lib/constants.ts), a [reconstrução exploratória Python](https://github.com/franklinbaldo/conde-incident/blob/main/norad528_reconstruction.py) e o [script Python exportado](https://github.com/franklinbaldo/conde-incident/blob/main/src/lib/pythonScriptExport.ts). Os três passaram a usar, para o 528, **RAAN 198,5261°** e os demais elementos do mesmo par preservado, em lugar de continuar operando com **284,1520°**.

| Questão | Antes da correção | Depois da PR #84 |
| --- | --- | --- |
| Referência operacional do 528 | Vetor legado com **284,1520°**, sem fonte primária rastreada | Par TLE **secundário** preservado, com **198,5261°**, época e hash |
| Elementos dos objetos 527 e 529 na interface | Valores ilustrativos sujeitos a leitura como medições | Identificados explicitamente como **hipóteses** sem par TLE primário |
| Local e horário de reentrada | Não demonstrados pelos dados | **Continuam não demonstrados** |

A [documentação da correção](https://github.com/franklinbaldo/conde-incident/blob/main/research/OPERATIONAL_528_REFERENCE.md) é cuidadosa: a mudança não declara que o valor antigo era impossível, mas o **retira da operação ativa** por falta de fonte. A versão histórica permanece no Git, disponível para auditoria. O [teste de regressão da PR #84](https://github.com/franklinbaldo/conde-incident/blob/main/tests/test_orbital_constants_provenance.py) exige correspondência textual entre os campos usados e o TLE preservado; também confere que os vetores 527/529 sejam classificados como hipóteses.

Essa regressão e a [integração no HEAD da PR #84](https://github.com/franklinbaldo/conde-incident/actions/runs/43208556432) tiveram resultados verdes. **O teste confirma que o código usa a fonte declarada, não que a fonte seja uma medição primária ou que a trajetória resultante esteja calibrada.**

## Por que uma origem melhor não é uma órbita final

Se uma cópia secundária informa **198,5261°** e outra repete esse valor, não surgem duas testemunhas independentes. Ambas podem reproduzir o mesmo rastreamento antigo, cuja cadeia até o equipamento original ainda não foi recuperada. O [registro C179](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md) distingue precisamente a recuperação moderna dos parâmetros de sua autenticidade histórica.

Há também uma armadilha temporal. A última época preservada para o 528 é de **27 de outubro**, enquanto a [NASA, *Satellite Situation Report*, 15/11/1963, página impressa 8 (página 10 do PDF)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), registra o objeto **1963 3B** com **8 NOV 63** na lista de decaimentos. O fac-símile é prova documental de que essa data constava no boletim de 1963; não contém hora de reentrada, posição terminal ou fragmento recolhido.

Do outro lado está o [FBIS 03, documento EOP-UAP-D001, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): uma transcrição da notícia da Rádio Tupi sobre uma esfera em Conde. **Ela comprova a circulação do relato, não a esfera, a cratera ou um impacto.** NASA e FBIS preservam informações de naturezas distintas; a coincidência de calendário não constrói um elo físico.

Até mesmo os programas corrigidos permanecem **exploratórios**. A planilha ou o script pode extrapolar uma órbita de outubro até novembro sob hipóteses atmosféricas, fases e simplificações escolhidas pelo pesquisador. Isso não transforma posições simuladas, faixas ou porcentagens em observações. Um código que passou a ler melhor sua fonte ainda precisa demonstrar erros, estabilidade numérica, autenticidade dos insumos e validação fora da amostra.

## O que mudou desde o capítulo 14

O capítulo anterior mostrou que **alterar a elegibilidade de uma única previsão** modifica um placar estatístico. Este mostra uma mudança de natureza diferente: **alterar a proveniência exigida de uma entrada muda o que o simulador tem o direito de chamar de referência**. A investigação não descobriu uma passagem sobre Conde. Ela retirou do seu fluxo operacional um ângulo que não conseguia sustentar documentalmente e registrou a origem secundária do substituto. É correção de método, não descoberta da posição de um satélite.

O encadeamento de evidência fica explícito: **C179/C181** documentam o par moderno atribuído ao 528 e os limites do formato; **C197/C201** documentam o dia registrado pela NASA e a dependência de catálogos; **C01–C03** preservam a notícia retransmitida, sem testemunha física independente. O [confronto C241-T10 da PR #14](https://github.com/franklinbaldo/conde-incident/pull/14) explica por que a diferença entre os RAANs não podia ser atribuída simplesmente aos dezesseis segundos. A nova PR #84 **não cria ocorrência orbital primária**, não acrescenta uma restrição Lean 4.35.0 baseada em medição certificada, nem demonstra um domínio físico admissível mais estreito. Fixar um parâmetro **para executar o software** não é provar que esse parâmetro era o verdadeiro estado histórico.

O próximo teste não é escolher o ângulo mais convincente para desenhar um mapa. É recuperar a **origem instrumental e a transformação de referencial dos elementos do 528**, de preferência com observações próximas de novembro e covariâncias, e confrontar previsões posicionais cegas com os registros dos objetos 527/529. Se esses dados excluírem Conde, a hipótese deve cair; se forem compatíveis, ainda faltará testar impacto e fragmentos. **Por ora, o código ganhou uma fonte rastreável. O lugar da reentrada continua sem testemunha.**

---

**Ficha de proveniência e limites:** [C179/C181](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md) (espelho moderno e verificação de formato); [C197/C201](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md) (boletim NASA contemporâneo, não terminal observado); [C01–C03](https://github.com/franklinbaldo/conde-incident/blob/main/research/evidence_matrix_C001-C238_2026-11-11.md) (uma cadeia jornalística Tupi→FBIS). [PR #83](https://github.com/franklinbaldo/conde-incident/pull/83) e [PR #84](https://github.com/franklinbaldo/conde-incident/pull/84), com [teste da referência operacional](https://github.com/franklinbaldo/conde-incident/blob/main/tests/test_orbital_constants_provenance.py); [C241-T10, PR #14](https://github.com/franklinbaldo/conde-incident/pull/14) permanece análise condicional do conflito, não observação independente. **Fonte de 1963 diretamente cotejada nesta rodada:** [NASA, folha impressa 8/PDF p. 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) e [FBIS 03, p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf). **Ausentes:** TLE primário do 528 com referencial/covariâncias, trilha instrumental terminal, identificação de destroços e validação de um impacto em Conde. **Resultado: indeterminado.**

# 🦅 Gavião: Caderno 13 / C243-T12, contraprova independente

**Issue #16; reportagem [PR #65](https://github.com/franklinbaldo/conde-incident/pull/65); base herdada #63.** Esta auditoria não edita o capítulo, não publica e não integra. Parecer factual condicionado ao resultado do replay independente no SHA final.

## 1. Autenticidade documental, grau e independência

- [NASA, Satellite Situation Report de 15/11/1963, p. impressa 8 / PDF página 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), imagem reinspecionada em 12/11: objeto 1963 3B, decaimento catalogado em 8 NOV 63, **sem hora/local**. C131/C197 são ocorrências do mesmo documento.
- [FBIS 03, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), imagem reinspecionada em 12/11: RADIO TUPI RIO, 8 NOV 63; é **relato radiofônico transcrito**, não prova de queda física. C01/C02 são uma cadeia, não observações independentes.
- [Espelho oxzoid/Space-Track 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. **Secundário, uma só linhagem**. Não autentica os TLEs originais, o referencial, o erro instrumental nem a identidade do objeto supostamente caído.

## 2. Consistência matemática e limites de Lean

Não há premissa empírica primária nova a habilitar a formalização Lean 4.35.0 de uma trajetória física. Um teste de previsão de movimento médio do catálogo não produz conjunto físico admissível não vazio e reduzido. Mesmo uma prova condicional de álgebra não autentica suas premissas observacionais.

## 3. Auditoria numérica independente e nota G13-E1

O [script Texugo pinado no SHA d31b864](https://github.com/franklinbaldo/conde-incident/blob/d31b86486283adb1fad5764285b16b2e73d07439/tools/texugo_holdout_529.py) calcula secante e OLS usando **somente** histórico 529 em suas fórmulas. **Entretanto o gate de elegibilidade dos alvos exige três épocas anteriores do 529 e três épocas anteriores de CADA doador 527 e 528.** Assim, “apenas dois registros” descreve os operandos da secante, **não os requisitos do conjunto avaliado**. Recomendar uma frase precisa no capítulo 13 sem descaracterizar a surpresa narrativa.

A ferramenta nova, tools/gaviao_ch13_recency_audit.py, **não importa a implementação Texugo**. Baixa o Parquet pinado por digest, lê datas UTC com resolução real, colapsa duplicatas idênticas e rejeita conflitantes, reproduz a elegibilidade por doadores, calcula independente a secante de dois pontos, a regressão OLS centrada de três pontos e a persistência, todos no mesmo alvo. Compara o RMSE histórico com os três números publicados C243-T12 e a contagem de 53 candidatos, 51 avaliados e 2 NOT_RUN. Seus diagnósticos adicionais, ainda a validar no CI, são RMSE por horizonte disjunto, deleção de um alvo sem reotimização e maior participação na soma dos erros quadráticos. São **análises retrospectivas pós-hoc**, não testes de significância ou evidência independente; a janela foi concebida após os resultados T10/T11.

A [reportagem #65](https://github.com/franklinbaldo/conde-incident/pull/65) tem a distinção principal correta: uma boa previsão do próximo movimento médio catalogado **não é** previsão posicional nem modelagem física conjunta. A ressalva G13-E1 serve para não sugerir que dois registros isolados bastariam para executar todo o protocolo ou obter as mesmas 51 pontuações. As famílias quadrático e transferência são citadas a partir do replay Texugo e não foram reimplementadas por este auditor.

## 4. Inferência de exclusão / identificação

Sem NORAD primário com proveniência, frame e covariância; sem medida de posição terminal, simulador calibrado, holdout posicional ou objeto no solo autenticado. Resultado físico: **Conde indeterminado**. O conflito entre RAAN legado 284,1520° e 198,5261° secundário segue sem genealogia instrumental. Uma reentrada catalogada não demonstra impacto.

**Pendente:** consultar o workflow independente no HEAD final para fixar resultados/horizontes; informar G13-E1 na PR #65. A [PR #3](https://github.com/franklinbaldo/conde-incident/pull/3) ainda implementa Zola, incompatível com a decisão SSG Rust da [PR #22](https://github.com/franklinbaldo/conde-incident/pull/22). CI editorial verde não libera a arquitetura. Sem merge, deploy, contatos ou alteração de blog pessoal.


## Resultado efetivo do replay independente no corpus pinado (12/11/2026)

O [workflow G13 #43194855578](https://github.com/franklinbaldo/conde-incident/actions/runs/43194855578), executado no SHA de implementação 1a474361da3417faac3686a635bc5171e035c078, concluiu **SUCCESS**: 12/12 testes sintéticos adversariais, download Parquet com SHA-256 conferido, leitura independente, 53 candidatos / **51 alvos pontuados e dois NOT_RUN**, reprodução das três famílias numéricas. Artefato JSON com previsões e erros por alvo: [#13932641520](https://github.com/franklinbaldo/conde-incident/actions/runs/43194855578/artifacts/13932641520), digest ZIP SHA-256 1f1e6bdeec9d0aa765ca16b2e67c60c2962811154e7937a1fb28cb747ac3cbac.

**RMSE agregado independente (rev/dia):** secante 2 pontos 0,0109350674861, OLS 3 pontos 0,0145442475385, persistência 0,0269039352225. Concordam com os valores C243-T12 publicados.

| Horizonte até próxima época 529 | Alvos | Secante 2 | OLS 3 | Persistência |
|---|---:|---:|---:|---:|
| Até 1 dia | 2 | **0,01428507** | 0,03763420 | 0,03943882 |
| >1 até 7 dias | 31 | **0,01289445** | 0,01547540 | 0,03068191 |
| >7 até 30 dias | 18 | 0,00545670 | **0,00543395** | 0,01602309 |
| >30 dias | 0 | NOT_RUN | NOT_RUN | NOT_RUN |

**Achado G13-E2:** a secante mantém vantagem sobre a persistência nos três estratos examinados, mas **não é a melhor das duas retas locais no estrato >7–30 dias**, em que OLS de três épocas vence marginalmente (0,00543395 vs 0,00545670 rev/dia). Como o estrato foi analisado após os resultados, isso não demonstra seleção prospectiva nem superioridade generalizável. Qualificar a expressão “vencedora” como **agregada**, e não universal por horizonte.

A **deleção de cada um dos 51 alvos, sem reajuste**, manteve a secante melhor que persistência e OLS em 51/51 comparações cada. Todavia o erro quadrático da secante é concentrado: o registro catalogado em 1963-12-29T20:28:24.196512Z responde por **47,65%** da sua soma de erros quadráticos. Esses diagnósticos são compatíveis: maior contribuição individual não significa que remover esse registro inverta o ranking. Deleções sobrepostas não são réplicas independentes.

**Incidente do CI:** o primeiro workflow #43194708524 falhou por erro **no teste sintético do próprio auditor**: esperava 23 na persistência de um exemplo linear em que o último valor correto era 11. A implementação estava correta; alterei o teste para verificar secante/OLS 23 e persistência 11 no commit 1a474361. O replay histórico e os 12 testes passaram depois. A alteração documental deste relatório ainda exige **novo CI no SHA final**.

Conclusão em quatro eixos mantém as classes: documentos NASA/FBIS autenticam apenas registros administrativos/jornalísticos limitados; dados Parquet são numericamente verificáveis, porém não instrumentais originais; sem restrição física Lean ou domínio reduzido; sem propagação calibrada nem localização. **INDETERMINADO**.

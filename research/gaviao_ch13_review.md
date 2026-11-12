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

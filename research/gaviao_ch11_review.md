# 🦅 Auditoria independente do Caderno 11, C243-T10

**Escopo:** revisão da [PR #59](https://github.com/franklinbaldo/conde-incident/pull/59), continuação da issue [#16](https://github.com/franklinbaldo/conde-incident/issues/16) e da [PR #57](https://github.com/franklinbaldo/conde-incident/pull/57). A reportagem da Coruja **não** é alterada. Não é publicação, parecer de impacto ou descoberta de um corpo.

## 1. Autenticidade documental e dependência

| Documento e ID da matriz | Grau de verificação | Dependência e alcance |
| --- | --- | --- |
| [NASA Satellite Situation Report, 15/11/1963, p. impressa 8, PDF índice 9](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), C131/C197 | Fac-símile reinspecionado visualmente em 12/11/2026: entrada 1963 3B, coluna DECAY 8 NOV 63 | C131 e C197 apontam para uma mesma fonte; dia civil apenas, SEM hora, longitude ou impacto |
| [FBIS 03 / Rádio Tupi, 08–09/11/1963, p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), C01/C02 | Fac-símile reinspecionado visualmente em 12/11/2026: texto da *notícia* e cabeçalho 2330 8 NOV 63 W | Cadeia Tupi→FBIS, não observação direta nem confirmação de cratera, esfera, corpo ou localização orbital |
| [oxzoid/Space-Track, arquivo 1963 revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), C243-T10 | **Espelho secundário**: SHA-256 esperado `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; conferência integral dos bytes ocorrerá no workflow do HEAD final | Uma linhagem, sem TLE/radar instrumental primário. NORAD 527, 528 e 529 não equivalem a três sensores independentes |
| [Matriz cumulativa, ocorrência C243-T10, commit 054f605](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/evidence_matrix_C001-C238_2026-11-11.md) e [relatório Texugo](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/texugo_holdout_529.md) | **Resultado numérico publicado pela PR #20**, 53 alvos, 51 pontuados, 2 NOT_RUN; replay prévio [Actions #43172444338](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338) | Reporter, matriz, teste e relatório reproduzem **o mesmo** experimento; não são testemunhos independentes |

A [matriz histórica C01–C238 da PR #1](https://github.com/franklinbaldo/conde-incident/pull/1) foi consultada juntamente com os acréscimos C241/C243 da pilha científica. Conflito **RAAN 284,1520° versus 198,5261°** ainda sem proveniência instrumental reconciliada. Não criar outro ID histórico nem converter resultados de software em fatos físicos.

## 2. Método numérico e contraprova

O [novo verificador](../tools/gaviao_ch11_prequential.py) reconstrói a cada origem a previsão de **uma próxima época** do NORAD 529, independentemente do código Texugo, usando `numpy.linalg.lstsq` (SVD) em lugar do resolvedor de equações normais. Reabre o Parquet SHA-pinado por intermédio do leitor de custódia independente do Gavião da PR #57. O 529 futuro e as épocas doadoras 527/528 posteriores à origem ficam fora do treinamento; nenhum modelo usa o próximo valor observado antes de pontuar.

Seis modelos são pontuados **sobre os mesmos alvos**: persistência do 529, polinômio quadrático do 529, transferência isolada 528, curvatura média 527/528, transferência isolada 527 e linear do 529. Cada origem sem ao menos três épocas **em cada objeto** é explicitamente `NOT_RUN`; regressões singulares também não viram zeros. Testes adversariais sintéticos verificam vazamento temporal, duplicatas, valores inválidos, origem UTC, ranking pareado e fechamento de inventário.

**Critérios numéricos a testar no HEAD final:** 53 alvos possíveis / 51 avaliados / 2 não executados; erros RMSE rev/dia de 0,026903935 (persistência), 0,074988368 (quadrático), 0,079369300 (528), 0,097122160 (média), 0,116988818 (527), 0,117357459 (linear); quadrático melhor em erro absoluto em 33/51, média em 18/51, zero empate. Estes valores são **do resultado Texugo**, e não devem ser atribuídos ao novo verificador antes do workflow verde no SHA real.

**Diagnóstico adicional e refutável:** os intervalos entre épocas são desiguais. O novo script registra o horizonte real de cada passo, agrupa as pontuações em até 1 dia, (1,7], (7,30] e >30 dias e calcula RMSE com os mesmos alvos dentro de cada grupo. Esse teste impede atribuir a vitória do baseline à mera etiqueta `next epoch` sem examinar a distância temporal. Os grupos são diagnósticos **pós-hoc**, não intervalos de confiança ou testes independentes. Não há garantia de que cada grupo possua observações; grupo vazio fica explícito.

**Controle de ciência versus propaganda:** o capítulo 10 C243-T9 usava *quatro cortes com horizonte potencialmente longo*, e o C243-T10 *rolling origin* com um único próximo catálogo. Não é comparação controlada mantendo a mesma distribuição de horizontes e treinamento. Assim, a expressão "inversão do placar" só é válida **com a mudança de desenho**, não como prova de mecanismo físico ou de superioridade universal da persistência.

## 3. Coerência Lean 4.35.0, física e inferência

Não há novo documento de observação orbital primária com época, frame, covariância e sensor. Os coeficientes quadráticos do movimento médio catalogado **não constituem** restrições instrumentais de estado r/v. Portanto, a cadeia proposta na PR #28 se interrompe antes da premissa física rastreável, do domínio orbital reduzido e não vazio, e do simulador terminal com erros/holdout. As provas Lean existentes certificariam apenas implicações **condicionais** às premissas inseridas, não autenticidade do espelho.

Não há medição posicional, desacoplamento instrumental provado, teste terminal ou localização. O conjunto de saídas científicas continua aberto; com as evidências atuais, **Conde permanece INDETERMINADO**. Nem uma reentrada orbital bem datada demonstraria impacto no solo.

## 4. Parecer editorial e gate

A reportagem #59 apresenta uma **novidade identificável** desde o capítulo 10: o teste negativo prequential C243-T10 com baseline de persistência. A prosa preserva `NOT_RUN`, o caráter pós-hoc, intervalos irregulares e ausência de causalidade entre NASA e FBIS. Os valores tabulados coincidem com o registro C243-T10 e estão ligados a commits estáveis. Recomenda-se manter a distinção entre *próximo registro* e *intervalo curto fixo*: uma previsão para a próxima época não equivale necessariamente a uma previsão para amanhã.

A PR #59 permanece draft e empilhada sobre #56; #56 depende da base #3, ainda divergente da decisão SSG Rust #22. A aprovação documental não supre CI verde ou a reconciliação arquitetural. Apenas 🐘 Elefante integra. Nenhum merge, publicação, contato externo nem edição do blog pessoal é autorizado.

**Gate desta PR de auditoria:** executar os testes sintéticos e o replay independente real no **SHA do último commit** via `.github/workflows/gaviao-ch11-independent.yml`, preservar JSON com a separação por horizonte e registrar resultado observado na memória final. Até o run, os novos números derivados são **NOT_VERIFIED**.

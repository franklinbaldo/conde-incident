# Gavião: revisão científica independente do Caderno 14

**Escopo:** issue #16, capítulo 14 na PR #68, Texugo #20, auditoria anterior Gavião #66. Esta fatia não altera reportagem, não publica e não integra; sua base é a PR #66.

## 1. Autenticidade, proveniência e independência

O replay numérico usa os bytes da revisão 4b4fb3a do espelho **secundário** oxzoid/Space-Track de 1963, SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09:
https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet

A avaliação T13 deriva da mesma linhagem que T12 e T10; calcular três modelos ou repetir a extração não cria três sensores nem prova autenticidade instrumental. Referências contemporâneas do capítulo: boletim NASA de 15/11/1963, página impressa 8 (PDF página 10), NTRS 19640001198, C131 e C197 são ocorrências da mesma fonte, que registra dia de decaimento sem hora/local: https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10. FBIS EOP-UAP-D001, página 1, C01/C02, retransmite notícia da Rádio Tupi, não uma inspeção de impacto: https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf. **Os fac-símiles foram analisados em rodadas anteriores e NÃO reinspecionados visualmente nesta fatia.**

## 2. Restrição Lean 4.35.0

A adição de uma época elegível ao modelo não constitui observação orbital independente. Nenhum novo referencial, elemento orbital primário com covariância ou limite numérico permite criar restrição Lean física autenticada ou reduzir domínio físico não vazio. Um teorema de elegibilidade é condicional aos dados de entrada. **Nenhuma nova prova Lean é alegada nesta PR.**

## 3. Método numérico falsificável

O verificador independente usa o leitor e validador de duplicatas desenvolvidos por Gavião na #66, mas **nenhum algoritmo nem JSON de resultados do Texugo**. Reabre o Parquet SHA-pinado e calcula três estratégias a partir somente do 529 estritamente anterior a cada alvo: persistência com 1 observação, secante com 2 e OLS centrada com 3, usando diferenças de época reais em segundos. Separa a elegibilidade do modelo da exigência conjunta original de três épocas anteriores de cada objeto 527, 528 e 529. Confere 54 épocas, 53 oportunidades, 53/52/51 avaliadas por modelo, 51 comuns, duas datas extras e RMSE de cada universo contra C243-T13.

**G14-I1, novo controle de concentração:** os RMSE publicados para a secante, 0,0109350675 em 51 épocas versus 0,0141676275 em 52, implicam algebricamente que o resíduo absoluto da época acrescida de 7/02/1963 vale cerca de **0,0658723 revoluções/dia**. Essa única época responde por cerca de **41,57% dos erros quadráticos** do universo de 52 e gera aumento de **29,56% no RMSE** ante os 51. O programa confronta essa identidade com o resíduo individual efetivo do Parquet. Antes do Actions verde no HEAD final, tais cifras derivadas são **previsões a confirmar**, não uma medição revisada. São métricas descritivas, não significância estatística, causalidade ou trajetória.

Controles sintéticos adversariais cobrem: intervalos irregulares, ausência de doadores, suportes não pareados, duplicatas, valores não finitos, origem cronológica e vazamento do valor alvo. O verificador rejeita números publicados incompatíveis, em vez de procurar um placar favorável. **Comparação de RMSE com 51 e 52 alvos distintos não pode ser classificada como vitória pareada.**

## 4. Limites de exclusão, identificação e publicação

A reportagem #68 apresenta delta real em relação a #65 e não atribui a fevereiro um novo evento físico. Não existe domínio orbital autenticado e reduzido, conjunto de envelopes de erro terminal, integração física calibrada com holdouts ou prova de queda ou exclusão de Conde. **CONDE = INDETERMINADO.** A PR #3 segue com Zola, enquanto a PR #22 estabelece decisão Rust SSG; build editorial verde não sana esse conflito nem autoriza deploy. Autoaprovação formal pelo proprietário pode ser vedada pelo GitHub.

**Próxima dúvida concreta:** recuperar fonte primária instrumental do registro de 7/02, covariâncias e quadro; fixar coortes/horizontes antes de novas comparações, incluindo casos em que a secante perde.

**Validação:** exigir GitHub Actions no SHA exato da branch G14 após todos os arquivos, memória OKF incluída. Não contar como CI próprio o CI da T13 nem um merge sintético.

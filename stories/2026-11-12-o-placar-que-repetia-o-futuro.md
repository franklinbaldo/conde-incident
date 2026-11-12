---
title: "O placar que repetia o futuro"
date: "2026-11-12"
summary: "Quatro testes de previsão pareciam oferecer 93 avaliações do futuro do NORAD 529. Eram apenas 28 épocas distintas, reutilizadas em janelas sobrepostas. O novo confronto preservou uma melhora pequena, mas revelou de onde ela vinha e o que não prova."
chapter: "10"
author: "Coruja · Caderno de investigação"
status: "C243-T8/T9: recontagem pós-hoc do espelho secundário; revisão independente pendente; sem inferência de impacto"
---

# O placar que repetia o futuro

**E se a previsão que parecia vencer três testes estivesse enfrentando várias vezes as mesmas observações?** A hipótese de usar dois objetos de um lançamento para ajudar a prever um terceiro já havia passado por quatro confrontos. A transferência de uma **curvatura ajustada à série temporal do movimento médio** de 527 e 528 para o **NORAD 529** melhorara três resultados e piorara um. Um placar animador, à primeira vista. Mas o 🦡 Texugo resolveu perguntar quantas datas diferentes realmente estavam por trás dele.

A resposta trouxe uma surpresa menos vistosa que uma órbita desenhada no mapa, e mais importante para julgar qualquer mapa futuro: **93 avaliações correspondiam a apenas 28 épocas distintas**. O experimento havia olhado o mesmo futuro repetidas vezes.

## Quatro portas para o mesmo período

No [capítulo 03](https://github.com/franklinbaldo/conde-incident/pull/26), vimos os quatro cortes temporais do [teste C243, PR #20](https://github.com/franklinbaldo/conde-incident/pull/20): 31 de agosto, 28 de setembro, 11 de outubro e 21 de outubro de 1963. Em cada corte, o modelo usa apenas épocas anteriores para ajustar suas curvas e tenta prever o movimento médio posterior do 529, uma grandeza expressa em revoluções por dia.

Isso protege cada ajuste contra o uso de dados futuros **naquele corte**. Não resolve outro problema: os quatro conjuntos de dados reservados para avaliação se sobrepõem. Uma época posterior a 21 de outubro aparece também no futuro dos três cortes anteriores. A [auditoria **C243-T8**](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/evidence_matrix_C001-C238_2026-11-11.md), feita sobre o arquivo histórico secundário, contou **28 + 24 + 21 + 20 = 93 pontuações**, mas somente **28 datas futuras únicas**.

Não eram 93 medições independentes e tampouco 93 acertos. Eram pontuações repetidas sobre uma coleção pequena de épocas catalogadas, usada em experiências retrospectivas relacionadas. Quatro placares não são automaticamente quatro confirmações.

## A contagem sem repetições

O Texugo então executou a contraprova **[C243-T9](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/texugo_holdout_529.md)**. Em vez de descartar os modelos, manteve o ajuste de cada corte com seu passado e dividiu o futuro em **quatro trechos sem sobreposição**. Cada época foi pontuada uma única vez. O resultado, reexecutado sobre o Parquet pinado, não forneceu a absolvição nem a condenação simples que um título apressado poderia prometer.

| Trecho futuro do 529 | Épocas únicas | Erro do modelo quadrático | Erro da média 527+528 |
| --- | ---: | ---: | ---: |
| Após 31/08, até 28/09 | 4 | **0,010525** | 0,011014 |
| Após 28/09, até 11/10 | 3 | 0,010712 | **0,009849** |
| Após 11/10, até 21/10 | 1 | 0,018127 | **0,016583** |
| Após 21/10 | 20 | 0,223237 | **0,215117** |
| **Agregado, cada época uma vez** | **28** | **0,188775** | **0,181910** |

Os valores são **RMSE de movimento médio, em revoluções por dia**, não quilômetros de erro posicional. O menor erro está destacado em cada trecho. No **primeiro**, a transferência piora a previsão. No terceiro, a aparente vitória é sustentada por **uma única época**. E **20 das 28 datas** estão concentradas no último trecho. A [contraprova independente do Gavião, PR #57](https://github.com/franklinbaldo/conde-incident/pull/57), mostrou uma concentração ainda maior do que a contagem sugere: **aproximadamente 99,9% da soma dos erros quadráticos** de cada modelo provêm desse trecho, bem como **aproximadamente 99,9% da diferença** dessas somas entre o quadrático e a média. Trata-se de uma decomposição aritmética *posterior* dos resultados do mesmo experimento, não de novos registros, independência ou significância estatística.

A média dos doadores continuou com erro agregado um pouco menor que o quadrático, **0,181909995 contra 0,188775134 rev/dia**. Portanto a remoção da dupla contagem não apaga toda a vantagem descritiva. Ela revela algo mais sutil: **a vantagem não é uniforme no tempo e sua pontuação total depende fortemente do trecho final**. Uma segunda escolha examinada retrospectivamente, usar só a curvatura do 528, produziu **0,145072060 rev/dia** no agregado; escolher a vencedora depois de ver o futuro não equivale a prever de forma cega.

O [código reprodutível](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/tools/texugo_holdout_529.py) verifica a partição, conta épocas distintas, preserva casos `NOT_RUN` e compara os modelos sem reaproveitar uma mesma data no agregado. No [GitHub Actions #43166235928](https://github.com/franklinbaldo/conde-incident/actions/runs/43166235928), no **SHA `74ff98f8`**, o replay real e os testes passaram; a execução anterior [#43165959868](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868) registrou **115 testes Python aprovados** e o [artefato com os resultados](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868/artifacts/13920171288). Verificação de programa não é autenticação de radar.

## A pergunta que esses números não respondem

O arquivo utilizado é o [espelho numérico oxzoid/Space-Track de 1963, revisão `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. Os três objetos provêm de **uma mesma linhagem secundária de catálogo**; não são três sensores independentes. As 28 épocas distintas tampouco viraram 28 testemunhas independentes ao serem contadas corretamente. Os cortes, os modelos alternativos e esta reanálise são **retrospectivos**, não uma validação prospectiva pré-registrada.

Há duas perguntas diferentes, e nenhuma deve responder pela outra. **A transferência ajuda a prever o movimento médio nesse arquivo e nesse desenho?** Às vezes: o agregado melhora um pouco, o primeiro trecho piora e os resultados não são uniformes. **Os objetos mantiveram uma relação física que permite reconstruir a posição do 528 em sua reentrada?** Esse teste não mede posições, sincronismo, fase orbital ou forças acopladas. Não oferece uma resposta.

Reinspecionei em imagem a [página impressa 8 do *Satellite Situation Report* da NASA, de 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10). O documento contemporâneo registra **1963 3B** na lista de decaimentos em **8 NOV 63**, sem hora, fuso demonstrado ou localização. As ocorrências [C131 e C197](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md) remetem à **mesma fonte NASA**, não a duas observações independentes. Também reinspecionei a [página 1 do FBIS 03](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), ocorrência **C01–C02**: é transmissão da notícia atribuída à Rádio Tupi sobre Conde, não medição do 528 nem comprovação de impacto. Essas duas cadeias documentam assuntos diferentes.

## O que mudou desde o capítulo 09

A descoberta anterior era um **arquivo orbital com grandes lacunas** entre as épocas catalogadas. Agora a auditoria encontrou um problema **na maneira de contar os resultados de previsão**: 93 pontuações se apoiavam em só 28 datas. A contraprova C243-T9 removeu a repetição no placar, preservou a piora no primeiro período e mostrou quanto o último período determina o resultado agregado.

A conclusão formalmente permitida é **condicional ao espelho com hash fixado, ao desenho pós-hoc e à implementação auditada**: nesse conjunto, os quatro futuros aninhados têm 28 épocas distintas e a comparação disjunta produz os erros relatados. Isso **não é** um teorema Lean 4.35.0 de posição, nem demonstra um domínio físico não vazio e reduzido de trajetórias. Nenhum novo TLE instrumental primário, intervalo de erro dinâmico, simulação de reentrada, hora ou lugar terminal foi obtido. As alternativas **Conde excluído, Conde exigido ou outro local demonstrado** permanecem sem suporte; a resposta física continua **indeterminada**. Mesmo localizar uma reentrada não provaria um impacto no solo.

**A próxima contraprova é perguntar se a vantagem persiste quando mudamos o objeto-alvo, em vez de escolher retrospectivamente aquele em que o modelo pareceu funcionar.** E, para sair do placar numérico e entrar na história física, a investigação ainda precisa de elementos originais com época, referencial, erro e proveniência, capazes de confrontar posições sem escolher Conde como destino.

---

**Ficha de rastreabilidade:** [C243-T8/T9 na matriz cumulativa da PR #20](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/evidence_matrix_C001-C238_2026-11-11.md), [relatório de holdout](https://github.com/franklinbaldo/conde-incident/blob/74ff98f808f8657bdd9b3aa3445e7a732858d074/research/texugo_holdout_529.md), [commit com replay verificado `dea14a0b`](https://github.com/franklinbaldo/conde-incident/commit/dea14a0ba0691cbe15490e194e8a0d21721530d7), [CI final da origem #43166235928](https://github.com/franklinbaldo/conde-incident/actions/runs/43166235928) e [Parquet secundário fixado](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet). **Estado de verificação:** numérico reexecutado sobre o espelho e código; fonte instrumental primária/épocas e erros originais NÃO RECUPERADOS; revisão editorial independente 🦅 e integração 🐘 pendentes. **Sem nova inferência geográfica.**

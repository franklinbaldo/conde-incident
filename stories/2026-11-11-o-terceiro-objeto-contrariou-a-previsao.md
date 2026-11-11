---
title: "O terceiro objeto contrariou a previsão"
date: "2026-11-11"
summary: "O primeiro confronto temporal com dados de 1963 deu três melhorias pequenas e uma piora. Os objetos 527 e 528 não ajudam sempre a prever o 529."
chapter: "03"
author: "Coruja · Caderno de investigação"
status: "Teste numérico retrospectivo em espelho secundário; reentrada não localizada"
---

# O terceiro objeto contrariou a previsão

**Se três objetos partiram no mesmo lançamento, os movimentos de dois deles permitem prever melhor o futuro do terceiro?** A pergunta parecia oferecer uma saída para o impasse do [capítulo anterior](https://github.com/franklinbaldo/conde-incident/blob/e23e1b7ec748171d5f3874e477406188de50ad6b/stories/2026-11-11-uma-orbita-sem-endereco.md). O NORAD 528 deixou a órbita em novembro de 1963; os objetos 527 e 529 continuaram circulando. Talvez os sobreviventes guardassem vestígios de uma dinâmica comum.

Agora a hipótese encontrou algo que faltava: um confronto numérico com registros datados que **não foram usados para ajustar as previsões**. O resultado não foi uma confirmação uniforme. Em um dos quatro cortes, o modelo que aproveitava os companheiros previu **pior** do que aquele que examinava apenas o próprio 529.

## Antes de perguntar ao satélite, verificar o arquivo

O teste só é tão confiável quanto a origem dos números. A [Tartaruga, na PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), auditou um [arquivo Parquet de elementos orbitais de 1963](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), publicado como **espelho secundário** de um histórico atribuído ao Space-Track. O arquivo, fixado por SHA-256, apresentou **21, 45 e 57 linhas** para 527, 528 e 529, respectivamente; descontadas repetições de época, são **20, 45 e 54 épocas distintas**. A [execução de custódia no GitHub Actions](https://github.com/franklinbaldo/conde-incident/actions/runs/43106556030) verificou os bytes e os controles numéricos.

Isso é um ganho de rastreabilidade, não a recuperação dos registros brutos dos radares. O Parquet reúne valores numéricos; não entrega os pares originais completos de cada TLE de época, o instrumento de observação ou uma cadeia arquivística primária de 1963. Também não constitui três fontes independentes: todos os objetos aparecem dentro da mesma linhagem de catálogo.

A auditoria trouxe uma correção operacional importante. O simulador usava para o 528 um nó ascendente de **284,1520°**, sem origem primária verificável. A Tartaruga passou a usar um par secundário preservado com **198,5261°**, época **27 de outubro de 1963, 14:40:16 UTC**, cujos campos concordaram com o Parquet dentro do arredondamento. A divergência histórica de **85,6259°** permanece registrada, não foi resolvida por votação entre dois números. A custódia e o desacordo estão em [C240–C241, PR #14](https://github.com/franklinbaldo/conde-incident/pull/14).

## Uma previsão que precisava aceitar a derrota

Na [PR #20](https://github.com/franklinbaldo/conde-incident/pull/20), o Texugo formulou uma comparação deliberadamente modesta. A medida prevista é o **movimento médio**, em revoluções por dia: quantas voltas por dia descrevem os elementos catalogados. Não é latitude, longitude nem posição cartesiana.

O primeiro competidor ajusta uma curva quadrática apenas ao histórico do **529** disponível até determinada data. O segundo estima a curvatura separadamente com **527 e 528**, toma a média dos dois coeficientes e transfere somente essa curvatura ao 529; o 529 ainda fornece seus próprios valores anteriores ao corte para ajustar o restante. Os dois tentam então prever registros **posteriores** do 529. A ferramenta inclui uma transferência de sinal deliberadamente invertido como controle negativo e impede que datas futuras entrem no treino.

Foram usados quatro cortes de 1963. O erro abaixo é o **RMSE do movimento médio**, em revoluções por dia; menor é melhor:

| Última data de treino (UTC) | Registros futuros do 529 | Só o 529 | Com curvatura dos vizinhos |
| --- | ---: | ---: | ---: |
| 31 de agosto | 28 | **0,210299** | 0,211762 |
| 28 de setembro | 24 | 0,216540 | **0,214537** |
| 11 de outubro | 21 | 0,223016 | **0,219896** |
| 21 de outubro | 20 | 0,223237 | **0,215117** |

A primeira linha é a mais reveladora. A transferência de curvatura **aumentou** o erro em aproximadamente **0,001463 rev/dia**. Nos três cortes posteriores ela o reduziu, mas por diferenças pequenas, e os conjuntos futuros se sobrepõem. Não são quatro experimentos instrumentais independentes, não houve teste de significância e ninguém pode selecionar somente as linhas favoráveis. Os resultados e o protocolo estão em [C242–C243 e no relatório do Texugo](https://github.com/franklinbaldo/conde-incident/blob/36b6064f6be8ebf155afff676129ae78b37785b2/research/texugo_holdout_529.md).

O experimento também encontrou uma falha no caminho dos dados: um relatório de auditoria íntegro não bastava para garantir que o **CSV extraído** fosse fiel ao Parquet. O verificador foi reforçado para reler os bytes originais, conferir SHA-1 e SHA-256 e comparar cada vínculo entre linha de origem, objeto, época e movimento médio. O [CI final da PR #20](https://github.com/franklinbaldo/conde-incident/actions/runs/43109127688), no commit 36b6064, passou incluindo esses controles e **26 testes**, mas aprovação do software não autentica o rastreamento militar original.

## O que esse fracasso permite concluir

O teste rejeita uma frase tentadora: **“usar os outros objetos sempre melhora a previsão”**. Não rejeita toda a ideia de perturbações compartilhadas, e tampouco demonstra que os três fragmentos continuaram próximos. Seus movimentos médios podem ter relações úteis em certas janelas e inúteis em outras. Este ensaio não ajusta um propagador dinâmico conjunto, não testa posições futuras em quilômetros e não valida uma órbita terminal do 528.

A única âncora contemporânea direta para seu fim orbital continua sendo a [página impressa 8 do Satellite Situation Report da NASA, de 15 de novembro de 1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10): o objeto **1963-003B** aparece com **8 NOV 63** na lista de decaimentos. **Não há hora ou lugar** nessa entrada. O relato de esfera em Conde, transmitido pela Rádio Tupi e preservado no FBIS, é outra cadeia documental. Uma melhora estatística dentro de um espelho orbital não as une.

## O que mudou desde o capítulo 02

Antes havia um integrador físico e verificações produzidas com dados sintéticos pela [PR #5 do Castor](https://github.com/franklinbaldo/conde-incident/pull/5). Agora há também um **teste temporal efetivamente executado** contra valores históricos de um acervo secundário, com resultados favoráveis e desfavoráveis preservados. A pergunta sobre os companheiros de lançamento deixou de ser somente uma promessa de método: uma versão simplificada dela pode falhar de modo observável.

O próximo exame precisa separar o que continua misturado: obter **elementos históricos primários completos e sua proveniência**, resolver as épocas e referenciais incompatíveis, e testar posições futuras com propagação dinâmica e controle SGP4 em dados reservados. Só depois fará sentido perguntar se o movimento dos 527 e 529 restringe, sem pressupor Conde, o lugar onde o 528 desapareceu.

**Nota de verificação:** a evidência numérica deste capítulo pertence às PRs #14 e #20, ainda sujeitas a revisão e integração; os valores são de um espelho secundário e os quatro holdouts são temporais, não independentes. A fonte NASA foi inspecionada por fac-símile; nenhum destroço, posição terminal ou testemunho de impacto novo foi obtido. Esta reportagem depende da integração editorial dos capítulos anteriores e não foi publicada no site.

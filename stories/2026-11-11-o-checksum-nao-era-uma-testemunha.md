---
title: "O checksum não era uma testemunha"
date: "2026-11-11"
summary: "Um confronto com 45 épocas orbitais encontrou zero cópias integrais do antigo vetor do NORAD 528. A verificação dos dígitos passou; a proveniência histórica, não."
chapter: "05"
author: "Coruja · Caderno de investigação"
status: "Falsificação de correspondência digital em espelho secundário; rastreamento primário não autenticado"
---

# O checksum não era uma testemunha

**Se duas linhas de elementos orbitais passam na conferência de seus dígitos, podemos atribuí-las a um radar de 1963?** Essa pergunta passou a importar tanto quanto a trajetória do objeto NORAD 528. Durante a investigação, o simulador exibiu um conjunto de números apresentado como histórico. Uma orientação de plano, em particular, **284,1520°**, não concordava com os **198,5261°** de outro registro atribuído ao mesmo objeto. O conflito não podia ser resolvido escolhendo o número que produzisse uma passagem mais próxima de Conde.

No [capítulo 04](https://github.com/franklinbaldo/conde-incident/pull/31), um memorando contemporâneo ensinou a distinguir uma política de recuperação de fragmentos de uma recuperação efetiva. A nova pista é de natureza diferente: a [Tartaruga, na PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), submeteu o antigo vetor orbital a uma comparação que ele podia perder. O resultado é uma **refutação limitada de proveniência**, não uma reentrada localizada.

## Dois dígitos corretos não são uma cadeia de custódia

O antigo [arquivo de constantes do simulador, anterior à correção](https://github.com/franklinbaldo/conde-incident/blob/eee7851d29e7bafa38ebcb36cab9da9dfa2f2afb/src/lib/constants.ts) continha duas linhas com aparência de TLE do objeto 00528, época literal **63300.61111111**, inclinação **81,8615°**, RAAN **284,1520°**, excentricidade **0,0084200** e movimento médio **15,74900000 revoluções/dia**. A Tartaruga preservou a origem digital desse conteúdo pelo blob Git **0284f1217557b0ea891b5e51b6ac56bd13529d3f**.

As duas linhas passam no algoritmo de checksum do formato TLE. É uma conferência útil contra certos erros de transcrição, mas não equivale a assinatura de um órgão de rastreamento. Também se pode produzir um checksum correto para uma linha construída posteriormente. **Não foi localizada a emissão primária NORAD ou SPADATS** que vincule aquele vetor a um instrumento, uma época e um referencial documentados.

A outra cadeia parte de um [arquivo numérico de 1963 publicado como espelho de históricos Space-Track](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), commit 4b4fb3a, SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. A extração auditada encontrou **45 épocas** para o 528. Esse Parquet não traz a custódia dos radares originais nem os pares completos de linhas TLE de cada observação. É uma fonte **secundária**, não 45 testemunhas instrumentais autônomas.

## A busca pelo registro inteiro

O teste novo, identificado na matriz como **C241-T2**, não procurou apenas a RAAN mais próxima. Comparou, *na mesma linha e na mesma época*, seis campos: inclinação, RAAN, excentricidade, argumento do perigeu, anomalia média e movimento médio. Os limites utilizados são de **arredondamento de texto e float32**, não margens de erro da órbita: 0,00008° para ângulos, 0,00000006 para excentricidade e 0,000000006 revoluções/dia para movimento médio. A coincidência de época foi examinada separadamente, com tolerância de **432 microssegundos**.

O [programa de confronto](https://github.com/franklinbaldo/conde-incident/blob/feature/tartaruga-tle-custody-1963/tools/legacy_528_fingerprint.py) manteve índices de origem, recusou arquivos CSV com hash incompatível e não combinou colunas de datas diferentes. No [GitHub Actions #43122019452](https://github.com/franklinbaldo/conde-incident/actions/runs/43122019452), sobre o commit **cb52253845f607d835f98839423b091d730cfda6**, a auditoria verificou os dados fixados e passou **30 testes**. O achado central foi negativo: **zero das 45 épocas reproduz o vetor completo de seis campos**, e nenhuma tem a época literal da linha legada.

Há uma coincidência parcial instrutiva. A RAAN mais próxima é **284,331085°**, no registro de índice físico **2998**, de **12 de agosto de 1963, 13:35:30,863616 UTC**. Ela difere dos 284,1520° antigos em **0,179085°**. Mas esse registro precede em cerca de 76 dias a época escrita no vetor legado, e seus outros elementos discordam: diferença de excentricidade de **0,0050768**, de argumento do perigeu de **97,4919°**, de anomalia média de **97,0254°** e de movimento médio de **0,30099865 revoluções/dia**. A semelhança de uma coluna não recupera a identidade das demais.

O registro secundário de **27 de outubro de 1963, 14:40:16,132512 UTC**, índice **3017**, tem RAAN **198,5261°** e excentricidade **0,0017147**. A época literal do vetor antigo é aproximadamente **14:40:00 UTC** do mesmo dia, portanto não é a mesma linha, mesmo antes de comparar os ângulos. A [documentação de custódia da Tartaruga](https://github.com/franklinbaldo/conde-incident/blob/feature/tartaruga-tle-custody-1963/research/tle_custody/README.md) preserva as divergências, os hashes e a série de controles, sem declarar um deles autêntico por preferência.

## Qual hipótese caiu?

A hipótese estreita **“o vetor legado completo foi copiado de uma das 45 épocas desse espelho, preservados os seis elementos”** é incompatível com o confronto executado. Isso é uma conclusão quantitativa reproduzível *sobre registros digitais definidos*. Não demonstra que o ângulo **284,1520°** nunca existiu em outro catálogo, que foi necessariamente inventado, ou que não veio de uma época diferente, de uma transformação desconhecida ou de uma montagem de campos. Todas essas origens precisariam de documentos e testes próprios.

O próprio uso do vetor secundário de **198,5261°** na versão corrigida do simulador obedece a um critério de **rastreabilidade de bytes e época**, não a uma autenticação primária. E não há motivo para somar a página do espelho, a página que reproduz um TLE e o catálogo derivado como se fossem três radares independentes. A cadeia de extração pode ser uma só.

A única âncora contemporânea examinada aqui é documental: o [Satellite Situation Report da NASA, de 15 de novembro de 1963, página impressa 8 (página 10 do PDF)](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10) lista **1963-003B** com **8 NOV 63** na coluna de decaimento. O fac-símile foi conferido. Não traz os seis elementos orbitais do teste, nem hora e lugar da reentrada. Já o [relato de Conde preservado pelo FBIS, EOP-UAP-D001, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf) é uma notícia retransmitida, não uma medição orbital. **Essas duas cadeias ainda não se cruzam por uma observação independente de impacto.**

## O que mudou desde o capítulo 04

Agora sabemos **qual afirmação sobre a origem do antigo vetor falhou num teste explícito**. Em termos de domínio admissível, o conjunto de *registros do espelho que coincidiriam integralmente com o vetor legado* ficou vazio; o conjunto de *registros secundários existentes na época de 27 de outubro* permanece não vazio. Nenhum desses conjuntos representa, sem premissas adicionais, as possíveis posições físicas do 528 em 8 de novembro.

Uma futura restrição em Lean 4.35.0 poderia codificar **condicionalmente** a inexistência daquela coincidência no corpus e explicitar os hashes, tolerâncias e campos usados. **Nenhuma nova prova Lean foi executada nesta reportagem.** Não seria legítimo converter a refutação documental em exclusão de Conde, probabilidade de queda, trajetória terminal ou coordenada de reentrada. Mesmo uma reentrada em certo lugar não demonstraria que um fragmento atingiu o solo.

Falta recuperar o conjunto primário de elementos de 1963, com épocas completas, convenções de referencial, proveniência e associação física do identificador 00528. Só então o domínio de parâmetros orbitais poderá ser restringido por observações autenticadas, propagado com erros controlados e confrontado com holdouts. **A próxima pergunta é onde nasceu o 284,1520°**: numa fonte orbital hoje perdida, em uma transformação explicável ou no próprio trabalho de reconstrução posterior? A resposta é relevante precisamente porque ainda não sabemos qual delas é verdadeira.

---

**Ficha de verificação:** resultado **C241-T2** na [matriz cumulativa da PR #14](https://github.com/franklinbaldo/conde-incident/blob/feature/tartaruga-tle-custody-1963/research/evidence_matrix_C001-C238_2026-11-11.md), execução de código sobre um espelho **secundário de linhagem única** no [run #43122019452](https://github.com/franklinbaldo/conde-incident/actions/runs/43122019452), CSV 528 SHA-256 **e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e**. O teste de seis campos passou no commit indicado; o HEAD posterior da PR #14 inclui documentação ainda sujeita a revalidação de CI. **Fonte instrumental primária: não recuperada. Observação terminal: não recuperada. Simulação de reentrada e prova Lean novas: não executadas.** A auditoria da [PR #32 do Gavião](https://github.com/franklinbaldo/conde-incident/pull/32) cobre os capítulos 01–04, não equivale à revisão independente deste capítulo 05. Publicação depende do Gavião e do Elefante.

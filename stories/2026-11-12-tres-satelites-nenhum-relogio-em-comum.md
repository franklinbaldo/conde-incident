---
title: "Três satélites, nenhum relógio em comum"
date: "2026-11-12"
summary: "Uma auditoria cruzou 45 épocas do NORAD 528 com as dos objetos 527 e 529. Não encontrou horários simultâneos; o último registro disponível ainda antecede em dias o decaimento noticiado pela NASA."
chapter: "06"
author: "Coruja · Caderno de investigação"
status: "Auditoria temporal de espelho secundário; sincronismo e trajetória terminal não demonstrados"
---

# Três satélites, nenhum relógio em comum

**Se os objetos 527 e 529 podem ajudar a reconstruir a história do 528, quantas vezes o arquivo os registrou no mesmo instante?** Até aqui, a investigação havia testado a transferência de curvatura entre os três objetos e encontrado resultados mistos. Depois, no [capítulo 05](https://github.com/franklinbaldo/conde-incident/pull/35), verificou que um antigo vetor orbital do simulador não coincidia integralmente com nenhum dos 45 registros numéricos disponíveis do 528. Agora a [Tartaruga, na PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), fez outra pergunta ao mesmo acervo: **as datas dos três objetos realmente se alinham para permitir um ajuste conjunto sem preencher lacunas às escondidas?**

O teste trouxe uma resposta negativa e um alerta sobre o tamanho do vazio que separa os dados catalogados da reentrada.

## Uma fonte, três séries e horários diferentes

O ponto de partida não é uma coleção de boletins originais de radar. É o [Parquet histórico de 1963 do espelho oxzoid, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), com SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. A auditoria de custódia extraiu desse arquivo **21 linhas do 527, 45 do 528 e 57 do 529**. Como algumas linhas repetem datas, são **20, 45 e 54 épocas distintas**, respectivamente. Essas contagens foram registradas na mesma cadeia de pesquisa, não em três rastreadores independentes.

A [nova ferramenta `cross_object_epoch_support.py`](https://github.com/franklinbaldo/conde-incident/blob/22745c1fb0339c6d9743da28e15a79e417e5123b/tools/cross_object_epoch_support.py) percorreu cada época do 528, procurou os registros cronologicamente mais próximos de 527 e 529 e preservou os índices de origem. Ela também rejeita índices duplicados conflitantes, números não finitos e datas fora de UTC. Não fabricou uma posição intermediária, não interpolou vetores e não ajustou uma órbita aos três conjuntos.

O confronto é identificado na [matriz cumulativa como **C241-T3**](https://github.com/franklinbaldo/conde-incident/blob/22745c1fb0339c6d9743da28e15a79e417e5123b/research/evidence_matrix_C001-C238_2026-11-11.md). É uma **inferência sobre disponibilidade de registros**, não uma observação instrumental nova.

## Zero simultaneidades não significa zero possibilidades

A auditoria definiu, antes de examinar os resultados, janelas de 6, 24 e 72 horas. A tabela mostra quantas das **45 épocas distintas do 528** tinham um registro de **ambos** os vizinhos dentro de cada janela:

| Distância máxima entre épocas catalogadas | Épocas do 528 com 527 e 529 próximos |
| --- | ---: |
| Mesmo instante UTC (0 microssegundo) | **0** |
| Até 432 microssegundos | **0** |
| Até 6 horas | **1** |
| Até 24 horas | **2** |
| Até 72 horas | **15** |

Os **432 microssegundos** representam metade da unidade temporal considerada na comparação de épocas TLE, **não uma precisão de radar medida**. Tampouco as janelas de 6, 24 e 72 horas são barras de erro físico. São perguntas sobre o calendário do arquivo.

O resultado mais forte é **zero entre 45**: nenhuma época do 528 coincidiu exatamente, nem dentro daquela meia unidade, com as épocas catalogadas de 527 ou 529. O resultado mais facilmente exagerado é **15 dentro de 72 horas**: são 15 ocasiões com vizinhos datados nas proximidades, **não 15 triangulações simultâneas**. Para esses confrontos, reaproveitam-se apenas **13 épocas distintas do 527** e **28 do 529**. Reutilizar o mesmo registro em diversas comparações não gera testemunhas novas.

A verificação foi executada no [GitHub Actions de custódia #43130289769](https://github.com/franklinbaldo/conde-incident/actions/runs/43130289769), no **HEAD 22745c1**, com o Parquet e o CSV derivados conferidos por hashes e **39 testes aprovados**, dos quais nove controlam adversarialmente a nova análise temporal. O [workflow científico #43130290274](https://github.com/franklinbaldo/conde-incident/actions/runs/43130290274) também concluiu com sucesso no mesmo SHA. O resultado do arquivo pinado foi medido na execução; as nove provas de robustez usam exemplos sintéticos. Nenhum desses testes autentica a estação que teria produzido os elementos em 1963.

## O silêncio depois de 27 de outubro

A última época disponível do **528 nesse espelho** é **27 de outubro de 1963, às 14:40:16,132512 UTC**. Para o 527 e o 529, o próprio arquivo prossegue até dezembro. **Não há, nesta cópia, época do 528 em novembro.** Essa ausência não autoriza afirmar que ninguém o observou na época ou que os boletins originais não existam; mostra apenas onde termina a série atualmente recuperada.

Conferimos novamente em fac-símile a [página impressa 8 (página 10 do PDF) do *Satellite Situation Report* da NASA, de 15 de novembro de 1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10). Na lista de decaimentos, **1963 3B** aparece com **8 NOV 63**. A NASA documenta o **dia**, não a hora, a longitude ou a latitude terminal. Entre a última linha secundária de outubro e essa data, qualquer trajetória exige propagação e incerteza acumulada. Preencher a lacuna com uma órbita que passa por Conde não seria recuperar uma medição.

O outro documento contemporâneo, o [FBIS 03, EOP-UAP-D001, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), preserva o relato da **Rádio Tupi** sobre uma esfera em Conde. Foi reinspecionado como **documento de transmissão de uma notícia**, não como medição espacial nem prova de um impacto. NASA e FBIS documentam fatos de natureza diferente; a coincidência de calendário ainda não liga fisicamente suas cadeias.

## O que o teste elimina e o que ainda não decide

A hipótese estreita de que *este arquivo secundário contém registros exatamente simultâneos dos três objetos* falhou. A hipótese de que objetos do mesmo lançamento **possam** ser ajustados conjuntamente não foi refutada: séries em instantes diferentes podem ser usadas num modelo dinâmico, **desde que** épocas, referenciais, erros e propagação sejam justificados. Por outro lado, encontrar 15 janelas próximas não comprova que um ajuste funcione; o [holdout do 529 na PR #20](https://github.com/franklinbaldo/conde-incident/pull/20) já ensinou que a informação dos vizinhos pode também piorar previsões.

Em linguagem do fluxo científico, **C241-T3** delimita um conjunto **documental**: os pares de épocas simultâneas desta cópia são inexistentes; pares dentro de 72 horas existem, mas são assíncronos e de uma mesma linhagem secundária. **Isso não estreita um domínio físico autenticado de latitudes, velocidades, coeficientes balísticos ou pontos de reentrada.** Uma eventual proposição em Lean 4.35.0 sobre ausência de coincidências dependeria do arquivo pinado e de sua regra de comparação, não constituiria prova de localização. **Não foi produzida nova prova Lean nem simulada uma reentrada nesta reportagem.**

A pergunta seguinte é concreta: **onde estão os pares TLE primários do 528 mais próximos de 8 de novembro, com época, referencial, incerteza, proveniência e identificação da peça?** Sem eles, não há confronto posicional cego que transforme os três calendários em limite físico reproduzível. A investigação ainda pode terminar excluindo Conde, encontrando outra região ou permanecendo indeterminada. Por enquanto, o relógio do arquivo não oferece a hora nem o endereço da queda, e a própria queda de um fragmento no solo segue sem demonstração.

---

**Ficha de fontes e limites:** [C241-T3 na matriz da PR #14](https://github.com/franklinbaldo/conde-incident/blob/22745c1fb0339c6d9743da28e15a79e417e5123b/research/evidence_matrix_C001-C238_2026-11-11.md), [relatório de custódia](https://github.com/franklinbaldo/conde-incident/blob/22745c1fb0339c6d9743da28e15a79e417e5123b/research/tle_custody/README.md), [CI do SHA final da fonte #43130289769](https://github.com/franklinbaldo/conde-incident/actions/runs/43130289769) e CSV agregado SHA-256 **3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231**. Primários NASA e FBIS: fac-símiles das páginas indicadas, lidos diretamente. **Independência:** NASA e FBIS registram categorias de informação distintas; o espelho de elementos 527/528/529 é uma cadeia secundária única, e o seu hash não autentica radar. **Não recuperados:** TLEs instrumentais originais, fase/estado terminal, prova de destroços em Conde. Revisão editorial independente do 🦅 Gavião e integração/publicação pelo 🐘 Elefante ainda necessárias.

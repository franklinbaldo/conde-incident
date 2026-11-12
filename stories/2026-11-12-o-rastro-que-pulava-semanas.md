---
title: "O rastro que pulava semanas"
date: "2026-11-12"
summary: "Havia 45 registros orbitais do NORAD 528 em um arquivo recuperado. Uma auditoria encontrou 32 intervalos superiores a três dias e uma lacuna de mais de 23 dias. A série não era a trilha contínua que o mistério parecia pedir."
chapter: "09"
author: "Coruja · Caderno de investigação"
status: "Auditoria C241-T7 de espelho secundário; lacunas documentais verificadas, trajetória terminal e impacto não determinados; revisão editorial pendente"
---

# O rastro que pulava semanas

**Se recuperamos 45 registros da órbita de um objeto que deixou de circular em novembro de 1963, por que ainda não conseguimos acompanhá-lo até o fim?** A resposta parecia estar escondida entre os números. Não no ângulo orbital, nem na potência de um simulador. No espaço em branco entre uma data e outra.

A [Tartaruga, na PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), submeteu os registros do objeto **NORAD 528** a uma pergunta que deveria preceder qualquer trajetória desenhada na tela: *de quanto em quanto tempo o arquivo realmente nos dá uma nova posição orbital catalogada?* O resultado mudou a escala do problema. **Dos 44 intervalos entre as 45 épocas recuperadas, 32 ultrapassam três dias.** Somente três não ultrapassam 24 horas. E existe um vazio documental de **23,53529262 dias**.

Não é uma descoberta sobre o lugar onde o satélite caiu. É uma descoberta sobre o quanto falta para sequer testar uma localização.

## A promessa dos quarenta e cinco registros

Nos [capítulos 06](https://github.com/franklinbaldo/conde-incident/pull/39) e [08](https://github.com/franklinbaldo/conde-incident/pull/50), esbarramos em duas limitações diferentes: os horários dos três objetos do lançamento não coincidiam exatamente *no espelho recuperado*, e o laboratório chegou a mostrar uma hora terminal e uma probabilidade sem observações suficientes para sustentá-las. Mas ainda havia uma tentação compreensível: **45 registros do 528 parecem muito próximos de uma sequência capaz de narrar o voo**.

A aparência engana. O material disponível é o [Parquet histórico oxzoid de 1963, revisão fixa 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`. A Tartaruga extraiu dele um CSV de **45 épocas distintas do 528**, SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`, preservando o índice de linha de cada registro.

É uma **fonte secundária derivada de uma só linhagem de dados**, não 45 boletins instrumentais originais de 1963. Mesmo um conjunto numérico autêntico, em dias esparsos, não revela por si só os acontecimentos entre seus registros.

## O teste que contou os silêncios

A nova auditoria, **[C241-T7 na matriz histórica](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/evidence_matrix_C001-C238_2026-11-11.md)**, ordenou as 45 épocas UTC e mediu a distância entre cada par consecutivo. O [código verificável](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/tools/raan_epoch_continuity_audit.py) conserva as datas e os `source_row`, recusa conflitos, trata corretamente a circularidade dos ângulos e **não inventa posições intermediárias**.

| Pergunta feita ao arquivo secundário | Resposta medida |
| --- | ---: |
| Épocas catalogadas do 528 | **45** |
| Intervalos entre épocas consecutivas | **44** |
| Intervalos superiores a 72 horas | **32** |
| Intervalos de até 24 horas | **3** |
| Maior intervalo sem novo registro nesta cópia | **23,53529262 dias** |

O maior salto ocorreu entre **6 de fevereiro de 1963, 05:33:01 UTC**, e **1º de março de 1963, 18:23:50 UTC**, nas linhas de origem **2978** e **2979**. Os horários completos e as frações de segundo estão registrados no [relatório de custódia C241-T7](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/tle_custody/README.md). Esse intervalo enorme não ocorreu às vésperas da reentrada, mas revela como a série inteira é descontínua.

O teste foi executado sobre o corpus fixado no [GitHub Actions #43155873680](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680), commit **`f3cb5d05`**, com **78 testes aprovados** e verificação do hash do arquivo. O [workflow científico do mesmo SHA](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873831) também passou. Testes aprovados significam que **essa contagem e seus controles são reproduzíveis**; não convertem as linhas do espelho em observações instrumentais independentes.

## A última linha e o dia oito

Perto de novembro, a lacuna importa ainda mais. A última época do 528 **nessa cópia** permanece **27 de outubro de 1963, 14:40:16,132512 UTC**. Entre esse registro e os limites civis de **8 de novembro**, decorreriam de **11,38870217 a 12,38870217 dias**, dependendo de qual limite do dia se usa para comparar. **Não é uma janela física de reentrada, nem uma estimativa de erro orbital.** São apenas diferenças de calendário para os extremos de um dia.

Conferi novamente o documento que realmente contém o dia: a [NASA, *Satellite Situation Report*, de 15 de novembro de 1963, página impressa 8, página 10 do PDF](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10). O item **1963 3B** aparece na lista de objetos decaídos com a data **8 NOV 63**. O boletim **não informa hora, latitude, longitude, ponto de impacto ou sobrevivência de fragmento**. As ocorrências [C197–C202 da matriz](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md) remetem à mesma fonte NASA, e não a seis observações independentes.

No outro ramo documental, o [FBIS 03, EOP-UAP-D001, página única](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), conserva uma notícia atribuída à **Rádio Tupi** sobre uma esfera em Conde. Sua ocorrência [C01–C02](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md) comprova a circulação do relato, **não a cratera ou a queda**. NASA e FBIS foram reinspecionados em fac-símile; um cataloga o dia de decaimento, outro retransmite uma notícia. Nenhum deles preenche os dias órbita por órbita.

## O que as lacunas permitem afirmar

Duas explicações convivem com esses vazios. **H-arquivo:** o espelho moderno preservou apenas parte dos elementos produzidos ou retidos no passado; outros registros podem existir em arquivos primários. **H-cobertura limitada:** o rastreamento histórico efetivamente disponível pode ter sido esparso, mas o espelho por si só **não mede essa cobertura instrumental**. As duas explicações não são excludentes. Procurar boletins primários com cadeia de custódia, incluindo datas ausentes do espelho, é o teste que pode começar a distingui-las.

Há ainda a divergência já conhecida entre as orientações orbitais **198,5261°** no par secundário preservado e **284,1520°** no vetor antigo de origem não demonstrada. C241-T7 identifica também uma diferença de **16,132608 segundos** entre suas épocas textuais. Isso **não prova que qualquer vetor esteja fisicamente errado**; impede tratá-los como cópias da mesma medição, no mesmo instante, ou resolver a discordância por simples média.

A tentação mais perigosa seria transformar o cálculo `Δângulo/Δtempo` entre pontos distantes numa taxa física comprovada de precessão. O relatório apresenta essas razões como **secantes aritméticas entre amostras catalogadas**, não como modelo dinâmico ajustado e testado. Um simulador pode preencher os dias vazios segundo hipóteses. Mas preencher não é observar.

## O que mudou desde o capítulo 08

Desta vez, a descoberta não é outra frase indevida na interface. É **uma auditoria nova da estrutura temporal da própria evidência orbital**: 32 de 44 intervalos excedem três dias, um ultrapassa 23 dias e a cópia termina mais de onze dias antes do início de 8 de novembro. A contagem **C241-T7** torna falseável a impressão de uma sequência quase contínua. Ela não exclui nem exige Conde e não localiza outra região.

O limite lógico é estreito e importante. **Se** o CSV com hash fixado reproduz corretamente aquelas 45 épocas, **então** seu conjunto de 44 intervalos tem as lacunas contadas. Isso pode ser expresso como uma propriedade do **arquivo**, mas **não oferece uma premissa física autenticada** de posição, velocidade, quadro de referência, força ou erro para uma restrição orbital em Lean 4.35.0. Nenhum domínio histórico de parâmetros foi reduzido; nenhuma nova simulação terminal ou holdout posicional foi executado nesta reportagem. E mesmo uma reentrada localizada não demonstraria impacto material em Conde.

A próxima pergunta é mais específica do que “onde caiu?”: **existe algum boletim instrumental original do 528 entre 27 de outubro e 8 de novembro, com data, referencial, parâmetros completos e cadeia de origem verificável?** Se aparecer, ele permitirá confrontar uma trajetória ajustada *sem escolher Conde como destino*. Se não aparecer, o silêncio continuará sendo **do acervo consultado**, não necessariamente do céu de 1963.

---

**Ficha de rastreabilidade:** [C241-T7 na matriz de custódia, PR #14](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/evidence_matrix_C001-C238_2026-11-11.md), [script de auditoria no SHA testado](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/tools/raan_epoch_continuity_audit.py), [relatório e resultados completos](https://github.com/franklinbaldo/conde-incident/blob/f3cb5d056af51135959acb88b6813b3018b210d5/research/tle_custody/README.md), [CI #43155873680](https://github.com/franklinbaldo/conde-incident/actions/runs/43155873680). Fonte numérica: espelho oxzoid **secundário único**, sem independência instrumental demonstrada; a existência de duas cópias não cria dois sensores. Fontes contemporâneas diretamente inspecionadas: NASA 15/11/1963, p. 8, **C197–C202**, data de decaimento apenas; FBIS 03, p. 1, **C01–C02**, relato retransmitido apenas. **Não recuperados:** 45 pares instrumentais completos, metadados de sensor/frame/erro, identificação física do componente e posição terminal. Integração/publicação dependem de revisão 🦅 e do 🐘 no **site Conde**, sem alteração no blog pessoal.

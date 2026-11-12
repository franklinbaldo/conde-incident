---
title: "Dezesseis segundos contra oitenta e cinco graus"
date: "2026-11-12"
summary: "Dois registros atribuídos ao NORAD 528 quase coincidem no relógio, mas discordam 85,6259° sobre a orientação orbital. Uma contraprova elimina, sob hipóteses J2 explícitas, a explicação mais estreita: que os 16 segundos de diferença bastariam. A origem da órbita histórica continua aberta."
chapter: "12"
author: "Coruja · Caderno de investigação"
status: "C241-T10: refutação matemática condicional; procedência orbital primária e localização da reentrada não verificadas"
---

# Dezesseis segundos contra oitenta e cinco graus

**Dois registros atribuídos ao mesmo objeto podem ter apenas dezesseis segundos de diferença no relógio e, ainda assim, apontar para planos orbitais separados por mais de oitenta e cinco graus?** Essa discrepância acompanhava a investigação do NORAD 528 desde os primeiros cálculos. Havia uma explicação aparentemente simples a testar: talvez o ângulo tivesse mudado porque as duas linhas não se referiam exatamente ao mesmo instante. A 🐢 Tartaruga decidiu perguntar quanto uma diferença tão pequena poderia realmente explicar.

A resposta é uma das mais nítidas desta série, com uma condição importante: **num modelo declarado de precessão J2, se os registros usarem a mesma referência orbital e diferirem apenas na época, dezesseis segundos não chegam nem perto de explicar o desvio**. O cálculo elimina essa justificativa estreita. Não escolhe qual registro é verdadeiro.

## O conflito estava nos próprios números

No antigo [código do simulador, preservado pelo Git blob `0284f121`](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/lib/constants.ts), o NORAD 528 aparecia com a orientação do plano orbital, chamada **ascensão reta do nó ascendente (RAAN)**, de **284,1520°**. Era apresentada como ângulo reconstruído, mas não acompanhada da cadeia de medições de 1963 capaz de autenticá-la.

Um [par TLE secundário arquivado pela Tartaruga](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/research/tle_custody/mirror_528_1963-10-27.tle), extraído de um catálogo moderno, apresenta **198,5261°**. TLE é um formato de duas linhas usado para representar elementos orbitais. Um dígito de verificação correto permite testar sua estrutura, **não** demonstrar quem mediu o satélite.

| Registro atribuído ao 528 | Época calculada em UTC | RAAN |
| --- | --- | ---: |
| Vetor legado no simulador, sem procedência instrumental comprovada | 27/10/1963, 14:39:59,999904 | 284,1520° |
| Par TLE de espelho secundário, custodiado | 27/10/1963, 14:40:16,132512 | 198,5261° |

A distância angular mínima entre esses valores, respeitando a volta completa de 360°, é **85,6259°**. A diferença entre os horários é de **16,132608 segundos**. A Tartaruga já havia constatado o conflito nos cadernos anteriores. Agora o tornou uma hipótese numérica falsificável, **C241-T10**, na [PR científica #14](https://github.com/franklinbaldo/conde-incident/pull/14).

Também há diferenças em outros elementos dos vetores. Assim, a história não é simplesmente a de dois relógios apontando para a mesma medição. A autenticidade, o referencial e até a origem do ângulo legado continuam sem comprovação independente.

## A conta que o relógio não conseguiu pagar

O teste fez uma pergunta deliberadamente mais modesta que “qual era a órbita verdadeira?”: **se os dois ângulos descrevessem o mesmo nó, no mesmo referencial, e toda a mudança fosse devida apenas a esses 16 segundos, a precessão secular J2 de primeira ordem conseguiria produzi-la?**

J2 representa uma parte conhecida do efeito gravitacional de a Terra não ser uma esfera perfeita. A fórmula aproximada permite calcular a mudança secular da orientação de uma órbita *sob premissas específicas*. A ferramenta da Tartaruga usa o movimento médio das linhas como aproximação kepleriana, as constantes físicas declaradas e as inclinações e excentricidades de cada vetor. **Não é SGP4 calibrado, observação de radar, nem reconstrução do movimento real em outubro de 1963.**

O resultado foi desconcertante para a hipótese do mero ajuste de horário:

| Quantidade testada em C241-T10 | Resultado |
| --- | ---: |
| Diferença entre as épocas | **16,132608 s** |
| Distância circular entre os dois ângulos | **85,6259°** |
| Mudança máxima estimada no intervalo pelo proxy J2 | **0,0002191°** |
| Taxa mínima para explicar o desvio nesse intervalo | **458.578,62° por dia** |
| Taxas seculares J2 calculadas dos dois vetores | cerca de **−1,173° por dia** |

A mudança que seria necessária é aproximadamente **390 mil vezes** maior que a mudança estimada pelo proxy J2 nesse intervalo. O teste ainda descontou **0,0001°** como limite combinado de arredondamento dos dois campos de quatro casas decimais. Nem isso muda a conclusão condicionada.

O confronto pode ser refeito com o [auditor de C241-T10](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/tools/tle_raan_epoch_offset_j2_audit.py), as duas linhas preservadas, o [espelho numérico de 1963, versão fixa `4b4fb3a`](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet) e a [ocorrência C241-T10 da matriz](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/research/evidence_matrix_C001-C238_2026-11-11.md). O [GitHub Actions de custódia no HEAD `1934198e`](https://github.com/franklinbaldo/conde-incident/actions/runs/43177947173) e as [verificações científicas no mesmo SHA](https://github.com/franklinbaldo/conde-incident/actions/runs/43177947176) passaram. Esses gates conferem a execução, **não** a identidade do sensor histórico.

## Uma hipótese caiu. A diferença continuou ali.

A conclusão do teste não é “o ângulo 284,1520° é impossível”. É mais precisa: **a explicação de que *apenas* deslocar a época em 16,132608 segundos reconciliaria os dois ângulos não funciona sob o mesmo referencial e a aproximação J2 declarada.**

Essa restrição deixa hipóteses rivais abertas. O ângulo legado pode ter sido construído sem fonte instrumental, transcrito incorretamente ou retirado de outro conjunto de dados. As linhas podem obedecer a diferentes referenciais, épocas de equinócio ou convenções de elementos, que não foram autenticados. Uma dinâmica histórica não modelada poderia exigir outra comparação. Os dois catálogos modernos podem repetir uma mesma linhagem de rastreamento, sem fornecer testemunhos independentes.

A pergunta mais tentadora seria: *se um dos valores está errado, não poderíamos simplesmente escolher o outro e calcular onde o 528 caiu?* Não. Um checksum válido e uma coincidência de ângulo com um espelho moderno não revelam o referencial instrumental, a covariância dos erros ou o estado físico terminal. Selecionar uma linha como verdade agora seria trocar um conflito visível por uma certeza fabricada.

## A documentação de novembro ainda não aponta um lugar

Reinspecionei a [página impressa 8, décima página do PDF, do *Satellite Situation Report* da NASA de 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10). A entrada **1963 3B** aparece com **8 NOV 63** na coluna de decaimento. É uma fonte **primária contemporânea** para a *data catalogada*, sem hora, latitude, longitude ou prova de fragmento recuperado. As ocorrências **C131/C197** remetem ao mesmo boletim, e não a dois rastreadores.

Também reli o [FBIS 03, página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), com a notícia atribuída à **Rádio Tupi do Rio**. A fonte, **C01/C02**, comprova a circulação do relato sobre uma esfera em Conde, não a observação física de impacto. FBIS e Tupi formam uma cadeia de transmissão jornalística. NASA e FBIS são documentos de naturezas diferentes: **a coincidência de data não cria uma ligação dinâmica entre eles**.

## O que mudou desde o capítulo 11

O [capítulo anterior](https://github.com/franklinbaldo/conde-incident/pull/59) examinou como modelos competiam para prever o próximo valor de **movimento médio do NORAD 529**. Sua auditoria independente posterior acrescentou uma exceção por horizonte: no estrato entre 7 e 30 dias, a média dos doadores venceu, apesar de perder no agregado. Essa correção pertence ao capítulo 11, não é a notícia deste texto.

**Agora a pergunta mudou de alvo e de natureza.** Voltamos ao **NORAD 528**, cujo vetor legadamente usado na reconstrução diverge de outro registro em 85,6259°. A contraprova **C241-T10** elimina **condicionalmente** uma explicação concreta para o conflito: o mero descompasso de dezesseis segundos sob precessão J2 comum. A diferença não pode mais ser descartada, nesse modelo, como um erro trivial de relógio. **Não foi identificado qual vetor, se algum, representa a orientação orbital histórica verdadeira.**

No fluxo documento → matriz → restrição Lean → domínio físico → simulação → holdout, o resultado permanece **na camada de auditoria documental e de hipótese matemática condicional**. A hipótese do ajuste temporal isolado perde sustentação; **nenhum domínio físico historicamente autenticado de trajetórias foi estreitado**. Não houve nova prova Lean 4.35.0, ajuste dinâmico terminal com erro validado nem observação independente que permita excluir ou exigir Conde. O estado continua **indeterminado**. Reentrada orbital e impacto no solo são fatos distintos.

O próximo documento decisivo seria uma **linha orbital original do NORAD 528**, com época, referencial, processo de obtenção, incertezas e identificação da peça, preferencialmente entre **27 de outubro e 8 de novembro de 1963**. Ela poderia confirmar um referencial, refutar a origem do vetor legado ou demonstrar um terceiro caminho. **Até lá, o relógio deixou de ser uma solução simples; a proveniência virou a pergunta central.**

---

**Ficha de evidências e independência:** **C241-T10** na [matriz da 🐢 Tartaruga / PR #14](https://github.com/franklinbaldo/conde-incident/pull/14), [auditor reproduzível](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/tools/tle_raan_epoch_offset_j2_audit.py), [código legado com ângulo conflitante, blob `0284f121`](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/lib/constants.ts), [par TLE secundário preservado](https://github.com/franklinbaldo/conde-incident/blob/1934198e260b9dae8c056587cc7a16c777d58d25/research/tle_custody/mirror_528_1963-10-27.tle), SHA-256 **18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd**, e Parquet secundário oxzoid 1963, SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. TLE/Parquet são **fontes derivadas possivelmente dependentes**; vetor legado é **não autenticado**; J2 é **inferência modelada condicional**. Fac-símiles primários NASA **p. impressa 8/PDF p.10, C131/C197** e FBIS **p.1, C01/C02** foram conferidos visualmente, mas não autenticam nenhuma RAAN. **Não recuperados:** TLEs NORAD instrumentais originais, referencial/erro histórico, peça 528 identificada fisicamente e qualquer prova de queda em Conde. Revisão factual independente do 🦅 Gavião e integração/publicação pelo 🐘 Elefante permanecem obrigatórias.

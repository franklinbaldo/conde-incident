---
type: Story
title: "Quinze segundos para salvar uma explicação"
description: "Caderno 14: três boletins NASA de 1963 exigiriam um resíduo de pelo menos 15 segundos por célula para sustentar a hipótese de um desvio comum a cada edição."
date: "2026-11-13"
summary: "Quando os períodos impressos de dois objetos se afastaram, foi possível medir quanto erro adicional seria necessário para insistir numa explicação editorial simples. O número é exato para o modelo, não para o céu."
chapter: "14"
author: "Coruja · Caderno de investigação"
status: "Fac-símiles NASA inspecionados; limite matemático condicional C241-P13, sem medição instrumental ou localização de reentrada"
---

# Quinze segundos para salvar uma explicação

Em novembro de 1963, dois objetos de um lançamento de janeiro continuavam nas folhas de acompanhamento de satélites. O terceiro, identificado como **1963 3B / NORAD 528**, já constava na relação de decaimentos com a data **8 de novembro**, sem hora ou lugar. A história da esfera noticiada em Conde, na Bahia, permanece separada dessa anotação: não se recuperou o elo físico entre elas.

Os sobreviventes, **1963 3A / 527** e **1963 3C / 529**, ofereceram outra coisa. A NASA imprimiu seus períodos orbitais em três edições sucessivas. A linha do primeiro ficou imóvel; a do segundo diminuiu. O [capítulo 13](https://franklinbaldo.github.io/conde-incident/stories/2026-11-13-o-minuto-que-nao-cabia-no-erro-de-edicao/) mostrou que um único desvio aditivo comum às linhas da mesma edição não bastava para explicar a mudança por simples arredondamento. Restava uma pergunta mais interessante: **quanto erro adicional seria necessário para salvar essa explicação?**

## Seis números, três folhas

A resposta começa numa coluna chamada *nodal period*. Nos fac-símiles da NASA, página impressa **5** de cada edição (página **7 do PDF**), aparecem estes valores:

| Edição do *Satellite Situation Report* | 527 / 3A | 529 / 3C | Distância entre as linhas |
| --- | ---: | ---: | ---: |
| [Nº 22, 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=7) | 94,6 min | 92,6 min | 2,0 min |
| [Nº 23, 30/11/1963](https://ntrs.nasa.gov/api/citations/19640002493/downloads/19640002493.pdf#page=7) | 94,6 min | 92,2 min | 2,4 min |
| [Nº 24, 15/12/1963](https://ntrs.nasa.gov/api/citations/19640003479/downloads/19640003479.pdf#page=7) | 94,6 min | 91,6 min | 3,0 min |

A distância entre os valores publicados cresceu **um minuto inteiro**. Isso não significa que uma órbita tenha evoluído exatamente assim entre 15 de novembro e 15 de dezembro. Essas datas são **das edições**, não os instantes comprovados das observações instrumentais. Tampouco três folhas compiladas por uma mesma cadeia NASA/NORAD/Smithsonian equivalem a três medições independentes.

Uma tentação seria dizer que alguém corrigiu igualmente os valores de ambos os objetos em cada nova edição. Mas uma correção comum desaparece quando subtraímos as duas linhas. A diferença não poderia passar de 2,0 para 3,0 minutos se os valores-base permanecessem constantes e o único ruído fosse o arredondamento a uma casa decimal.

## O preço da hipótese

Para tornar o teste menos rígido, admitamos agora três ingredientes: um período-base constante para cada objeto, uma correção comum às duas linhas de cada edição e um **resíduo individual**, que pode variar de objeto para objeto e de edição para edição.

Nesse modelo, a diferença impressa entre 527 e 529 é a diferença entre os dois valores-base, acrescida da diferença entre seus resíduos. Se o valor absoluto de cada resíduo for limitado a **E**, cada diferença entre linhas pode desviar até **2E** de sua base comum. Entre a menor e a maior diferença publicada, a amplitude possível é de **4E**.

A amplitude encontrada *nas tabelas* foi **1,0 minuto**. Portanto, para que o modelo caiba nas seis células, **4E precisa ser pelo menos 1,0 minuto**: o menor resíduo máximo possível é **0,25 minuto, ou 15 segundos por célula**.

É um limite exato dentro da hipótese, não apenas uma aproximação conservadora. Existe um conjunto artificial de bases, correções e resíduos que reproduz todos os seis valores com no máximo quinze segundos em cada célula. A [verificação formal C241-P13](https://github.com/franklinbaldo/conde-incident/pull/450) demonstra tanto a necessidade desse mínimo quanto uma solução que o atinge.

Para comparar escalas: um número publicado com uma casa decimal tem uma margem convencional de arredondamento de **0,05 minuto**, isto é, **3 segundos**. O mínimo exigido pelo modelo mais flexível é **cinco vezes essa margem**. Assim, mero arredondamento não basta; seria preciso admitir outros resíduos, cujo significado e origem ainda não foram estabelecidos.

## O que quinze segundos não dizem

Os quinze segundos **não são um erro instrumental medido**, um desvio real descoberto nos arquivos ou um parâmetro balístico calculado. São o menor orçamento de resíduo de um modelo matemático escolhido para testar a hipótese editorial. A construção que atinge o limite não reconstitui o procedimento histórico de compilação da NASA; apenas prova que o limite é alcançável nas contas.

A queda do período publicado para 529 poderia envolver atualização de elementos orbitais, diferenças entre métodos, evolução física, correções próprias daquele objeto ou uma combinação de fatores. A série disponível não discrimina essas alternativas. Faltam as épocas das observações brutas, estações, convenções, precisão e erros correlacionados.

E o 528? O boletim de **15/11/1963** registra seu decaimento em **8/11** na seção de objetos decaídos, mas não traz um relógio nem um endereço de reentrada. Uma desigualdade calculada a partir de 527 e 529 não transfere automaticamente informação terminal para 528, muito menos demonstra que algo caiu em Conde.

Há, contudo, progresso real. A pergunta deixou de ser apenas se a explicação simples cabia nas tabelas. Agora sabemos exatamente **quanto ela teria de ceder** para acomodá-las. Quando surgirem registros instrumentais com época e incerteza, esses quinze segundos servirão como referência para confrontar, e não presumir, a história por trás da impressão.

---

**Ficha de verificabilidade.** Fonte primária: NASA, *Satellite Situation Reports* nº 22 (15/11/1963), nº 23 (30/11/1963) e nº 24 (15/12/1963), página impressa 5 / PDF 7, links acima. A custódia e os seis valores vêm de [C241-P12](https://github.com/franklinbaldo/conde-incident/pull/437); o limite inferior e a testemunha de atingibilidade, de [C241-P13](https://github.com/franklinbaldo/conde-incident/blob/main/research/constraints/C241-P13_offset_robustness.json) e da [PR científica #450](https://github.com/franklinbaldo/conde-incident/pull/450). Modelo condicional, fontes de mesma linhagem, sem época instrumental conhecida nem nova restrição física de reentrada. Não há prova de impacto em Conde.

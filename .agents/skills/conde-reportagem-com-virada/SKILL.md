---
name: conde-reportagem-com-virada
description: Transformar avanços verificáveis da investigação Conde em reportagens surpreendentes, com suspense factual, clareza e proveniência preservada.
---

# 🦉 Coruja: surpreender sem adulterar a prova

**Objetivo:** produzir jornalismo de investigação que o leitor queira acompanhar, e não atas de testes. O “spin” desejado é **ângulo narrativo interessante**, jamais torção da evidência. A pergunta, a descoberta e a virada vêm à frente. IDs, hashes e instrumentação sustentam a história, sem substituí-la.

## Quando e com o quê

Acione esta skill **antes de planejar ou revisar cada novo capítulo**. Leia `AGENTS.md`, `team/coruja.md`, `stories/README.md`, todos os capítulos relevantes e especialmente o último. Recolha as PRs dos animais, a matriz cumulativa, a fonte original com página ou época, os testes no SHA correspondente e os limites de independência.

**Não existe capítulo novo sem novidade verificável desde o anterior.** Um experimento que falhou, uma hipótese derrubada ou uma pista documental que mudou de sentido valem notícia. Mais uma compilação verde, uma releitura da mesma fonte e um número de hash isolado não valem.

## Descobrir a história em cinco perguntas

Escreva, primeiro para si:

1. **A aposta:** o que parecia possível descobrir ou esclarecer?
2. **O obstáculo:** qual documento, número, lacuna ou teste se interpôs?
3. **A virada:** que expectativa os fatos contrariaram? O que passou a ser possível ou impossível sustentar?
4. **A fronteira:** qual é a conclusão mais forte *defensável*? O que continua desconhecido?
5. **A próxima testemunha:** qual observação independente distinguiria duas explicações concorrentes?

Escolha **uma virada central**. Se o fato mais forte for negativo, não o esconda: a falha de uma previsão pode ser a melhor notícia da rodada.

## Ensaio de três ganchos

Antes da redação, proponha três manchetes/aberturas e escolha a mais **surpreendente que permaneça literalmente verdadeira**:

- **Paradoxo documental:** “Como reconstruir o trajeto de três objetos se a cópia recuperada de suas órbitas não registra horários idênticos?”
- **Expectativa contrariada:** “Dois objetos irmãos deveriam ajudar a prever o terceiro. Em um dos testes, a previsão piorou.”
- **Cronologia invertida:** “E se a discussão oficial sobre recuperar fragmentos fosse anterior à notícia de Conde?”

Nunca transforme “zero coincidências **neste arquivo**” em “ninguém os observou juntos”. Nunca troque “um dos quatro testes piorou” por “o modelo fracassou em todos”. O título deve resistir à leitura isolada. Exemplo: **“O cálculo que piorou a previsão”**, não “A órbita que provou a queda”.

## Cinco movimentos de uma reportagem

1. **Pergunta + promessa.** Comece por um enigma real e sua importância, num parágrafo curto. Não abra com SHA, número de PR ou nome de ferramenta.
2. **A aposta dos investigadores.** Apresente hipóteses rivais e aquilo que cada uma preveria de diferente.
3. **O teste auditável.** Mostre como o documento foi localizado ou como o experimento foi feito; inclua o dado crucial, denominador, período e fonte.
4. **A virada com ressalva incorporada.** Dê espaço para o resultado surpreender, depois explicite qual leitura sedutora ele **não** autoriza. Ressalva essencial deve aparecer no próprio corpo, não escondida na última nota.
5. **Fecho com próxima pista.** Termine com a observação específica que pode fazer a investigação avançar, inclusive se ela contrariar a hipótese de Conde. Evite o automático “a história continua”.

Use subtítulos que movam a trama (“O problema estava no calendário”, “A previsão falhou justamente ali”), não apenas “Metodologia / Resultados / Discussão”. Alterne frases curtas no momento da virada com explicação mais serena. Explique siglas na primeira aparição. A leitura deve funcionar mesmo para quem nunca ouviu falar de RAAN, TLE ou holdout.

## Exemplo: do relatório à surpresa, com o mesmo fato

**Inerte, embora correto:**

> C241-T3 comparou 45 épocas de NORAD 528 com 527/529 e obteve 0 coincidências exatas, 1/2/15 até 6/24/72 horas.

**Abertura com tensão legítima:**

> O plano parecia promissor: usar dois objetos do mesmo lançamento para reconstruir o caminho do terceiro. Mas o primeiro obstáculo não estava na gravidade. Estava no calendário. Em 45 épocas recuperadas do NORAD 528, nenhuma coincide exatamente com as dos outros dois. Como comparar posições simultâneas se o arquivo não oferece sequer a mesma hora?

**Parágrafo seguinte obrigatório:** trata-se de **épocas de uma única cópia histórica secundária**, não de prova de que o rastreamento instrumental jamais os observou juntos. Explique então as janelas de 6/24/72 horas e o que cada contagem realmente mede. A surpresa deve sobreviver à correção de escala.

## Linguagem com energia, sem sensacionalismo

- Primeiro diga **o que aconteceu**: “a previsão piorou em um dos quatro cortes”. Depois introduza RMSE, período e decimais.
- Verbos fortes são permitidos com objeto preciso: **“refutou a hipótese X”**, **“contrariou a previsão Y”**, **“a fonte documentou o relato Z”**. Proibido “comprovou a queda” quando só há dia de decaimento orbital ou notícia retransmitida.
- Mostre o caminho da apuração, os impasses, os testes adversos e o que a equipe aprendeu; nunca invente testemunhas, emoções, cenas de 1963, falas, entrevistas ou reações.
- Sem avalanche de siglas: mantenha o texto principal narrativo e use tabela ou ficha para números de apoio, IDs, hashes, PRs, repositórios e condições de reprodução. Ainda assim, associe cada afirmação decisiva a uma referência clicável.
- O leitor deve perceber o peso de uma refutação sem que ela seja apresentada como derrota total da investigação.

## Controle de verdade antes de entregar

Faça duas leituras: **como leitor leigo** e **como revisor adversarial**.

- A abertura desperta uma pergunta que os documentos realmente permitem fazer?
- Está claro o **delta** desde o capítulo anterior? Há uma virada verificável?
- O título continua exato sem as ressalvas do rodapé?
- Para cada fato decisivo há **URL, página/época, ID da matriz, proveniência, independência e grau de verificação**?
- Fonte primária inspecionada, notícia contemporânea retransmitida, catálogo secundário, inferência, hipótese e simulação permanecem distintos? Três registros de uma linhagem não viram três sensores.
- A prova Lean é declarada **condicional às premissas**? A simulação informa entradas, incertezas e holdouts? Reentrada não virou impacto?
- O teste negativo é negativo **deste universo observado**, não prova universal? Os holdouts desfavoráveis permanecem visíveis?
- O final propõe uma **nova observação discriminante**, não uma repetição do mesmo exame?

Se a melhor descoberta for “ainda não podemos concluir”, mostre exatamente **qual crença foi enfraquecida** e **qual experimento destravaria a resposta**. Isso pode ser jornalismo fascinante sem uma única afirmação inflada.

## Entrega no projeto

Use `stories/YYYY-MM-DD-slug.md`, com `title/date/summary/chapter/author/status`, pergunta inicial real, arco narrativo, **O que mudou**, referências primárias, PRs e matriz. Um novo capítulo por PR editorial **somente se houver avanço material**; caso contrário, memória de investigação negativa. Revisão factual independente pelo 🦅 Gavião, integração/publicação pelo 🐘 Elefante **apenas no site Conde**. O blog pessoal é intocável.

**Regra central:** é mais interessante dizer **“o teste que prometia localizar a queda mostrou por que a localização ainda não é demonstrável”** do que vender uma resposta que os dados não dão.

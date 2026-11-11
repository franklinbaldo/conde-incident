---
title: "Uma órbita sem endereço"
date: "2026-11-11"
summary: "Um novo cálculo acompanha posição e velocidade ao mesmo tempo. Sete testes passaram; nenhum deles ainda diz onde o objeto 528 reentrou."
chapter: "02"
author: "Coruja · Caderno de investigação"
status: "Modelo experimental; localização não demonstrada"
---

# Uma órbita sem endereço

**Como reconstruir os últimos movimentos de um objeto espacial quando o documento mais seguro informa apenas o dia em que ele deixou a órbita?** A pergunta atravessou o [primeiro capítulo](https://github.com/franklinbaldo/conde-incident/blob/feature/coruja-reportage/stories/2026-11-11-o-dia-em-que-dois-relatos-se-cruzaram.md). Ali estavam dois fios que não se tocavam: o registro de decaimento de um componente orbital e a notícia de uma esfera em Conde, na Bahia. Agora apareceu uma ferramenta para submeter uma das possíveis ligações a testes mais rigorosos. Ainda não apareceu a ligação propriamente dita.

## O passo que faltava ao cálculo

Na [PR #5, desenvolvida pelo Castor](https://github.com/franklinbaldo/conde-incident/pull/5), entrou um núcleo experimental que calcula **posição e velocidade juntas**, a cada passo. Em vez de escolher uma longitude ou ajustar a fase orbital até passar sobre Conde, o programa integra o movimento em coordenadas cartesianas inerciais. A gravidade terrestre é seu ponto de partida; a deformação gravitacional representada por *J2* pode ser incluída. O arrasto atmosférico só entra se alguém fornecer uma função de densidade, o parâmetro aerodinâmico e a procedência desses dados.

Parece um detalhe técnico. Não é. Ao forçar o modelo a carregar simultaneamente posição, velocidade, forças e condições iniciais, fica mais difícil esconder uma escolha arbitrária dentro de um mapa convincente. O código também distingue um **limiar de altitude definido pelo pesquisador** do impacto no solo: cruzar uma superfície matemática não comprova onde caiu qualquer destroço.

A implementação está disponível em [`orbitPhysics.ts`](https://github.com/franklinbaldo/conde-incident/blob/3f68ed2ed245efa84818e032a70fc2be11825de2/src/lib/orbitPhysics.ts), com [protocolo de hipóteses e limitações](https://github.com/franklinbaldo/conde-incident/blob/3f68ed2ed245efa84818e032a70fc2be11825de2/research/ORBIT_PHYSICS.md). Ela não substitui o SGP4 já usado no projeto: elementos orbitais médios de um TLE não são, automaticamente, a posição e a velocidade osculadoras exigidas por esse novo integrador.

## Sete verificações. Nenhuma coordenada de queda.

Os [sete testes automatizados](https://github.com/franklinbaldo/conde-incident/blob/3f68ed2ed245efa84818e032a70fc2be11825de2/tests/orbitPhysics.test.mjs) exercitam situações construídas para conferir consistência do programa: conservação de energia e momento angular sem arrasto, comportamento do termo J2, efeito dissipativo de uma atmosfera sintética, refinamento do instante em que se cruza uma altitude, rejeição de entradas inválidas, reprodução de uma amostra com a mesma semente e recuperação aproximada de velocidade a partir de posições **geradas pelo próprio modelo**. A [execução no GitHub Actions](https://github.com/franklinbaldo/conde-incident/actions/runs/43093340793) passou no commit `3f68ed2`.

Isso comprova que os controles escolhidos foram satisfeitos pelo código naquela versão. **Não comprova uma trajetória de 1963.** O último teste é especialmente instrutivo: recuperar parâmetros quando a resposta foi produzida pelo mesmo simulador não equivale a prevê-los diante de observações históricas desconhecidas. O teste cego com os objetos **527 e 529** ainda não foi realizado; os dados observacionais originais necessários não foram estabelecidos com proveniência e referencial compatíveis.

## O documento que continua impondo o limite

Na [página impressa 8 do *Satellite Situation Report* da NASA, de 15 de novembro de 1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), a entrada **1963 3B** aparece na lista de objetos decaídos com a data **8 NOV 63**. É uma fonte contemporânea diretamente inspecionável. **Não traz hora, posição terminal ou registro de recuperação em Conde.**

Além disso, a [matriz histórica C001–C238 da PR #1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md) registra um conflito ainda não resolvido: a orientação orbital expressa por RAAN surge como cerca de **198,5261°** em uma série derivada e **284,1520°** na configuração anterior do site. Os valores não podem ser misturados nem promediados. Antes de calcular a última passagem, é preciso saber a época, a origem e a natureza de cada conjunto de elementos.

E as hipóteses concorrentes? A ideia de uma reentrada associada à notícia baiana continua **possível, mas não demonstrada**. A hipótese de um boato jornalístico e a de um acontecimento local banal ampliado pelo noticiário não são decididas por um teste numérico de conservação de energia. Nenhuma dessas alternativas ganhou uma testemunha física nesta rodada.

## A próxima prova precisa vir de fora do simulador

O avanço é real, porém metodológico: existe agora um cálculo que permite testar trajetórias inteiras sem lhes atribuir um endereço antecipadamente. O próximo salto exigirá **épocas e elementos originais rastreáveis para 527, 528 e 529**, estados compatíveis, condições atmosféricas justificadas e uma previsão confrontada com dados reservados fora do ajuste. Se o modelo não resistir a esse confronto, o fracasso será parte da reportagem.

Por enquanto, o objeto 528 tem uma data documental de decaimento. **Não tem, nesta investigação, uma coordenada de reentrada demonstrada.**

---

**Nota de verificação:** este capítulo relata uma implementação experimental e os testes registrados na PR #5, ainda sujeita a revisão e integração. A aprovação sintética no commit citado não equivale à validação histórica da órbita, à confirmação de destroços em Conde ou à publicação deste artigo no site.

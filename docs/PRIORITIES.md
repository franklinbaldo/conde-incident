---
type: Guide
title: Prioridades vigentes do projeto Conde
description: Fila canônica de pesquisa, reavaliada pela direção de pesquisa a cada rodada por valor de informação, com issue e responsável, o que está pausado e como ler as orientações do Elefante.
---

# Prioridades vigentes do projeto Conde

**Prioridades reavaliadas pela direção de pesquisa (🐘 Elefante) a cada rodada, por valor de informação; o dono (Franklin) pode mudá-las a qualquer momento.** A lista nasceu de uma conversa com o dono em 14/11/2026 sobre os defeitos daquele momento; ele delegou a reavaliação à direção de pesquisa, que avisa o dono do que mudou e por quê. Este arquivo é a fila canônica do projeto. Instrução em chat isolado não substitui este arquivo.

**Última reavaliação:** 15/11/2026 ~19h UTC (Conde `70888ac9`). A prioridade 1 continua sem hora, local ou testemunha de Conde em fonte fora dos Diários Associados: 42 das 209 páginas lidas por inteiro, todas negativas para hora (contagem conferida pelo 🦅 Gavião, G97). A ordem das prioridades não muda; esta reavaliação grava um **critério de parada** para a leitura (seção [Critério de parada](#critério-de-parada-da-leitura)): o núcleo noticioso de 9 a 14/11 (capa, política nacional, internacional e agências, policial, ciência), não as 209 páginas. Classificados, esporte, sociedade e suplementos não são lidos. Os lotes foram redistribuídos para cobrir esse núcleo. A [matriz G84](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_G84_DOCUMENT_DECISION_20261115.md) ([PR #1030](https://github.com/franklinbaldo/conde-incident/pull/1030)) sustenta a ordem: só uma **hora do fenômeno** em fonte independente separa 528 de 637; o relógio FBIS e os elementos de 1–8/11 sozinhos não decidem. Reavaliações anteriores: `git log -p docs/PRIORITIES.md`.

**Pergunta central:** o que reduz a incerteza sobre a ligação entre o evento de Conde (BA, nov/1963) e os satélites (NORAD 528 = 1963-3B; rival 637 = 1963-35A)?

## Prioridades, por valor de informação

| # | Frente | Issue | Responsável |
|---|---|---|---|
| 1 | Hora local do suposto evento em fonte fora dos Diários Associados (o *Diário de Notícias* de Salvador é dos Diários Associados desde 1943, R71, [PR #1009](https://github.com/franklinbaldo/conde-incident/pull/1009): serve para a cadeia, não como fonte independente). **Rota aberta: leitura integral, página por página, das edições pós-evento já custodiadas** da Hemeroteca Digital BN (acesso sem login a partir do Ifro): *Última Hora* NE/Recife 9–14/11 (765147, 00472–00477), *Última Hora* do Rio 9/11 (386030, 04200; 10/11 sem edição regular entre 04200 e 04201, especial não excluída), *Correio da Manhã* 9 e 10/11 (089842, 21657 e 21658). Cobertura, onde fica o noticiário e quem lê o quê: [seção abaixo](#ordem-de-leitura-da-prioridade-1). Censo de acesso entregue pelo 🦎 Lagarto ([PR #1057](https://github.com/franklinbaldo/conde-incident/pull/1057); última passada R75, [PR #1065](https://github.com/franklinbaldo/conde-incident/pull/1065)): *Correio da Manhã* 12–14/11 = 21659–21661 pela capa, não lidas; 11/11 sem edição comprovada; catálogos de *Jornal do Brasil*, *Última Hora* do Rio, *Tribuna da Imprensa* e *A Noite* em 403; nenhuma coleção elegível de São Paulo ou Salvador achada (não prova inexistência). Parada: núcleo noticioso de 9–14/11 lido por inteiro ([critério](#critério-de-parada-da-leitura)), artigo como unidade; negativo de página não é negativo de edição. **Depende do dono** ([#884](https://github.com/franklinbaldo/conde-incident/issues/884)): *A Tarde* e *Jornal da Bahia* (item 2), *O Globo* de 8–9/11 (item 1), anexos do A-628 (item 4). Já lido: Blue Book NARA 302531012 (campo `Local` em branco, PR #1009) | [#871](https://github.com/franklinbaldo/conde-incident/issues/871) | 🦀 Caranguejo, 🦫 Castor, 🐢 Tartaruga, 🦌 Cervo; lote fechado com 🦦 Lontra (seção abaixo) |
| 2 | Cruzamento das janelas do plano 528/637 com o limite superior do relato: convenção do `2330` FBIS (GMT ou hora da Guanabara, Decreto 52.700) e hora do roteiro Tupi de 8/11. As janelas já existem (#892, G76); falta o relógio. Pela matriz G84, o relógio só diz se a passagem do 528 de 08/11 ~23h43Z veio antes ou depois da transmissão; sozinho não separa 528 de 637 | [#886](https://github.com/franklinbaldo/conde-incident/issues/886) (relógio), [#870](https://github.com/franklinbaldo/conde-incident/issues/870) (janelas) | 🐙 Polvo; 🦫 Castor consome. Apoio do 🦎 Lagarto: 0 candidatos FBIS de novembro de 1963 em acervo aberto ([#886](https://github.com/franklinbaldo/conde-incident/issues/886#issuecomment-6888170176)); a rota é o item 5 da #884 |
| 4 | Elementos orbitais de 1–8/11/1963 do 528/637 (Space-Track, SPADATS, RAE/SAO, registros soviéticos com data de 7–9/11) | [#396](https://github.com/franklinbaldo/conde-incident/issues/396), [#545](https://github.com/franklinbaldo/conde-incident/issues/545) | Em espera enquanto 🐢 Tartaruga e 🦦 Lontra estão na #871; retomar quando a #871 tiver resposta ou quando chegar o item 3 da #884 (Space-Track) |


### Janela autorizada: observações amadoras de 1963 (15/11/2026)

O **dono autorizou explicitamente** a pesquisa dos registros originais de observadores amadores (rádio e óptica) para melhorar os modelos do 528/637. A [#1093](https://github.com/franklinbaldo/conde-incident/issues/1093) é uma **rota documental nova e paralela**, especializada da #396, e **não substitui nem atrasa** o núcleo de imprensa [#871](https://github.com/franklinbaldo/conde-incident/issues/871), ainda prioridade 1. Abrir apenas censo verificável de fontes e recuperação de dados originais, sem modelo novo por catálogo. A espera geral da #396 continua, **exceto esta rota delimitada** autorizada pelo dono.

- **🦦 Lontra**: rastrear fac-símiles dos arquivos Smithsonian Moonwatch RU255 (caixas 10, 15, 21, 22), WSRN SID 65-1176 e, subsidiariamente, Kettering 1960–64, com custódia e negativo de acesso, na [lontra#11](https://github.com/franklinbaldo/lontra/issues/11). Não contatar acervos sem autorização. O censo cabe em uma rodada; não prolongar catálogo inacessível.
- **🐢 Tartaruga**: depois do lote #871 e de receber documento original, verificar SDC/COSPAR 527/528/529/637, datas UTC, instrumentos, referencial, error bars e independência, na [tartaruga#10](https://github.com/franklinbaldo/tartaruga/issues/10).
- **🐝 Abelha, 🐙 Polvo e 🦫 Castor**: somente após medida instrumental validada, respectivamente grafo/proveniência ([abelha#10](https://github.com/franklinbaldo/abelha/issues/10)), consequências Lean ([polvo#19](https://github.com/franklinbaldo/polvo/issues/19)), e atualização orbital com baseline congelado + holdout ([castor#11](https://github.com/franklinbaldo/castor/issues/11)). Brilho/rotação não são astrometria; 528 não tem rádio próprio comprovado. Sem observação nova, sem mudança física de modelo.
- **Gate:** catálogo/boletim/efeméride não é observação original; registrar `SOURCE_CATALOG_ONLY`, `CONFIRMED_INSTRUMENT` ou `ACCESS_BLOCKED`; nenhuma atribuição de local/hora de queda por mera compatibilidade orbital. CI verde no SHA da PR; Jatobá controla, executores gratuitos externos quando necessários.


Entregues e fora da lista: hipótese nula narrativa ([#887](https://github.com/franklinbaldo/conde-incident/issues/887), 🦀 Caranguejo), parada atingida em 15/11/2026: *Última Hora* Nordeste/Recife, semana-alvo 4–8/11 (48/48 páginas, [PR #1049](https://github.com/franklinbaldo/conde-incident/pull/1049)) e semana-controle 7–11/10 (48/48, [PR #1051](https://github.com/franklinbaldo/conde-incident/pull/1051)), nenhum motivo composto do FBIS confirmado; o buraco de quatro metros das estátuas em 8/11 é outra notícia, sem anterioridade provada. Um só jornal (25 slots do *Jornal do Brasil* em HTTP 403), microtexto parcialmente ilegível: taxa-base `null`, H0–H3 `UNDETERMINED`, não é prova de ausência nem de fraude. Semanas de 14 e 21/10 e dezembro ficam `NOT_READ`; reabrir só com evidência nova. Erro de dia dos controles e transferência condicional ao 528 ([PR #1019](https://github.com/franklinbaldo/conde-incident/pull/1019), sem calibração física); teste do plano orbital 528 × 637 ([PR #892](https://github.com/franklinbaldo/conde-incident/pull/892); sensibilidade a pontos modernos e ramos de relógio em [PR #944](https://github.com/franklinbaldo/conde-incident/pull/944)). Nova sensibilidade de ponto ou de modelo sem observação nova é baixo retorno.

Tabela de decisão por documento: entregue ([matriz G84](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_G84_DOCUMENT_DECISION_20261115.md), [PR #1030](https://github.com/franklinbaldo/conde-incident/pull/1030), 🦫 Castor). Itens 1, 2 e 4 da #884 podem separar 528, 637 ou nenhum, se trouxerem hora do fenômeno; itens 3 e 5 sozinhos não decidem. Nova matriz ou sensibilidade sem documento novo é baixo retorno.

Caderno (`stories/`): linha editorial e cadência na [#885](https://github.com/franklinbaldo/conde-incident/issues/885), com 🦉 Coruja; no máximo um capítulo por dia, e só a partir de uma ficha de linha narrativa com pelo menos metade dos nós `DOC`. Fichas em `research/editorial/`: J (5/7 `DOC`), D (6/9 `DOC`, [PR #1054](https://github.com/franklinbaldo/conde-incident/pull/1054)) e F (6/9 `DOC`, [PR #1068](https://github.com/franklinbaldo/conde-incident/pull/1068)) cumprem a cota. **Decisão do dono (15/11/2026):** o Caderno volta a publicar; o próximo capítulo é o episódio do carimbo `Hoax` (ficha J), no primeiro dia local sem publicação (15/11 ou 16/11); a virada pode ser a própria incerteza, dita uma vez; D e F seguem na fila, um capítulo por dia; a 🦉 pode contestar a escolha ([pedido](https://github.com/franklinbaldo/conde-incident/issues/885#issuecomment-6903305228)).

Bloqueios que só o dono destrava (login, acervo pago, pedido a acervo, consulta presencial): [#884](https://github.com/franklinbaldo/conde-incident/issues/884), no máximo 5 itens. Não tentar contornar.

## Ordem de leitura da prioridade 1

Estado em 15/11/2026 ~19h UTC (Conde `70888ac9`). "Integral" é página lida coluna por coluna (`EXAMINADA` ou `LIDO_INTEGRAL_*`); panorama, recorte e triagem lexical não contam. Números são páginas do PDF; o fólio impresso pode diferir (00472: PDF 3 = p. 7 e PDF 4 = p. 3, CGEO-78). Núcleo = páginas que o critério de parada exige.

| Jornal, edição (data) | Págs. | Integral | Ilegível em parte | Núcleo por ler |
|---|---|---|---|---|
| *Última Hora* NE 00472 (9/11) | 10 | 1, 2, 3, 5, 7, 8, 10 | 4, 6, 9 | nenhum |
| *Última Hora* NE 00473 (10/11) | 18 | 1, 4, 5, 6 | | nenhum |
| *Última Hora* NE 00474 (11/11) | 10 | 1, 2, 3, 6 | | 4 |
| *Última Hora* NE 00475 (12/11) | 10 | 1, 4, 5, 6, 7 | | nenhum |
| *Última Hora* NE 00476 (13/11) | 10 | nenhuma | | 1, 4, 5, 6 |
| *Última Hora* NE 00477 (14/11) | 10 | 7 | | 1, 4, 5, 6 |
| *Última Hora* Rio 04200 (9/11) | 16 | 6, 7, 9, 13 | 8 | 1, 2, 4 |
| *Correio da Manhã* 21657 (9/11) | 28 | 1–8, 21 | | 9 até o fim do 1º caderno (provavelmente 12) |
| *Correio da Manhã* 21658 (10/11) | 97 | 1–8 | | 9 até o fim do 1º caderno (extensão a mapear) |
| **Total das 209** | **209** | **42** | **4** | |

Fora das 209, entram no núcleo: *Última Hora* Rio 04201 (11/11) p. 1, 2, 4, 6, 8, e *Correio da Manhã* 21659–21661 (12–14/11), 1º caderno; edições identificadas pela capa, não custodiadas nem lidas. *Última Hora* Rio 04202–04204 (12–14/11) identificadas pela capa e custodiadas ([PR #1098](https://github.com/franklinbaldo/conde-incident/pull/1098)); entram no núcleo, interior ainda não lido.

**Onde fica o noticiário** (panoramas e leituras R68–R79, CGEO-76 a 81, G86 a G91, R81):

- *Última Hora* NE: p. 1 capa; p. 4 política nacional e Congresso; **p. 5 internacional por agência e espaço** (em 00474, classificados; em 00477, Congresso e Forças Armadas); **p. 6 policial**; p. 7 crônica de Stanislaw; depois sociedade, cinema, classificados e esporte.
- *Última Hora* Rio: p. 1 capa; p. 2 IPM e notícias locais; p. 4 política nacional; **p. 6 internacional e TELETIPO**; **p. 8 polícia**; p. 9–16 segundo caderno (variedades, turfe, futebol).
- *Correio da Manhã*: 1º caderno com noticiário geral, internacional e policial (21657 p. 1–8 e 21658 p. 1–8 lidas; 21658 p. 8 traz "PRECIPITAÇÃO DE OBJETOS CONTINUA"); "Aviação e Astronáutica" no 2º caderno (21657 p. 21).

## Critério de parada da leitura

Decisão da direção de pesquisa em 15/11/2026 ~19h UTC. A leitura das edições custodiadas **para** quando todas as páginas do núcleo estiverem `EXAMINADA` ou `ILEGÍVEL_PARCIAL` com o trecho ilegível registrado:

1. **Núcleo:** em cada edição de 9 a 14/11 dos três jornais (*Última Hora* NE e Rio, *Correio da Manhã*), capa, política nacional, internacional e agências (teletipo), policial e ciência ou astronáutica. Na prática, as páginas da coluna "Núcleo por ler" e o parágrafo seguinte à tabela. No *Correio*, o 1º caderno inteiro, mais páginas de ciência ou astronáutica de outros cadernos.
2. **Fora do núcleo, não se lê:** classificados, esporte, turfe, sociedade, cinema, variedades, publicidade de página inteira e suplementos. Exceção: um panorama, índice ou chamada de capa que aponte matéria sobre Conde, objeto caído, satélite, esfera ou disco; então só aquela página.
3. **Com zero hora no núcleo:** registra-se o negativo na #871 com denominador por jornal, edição e seção (páginas lidas, ilegíveis em parte, não lidas por estarem fora do núcleo). Não é negativo de edição nem prova de ausência; a prioridade 1 passa a depender só da #884 (itens 1, 2 e 4). Decisão do dono (15/11/2026): fechado o núcleo, a direção de pesquisa passa a duas rodadas por dia até o dono entregar item da #884 ou aparecer evidência nova.
4. **Com hora candidata:** vai primeiro à #871; a leitura continua nas edições seguintes do mesmo jornal, atrás de desdobramento.

Mapear cadernos (cabeçalho e fólio de cada página do PDF) não é leitura e pode ser feito de uma vez; serve para delimitar o 1º caderno.

**Divisão** (cada leitor pode contestar no seu recado):

| Leitor | Lote, nesta ordem | Depois |
|---|---|---|
Estado em 15/11/2026 ~23h UTC (decisão do dono): *Última Hora* NE, *Correio* 21657–21659 e *Última Hora* Rio 04200–04201 completos no núcleo. Falta:

| Leitor | Lote fechado | Depois |
|---|---|---|
| 🐢 Tartaruga ([tartaruga#9](https://github.com/franklinbaldo/tartaruga/issues/9)) | *Correio* 21660 PDF 5–12; 21661 PDF 1–13 | parar |
| 🦫 Castor ([castor#10](https://github.com/franklinbaldo/castor/issues/10)) | *Última Hora* Rio 04202 (12/11): política nacional, internacional/teletipo, policial, ciência | parar; sem acesso ao PDF, `NOT_RUN` na #871 e a 04202 passa à 🦦 |
| 🦦 Lontra ([lontra#10](https://github.com/franklinbaldo/lontra/issues/10)) | *Última Hora* Rio 04203 e 04204 (13–14/11), mesmas seções | parar |

Método único, o do 🦀 (CGEO-73/76): SHA do PDF original; página renderizada vista por inteiro em quadrantes ampliados; artigo como unidade; `EXAMINADA` ou `ILEGÍVEL_PARCIAL` com o trecho; OCR só como apoio. Artigo sobre Conde, Bahia, objeto caído, satélite, esfera ou balão: título, página, crédito e, se houver, hora, local e testemunha literais. Hora candidata vai primeiro à #871.

## Se a sua frente depende da fila do dono

A prioridade 2 e a parte baiana da prioridade 1 esperam documento que só o dono obtém ([#884](https://github.com/franklinbaldo/conde-incident/issues/884)); a leitura das edições custodiadas da prioridade 1 está aberta. Antes de declarar uma frente dependente só do dono, confira se toda rota aberta foi lida por inteiro, não só em panorama. Se a sua frente está nessa situação:

1. **Não fabrique fatia.** Nova sensibilidade, novo contador zerado ou nova busca no mesmo acervo fechado não reduzem a incerteza.
2. **Registre o negativo ou o bloqueio uma vez**, na issue da frente, com a evidência (URL, status HTTP, guia do acervo). Se o bloqueio for algo que só o dono destrava, diga qual item da #884 cobre ou proponha um item.
3. **Escolha da lista abaixo** ou **encerre a rodada com nota curta** ("frente bloqueada por #884 item N; nada novo"). Encerrar sem PR é resultado válido.

**Lontra e Cervo:** entregaram os lotes fechados de 15/11 ~17h UTC ([PR #1082](https://github.com/franklinbaldo/conde-incident/pull/1082), [PR #1081](https://github.com/franklinbaldo/conde-incident/pull/1081)); recebem novo lote em 15/11 ~19h UTC (seção acima).

Trabalho aberto e não bloqueado (15/11/2026 ~19h UTC):

- Prioridade 1: leitura do núcleo das edições de 9–14/11, na divisão da seção acima, até o critério de parada; quem estiver livre e tiver acesso à Hemeroteca pede um lote na #871, sem pegar página já atribuída.
- Fichas de linha narrativa da 🦉 Coruja que não dependam de fonte bloqueada (exemplo entregue: ficha J, carimbo `Hoax` do Blue Book, [PR #1016](https://github.com/franklinbaldo/conde-incident/pull/1016)); [#885](https://github.com/franklinbaldo/conde-incident/issues/885).
- Migração para o grafo cumulativo ([#88](https://github.com/franklinbaldo/conde-incident/issues/88)) **apenas** de ocorrências ligadas às prioridades 1–3.
- Auditoria retrospectiva do 🦅 Gavião em PRs já integradas das prioridades (como a G81, [PR #1017](https://github.com/franklinbaldo/conde-incident/pull/1017)).

## Pausado enquanto as prioridades 1–4 estiverem abertas

- Polimento de UX, SSG e CI além de defeito real (quebra de build ou publicação, acessibilidade bloqueante, página publicada errada).
- Guardas de genealogia de catálogo.
- Covariância óptica e IERS.
- Meteorologia.
- Priors de massa.
- Cartografia fina.

Uma PR nessas frentes diz na descrição qual defeito real corrige ou qual decisão autoriza. Animais dessas frentes recebem tarefa de apoio às prioridades pelo Elefante (ver [#339](https://github.com/franklinbaldo/conde-incident/issues/339)).

## Como ler as orientações do Elefante

- Antes de escolher a fatia da rodada, ler este arquivo e os comentários na **própria issue** assinados `De: 🐘 Elefante` (ou, antes de 14/11/2026 ~19h UTC, "orientador"). Uma orientação do Elefante na issue do animal faz parte desta fila.
- O 🐘 Elefante é uma identidade só, com dois executores; as orientações valem igualmente. Em conflito, prevalece a decisão mais recente e explícita do dono.
- Discordar é permitido: responda na issue com o motivo e a evidência. Não responder e seguir outra frente não é discordância.
- Orientação ignorada é reiterada uma vez; depois disso o Elefante relata ao dono e pode reatribuir a issue.

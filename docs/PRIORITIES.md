---
type: Guide
title: Prioridades vigentes do projeto Conde
description: Fila canônica de pesquisa, reavaliada pela direção de pesquisa a cada rodada por valor de informação, com issue e responsável, o que está pausado e como ler as orientações do Elefante.
---

# Prioridades vigentes do projeto Conde

**Prioridades reavaliadas pela direção de pesquisa (🐘 Elefante) a cada rodada, por valor de informação; o dono (Franklin) pode mudá-las a qualquer momento.** A lista nasceu de uma conversa com o dono em 14/11/2026 sobre os defeitos daquele momento; ele delegou a reavaliação à direção de pesquisa, que avisa o dono do que mudou e por quê. Este arquivo é a fila canônica do projeto. Instrução em chat isolado não substitui este arquivo.

**Última reavaliação:** 15/11/2026 ~17h UTC (Conde `a5899021`). A prioridade 1 continua sem hora, local ou testemunha de Conde em fonte fora dos Diários Associados. O gargalo agora é o ritmo: 13 das 209 páginas das edições pós-evento já custodiadas foram lidas por inteiro, a cerca de 2 páginas por rodada por leitor. A ordem das prioridades não muda; esta reavaliação fixa uma **ordem de leitura por valor**, divide as páginas sem sobreposição e chama a 🦦 Lontra e o 🦌 Cervo, livres, para lotes fechados (seção [Ordem de leitura da prioridade 1](#ordem-de-leitura-da-prioridade-1)). O critério de "lido por inteiro" não muda. A [matriz G84](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_G84_DOCUMENT_DECISION_20261115.md) ([PR #1030](https://github.com/franklinbaldo/conde-incident/pull/1030)) sustenta a ordem: só uma **hora do fenômeno** em fonte independente separa 528 de 637; o relógio FBIS e os elementos de 1–8/11 sozinhos não decidem. Reavaliações anteriores: `git log -p docs/PRIORITIES.md`.

**Pergunta central:** o que reduz a incerteza sobre a ligação entre o evento de Conde (BA, nov/1963) e os satélites (NORAD 528 = 1963-3B; rival 637 = 1963-35A)?

## Prioridades, por valor de informação

| # | Frente | Issue | Responsável |
|---|---|---|---|
| 1 | Hora local do suposto evento em fonte fora dos Diários Associados (o *Diário de Notícias* de Salvador é dos Diários Associados desde 1943, R71, [PR #1009](https://github.com/franklinbaldo/conde-incident/pull/1009): serve para a cadeia, não como fonte independente). **Rota aberta: leitura integral, página por página, das edições pós-evento já custodiadas** da Hemeroteca Digital BN (acesso sem login a partir do Ifro): *Última Hora* NE/Recife 9–14/11 (765147, 00472–00477), *Última Hora* do Rio 9/11 (386030, 04200; 10/11 sem edição regular entre 04200 e 04201, especial não excluída), *Correio da Manhã* 9 e 10/11 (089842, 21657 e 21658). Cobertura, onde fica o noticiário e quem lê o quê: [seção abaixo](#ordem-de-leitura-da-prioridade-1). Censo de acesso entregue pelo 🦎 Lagarto ([PR #1057](https://github.com/franklinbaldo/conde-incident/pull/1057); última passada R75, [PR #1065](https://github.com/franklinbaldo/conde-incident/pull/1065)): *Correio da Manhã* 12–14/11 = 21659–21661 pela capa, não lidas; 11/11 sem edição comprovada; catálogos de *Jornal do Brasil*, *Última Hora* do Rio, *Tribuna da Imprensa* e *A Noite* em 403; nenhuma coleção elegível de São Paulo ou Salvador achada (não prova inexistência). Parada: cada edição lida por inteiro, artigo como unidade; negativo de página não é negativo de edição. **Depende do dono** ([#884](https://github.com/franklinbaldo/conde-incident/issues/884)): *A Tarde* e *Jornal da Bahia* (item 2), *O Globo* de 8–9/11 (item 1), anexos do A-628 (item 4). Já lido: Blue Book NARA 302531012 (campo `Local` em branco, PR #1009) | [#871](https://github.com/franklinbaldo/conde-incident/issues/871) | 🦀 Caranguejo, 🦫 Castor, 🐢 Tartaruga; lotes fechados com 🦦 Lontra e 🦌 Cervo (seção abaixo) |
| 2 | Cruzamento das janelas do plano 528/637 com o limite superior do relato: convenção do `2330` FBIS (GMT ou hora da Guanabara, Decreto 52.700) e hora do roteiro Tupi de 8/11. As janelas já existem (#892, G76); falta o relógio. Pela matriz G84, o relógio só diz se a passagem do 528 de 08/11 ~23h43Z veio antes ou depois da transmissão; sozinho não separa 528 de 637 | [#886](https://github.com/franklinbaldo/conde-incident/issues/886) (relógio), [#870](https://github.com/franklinbaldo/conde-incident/issues/870) (janelas) | 🐙 Polvo; 🦫 Castor consome. Apoio do 🦎 Lagarto: 0 candidatos FBIS de novembro de 1963 em acervo aberto ([#886](https://github.com/franklinbaldo/conde-incident/issues/886#issuecomment-6888170176)); a rota é o item 5 da #884 |
| 4 | Elementos orbitais de 1–8/11/1963 do 528/637 (Space-Track, SPADATS, RAE/SAO, registros soviéticos com data de 7–9/11) | [#396](https://github.com/franklinbaldo/conde-incident/issues/396), [#545](https://github.com/franklinbaldo/conde-incident/issues/545) | Em espera enquanto 🐢 Tartaruga e 🦦 Lontra estão na #871; retomar quando a #871 tiver resposta ou quando chegar o item 3 da #884 (Space-Track) |

Entregues e fora da lista: hipótese nula narrativa ([#887](https://github.com/franklinbaldo/conde-incident/issues/887), 🦀 Caranguejo), parada atingida em 15/11/2026: *Última Hora* Nordeste/Recife, semana-alvo 4–8/11 (48/48 páginas, [PR #1049](https://github.com/franklinbaldo/conde-incident/pull/1049)) e semana-controle 7–11/10 (48/48, [PR #1051](https://github.com/franklinbaldo/conde-incident/pull/1051)), nenhum motivo composto do FBIS confirmado; o buraco de quatro metros das estátuas em 8/11 é outra notícia, sem anterioridade provada. Um só jornal (25 slots do *Jornal do Brasil* em HTTP 403), microtexto parcialmente ilegível: taxa-base `null`, H0–H3 `UNDETERMINED`, não é prova de ausência nem de fraude. Semanas de 14 e 21/10 e dezembro ficam `NOT_READ`; reabrir só com evidência nova. Erro de dia dos controles e transferência condicional ao 528 ([PR #1019](https://github.com/franklinbaldo/conde-incident/pull/1019), sem calibração física); teste do plano orbital 528 × 637 ([PR #892](https://github.com/franklinbaldo/conde-incident/pull/892); sensibilidade a pontos modernos e ramos de relógio em [PR #944](https://github.com/franklinbaldo/conde-incident/pull/944)). Nova sensibilidade de ponto ou de modelo sem observação nova é baixo retorno.

Tabela de decisão por documento: entregue ([matriz G84](https://github.com/franklinbaldo/conde-incident/blob/main/research/statistics/C241_G84_DOCUMENT_DECISION_20261115.md), [PR #1030](https://github.com/franklinbaldo/conde-incident/pull/1030), 🦫 Castor). Itens 1, 2 e 4 da #884 podem separar 528, 637 ou nenhum, se trouxerem hora do fenômeno; itens 3 e 5 sozinhos não decidem. Nova matriz ou sensibilidade sem documento novo é baixo retorno.

Caderno (`stories/`): linha editorial e cadência na [#885](https://github.com/franklinbaldo/conde-incident/issues/885), com 🦉 Coruja; no máximo um capítulo por dia, e só a partir de uma ficha de linha narrativa com pelo menos metade dos nós `DOC`. Fichas em `research/editorial/`: J (5/7 `DOC`) e D (6/9 `DOC`, [PR #1054](https://github.com/franklinbaldo/conde-incident/pull/1054)) cumprem a cota, mas a própria 🦉 as declara não publicáveis sem virada documental no nó decisivo.

Bloqueios que só o dono destrava (login, acervo pago, pedido a acervo, consulta presencial): [#884](https://github.com/franklinbaldo/conde-incident/issues/884), no máximo 5 itens. Não tentar contornar.

## Ordem de leitura da prioridade 1

Estado em 15/11/2026 ~17h UTC (Conde `a5899021`). "Integral" é página lida coluna por coluna (`EXAMINADA` ou `LIDO_INTEGRAL_*`); panorama, recorte e triagem lexical não contam. Números são páginas do PDF; o fólio impresso pode diferir (00472: PDF 3 = p. 7 e PDF 4 = p. 3, CGEO-78).

| Jornal, edição (data) | Págs. | Integral | Só panorama ou recorte | Por ler |
|---|---|---|---|---|
| *Última Hora* NE 00472 (9/11) | 10 | 1, 2, 3, 5 | 4 e 6 ilegíveis em parte; 7–10 | 6 |
| *Última Hora* NE 00473 (10/11) | 18 | 5 | as outras 17 | 17 |
| *Última Hora* NE 00474 (11/11) | 10 | nenhuma | 10 | 10 |
| *Última Hora* NE 00475 (12/11) | 10 | 5 | 9 | 9 |
| *Última Hora* NE 00476 (13/11) | 10 | nenhuma | só a nota da p. 5 | 10 |
| *Última Hora* NE 00477 (14/11) | 10 | 7 | 9 | 9 |
| *Última Hora* Rio 04200 (9/11) | 16 | 9, 13 | 14 (1–5 a 190 dpi; recortes da p. 6) | 14 |
| *Correio da Manhã* 21657 (9/11) | 28 | 1, 2, 5, 21 | 24 | 24 |
| *Correio da Manhã* 21658 (10/11) | 97 | nenhuma (só a matéria da p. 8) | | 97 |
| **Total** | **209** | **13** | | **196** |

Fora da conta: *Última Hora* Rio 04201 (11/11) e *Correio da Manhã* 21659–21661 (12–14/11), identificadas pela capa e não lidas.

**Onde fica o noticiário em que Conde sairia** (só o que os panoramas e leituras registram: R68, R69, R71, CGEO-76 a 79, G86 a G89, R74, R76, R77):

- *Última Hora* NE: p. 1 capa; p. 2–4 política (p. 4 nacional e Congresso em 00473 e 00475); **p. 5 internacional por agência (FP, AP) e espaço** (Explorer 18 em 00473, Polet I em 00475, Cosmos 21 em 00476; em 00477 a p. 5 traz Congresso e Forças Armadas; em 00474, classificados); **p. 6 policial** (00472 a 00475 e 00477); p. 7 crônica de Stanislaw (00475, 00477); depois sociedade, cinema, classificados e esporte (00473 p. 13–18, suplemento feminino). 00476 fora da p. 5: seção não identificada.
- *Última Hora* Rio 04200: p. 1 capa; p. 2 IPM e notícias locais; p. 4 política nacional e Congresso; **p. 6 internacional e coluna TELETIPO** (condensado de ANSA, UPI, FP e outras); **p. 8 polícia**; p. 9–16 segundo caderno (variedades, turfe, futebol).
- *Correio da Manhã* 21657: 1º caderno com noticiário geral (p. 1, 2 e 5 lidas); p. 21 é a p. 9 do 2º caderno (Aviação e Astronáutica), logo o 1º caderno ocupa provavelmente as PDF 1–12 (inferência pelo fólio, a conferir). Demais seções não identificadas.
- *Correio da Manhã* 21658: p. 8 noticiário ("PRECIPITAÇÃO DE OBJETOS CONTINUA"); demais seções não identificadas.

**Ordem:** (1) noticiário nacional, policial, teletipo ou agências e ciência das edições de 9 e 10/11; (2) as mesmas seções de 11–14/11; (3) o resto. Negativo de edição só com todas as páginas.

**Divisão** (sugestão da direção; cada leitor pode contestar no seu recado):

| Leitor | Lote, nesta ordem | Depois |
|---|---|---|
| 🦫 Castor ([castor#10](https://github.com/franklinbaldo/castor/issues/10)) | *Última Hora* Rio 04200: p. 6, 8, 4, 1, 2 | 3, 5, 7, 10–12, 14–16; 04201 só com novo pedido |
| 🦀 Caranguejo ([caranguejo#5](https://github.com/franklinbaldo/caranguejo/issues/5)) | 00472 p. 4 e 6 (trechos ilegíveis); 00473 p. 1, 4, 6; depois 00476 p. 1, 5, 6 e 00477 p. 1, 5, 6 | resto de 00472, 00473, 00476 e 00477 |
| 🐢 Tartaruga ([tartaruga#9](https://github.com/franklinbaldo/tartaruga/issues/9)) | *Correio* 21657: p. 3, 4, 6, 7, 8, depois 9–12 | 13–28; depois 21658 a partir da p. 9 |
| 🦦 Lontra ([lontra#10](https://github.com/franklinbaldo/lontra/issues/10)), lote fechado | 00474 p. 1, 2, 3, 6; 00475 p. 1, 4, 6, 7 | parar |
| 🦌 Cervo ([cervo#6](https://github.com/franklinbaldo/cervo/issues/6)), lote fechado | *Correio* 21658: p. 1–8 (a p. 8 inteira) | parar |

Método único, o do 🦀 (CGEO-73/76): SHA do PDF original; página renderizada vista por inteiro em quadrantes ampliados; artigo como unidade; `EXAMINADA` ou `ILEGÍVEL_PARCIAL` com o trecho; OCR só como apoio. Artigo sobre Conde, Bahia, objeto caído, satélite, esfera ou balão: título, página, crédito e, se houver, hora, local e testemunha literais. Hora candidata vai primeiro à #871.

## Se a sua frente depende da fila do dono

A prioridade 2 e a parte baiana da prioridade 1 esperam documento que só o dono obtém ([#884](https://github.com/franklinbaldo/conde-incident/issues/884)); a leitura das edições custodiadas da prioridade 1 está aberta. Antes de declarar uma frente dependente só do dono, confira se toda rota aberta foi lida por inteiro, não só em panorama. Se a sua frente está nessa situação:

1. **Não fabrique fatia.** Nova sensibilidade, novo contador zerado ou nova busca no mesmo acervo fechado não reduzem a incerteza.
2. **Registre o negativo ou o bloqueio uma vez**, na issue da frente, com a evidência (URL, status HTTP, guia do acervo). Se o bloqueio for algo que só o dono destrava, diga qual item da #884 cobre ou proponha um item.
3. **Escolha da lista abaixo** ou **encerre a rodada com nota curta** ("frente bloqueada por #884 item N; nada novo"). Encerrar sem PR é resultado válido.

**Lontra:** a fatia R73 foi encerrada ([PR #1038](https://github.com/franklinbaldo/conde-incident/pull/1038)); em 15/11 ~17h UTC a 🦦 Lontra recebe um lote fechado de 8 páginas da prioridade 1 (seção acima).

Trabalho aberto e não bloqueado (15/11/2026 ~17h UTC):

- Prioridade 1: leitura das edições custodiadas, na ordem e divisão da seção acima; quem estiver livre e tiver acesso à Hemeroteca pede um lote na #871, sem pegar página já atribuída.
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

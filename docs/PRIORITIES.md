---
type: Guide
title: Prioridades vigentes do projeto Conde
description: Fila canônica de pesquisa, reavaliada pela direção de pesquisa a cada rodada por valor de informação, com issue e responsável, o que está pausado e como ler as orientações do Elefante.
---

# Prioridades vigentes do projeto Conde

**Prioridades reavaliadas pela direção de pesquisa (🐘 Elefante) a cada rodada, por valor de informação; o dono (Franklin) pode mudá-las a qualquer momento.** A lista nasceu de uma conversa com o dono em 14/11/2026 sobre os defeitos daquele momento; ele delegou a reavaliação à direção de pesquisa, que avisa o dono do que mudou e por quê. Este arquivo é a fila canônica do projeto. Instrução em chat isolado não substitui este arquivo.

**Entrega técnica em 15/11/2026, 🦌 Cervo:** a antiga prioridade 3, erro de dia e aplicação congelada ao 528, foi concluída pela [PR #1019](https://github.com/franklinbaldo/conde-incident/pull/1019) após a [#1013](https://github.com/franklinbaldo/conde-incident/pull/1013) e auditoria [#1017](https://github.com/franklinbaldo/conde-incident/pull/1017). A dinâmica de 27/10 **não refina** o dia NASA `8 NOV`: somente alguns cenários condicionais o interceptam, e o estrato apenas-637/mediana-3 não o intercepta. Sem hora, sigma ou limite físico. A frente sai da lista ativa; cabe ao 🐘 Elefante reavaliar a numeração/prioridade das demais frentes. Nova seção "Se a sua frente depende da fila do dono": quase tudo o que resta nas prioridades 1 e 2 depende da [#884](https://github.com/franklinbaldo/conde-incident/issues/884), e frente bloqueada não justifica fatia fabricada. Correção de fato: o *Diário de Notícias* de Salvador pertence aos Diários Associados desde 1943 ([R71 da 🐢, PR #1009](https://github.com/franklinbaldo/conde-incident/blob/main/research/editorial/conde_local_hour_bluebook_2026_11_C241_TARTARUGA_R71.md)), logo não é fonte independente; as fontes baianas independentes da prioridade 1 são *A Tarde* e *Jornal da Bahia*. Reavaliação anterior, 15/11/2026 ~02h UTC: nenhuma fonte trouxe hora local do evento; no Blue Book (NARA 302531012) o campo `Local` da hora está em branco na imagem 0809, e os horários de 0810–0811 são relógios das mensagens ([PR #1009](https://github.com/franklinbaldo/conde-incident/pull/1009)). Em 14/11/2026 ~21h UTC o teste do plano orbital 528 × 637 (antiga prioridade 3) foi entregue pela PR #892 e pela G76 (PR #944) e saiu da lista de pendências; no lugar subiu o cruzamento das janelas do plano com o limite superior do relato, que pode excluir janelas do 528 sem depender de documento novo.

**Pergunta central:** o que reduz a incerteza sobre a ligação entre o evento de Conde (BA, nov/1963) e os satélites (NORAD 528 = 1963-3B; rival 637 = 1963-35A)?

## Prioridades, por valor de informação

| # | Frente | Issue | Responsável |
|---|---|---|---|
| 1 | Hora local do suposto evento em fonte fora dos Diários Associados. Baianas independentes: *A Tarde* e *Jornal da Bahia*; fora da Bahia: *O Globo*, *Última Hora* Nordeste; documentos: Blue Book NARA 302531012 (campo `Local` em branco, PR #1009), anexos do A-628. O *Diário de Notícias* de Salvador é dos Diários Associados (R71, PR #1009): serve para reconstruir a cadeia, não como fonte independente. Rota aberta: *Última Hora* (PE) de 1963 baixa sem login na coleção 765147 da Biblioteca Nacional ([PR #1002](https://github.com/franklinbaldo/conde-incident/pull/1002)); 9–12/11 custodiadas ([PR #1004](https://github.com/franklinbaldo/conde-incident/pull/1004)), páginas internas em leitura ([PR #1011](https://github.com/franklinbaldo/conde-incident/pull/1011)) | [#871](https://github.com/franklinbaldo/conde-incident/issues/871) | 🐢 Tartaruga (Blue Book, *Diário de Notícias*); 🦦 Lontra (*A Tarde*, *Última Hora* de 9–12/11) |
| 2 | Cruzamento das janelas do plano 528/637 com o limite superior do relato: convenção do `2330` FBIS (GMT ou hora da Guanabara, Decreto 52.700) e hora do roteiro Tupi de 8/11. As janelas já existem (#892, G76); falta o relógio | [#886](https://github.com/franklinbaldo/conde-incident/issues/886) (relógio), [#870](https://github.com/franklinbaldo/conde-incident/issues/870) (janelas) | 🐙 Polvo; 🦫 Castor consome. Apoio do 🦎 Lagarto: 0 candidatos FBIS de novembro de 1963 em acervo aberto ([#886](https://github.com/franklinbaldo/conde-incident/issues/886#issuecomment-6888170176)); a rota é o item 5 da #884 |

| 4 | Elementos orbitais de 1–8/11/1963 do 528/637 (Space-Track, SPADATS, RAE/SAO, registros soviéticos com data de 7–9/11) | [#396](https://github.com/franklinbaldo/conde-incident/issues/396), [#545](https://github.com/franklinbaldo/conde-incident/issues/545) | Em espera enquanto 🐢 Tartaruga e 🦦 Lontra estão na #871; retomar quando a #871 tiver resposta ou quando chegar o item 3 da #884 (Space-Track) |
| 5 | Hipótese nula narrativa: enredo montado com peças de redação | [#887](https://github.com/franklinbaldo/conde-incident/issues/887) | 🦀 Caranguejo. Apoio do 🦇 Morcego: os 25 slots do *Jornal do Brasil* deram HTTP 403 na BN, sem coleta ([#887](https://github.com/franklinbaldo/conde-incident/issues/887#issuecomment-6887750028)); seguir com os slots da *Última Hora* já custodiados |

Entregues e fora da lista: erro de dia dos controles e transferência condicional ao 528 ([PR #1019](https://github.com/franklinbaldo/conde-incident/pull/1019), sem calibração física); teste do plano orbital 528 × 637 ([PR #892](https://github.com/franklinbaldo/conde-incident/pull/892); sensibilidade a pontos modernos e ramos de relógio em [PR #944](https://github.com/franklinbaldo/conde-incident/pull/944)). Nova sensibilidade de ponto ou de modelo sem observação nova é baixo retorno.

Tabela de decisão por documento: para cada item da #884 (e o roteiro da Rádio Tupi do Rio de 8/11), que resultados ele pode trazer e o que cada um faz com 528 e 637, sem probabilidades e com `NÃO_AVALIÁVEL` onde o repositório não basta ([#1020](https://github.com/franklinbaldo/conde-incident/issues/1020), 🦫 Castor). Serve para ordenar a fila do dono.

Caderno (`stories/`): linha editorial e cadência na [#885](https://github.com/franklinbaldo/conde-incident/issues/885), com 🦉 Coruja; no máximo um capítulo por dia, e só a partir de uma ficha de linha narrativa com pelo menos metade dos nós `DOC`.

Bloqueios que só o dono destrava (login, acervo pago, pedido a acervo, consulta presencial): [#884](https://github.com/franklinbaldo/conde-incident/issues/884), no máximo 5 itens. Não tentar contornar.

## Se a sua frente depende da fila do dono

Quase tudo o que resta nas prioridades 1 e 2 espera documento que só o dono obtém ([#884](https://github.com/franklinbaldo/conde-incident/issues/884)). Se a sua frente está nessa situação:

1. **Não fabrique fatia.** Nova sensibilidade, novo contador zerado ou nova busca no mesmo acervo fechado não reduzem a incerteza.
2. **Registre o negativo ou o bloqueio uma vez**, na issue da frente, com a evidência (URL, status HTTP, guia do acervo). Se o bloqueio for algo que só o dono destrava, diga qual item da #884 cobre ou proponha um item.
3. **Escolha da lista abaixo** ou **encerre a rodada com nota curta** ("frente bloqueada por #884 item N; nada novo"). Encerrar sem PR é resultado válido.

Trabalho aberto e não bloqueado (15/11/2026 ~03h UTC):

- Leitura integral da *Última Hora* (PE) de 9–12/11/1963: rota BN aberta ([PR #1002](https://github.com/franklinbaldo/conde-incident/pull/1002)), PDFs custodiados ([PR #1004](https://github.com/franklinbaldo/conde-incident/pull/1004)), 35 páginas internas de 00473–00475 pendentes depois da [PR #1011](https://github.com/franklinbaldo/conde-incident/pull/1011). Prioridade 1, #871, com a 🦦 Lontra.
- Hipótese nula narrativa ([#887](https://github.com/franklinbaldo/conde-incident/issues/887)) com as fatias já pré-registradas (CGEO-64, `research/editorial/cgeo64_null_narrative_prereg_20261114.json`) nos slots da *Última Hora* com capa datada (CGEO-66, [PR #1012](https://github.com/franklinbaldo/conde-incident/pull/1012)). Os 25 slots do *Jornal do Brasil* estão bloqueados (HTTP 403 na BN).
- Tabela de decisão por documento ([#1020](https://github.com/franklinbaldo/conde-incident/issues/1020)).
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

---
type: Guide
title: Prioridades vigentes do projeto Conde
description: Fila canônica de pesquisa, reavaliada pela direção de pesquisa a cada rodada por valor de informação, com issue e responsável, o que está pausado e como ler as orientações do Elefante.
---

# Prioridades vigentes do projeto Conde

**Prioridades reavaliadas pela direção de pesquisa (🐘 Elefante) a cada rodada, por valor de informação; o dono (Franklin) pode mudá-las a qualquer momento.** A lista nasceu de uma conversa com o dono em 14/11/2026 sobre os defeitos daquele momento; ele delegou a reavaliação à direção de pesquisa, que avisa o dono do que mudou e por quê. Este arquivo é a fila canônica do projeto. Instrução em chat isolado não substitui este arquivo.

**Última reavaliação:** 15/11/2026 ~02h UTC (ordem mantida; responsáveis e estado atualizados). Nenhuma fonte trouxe hora local do evento: no Blue Book (NARA 302531012) o campo `Local` da hora está em branco na imagem 0809, e os horários de 0810–0811 são relógios das mensagens ([PR #1009](https://github.com/franklinbaldo/conde-incident/pull/1009)); o *Diário de Notícias* de Salvador é dos Diários Associados desde 1943, logo não é independente da rede. Reavaliação anterior, 14/11/2026 ~21h UTC: o teste do plano orbital 528 × 637 (antiga prioridade 3) foi entregue pela PR #892 e pela G76 (PR #944) e saiu da lista de pendências; no lugar subiu o cruzamento das janelas do plano com o limite superior do relato, que pode excluir janelas do 528 sem depender de documento novo.

**Pergunta central:** o que reduz a incerteza sobre a ligação entre o evento de Conde (BA, nov/1963) e os satélites (NORAD 528 = 1963-3B; rival 637 = 1963-35A)?

## Prioridades, por valor de informação

| # | Frente | Issue | Responsável |
|---|---|---|---|
| 1 | Hora local do suposto evento em fonte fora dos Diários Associados (*A Tarde*, *Jornal da Bahia*, *O Globo*, *Última Hora* Nordeste, Blue Book NARA 302531012, anexos do A-628; o *Diário de Notícias* serve para reconstruir a cadeia, não como fonte independente). Rota aberta: *Última Hora* (PE) de 1963 baixa sem login na coleção 765147 da Biblioteca Nacional ([PR #1002](https://github.com/franklinbaldo/conde-incident/pull/1002)); 9–12/11 custodiadas ([PR #1004](https://github.com/franklinbaldo/conde-incident/pull/1004)), páginas internas em leitura ([PR #1011](https://github.com/franklinbaldo/conde-incident/pull/1011)) | [#871](https://github.com/franklinbaldo/conde-incident/issues/871) | 🐢 Tartaruga (Blue Book, *Diário de Notícias*); 🦦 Lontra (*A Tarde*, *Última Hora* de 9–12/11) |
| 2 | Cruzamento das janelas do plano 528/637 com o limite superior do relato: convenção do `2330` FBIS (GMT ou hora da Guanabara, Decreto 52.700) e hora do roteiro Tupi de 8/11. As janelas já existem (#892, G76); falta o relógio | [#886](https://github.com/franklinbaldo/conde-incident/issues/886) (relógio), [#870](https://github.com/franklinbaldo/conde-incident/issues/870) (janelas) | 🐙 Polvo; 🦫 Castor consome; apoio pedido ao 🦎 Lagarto (candidatos FBIS de novembro de 1963) |
| 3 | Erro empírico da previsão de decaimento em controles com dia conhecido (637 e outros do SSR NASA), depois aplicado ao 528 | [#647](https://github.com/franklinbaldo/conde-incident/issues/647) | 🦌 Cervo |
| 4 | Elementos orbitais de 1–8/11/1963 do 528/637 (Space-Track, SPADATS, RAE/SAO, registros soviéticos com data de 7–9/11) | [#396](https://github.com/franklinbaldo/conde-incident/issues/396), [#545](https://github.com/franklinbaldo/conde-incident/issues/545) | Em espera enquanto 🐢 Tartaruga e 🦦 Lontra estão na #871; retomar quando a #871 tiver resposta ou quando chegar o item 3 da #884 (Space-Track) |
| 5 | Hipótese nula narrativa: enredo montado com peças de redação | [#887](https://github.com/franklinbaldo/conde-incident/issues/887) | 🦀 Caranguejo; apoio pedido ao 🦇 Morcego (custódia dos slots do *Jornal do Brasil*) |

Entregue e fora da lista: teste do plano orbital 528 × 637 ([PR #892](https://github.com/franklinbaldo/conde-incident/pull/892); sensibilidade a pontos modernos e ramos de relógio em [PR #944](https://github.com/franklinbaldo/conde-incident/pull/944)). Nova sensibilidade de ponto ou de modelo sem observação nova é baixo retorno.

Caderno (`stories/`): linha editorial e cadência na [#885](https://github.com/franklinbaldo/conde-incident/issues/885), com 🦉 Coruja; no máximo um capítulo por dia, e só a partir de uma ficha de linha narrativa com pelo menos metade dos nós `DOC`.

Bloqueios que só o dono destrava (login, acervo pago, pedido a acervo, consulta presencial): [#884](https://github.com/franklinbaldo/conde-incident/issues/884), no máximo 5 itens. Não tentar contornar.

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

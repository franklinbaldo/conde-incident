---
type: Skill
title: "Skill do Conde: coruja"
name: conde-coruja
description: Produzir capítulos jornalísticos do Caderno Conde somente quando houver avanço documental ou experimental auditável.
---

# 🦉 Coruja: skill de trabalho no Conde

**Projeto atual:** `franklinbaldo/conde-incident`.
**Regra comum:** seguir `AGENTS.md` da `main` e `franklinbaldo/cafezinho/team/coruja.md`, criar PRs pequenas, consultar evidências e registrar OKF. Esta skill é mantida principalmente pelo próprio agente.

## Missão
Contar a investigação como sequência de descobertas, erros e perguntas vivas, sem modificar fatos. Cada capítulo Markdown corresponde a novidade verificável, não a uma contagem de PRs verdes.

## Em cada rodada
1. Ler `AGENTS.md`, `franklinbaldo/cafezinho/team/coruja.md`, esta skill, capítulos anteriores e PRs científicas novas, preservando IDs, datas e genealogia dos relatos.
2. Consultar a skill complementar `conde-reportagem-com-virada` quando disponível; elaborar pergunta, aposta, teste, resultado surpreendente e próximo registro discriminante.
3. Distinguir reportagem Tupi/FBIS, documento NASA, TLE secundário, hipótese de balão e cálculos exploratórios. Registrar fonte e incerteza próxima da afirmação; nunca apresentar 1963 como cena testemunhada não documentada.
4. Criar somente um capítulo por PR **pequena**, com links, testes da estrutura e build do gerador de site escolhido pelo projeto; não publicar ou alterar o blog pessoal.
5. Confirmar CI do SHA e merge próprio se a dependência editorial estiver resolvida; registrar artigo, fonte, decisão e próximo gancho no OKF.

## Contrato com o leitor externo

A história pertence ao leitor curioso sobre **o que ocorreu (ou teria ocorrido) em Conde em 1963**, não ao público interno de desenvolvedores. Ao editar cada artigo, aplicar a [skill pessoal da Coruja](https://github.com/franklinbaldo/coruja/blob/main/.agents/skills/coruja/SKILL.md):

- Abertura: pergunta verdadeira sobre o episódio, seguida por documento, testemunho documental ou resultado que a esclareça.
- Desenvolvimento: hipóteses concorrentes, virada comprovada, limites da fonte e próxima observação discriminante. Suspense vem da investigação, não de cenas inventadas.
- **Não narrar mudanças no site anterior, commits, PRs, workflows, versões, CI ou contagens de testes como notícia sobre 1963.** Quando método científico mudar uma interpretação, contar a consequência para o caso. Deixar rastreabilidade técnica em notas discretas e PRs do projeto.
- Ao recuperar capítulos antigos, reescrever passagens internas para o público geral, sem apagar documentos originais, limites ou resultados negativos. Isso é correção editorial, não capítulo novo nem descoberta científica.

## Linha editorial: uma história inteira antes de outra nota (Conde #885)

**Referência de método, sem imitação de voz:** *The Constant*, de Mark Chrisler, como exemplo de narrativa investigativa sobre como uma versão errada nasceu, circulou, pareceu razoável e encontrou uma contraprova. A voz é autoral, em português brasileiro, com ironia seca apenas quando os próprios documentos a sustentarem.

1. **O erro e as pessoas:** recuperar quem publicou, leu, corrigiu ou retransmitiu, sem atribuir intenções, testemunhos ou cenas imaginárias.
2. **A digressão paga:** uma tabela soviética, um telégrafo ou uma crônica só entra quando explica algo concreto do caso Conde. Toda peça retorna à notícia de 1963.
3. **A virada documental:** mostrar a hipótese plausível, o documento que a fortaleceu ou desfez e a pergunta ainda testável. Não ocultar um fato conhecido para fabricar suspense.
4. **O tema maior:** contágio de versões, cópias tomadas como observações independentes, data de catálogo confundida com lugar, e limites de uma apuração à distância.
5. **A prova manda:** manter fontes primárias, independência, ressalva precisa no ponto necessário e distinção entre notícia, parecer administrativo, dado orbital e vestígio físico. Nenhuma redução de rigor pelo efeito narrativo.

**Porta de entrada:** manter [*O que sabemos até agora*](/conde-incident/o-que-sabemos/) (página, não capítulo) com atualização datada e máximo de 2.000 palavras. A primeira leitura deve incluir o relato Tupi/FBIS, a negativa consular, hipótese meteorológica, NORAD 528 e rival 637, e a falta de hora/observação física. Apontar do dossiê para essa página. Melhorar o acesso no índice do Caderno em coordenação com o dono dos templates/SSG; nunca alterar template comum em conflito.

**Cadência:** preferir consolidar capítulos existentes e notas de evidência. Durante a consolidação, no máximo uma história nova por dia. Material de custódia e negativas sem virada ficam em `research/` e memória, não ganham manchete por contagem de PRs.

**Teste de saída por artigo:** leitor de fora compreende a história sem GitHub? A incerteza foi dita uma vez com precisão, sem repetição? Há uma ligação explícita com Conde? O texto não tem SHA, bytes, HTTP, pipeline ou detalhes de CI no corpo? Links e IDs históricos foram preservados? Se um teste falhar, reescrever antes da PR.

## Fronteiras
Nenhuma história sem delta. Incompatibilidade de fonte ou cálculo contrário à hipótese é notícia tão válida quanto confirmação.

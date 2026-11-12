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

## Fronteiras
Nenhuma história sem delta. Incompatibilidade de fonte ou cálculo contrário à hipótese é notícia tão válida quanto confirmação.

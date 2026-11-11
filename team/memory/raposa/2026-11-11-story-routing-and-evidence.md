# OKF — 🦊 Raposa, 2026-11-11: links estáveis no Caderno

## Contexto e fonte
- Repositório: `franklinbaldo/conde-incident`; issue [#9](https://github.com/franklinbaldo/conde-incident/issues/9), PR editorial base [#3](https://github.com/franklinbaldo/conde-incident/pull/3), matriz científica base [#1](https://github.com/franklinbaldo/conde-incident/pull/1).
- Normas lidas na `main`: `AGENTS.md` e `team/raposa.md`.
- Código observado na branch da Coruja, commit `d587eb68b46ce65457c817e6bffaa2e4a91e2fd8`: `src/components/Reportage.tsx` armazenava capítulo só em `useState` e os cards eram `button`; `src/App.tsx` mantinha a aba apenas em memória. Resultado deduzido do código: recarregar ou copiar URL não preserva seleção, Back/Forward não sincroniza. **Não houve teste visual no navegador até aqui.**
- Proveniência de pesquisa somente para contexto editorial: matriz histórica C001–C238 em `research/evidence_matrix_C001-C238_2026-11-11.md` no commit `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b` da PR #1. A matriz separa C01 (relato da Rádio Tupi via FBIS) e C197–C202 (registro NASA de data de decaimento): documentos de natureza diferente; não provam local de impacto, hora ou ligação causal.

## Alterações desta sessão
- Implementação separada, empilhada sobre a PR #3, sem editar o capítulo da Coruja.
- Contrato de URL em `src/lib/storyRoutes.ts`: `#/stories`, `#/stories/<slug>`, `#/tab/<aba>`; slugs inválidos rejeitados e slugs não presentes mostrados como não encontrados.
- `App.tsx`: restaurar aba da URL, reagir a `hashchange`, sincronizar clique de aba e browser Back/Forward.
- `Reportage.tsx`: cards e retorno viram links nativos de teclado/cópia, foco no título, `lang=pt-BR`, datas com `time`, layout móvel responsivo e ponte explícita para snapshot da matriz da PR #1, com distinção entre fontes e observações.
- Teste de rotas `tests/storyRoutes.test.mjs` no CI editorial da PR empilhada; `stories/README.md` documenta rotas e integração pendente.

## Grau de verificação / limites
- **INSPECIONADO**: contratos e conteúdo do código nas branches #1/#3; matriz C001–C238 consultada para contexto, sem nova observação documental.
- **IMPLEMENTADO, não validado ainda por CI no momento de escrever**: roteamento, renderização e navegação. Verificar no run da PR o SHA final, `node --experimental-strip-types --test`, `bun run lint`, dois builds Vite.
- **NOT_RUN**: navegação manual móvel, leitor de tela, visualização do mapa nesta combinação, integração final das abas Evidence + Caderno, publicação GitHub Pages; não chamar build de deploy.
- **Sem contato externo e sem edição do blog pessoal**; nenhum dado orbital ou alegação de testemunha foi alterado.

## Próxima dúvida / handoff
Quando 🐘 integrar #1 e #3, reconciliar `App.tsx`/`Navigation.tsx` conservando `research` e `reportage`; o roteador de abas precisa reconhecer `research` e a ligação à matriz pode tornar-se uma navegação direta para Evidence. 🦅 deve revisar a semântica da ponte documental. CI da PR empilhada precisa terminar verde no HEAD final antes do merge. O SHA do commit final e URL do run devem ficar registrados na descrição da PR, pois este cartão é escrito antes da conclusão do CI.

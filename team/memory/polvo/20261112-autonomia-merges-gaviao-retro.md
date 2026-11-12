# 🐙 Polvo — mudança de governança por decisão do proprietário (12/11/2026)

- Repositório único: https://github.com/franklinbaldo/conde-incident
- Decisão: agentes autores deixam de depender do merge central do Elefante e da revisão prévia do Gavião. Todos podem fazer merge da própria PR pequena após CI necessário no HEAD real, dependências e conflitos tratados; preservar fontes e avisos científicos, sem rebase nem force-push.
- Gavião: revisão **retrospectiva cumulativa** de todos os merges desde checkpoint gravado em team/memory/gaviao/, com relatório de falhas e pequenas correções.
- Elefante: coordena equipes, questões, prioridades, dependências, chamadas e integração transversal; não detém aprovação exclusiva.
- Escopo documental: AGENTS.md, oito fichas team/*.md e scripts/agent-owned-merges.test.mjs. A matriz da PR #1 não foi modificada. Não altera blog, fonte histórica, modelo orbital, simulação nem arquivo externo.
- Prova de ausência de afirmações científicas novas: a mudança é somente organizacional. CI deve incluir os novos testes Node e Bun TypeScript/build; após commit e merge verificar GitHub Actions no HEAD. Nenhuma execução de Lean é pretendida enquanto formal/ não integrar a main.
- Próximo passo: cada dono deve decompor seus ramos extensos em PRs independentes, realizar merge das fatias verificadas e registrar o SHA; Gavião revisa a janela desde o último checkpoint. O passado em Git não é apagado.

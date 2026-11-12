---
type: AgentMemory
title: "🦊 Triangulação: retirar corredor e relógio inventados"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
verification: CI_PENDING_ON_FINAL_HEAD
---

## Leitura e fonte

- Reli integralmente AGENTS.md e team/raposa.md na main, o estado das PRs #1/#3/#24/#28 e das issues, a issue #9 e seus handoffs, o cartão OKF anterior e a matriz cumulativa C001–C238 hospedada na PR #1. A PR #28 continua proposta, não integrada na main.
- Fonte do problema: [TriangulationDashboard.tsx antes desta alteração](https://github.com/franklinbaldo/conde-incident/blob/de062ab77febfb66d14f58fa14f597c44d63b69d/src/components/TriangulationDashboard.tsx). A tela exibia como fato uma passagem 08/11/1963 19:48 UTC, corredores do 527, latitude/longitude/altura pontuais, arrasto calibrado, certeza absoluta e exclusão de tempestades. Isso não é fundamentado por ajuste dinâmico/holdout verificados.
- Base documental de segunda leitura: [matriz C001–C238, SHA pinado da PR #1](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md). C197–C202 descrevem a data de decaimento registrada em [NASA SSR 15/11/1963, p. impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), sem hora ou coordenadas. Série RAAN 284,1520° vs ~198,5261° continua conflitada e não conciliada. C44–C46 têm ocorrências geográficas e orbitais distintas. Os resultados do holdout 529 são condicionais aos dados e modelos utilizados. NÃO houve nova inspeção do fac-símile NASA ou de TLEs nesta rodada.
- Independência: NASA/NORAD podem partilhar rastreamento; a cadeia Tupi→FBIS não são duas observações físicas. Um checksum não autentica custódia.

## Fatia entregue

- Substituído o painel de triangulação de 551 linhas que calculava falsa passagem histórica e supostos corredores intransponíveis por comparação documental interativa dos objetos 527/528/529, com seleção por botões, aria-pressed, região de detalhe anunciada, foco visível e conteúdos PT/EN.
- Cada objeto distingue conhecimento sustentado e o que permanece não demonstrado. Fluxo visível conecta custódia RAAN → restrições Lean condicionais C44–C46 → domínio admissível/erro numérico ausentes → contraprova holdout 529, sem fabricar intervalo, posição, probabilidade ou relógio terminal.
- Deep links apontam para ocorrências reais #/research/c197, #/research/raan, #/research/holdout529, #/research/c44-orbital e mapa exploratório. Fonte matriz e NASA estão disponíveis no contexto. PR #43 é indicada como contrato de cenários ainda não integrado.
- Arquivos: src/components/TriangulationDashboard.tsx (commit de código 4ecec38b868f83eba71a491f79bb0d75496c38e8), tests/triangulationScientificLimits.test.mjs (commit de testes 9e2d1eace7fc7d60200c67bf5a4d6205a8db54cf). Física, TLE, matriz, Markdown da Coruja, blog pessoal, publicação e contatos não tocados.

## Verificação, limites e próxima dúvida

- Verificado por leitura estática de código: o painel anterior fazia afirmações sem proveniência suficiente e o novo painel não calcula nem renderiza corredor, suposta passagem ou hora terminal.
- CI no HEAD que inclui esta memória: pendente neste momento; conferir Actions e atualizar handoff com SHA literal e conclusão. Regressões Node, TypeScript/Vite, Zola e auditoria HTML devem ser reexecutados no HEAD final. Não usar gate anterior.
- NOT_VERIFIED: teste interativo em navegador móvel/leitor de tela, integridade física dos dados, TLEs primários, domínio admissível não vazio, erro/holdout dinâmico calibrado, revisão Gavião, integração #1/#3/#24, deploy Pages. Conclusão científica continua indeterminada.
- Próxima dúvida: a aba de sensibilidade atmosférica e a visualização dos TLEs ainda sugerem precisão/confiabilidade além dos limites atuais? Auditar componentes sem alterar a física. Gavião revisa e Elefante coordena a integração.

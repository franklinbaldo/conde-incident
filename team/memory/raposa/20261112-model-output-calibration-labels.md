---
type: AgentMemory
title: "🦊 Hipóteses numéricas sem aparência de observação"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
verification: CI_pending_on_final_memory_commit
---

## Origem, custódia e leitura desta rodada

- Reli integralmente `AGENTS.md` e `team/raposa.md` da `main`, a issue #9, PRs #1/#3/#24/#28, discussões de #9, memória OKF anterior e matriz C001–C238 da PR #1. A PR #28 ainda estava aberta, então separam-se seu fluxo proposto e o AGENTS da main vigente.
- [Matriz cumulativa C001–C238](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md): C01/C02 são relato documentado dependente de Tupi→FBIS, C197–C202 dão somente o **dia** 08/11 de decaimento catalogado pela NASA; C44–C46 têm ocorrências duplicadas; a RAAN histórica segue não conciliada. Esta é inspeção de repositório, **não** nova inspeção de documento primário.
- Inspecionados [`src/lib/monteCarlo.ts`](https://github.com/franklinbaldo/conde-incident/blob/raposa/zola-evidence-lab-deeplinks/src/lib/monteCarlo.ts) e [`src/lib/inverseSolver.ts`](https://github.com/franklinbaldo/conde-incident/blob/raposa/zola-evidence-lab-deeplinks/src/lib/inverseSolver.ts): o primeiro usa `Math.random()` inclusive para fase orbital e RAAN 284.152, sem seed ou holdout cego. O segundo calcula distâncias e heurísticas de viabilidade sob órbita legada; seu próprio rótulo ALTA/MODERADA não é validação empírica. Não foram mudados.
- Antes da correção a UI Monte Carlo dizia “Probabilidade empírica” e “Veredito Final”, afirmava admissibilidade e apresentava ausência física de esfera como fato. O leitor inverso autoescolhia a passagem mais próxima em 08/11 e exibia notas e semáforos de “Viabilidade Física” sem calibração.

## Entrega observável

- `MonteCarloVisualizer.tsx`: legenda, cabeçalho e cartões declaram **amostras sintéticas** e **fração da amostra**, nunca chances históricas. O canvas ganhou texto alternativo e explicação visual. Removido o parecer bayesiano não sustentado; agora há links à NASA C197–C202, conflito RAAN e holdout 529. Assumida ausência de seed e de domínio admissível validado.
- `InversePassInspector.tsx`: retirado o selecionador automático de uma suposta passagem histórica; cada cenário precisa ser escolhido pelo leitor (botão de teclado/aria-pressed), e a troca de dia limpa a seleção. Retirados badges físicos e notas de modelo que vendiam viabilidade; horas/parâmetros são explicitamente modelados. Links para C197, C44 orbital e RAAN; as medições documentais não mudaram.
- `tests/modelUXScientificLimits.test.mjs`: quatro regressões do contrato UX e da origem sintética do código. São guardas de apresentação e de proveniência do software, **não** testes físicos ou testes visuais reais.
- Auditoria do gate: o [run #43159611259](https://github.com/franklinbaldo/conde-incident/actions/runs/43159611259) passou 19/19 testes, lint, Vite, Zola e check-site, porém o checkout do log era um **merge sintético** (9b7e2e2) com head 09cf92bb; não constitui execução literal do HEAD. A workflow passou então a selecionar explicitamente `github.event.pull_request.head.sha` e afirmar `git rev-parse HEAD`. CI do novo commit de memória ainda **PENDING**.
- Commits parciais: `3867fb0b` (Monte Carlo), `850d46fc` (inversão), `46cd0aec` (regressões), `09cf92bb` (primeira memória) e `43b73458` (checkout exato); o SHA final da PR incluirá este cartão de memória. Não alterados textos jornalísticos da Coruja, núcleo científico, blog pessoal, rastreamento ou arquivos históricos.

## Verificação, incerteza e próxima dúvida

- Verificado por leitura do código: existência dos rótulos indevidos no código anterior e sua substituição na proposta. GitHub Actions no SHA **final** ainda deve ser consultado. Build TypeScript/Vite, Zola check/build e auditoria de rotas: **PENDING** neste registro, não atribuir PASS antecipado.
- **NOT_VERIFIED:** distribuição calibrada, fator balístico real, datas/posições de impacto, independente 527/529, domínio físico não vazio, Lean integrado, leitores de tela/dispositivos, deploy Pages. Inferência histórica segue indeterminada; NASA compartilha possível cadeia de rastreamento com NORAD, não são duas testemunhas.
- Próxima dúvida: a tela legada `TriangulationDashboard.tsx` ainda inclui o relógio de 19h48 em 08/11 e linguagem de certeza absoluta; examinar/remover com escopo e testes próprios, sem reescrever física. 🦅 Gavião revisa, 🐘 Elefante concilia #1/#3/#24 e só integra com CI no HEAD da integração.

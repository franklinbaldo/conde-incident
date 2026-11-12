---
type: AgentMemory
title: "🦊 Sem horário terminal inventado ao abrir o mapa"
description: "PR #24, issue #9: remover 19h48 UTC da inicialização, distinguir dia de catálogo de evento e evitar badges que exageram certeza"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
code_commit: 9b13285605fefae14abee3cb8486cb688656d434
verification: code_inspection_ci_pending
---

## Fonte, custódia e decisão

- Consultei integralmente `AGENTS.md` e `team/raposa.md` na `main`, issue #9, PRs abertas #1/#3/#24/#28, a árvore da branch e os cartões OKF da Raposa. A PR #28 continua aberta; o fluxo proposto foi respeitado sem afirmar que já entrou na `main`.
- Matriz cumulativa da [PR #1, SHA 38ee0f0](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md): C01/C02 têm origem comum Tupi/FBIS (linhas 19–20); C44–C46 têm ocorrências geográficas e orbitais distintas (linhas 164–177); C197–C202 documentam o dia de decaimento 08/11/1963 em boletim NASA de 15/11, **sem hora/posição terminal** (linhas 899–912). Usei essa matriz e a auditoria prévia, sem nova inspeção de fac-símile nem observação física.
- Defeito reproduzível por inspeção: apesar da ablação anterior no `OrbitalMap.tsx`, `src/App.tsx` ainda iniciava `sharedTimeMs` em `1963-11-08T19:48:00Z`, propagando uma hora fictícia como cursor inicial do mapa. O código do mapa não podia garantir que a tela deixasse de insinuar um instante terminal.
- Agora `sharedTimeMs` inicia `undefined`; `OrbitalMap` usa o padrão exploratório preexistente `LAUNCH_MS` enquanto o visitante não seleciona horário. Isso é **marco de interface**, não órbita validada. A interação inversa continua podendo alterar o tempo, ainda sob hipótese.
- A navegação substitui «Decaimento» por «Dia catalogado», descreve a coordenada de Conde como **sede aproximada** (não local de queda), troca «Veredito» e «Rastreamento» por rótulos cautelosos, remove selos «Checksums 100%», «7 Respostas», «N=5000» e «Desclassificados», e marca seleção de PT/EN com `aria-pressed` e `role=group`. O rodapé aponta que a posição terminal não está validada.
- Regressões em `tests/mapScientificLimits.test.mjs` verificam ausência do relógio inventado em `App`, estado inicial indefinido, default exploratório do mapa, descrição do dia/coordenada, acessibilidade do idioma e retirada dos selos. Esses testes são de código e contrato de interface, **não** ensaio em navegador, sensor nem validação científica.
- Nenhum Markdown jornalístico `stories/*.md`, arquivo de blog pessoal, cálculo orbital, Lean, matriz ou evidência histórica foi modificado. Branch/PR #24 existente, sem rebase, force-push ou merge.

## Verificação e próximo problema

**Inspeção de código:** alterações gravadas até `9b13285605fefae14abee3cb8486cb688656d434` e fontes consultadas como acima. **CI GitHub Actions no SHA final incluindo esta memória:** ainda não confirmado ao escrever o cartão, requer conferir `build` (Node, TypeScript, Vite, Zola, HTML). **NOT_VERIFIED:** teste real de mobile/leitor de tela, integração com #1/#3, validade dos modelos físicos e deploy Pages. A simples aprovação do build não seria publicação.

**Próxima dúvida falsificável:** o início em marco de lançamento, herdado do mapa, ainda sugere predição física além da época dos TLEs? A equipe de dinâmica precisa especificar o domínio temporal sustentado por dados históricos; a UI pode então restringir o cursor sem inferir hora final. 🦅 auditar teclado/idioma e 🐘 reconciliar bases antes de integração.

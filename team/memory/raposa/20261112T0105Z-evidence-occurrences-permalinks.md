---
type: AgentMemory
title: "🦊 Ligações permanentes de ocorrências e cadeia de premissas no laboratório"
description: "Fatia verificável da PR #24: C44–C46 com namespaces distintos, foco acessível e limites do Lean visíveis"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
code_commit: e0eb6008d840cfaa7392a8a6bb238fa128d8d532
---

## Fonte e grau de verificação

- **Lido diretamente na main (GitHub)**: `AGENTS.md` e `team/raposa.md`; issue #9, PRs #1, #3, #24, #28, outros PRs ativos e avisos de colisão nas PRs #14/#25/#27. A #28 ainda é proposta aberta, não norma da main. Ficheiro base da própria PR #24: HEAD anterior `34cc60cb414fc5e8bf225fc8627c46a4bd77f912`.
- **Matriz lida integralmente do snapshot PR #1**: `research/evidence_matrix_C001-C238_2026-11-11.md` no SHA `38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`; C01/C02 linhas 19–20, C44–C46 solo/geologia linhas 160–168, segunda ocorrência C44–C46 ajuste orbital linhas 171–185, C197–C202 linhas 899–912. C44–C46 têm duas identidades textuais distintas; não usar rótulo puro como ID global. C240/C241 colidem entre propostas científicas e arquivísticas ainda não reconciliadas; deliberadamente não foram incorporados como fatos únicos.
- **Lean examinado diretamente, não compilado nesta rodada**: `formal/Conde1963/Core.lean` da PR #1: `no_double_count_tupi` (L26–33), `date_alone_does_not_identify_place` (L79–100), `more_constraints_never_expand` (L102–107), `joint_model_did_not_beat_quadratic_on_holdout` (L60–65), `last528` (L67–77). Teoremas assumem registros e predicados; não autenticam radar nem asseguram domínio não vazio. O último elemento orbital é dado no código, não resultado provado.
- **Código escrito na PR #24**: `src/lib/labRoutes.ts` agora rejeita ocorrência desconhecida e diferencia `#/research/c44-geographic` de `#/research/c44-orbital`; `EvidenceTrace.tsx` expõe links por ocorrência, fonte, premissa, prova condicional (quando disponível), estado de domínio e holdouts; cartões focados após navegação e seleção visível; texto em PT/EN. `src/App.tsx` propaga idioma e atualiza `document.documentElement.lang`; os capítulos Zola apontam a C01 e C197 sem atribuir causalidade; testes de rotas e auditoria de HTML ampliados.
- **Evidência científica separada**: PR #14 examina origem TLE, PR #20 controla holdout 529, PR #25 aponta registros NARA e PR #27 registra colisões C240/C241. Não transformar sucesso de testes formais ou de hash em observação espacial. Conflito RAAN 284,1520° vs ~198,5261° continua aberto. NASA documenta 08/11 como dia do decaimento, não hora ou local terminal.
- **Verificado via escrita GitHub**: commit de código `e0eb6008d840cfaa7392a8a6bb238fa128d8d532`, branch `raposa/zola-evidence-lab-deeplinks`, sem rebase/force-push/merge. **Ainda NOT_VERIFIED ao registrar este cartão:** CI no HEAD com memória, teste visual real mobile/teclado/leitor de tela, integração da #1/#3 e deploy. Asserções Node são teste da gramática de URLs, não teste do navegador ou física.

## Resultado e próxima dúvida

A UI comunica cinco etapas com níveis distintos de verificação; domínio físico não vazio, intervalos precisos e identificação de Conde permanecem `NOT_VERIFIED` / indeterminados. Não modifiquei reportagens `stories/*.md`, blog pessoal, núcleo Lean nem física.

**Próxima dúvida falsificável:** após reconciliar as colisões globais C240/C241, qual chave de ocorrência estável será adotada pela matriz única para exportar links diretos sem duplicar registros? 🦅 deve verificar leitura por teclado, foco de hash e rotas profundas em navegador; 🐘 deve integrar só com PRs de base conciliadas e CI verde no SHA final. Conferir novamente GitHub Actions após este cartão antes de qualquer aceite.

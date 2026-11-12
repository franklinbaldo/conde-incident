---
type: AgentMemory
title: "🦊 Mapa: retirar instante de impacto fictício e rotular marcos ilustrativos"
description: "PR #24, issue #9: ablação de falsas medições terminais, regressão e navegação por teclado no mapa"
date: 2026-11-12
agent: raposa
repository: franklinbaldo/conde-incident
issue: 9
pr: 24
code_commit: abb0619a7ef3ea1e15de8b0f7fadf281fbada51b
verification: code_reviewed_and_ci_partial
---

## Fontes e escopo da verificação

- **Diretrizes lidas integralmente na main:** `AGENTS.md` e `team/raposa.md`. Conferidas issue #9, PRs #1, #3, #24 e proposta científica ainda aberta #28; retomado o branch existente `raposa/zola-evidence-lab-deeplinks`, não houve merge ou force-push.
- **Documento cumulativo consultado no snapshot da PR #1 (`38ee0f01134f6a1ee07c9346945d058d2ad3ce0b`):** `research/evidence_matrix_C001-C238_2026-11-11.md`, em especial C197–C202 (NASA, decaimento registrado em **08/11/1963**, sem hora/posição terminal), C01/C02 (uma mesma cadeia de relato) e ocorrências C44–C46. Esta rodada não reinspecionou o fac-símile NASA em si e não cria uma nova evidência histórica.
- **Diagnóstico observado diretamente no código antes da mudança:** o mapa abria um painel de `MOMENTO DO IMPACTO` às 19:48 UTC/16:48 locais, apresentava ~844 km, ~91 km, ΔM +44,8°, B = 0,022 m²/kg, `~0,006%` e o qualificativo de único corredor fisicamente plausível sem lastro validado. As entradas `OBS-07`, `OBS-08` e `OBS-11` eram exibidas como observações de instante terminal, incluindo horários arbitrários de fim do dia. A própria `AGENTS.md` proíbe converter data NASA em timestamp 23:59 ou localização.
- **Alteração de UX na PR #24:** eliminado painel e controle de pausa no suposto impacto; `publicMilestones` retira do mapa esses três marcadores não observados, **sem apagar o catálogo legado nem modificar núcleo físico**. Mensagem persistente PT/EN explica modelo vs. observação e aponta para `#/research/c197` e `#/research/raan`. Marcadores e faixas sintéticas ficam desligados por padrão; nomenclatura de medição radar foi substituída por marco ilustrativo. Os pinos da linha do tempo restante agora são `button` com nome acessível/foco de teclado.
- **Regressões:** `tests/mapScientificLimits.test.mjs` garante filtragem, ausência das frases/números terminais indevidos, avisos e links; `pages.yml` executa todos os testes Node, além de TypeScript/Vite/Zola. No SHA intermediário `75dbed046867e9d2caf84c8e0edf555ac577f20f`, o [GitHub Actions #43140088886](https://github.com/franklinbaldo/conde-incident/actions/runs/43140088886) teve **build SUCCESS** e `deploy SKIPPED`. A limpeza de ramificações mortas e acessibilidade dos pinos avançou depois, até `abb0619a`; requer novo CI no HEAD final **com esta memória** antes do aceite.
- **Não verificado:** qualidade visual em navegador móvel e leitor de tela, integração após merge de #1/#3, integridade física dos pontos do modelo, prova Lean integrada, deploy Pages. Nenhuma publicação, blog pessoal, contato externo, autoria da Coruja, cálculo orbital ou observação nova.

## Limite científico e próxima dúvida

A supressão é **somente de apresentação**: `NORAD_OBSERVATION_EVENTS` e outras fontes legadas ainda contêm dados sintéticos; o próximo trabalho científico deve auditar as épocas, a proveniência de todos os pontos de navegação e o conflito RAAN 284,1520° versus ~198,5261°. Não inferir possibilidade, exclusão ou instante de impacto apenas da renderização. A tela permanece uma **simulação exploratória com resultado indeterminado**, não uma reconstrução histórica.

**Próxima verificação:** 🦅 testar teclado e experiência em viewport móvel, 🐘 reconciliar a pilha #1/#3/#24 e passar CI no SHA integrado; equipe de física precisa fornecer intervalos admissíveis com unidades, erros e holdouts antes de qualquer geolocalização. Conferir o run novo referente ao commit final desta rodada.

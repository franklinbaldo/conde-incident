---
type: Guide
title: 'G45: descoberta vazia de testes Node não pode aprovar integração'
description: Auditoria de 13 integrações e contraprovas executáveis do gate de descoberta Node.
---

# 🦅 G45: o gate de testes não pode ficar vazio

## Janela congelada

Conde `main` após `5b72218b98621637d28000a3c82d86496585a9be` até `23b69249fddb897945f611d47247a8d6428fe2a7`, antes da correção G45: **13 integrações first-parent**, **17 commits no DAG** e **dois merges convencionais** (#582 e #583). O [manifesto](gaviao-main-window-20261113-g45.json) contém cada SHA, pais e arquivos alterados. CI histórico individual: `NOT_CHECKED`; nenhuma aprovação é presumida. Inclui o reparo #588, cujos testes orbitais agora aparecem nominalmente no workflow, e as novidades documentais #578, #580–#585, UX #587/#589 e artigo #590.

## G45-F1: retorno zero com nenhum teste Node descoberto

O workflow `Integration checks (exact head)` executa testes Python com descoberta vazia proibida, porém o passo Node `Execute present Node regression suites` terminava com `echo NO_NODE_TEST_FILES` e **exit 0** se ambos os globs `scripts/**/*.test.mjs` e `tests/**/*.test.mjs` não encontrassem nada. Contraprova executada em diretório temporário vazio: o script original retornou 0 e não executou Node. Isso significa uma lacuna do contrato de CI, **não** prova que merges reais tenham omitido testes. Hoje o projeto tem dezenas de testes Node; a condição requer ausência total ou renomeação dos arquivos, portanto não é uma afirmação de falha histórica.

**Correção proposta:** abortar o passo com `::error::` e `exit 1` quando a descoberta estiver vazia. `tests/test_ci_node_discovery_gate.py` extrai e executa o corpo Bash **real do workflow** em diretórios temporários: caso negativo sem testes deve falhar, caso positivo com `tests/smoke.test.mjs` deve executar um `node` substituto verificável. Antes da correção, 1 teste passou e 1 reprovou; depois, **2/2 passaram**. Isso protege o caso de conjunto vazio, não substitui contagem efetiva/execução de suites em CI, nem audita número de testes internos.

## Limites científicos e próximos passos

O conteúdo de C241-L33 (registro ONU) demonstra classificação administrativa, **não** uma época de observação ou posição terminal; L35 e P22/P29 permanecem documentais ou condicionais. Nenhum desses merges, por si, estabelece a trajetória terminal do NORAD 528. **Conde segue indeterminado.** Exigir CI do HEAD final da PR, depois CI pós-merge, antes de declarar integração concluída; próxima janela começa após `23b69249`, incluindo a própria correção G45.

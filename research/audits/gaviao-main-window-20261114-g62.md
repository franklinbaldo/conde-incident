---
type: Guide
title: '🦅 G62: gatilhos completos para replay óptico IERS e tempo de luz'
description: 'Auditoria retrospectiva de 16 commits após G61, com contraprova source-only nos filtros do replay original IERS.'
---

# G62: não deixar o tempo de luz escapar do replay IERS

**Recorte congelado:** `09ecdd81b5e62b0e955f4f1f9fdfa83097612480` (exclusivo) → `1673fa6` (inclusivo), 16 commits no DAG. Foram examinados os arquivos alterados nesta janela, com foco no replay IERS associado às integrações #786 (sensibilidade de tempo de luz) e #791 (Jacobiana/covariância 6D). Os checks individuais históricos de todos os commits da janela permanecem **NOT_CHECKED**. Não há pretensão de revisão linha a linha dos demais 14 commits.

## G62-F1: fontes diretas sem gatilho específico de CI

A configuração `.github/workflows/iers-eop-1963.yml` já executava `test_iers_1963_optical.py`, que passou a importar `tools/iers_1963_optical_lighttime.py` e `tools/iers_1963_optical_lighttime_jacobian.py`. Entretanto, nenhum desses dois módulos estava incluído nos filtros `on.pull_request.paths` ou `on.push.paths`. Uma edição isolada da implementação, sem tocar testes, não dispararia o replay especializado de bytes IERS de 1963. As duas notas de fronteira científica G60/G61 também faltavam nos filtros. A inclusão desses caminhos não declara que houve falha histórica do replay nem substitui checks gerais.

**RED:** adicionado `tests/test_iers_1963_workflow_paths.py`, que falhou nos dois casos antes de alterar o YAML, listando cinco ausências em `pull_request` e cinco em `push` (incluído o próprio teste novo). A política percorre os blocos de eventos, não apenas substrings em nomes de comandos.

**GREEN:** adicionar os cinco caminhos aos dois eventos, executar o novo teste no próprio workflow depois do replay óptico original e testar mutantes que removem individualmente cada caminho de cada evento. Resultado local: 2/2 testes de política aprovados, dez mutantes rejeitados. O CI original também baixa a fonte IERS remota e confere o hash nos validadores científicos; o teste novo é complementar, não substituto.

**Limite científico:** a Jacobiana 6D e a covariância angular são condicionais ao estado orbital informado, não são medições instrumentais de NORAD 528. Nenhum evento novo, posição terminal, hora de impacto ou evidência de queda em Conde é inferido desta auditoria. CI do HEAD autoral e reexecução dos bytes IERS precisam ser verificados antes de integrar.

Referências: [PR #786](https://github.com/franklinbaldo/conde-incident/pull/786), [PR #791](https://github.com/franklinbaldo/conde-incident/pull/791), [G60 #767](https://github.com/franklinbaldo/conde-incident/pull/767).

---
type: Guide
title: 'G40: integridade dos passos universais de CI'
description: Auditoria retrospectiva científica, editorial e de software de dezesseis integrações; contraprova e reparo de desvio dos testes essenciais.
---

# 🦅 G40: os passos de CI também precisam executar

## Corte e genealogia

Auditoria da `main` **exclusiva** de `4a5f0d35bc10c14927e1b948b63c516f5184ddfb` até **inclusiva** de `9a2f98151d3e9db98384f532cee6d5cea90958dd`, congelada antes da correção G40. O [manifesto G40](gaviao-main-window-20261113-g40.json) enumera, por commit, SHAs, pais, PR, alterações pela primeira linha de pais e resultado da API oficial de check-runs no momento da auditoria.

**Contagem:** 16 integrações na linha principal, 23 commits no DAG, dois merges convencionais (#501, #506), sete commits laterais. Os demais foram integrados com um pai. Todos os commits da linha principal estão ligados a PRs por mensagem; um commit lateral não equivale a um push direto na `main`.

No snapshot consultado em 13/11/2026, as integrações #497 e #498 contêm, respectivamente, **um e dois checks `cancelled`**, registrados sem os converter em `success`; as demais apresentaram check-runs com conclusão `success` na consulta. Essa é uma fotografia dos checks registrados, não reexecução independente de todos os workflows.

## G40-F1: um *job* verde pode conter testes ausentes

A PR [#509](https://github.com/franklinbaldo/conde-incident/pull/509) protegeu os jobs `web`, `lean` e `prek` contra `if:` e `continue-on-error` no nível do job. A verificação não percorria os **steps**. Com o mesmo job presente, uma mudança em `Run prek hooks over all tracked files` para `if: false`, `continue-on-error: true` ou `run: echo gate-disabled` **continuava aceita pela política**. O mesmo vale para outros passos essenciais. Não há evidência de que uma alteração maliciosa tenha ocorrido na execução histórica; trata-se de falha de proteção demonstrada em mutantes sintéticos.

**Red/green:** o novo teste adversarial falhou localmente contra a implementação anterior (condições e substituição de comando aceitas). O reparo requer exatamente uma ocorrência dos passos essenciais em cada job, comandos esperados e ausência de desativação ou tolerância no nível do step. A exceção `if: steps.detect.outputs.available == 'true'` na compilação Lean é mantida como condição legítima, ligada ao detector prévio. Há também controles de remoção de passos e controle positivo do workflow atual.

**Limite do reparo:** é análise estática de um subconjunto explícito de YAML. Não prova a semântica de scripts Bash arbitrários, não verifica o SHA remoto por si só e não substitui a execução real no HEAD da PR e na `main`. Mudanças legítimas em um comando protegido exigem revisar a política junto ao comando.

## Checagem científica e editorial

A janela incorporou novas transcrições NASA, separação da precisão documental do decaimento de NORAD 528, diagnóstico secundário de época TLE, pistas cartográficas PETROBRAS, investigação editorial da *Última Hora* e atualização do Caderno 17. Esses artefatos têm categorias distintas e não acrescentam, por esta auditoria, uma medição instrumental original independente de hora ou posição terminal. O levantamento do G40 não reabriu os PDFs externos nem validou independentemente seus bytes.

A retificação DocReader 00471/00507 deve continuar tratada como correção de localização editorial: índice de páginas não equivale a imagem recuperada ou texto do artigo verificado. O diagnóstico de TLE secundário não é uma segunda observação instrumental independente. Nenhuma dessas novas ligações permite declarar demonstrada a queda, o sobrevoo ou o horário do NORAD 528.

## Validação e continuidade

Os testes focados `test_ci_event_policy_all_workflows.py` e `test_ci_universal_steps.py` passaram no checkout corretivo; o verificador de arquivos de 20.000 bytes também passou. A execução integral de `prek` na casa privada antiga G38 excedeu o limite de memória do Jatobá e não pode ser anunciada como sucesso na `main` atual. A decisão de merge depende da CI real do HEAD corretivo, sem atalhos. O G41 começará depois de `9a2f9815`, incluindo a PR corretiva e novas integrações concorrentes.

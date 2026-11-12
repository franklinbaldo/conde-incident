# OKF | 🦡 Texugo | 2026-11-12 | C243-T12

## Contexto e objetivo
Issue #19, PR #20 empilhada #1 → #14 → #20. Retomada após C243-T11 (HEAD anterior `5a543b6954d635359e9e51e7f5aa10c4774e5e51`). O resultado anterior de persistência 0,026904 vs quadrático 0,074988 e conjunto 0,097122 rev/dia motivou um teste adversarial de tendências locais. Não há outro ticket do Texugo.

## Fatos implementados e a verificar
- `tools/texugo_holdout_529.py`: dois controles target-only (secante 2 épocas 529, OLS 3 épocas 529) na avaliação prequential existente; horizonte/pareamento T10 mantidos.
- `tests/test_texugo_holdout_529.py`: casos sintéticos para melhoria, piora, temporalidade, pareamento e NOT_RUN.
- Registro C243-T12 na matriz e metodologia em `research/texugo_holdout_529.md`.
- Último SHA de código/testes conhecido antes desta memória: `6c96126627704810a211f06d17ff12a17e7e97a3`; SHA definitivo de branch será identificado no GitHub Actions e na PR. **CI e resultado histórico T12: NOT_RUN ao criar esta memória**; não herdar PASS de T11.

## Proveniência, limitações e próxima pergunta
Espelho numérico secundário oxzoid/Space-Track revisão 4b4fb3a (SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09); sem fonte instrumental independente. Documento NASA 15/11/1963 p.8 certifica apenas dia de decaimento 1963-003B, sem hora/local. Conflito RAAN ainda aberto. Esta análise do movimento médio não fornece domínio físico nem hipótese empírica autenticada para Lean 4.35.0 e não prova queda ou probabilidade em Conde. **Próximo passo:** verificar teste de regressão e executar espelho efetivo no HEAD; relatar resultados negativos sem filtrar, não escolher tamanho com base no placar; conciliar os commits da Tartaruga antes da integração, sem rebase/force-push. Revisão Gavião, integração Elefante.

## Rastro
https://github.com/franklinbaldo/conde-incident/issues/19
https://github.com/franklinbaldo/conde-incident/pull/20
https://github.com/franklinbaldo/conde-incident/commit/6c96126627704810a211f06d17ff12a17e7e97a3

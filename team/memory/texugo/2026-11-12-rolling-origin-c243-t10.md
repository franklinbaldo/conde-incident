# OKF 🦡 Texugo 12/11/2026 C243-T10

- Contexto: retomar PR #20/issue #19; C243-T8/T9 demonstraram pontuação aninhada e Gavião #57 já audita SSE de forma independente. Investigar horizonte novo sem repetir essa auditoria.
- Fato implementado: rolling_origin_diagnostics no mesmo script e campo rolling_origin_holdout do JSON custodiado, comparando quadrático com média, 527/528 isolados, linear e persistência na próxima época do 529. Quatro controles sintéticos novos verificam cronologia, falsificação, ausência de vazamento, ausência de falso PASS e deduplicação. Não há script/workflow novo.
- Linhagem: oxzoid/Space-Track 1963 rev 4b4fb3a, Parquet SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Um catálogo secundário; NASA 15/11/1963 p.8 é dia apenas.
- Estado no momento da criação: testes e replay reais NOT_RUN até confirmação Actions no HEAD final. Modelos são retrospectivos e permitem alvos anteriores no treino seguinte; não são medições independentes, nem previsões de órbita, nem posterior probabilístico.
- Ausências: TLEs instrumentais completos e reconciliação RAAN. Domínio físico Lean/simulação de impacto: BLOQUEADOS. Conde INDETERMINADO.
- Rastreio: https://github.com/franklinbaldo/conde-incident/issues/19 ; https://github.com/franklinbaldo/conde-incident/pull/20 ; HEAD anterior aprovado 74ff98f808f8657bdd9b3aa3445e7a732858d074. Anotar novo SHA e CI no parecer após execução.
- Próximo: analisar vitórias e derrotas do novo controle, exigir CI no SHA final, Gavião revê, Elefante integra depois das dependências; sem merge, contato ou blog.


- Encerramento observado: commit de implementação [054f605](https://github.com/franklinbaldo/conde-incident/commit/054f60509729a2807644ed37bc571b6953ddc160), [Actions #43172444338](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338) **SUCCESS 132 testes**, artefato #13922149343. 53 pares consecutivos, 51 pontuados, 2 NOT_RUN; quadrático vence 33, conjunto 18. RMSE: persistência 0,026903935; quadrático 0,074988368; conjunto 0,097122160 rev/dia. Achado negativo: melhora T9 não se mantém na previsão da próxima época e um baseline ingênuo supera ambos. A sequência reutiliza observações anteriores; não são 51 réplicas nem teste prospectivo.
- Reconciliação: incluir C241-T9 da base #14 por merge verdadeiro (dois pais), copiando integralmente seus blobs de código/testes/custódia sem alterações. A validação desse novo HEAD exige novo Actions. Sem merge de PR, rebase, force push, publicação ou contato.

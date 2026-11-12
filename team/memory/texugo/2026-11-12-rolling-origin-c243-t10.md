# OKF 🦡 Texugo 12/11/2026 C243-T10

- Contexto: retomar PR #20/issue #19; C243-T8/T9 demonstraram pontuação aninhada e Gavião #57 já audita SSE de forma independente. Investigar horizonte novo sem repetir essa auditoria.
- Fato implementado: rolling_origin_diagnostics no mesmo script e campo rolling_origin_holdout do JSON custodiado, comparando quadrático com média, 527/528 isolados, linear e persistência na próxima época do 529. Quatro controles sintéticos novos verificam cronologia, falsificação, ausência de vazamento, ausência de falso PASS e deduplicação. Não há script/workflow novo.
- Linhagem: oxzoid/Space-Track 1963 rev 4b4fb3a, Parquet SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Um catálogo secundário; NASA 15/11/1963 p.8 é dia apenas.
- Estado no momento da criação: testes e replay reais NOT_RUN até confirmação Actions no HEAD final. Modelos são retrospectivos e permitem alvos anteriores no treino seguinte; não são medições independentes, nem previsões de órbita, nem posterior probabilístico.
- Ausências: TLEs instrumentais completos e reconciliação RAAN. Domínio físico Lean/simulação de impacto: BLOQUEADOS. Conde INDETERMINADO.
- Rastreio: https://github.com/franklinbaldo/conde-incident/issues/19 ; https://github.com/franklinbaldo/conde-incident/pull/20 ; HEAD anterior aprovado 74ff98f808f8657bdd9b3aa3445e7a732858d074. Anotar novo SHA e CI no parecer após execução.
- Próximo: analisar vitórias e derrotas do novo controle, exigir CI no SHA final, Gavião revê, Elefante integra depois das dependências; sem merge, contato ou blog.

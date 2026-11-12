# 🦡 Texugo | Conde | 2026-11-12 | C243-T9 | antichurn de holdout

- **Issue/PR:** exclusivamente franklinbaldo/conde-incident, issue #19, PR #20; AGENTS.md, team/texugo.md na main e matriz/PRs/issues consultadas nesta rodada. Nenhuma outra issue criada nem branch alheia editada.
- **Diagnóstico:** C243-T8 registra 93 pontuações sobre apenas 28 épocas futuras do 529. Quatro holdouts aninhados não são quatro réplicas independentes.
- **Fatia:** disjoint_horizon_diagnostics no mesmo leitor tools/texugo_holdout_529.py, sem novo script/workflow. Uma época futura pertence a um único trecho, coeficientes continuam pré-corte, RMSE agregado ponderado por observação distinta e NOT_RUN contabiliza faltantes. Dois testes sintéticos adversariais conferem partição, ponderação, falta de dados e rejeição de duplicatas.
- **Proveniência:** espelho secundário oxzoid/Space-Track 1963 revisão 4b4fb3a, SHA256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09, confrontado Parquet↔CSV por C243. Não são sensores independentes. NASA 15/11/1963 p.8 só atesta dia de decaimento.
- **Teste preliminar isolado:** quatro épocas SINTÉTICAS confirmaram 4 pontos distintos e RMSE agregado sqrt(7.5), e 3/4 pontos quando um corte era NOT_RUN; não é replay de catálogo.
- **Estado antes do CI:** resultados históricos T9 e testes do repositório NOT_RUN até execução do workflow GitHub Actions no HEAD final. Confirmar links no parecer da PR, não antecipar PASS. Base #14 avançou e requer reconciliação antes de revisão/integração.
- **Próxima falsificação:** conferir tamanhos 4/3/1/20 e sinal de diferença frente ao baseline no replay; interpretar eventual superioridade apenas como pós-hoc, não acoplamento orbital, triangulação ou localização. Faltam observações instrumentais primárias com época/frame/erro e resolver conflito RAAN para restrições Lean/estado orbital. Gavião revisa, Elefante integra. Não houve blog, contato, rebase, force-push nem merge.


## Resultado de fechamento após o primeiro replay e merge de base

- Branch própria reconciliada com a Tartaruga C241-T8 por verdadeiro commit de dois pais dea14a0ba0691cbe15490e194e8a0d21721530d7; zero commits atrás da base a862b264aad1b23101458953336340e42a9c7ef7 na comparação então consultada. Sem rebase/force-push, sem merge da PR.
- [Texugo Actions #43165959868](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868), [custódia #43165959736](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959736), [Scientific checks #43165959834](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959834): PASS no SHA acima, 115 testes Python + replay Parquet original. [Artefato #13920171288](https://github.com/franklinbaldo/conde-incident/actions/runs/43165959868/artifacts/13920171288).
- O futuro de 529 foi alocado em 4/3/1/20 épocas únicas, sem duplicação; primeira janela **PIOROU** perante baseline, agregado 0,188775134 (quadrático) vs 0,181909995 (média), doador 528 0,145072060 rev/dia (pós-hoc). Vinte das 28 épocas concentram-se na janela final.
- Resultado documental será anotado em commit posterior; **exigir novamente GitHub Actions no novo HEAD antes de parecer de revisão**. Fonte segue secundária única, TLEs primários/RAAN/Conde indeterminados.

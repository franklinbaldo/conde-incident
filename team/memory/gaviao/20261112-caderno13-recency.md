# OKF 🦅 Gavião | 12/11/2026 | Caderno 13 / C243-T12

## O — Observação e custódia
- Li AGENTS.md, team/gaviao.md da main, issue #16, PRs #3/#20/#22/#28/#62/#63/#65 e matriz cumulativa C243-T12 no head d31b86486283adb1fad5764285b16b2e73d07439.
- Reinspecionei as imagens do boletim NASA 15/11/1963 p. impressa 8/PDF 10 (somente dia 08/11 para 1963 3B) e FBIS 03 p.1 (transcrição da notícia da Rádio Tupi, não queda provada). São cadeias com dependência, não confirmações independentes de impacto.
- Parquet numérico oxzoid Space-Track rev 4b4fb3a SHA-256 c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09. Primários TLE instrumentais com erro e frame: NOT_VERIFIED.

## K — Conhecimento e teste
- Achado G13-E1: a secante e OLS da PR #20 usam só 529 nas fórmulas, mas a elegibilidade da coorte de 51 alvos requer ao menos três épocas anteriores do 529 e de cada doador 527/528. A expressão “apenas dois registros” exige distinção entre fórmula e protocolo.
- Criei auditor independente por fonte Parquet pinada, datas UTC, duplicatas, secante, OLS, persistência, RMSE 51/2, horizontes disjuntos, exclusão de um alvo sem refit e controle de maior erro; 12 testes adversariais com dados sintéticos, explicitamente não históricos.
- Não importar o código Texugo; CI deve demonstrar no HEAD final números da coorte e RMSE histórico. Janelas pós-hoc, série secundária única, sem premissa Lean física, domínio orbital reduzido, simulação terminal ou impacto. Conde INDETERMINADO.

## F — Falhas, próximos testes e handoff
- Sem resultado do novo workflow, não declarar PASS empírico, mudança de vencedor por horizonte nem quantidade de reversões. Registrar o gate após execução.
- Próxima dúvida: secante supera persistência em cada horizonte civil e em deleção de alvo extremo? E a elegibilidade dependente de doadores restringe o significado da comparação entre fórmulas?
- Solicitar precisão G13-E1 na PR #65, conferir CI do SHA corrigido. PR #3 ainda Zola × decisão SSG Rust #22: sem aprovação de integração.
- Trabalhar apenas neste repositório. Nenhum merge, deploy, contato, alteração de blog pessoal, rebase nem force push.

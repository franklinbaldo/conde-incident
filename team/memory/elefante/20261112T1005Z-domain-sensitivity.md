# 🐘 Elefante: testemunhas mínimas e sensibilidade de domínios

- Data: 2026-11-12, turno de 06h America/Porto_Velho. Repositório exclusivo franklinbaldo/conde-incident.
- Trabalho retomado: PR #43 sobre alternativas documentais RAAN, empilhada na #37 de intervalos racionais; nova fatia em ramo próprio. Nenhum ramo de outro agente editado.
- Fontes consultadas diretamente: main em eee7851d29e7bafa38ebcb36cab9da9dfa2f2afb, AGENTS.md, team/elefante.md, issues #6/#13/#15/#19/#4 e PRs #1/#3/#22/#28/#37/#43/#58/#61/#64. Matriz cumulativa research/evidence_matrix_C001-C238_2026-11-11.md da PR #1, incluindo errata NASA C197. Fonte documental da matriz: https://github.com/franklinbaldo/conde-incident/pull/1.
- Fato de plataforma diretamente verificado: GET /repos/franklinbaldo/conde-incident mostrou has_pages=false e main sem workflow. Não foi possível confirmar Pages configurado via GitHub Actions nem deploy HTTP; publicação NÃO VERIFICADA.
- Entrega proposta: auditoria de sensibilidade por exclusão de cada restrição e testemunha por remoção mínima, usando aritmética racional exata já existente. Evidência e status Lean continuam declarados, não autenticados. Sem TLE novo, localização, hora ou probabilidade. Inclui testes contrafactuais e workflow.
- Grau de verificação: os testes Node e GitHub Actions devem ser conferidos no SHA FINAL desta PR; não atribuir resultado antecipado. Sensibilidade é resultado lógico condicional de dados de entrada, não observação histórica ou prova Lean.
- Ordem de dependências: #37 → #43 → esta PR; #1/#61/#64 e #3/SSG Rust exigem reconciliação e revisão do Gavião. #28 depende do CI comum da #58; priorizar custódia TLE 527–529 e RAAN, depois Lean, domínios, simulação e holdout.
- Próxima dúvida: quais restrições com proveniência auditável permanecem individualmente pivôs após separar 198,5261° e 284,1520° por documento, época e frame? Nenhum desses valores é usado como observação verificada nesta entrega.
- Revisão: aguardar Gavião independente e CI do HEAD final. Sem merge próprio, contato externo, alteração do blog, force-push ou rebase.

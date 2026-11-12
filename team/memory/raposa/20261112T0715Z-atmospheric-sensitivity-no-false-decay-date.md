# OKF — 🦊 Raposa, 12/11/2026 07:15 UTC: sensibilidade atmosférica sem ajuste terminal fictício

## Contexto retomado
- Escopo exclusivo: `franklinbaldo/conde-incident`, issue #9, PR draft #24 empilhada na #3 (Zola), base científica #1 ainda draft; #28 propõe fluxo científico, não está na main.
- Li `AGENTS.md`, `team/raposa.md`, issues e PRs abertas, a matriz cumulativa C01–C238 na #1, `research/SCIENTIFIC_AUDIT.md`, o componente legado e a lei de densidade em `src/lib/astrodynamics.ts`. A pergunta desta sessão: a aba "Arrasto & Termosfera" apresenta resultados simulados como datas físicas verificadas?
- O código anterior `src/components/AtmosphereSensitivity.tsx` fabricava a data de chegada a 120 km por uma expressão de potência calibrada para produzir 12 dias em H=45, marcava 08/11 como "exata concordância", rotulava a expressão como "integração numérica", exibia tabela histórica datada sem rastreamento físico, afirmava parâmetros ambientais de novembro e mostrava F10.7/B como se fossem medidas. O cursor Ap era criado mas não influía no cálculo. Isso é defeito **confirmado por inspeção do código**, não uma nova observação histórica.

## Fatia de implementação
- Substituí a falsa chegada e a tabela de datas por perfil **relativo e adimensional** de densidade, gerado somente por `getThermosphericDensity` a alturas ilustrativas de 120–320 km e normalizado ao mesmo modelo em 200 km. A normalização elimina a densidade de referência do resultado exibido, que continua apenas uma forma de função, não uma medição física. Retirei sliders de F10.7, B e Ap e mantenho apenas H, explicitamente hipotético 35–65 km, **sem** interpretá-lo como domínio admissível.
- Acrescentei controle com label/descrição, tabela semântica e alternativa textual a barras `aria-hidden`, layout móvel, navegação por teclado, textos PT/EN e fontes próximas aos limites, com IDs C191–C194 e C197–C202, deep links Evidence (dia NASA/RAAN), Lean condicional, #37 (contraprovas de domínios), #43 (cenários TLE) e mapa.
- `tests/atmosphereScientificLimits.test.mjs`: quatro regressões estáticas contra falsa data/integração, falso resultado físico, sliders inertes, falta de tabela acessível, links e limites científicos. Registra o que o teste **não** comprova: integridade dos dados/hipóteses, funcionamento visual real ou modelo orbital.
- Nenhum capítulo da Coruja, TLE, física, modelo de arrasto, blog pessoal, contato externo, merge ou deploy editado.

## Fontes, grau e independência
- **CONFIRMADO / código:** o componente antigo e a expressão de falso ajuste; `src/lib/astrodynamics.ts`, função `getThermosphericDensity`. Matemática da razão: `rho(h,H)/rho(200,H)`, sem entrada observada adicional.
- **MATRIZ LIDA / secundária nesta sessão:** `research/evidence_matrix_C001-C238_2026-11-11.md` da #1, C191–C194 (linhas 862–891), C197–C202 (899–912). C192 chama o intervalo H 44,8–48,9 km de **modelo hipotético**; C193 é Explorer XVII em abril–junho, não novembro. C194 distingue a proveniência NASA/NORAD. Não autentiquei dados de termósfera nesta sessão.
- **ORIGINAL CITADO, NÃO REINSPECIONADO NESTA RODADA:** NASA Satellite Situation Report (15/11/1963, p. impressa 8), https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10; registra **dia** 08/11 para 1963-003B, não hora/posição.
- **LEAN/CONTRAPROVAS APONTADOS, NÃO REEXECUTADOS AQUI:** Core.lean da #1 e PRs #37/#43; domínios físicos não vazios e reduzidos e uma propagação com holdout calibrado **não comprovados** nesta UI. A PR #28 continua proposta.
- Dependência: C191/C192 são derivações e não sensores; NASA/NORAD podem compartilhar rastreamento; não somar como testemunhos independentes.

## Verificação e próximos passos
- Commits de código/teste desta fatia: `5dcf48ec` (componente), `836223c1` (teste), `80f500df` (âncoras corretas). O gate definitivo será no HEAD **posterior a esta memória**; verificar a execução Actions por SHA real antes de comunicar PASS. Nenhuma verificação visual móvel, leitor de tela ou deploy nesta sessão.
- **Próxima dúvida:** quais outros componentes ainda dizem "densidade", "data/hora" ou "probabilidade" com aparente calibração, sobretudo a auditoria TLE e o arquivo? Como conciliar a #24 com a #1 e os capítulos empilhados da Coruja sem perder links?
- Handoff: 🦅 revisão independente de rótulos e navegação; 🐘 reconciliação das #1/#3/#24 e CI sobre o SHA reconciliado. Resultado científico **indeterminado**.

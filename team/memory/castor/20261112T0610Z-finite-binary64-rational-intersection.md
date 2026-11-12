# 🦫 Castor | 2026-11-12 06:10 UTC | issue #4 / PR #5

## Continuidade e contratos
- Li `AGENTS.md` e `team/castor.md` na main; consultei as issues/PRs abertas, #5/#4, #1/#14/#28/#37/#43 e retomei a mesma branch `castor/coupled-rv-j2-drag-inverse-4`.
- Matriz cumulativa `research/evidence_matrix_C001-C238_2026-11-11.md` ausente da main; consultada na branch `research/scientific-integrity-foundation`, blob `a7978c3a75a153b16ab70118a92c434bba674cb7`. Extensões C240/C241 documentadas na PR #14 permanecem custódia derivada.
- Sem alterações em blog, contatos externos, mudanças de issue, merges, rebase ou force-push.

## FATIA física e contraprova
- Corrigido `src/lib/orbitDeclaredDomainBridge.ts`: a antiga aproximação `Number(n)/Number(d)` podia tornar `10^400/10^400` (EXATAMENTE 1) um falso `NOT_RUN_FLOAT64_PRECISION` por `Infinity/Infinity = NaN`; singleton subnormal `1/2^1074` também falhava por underflow intermediário.
- Agora há busca binária determinística sobre a ordenação de **todos e apenas os Float64 finitos**, com comparação exata `BigInt` contra cada racional. O limite inferior é o primeiro Float64 >= limite racional e o superior é o último Float64 <= limite racional; não arredondar para fora. Domínios com zero pontos representáveis permanecem `NOT_RUN_FLOAT64_PRECISION`, sem órbita fictícia.
- Inclui limites racionais além de ±`Number.MAX_VALUE` quando a interseção finita é não vazia, sem promover limites físicos ou gerar dados históricos. Continua apenas um **subconjunto representável**, jamais um enclosure exato de trajetórias.
- +5 testes sintéticos em `tests/orbitDeclaredDomainBridge.test.mjs`: grandes razões racionais, sinal, subnormais, limites acima do alcance e intervalo com zero como único ponto. Documentação `research/ORBIT_PHYSICS.md` atualizada.

## Reprodução e evidência objetiva
- Commits de código/teste/docs: `446a542afeef62c34353145ef600ad0a9c00b4d2`, `33154a43fe270e44384c8d41d6f2e762144acbe5`, `5882cc89ea7c83188a51a57b41cb683b2aa5ef83`.
- GitHub Actions **SUCCESS 69/69 PASS, 0 FAIL**, run https://github.com/franklinbaldo/conde-incident/actions/runs/43166128249, job https://github.com/franklinbaldo/conde-incident/actions/runs/43166128249/job/131008304155, checkout verificado no SHA exato `5882cc89ea7c83188a51a57b41cb683b2aa5ef83`. Comando no workflow: `node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs tests/orbitEnergyAudit.test.mjs tests/orbitHoldoutAudit.test.mjs tests/orbitConditionalFit.test.mjs tests/orbitTrainingAudit.test.mjs tests/orbitAlternativeFits.test.mjs tests/orbitDeclaredDomainBridge.test.mjs`.
- Esta memória é commit posterior ao SHA testado. Reexecutar CI no novo HEAD para gate final antes da revisão/integração.

## Linhagem e resultados negativos
- Fonte primária documental **C197**: NASA/Goddard, *Satellite Situation Report*, vol.3 nº22, 15/11/1963, página impressa 8, NTRS 19640001198, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf ; registra **somente o dia** de decaimento 08/11/1963 de 1963-003B, sem hora, coordenadas ou estado r/v. Dependência NASA/NORAD não conta como dupla medição.
- C25/C179–C185 e espelho C240/C241 não são observações cartesianas independentes; RAAN 198,5261° versus 284,1520° continua sem proveniência primária reconciliada.
- **NOT_RUN:** restrições **históricas** provadas em Lean 4.35.0 e export com hash; holdout cego original 527/529 com época/quadro/covariância; comparação real com SGP4; calibração de arrasto histórico e Cd·A/m; posição terminal do 528. Nenhuma conclusão para Conde, exclusão, reentrada física ou impacto.
- TypeScript estrito global: NOT_RUN; os 69 testes de execução Node/CI são **SINTÉTICOS**.
- Próximo: revisão independente 🦅 da aritmética/contraprovas e obtenção do contrato Lean empírico mais observações originais antes do confronto físico. Integração somente por 🐘 Elefante.

# OKF — 🦫 Castor | 2026-11-12T09:01Z | sensibilidade: pivoteamento de respostas quase colineares

## Escopo e retomada
- Repositório exclusivo: https://github.com/franklinbaldo/conde-incident ; issue única [#4](https://github.com/franklinbaldo/conde-incident/issues/4); PR própria [#5](https://github.com/franklinbaldo/conde-incident/pull/5), branch `castor/coupled-rv-j2-drag-inverse-4`, draft e SEM merge.
- Base ao iniciar: `d28ed9740b37cc81eea0a6875b877b196f673d5e` (56 ahead / 0 behind da main consultada).
- Lidos `AGENTS.md`, `team/castor.md` na main, PRs/issues abertos, matriz `research/evidence_matrix_C001-C238_2026-11-11.md` da draft [#1](https://github.com/franklinbaldo/conde-incident/pull/1) (blob `a7978c3a75a153b16ab70118a92c434bba674cb7`), contrato científico proposto na [#28](https://github.com/franklinbaldo/conde-incident/pull/28) e continuação da própria PR #5. Não foi criada issue.
- Revisão independente solicitada 🦅 Gavião; integração exclusiva 🐘 Elefante.

## Avanço científico verificável
- Em `src/lib/orbitVelocityRank.ts`, novo rank condicional com pivoteamento pelo maior resíduo, ortogonalização duas vezes e limiar de quilômetros declarado. Em `orbitSensitivityAudit.ts`, substituída a aceitação `vx→vy→vz` por pivôs fortes e preservada a distinção de eixos fixos por premissa vs livres. Nenhuma transformação TLE→ECI ou adaptação de baseline SGP4.
- **Contraprova sintética negativa reproduzível:** colunas quase paralelas `[1,0,0]`, `[10,0.11,0]` km, corte `0.1 km`: a ordem fixa pode indicar rank 2 ou 1, dependendo da ordem; pivô por norma residual indica rank 1, invariável à troca. Com coluna `[0,0,2]` km, rank 2. Casos 3D independentes, zeros, limiar variável, configuração inválida e estouro Float64 também cobertos.
- O rank é LOCAL, depende da sonda, tolerância, época, quadro inercial e dinâmica. Pivô escolhido não identifica causalmente eixo orbital. Nenhum erro absoluto certificado, nenhuma restrição global/Lean verificada ou inferência de reentrada/impacto.
- `tests/orbitVelocityRank.test.mjs`: seis novas regressões exclusivamente sintéticas; workflow `.github/workflows/orbit-physics.yml` executa o novo arquivo no SHA exato do head. Documentação atualizada em `research/ORBIT_PHYSICS.md`.
- Commits nesta fatia: [ba876d6](https://github.com/franklinbaldo/conde-incident/commit/ba876d6c9e5f07df0c68770b8748e0845622bc47), [c76de1e](https://github.com/franklinbaldo/conde-incident/commit/c76de1e7888ad8d4ad1936c3afaf7e1741dcd2ea), [3bf88f6](https://github.com/franklinbaldo/conde-incident/commit/3bf88f657eb0bbf1c060d0233117cd3896c9e870), [beddb20](https://github.com/franklinbaldo/conde-incident/commit/beddb204ae9af54515751ff32817fcce84c66f1c), [31b2666](https://github.com/franklinbaldo/conde-incident/commit/31b2666df6d09a0d6b15952ddedde4e3689772b9).
- **CI desta fatia no momento da escrita:** PENDING/NOT_VERIFIED; confirmar run GitHub Actions em HEAD final (após este cartão), registrar contador e SHA no comentário da PR. Não atribuir PASS sem log.

## Linhagem e fronteira da evidência
- Fonte contemporânea original: NASA/Goddard, *Satellite Situation Report*, vol. 3 nº 22, 15/11/1963, p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf). Matriz C197, com errata C197–C202: `1963 3B / 8 NOV 63` é dia de decaimento catalogado, **não hora/local** nem observação instrumental do impacto.
- Registros orbitais C25/C179–C185 são espelhos secundários com possível ancestral comum; RAAN 198.5261° contra 284.1520° permanece sem resolução. NASA/NORAD/catálogos do mesmo rastreamento não são observações independentes.
- Testes de rank são construções matemáticas sintéticas, sem ID documental novo porque não são observações históricas.
- **NOT_RUN:** caixas históricas certificadas em Lean 4.35.0, validação cega original de NORAD 527/529 com época/quadro/covariância, comparação com SGP4, calibração de densidade e CdA/m de 1963, hora e posição terminal NORAD 528. Resultado geográfico: INDETERMINADO; nenhuma probabilidade de queda.

## Próxima pergunta e handoff
- Revisar o rank pivotado quando colunas estiverem quase paralelas no limite do erro numérico; confrontar múltiplas amplitudes de sonda antes de qualquer alegação de identificabilidade global. Obter estados 527/529 observados com UTC, quadro, incerteza e linhagem verificável e domínios Lean auditados antes do confronto histórico.
- Sem blog, publicação, contato com pessoas/arquivos, merge, rebase ou force-push.

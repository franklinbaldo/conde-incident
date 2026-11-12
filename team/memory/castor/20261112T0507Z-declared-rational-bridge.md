# 🦫 Castor | 2026-11-12 05:07 UTC | PR #5, issue #4

## Contexto lido
- `AGENTS.md` e `team/castor.md` integralmente na `main`, PR/issue abertas e própria PR #5 (`castor/coupled-rv-j2-drag-inverse-4`); retomei a issue #4.
- Matriz cumulativa `research/evidence_matrix_C001-C238_2026-11-11.md` lida na branch `research/scientific-integrity-foundation`, blob `a7978c3a75a153b16ab70118a92c434bba674cb7`, pois ainda não está na main.
- Interfaces condicionais PR #37 e #43, ainda abertas/draft, inspecionadas pelo próprio código; fluxo #28 ainda em PR.

## FATIA REAL
- Novo `src/lib/orbitDeclaredDomainBridge.ts`: consome resultados *declarados* `conde.alternative-domains/v1` de #43 sem importar código não integrado, converte somente `vx,vy,vz` racionais para caixas cartesianas por alternativa, conservando ocorrências, URL e grupos de linhagem **declarados**.
- Converte limites racionais com BigInt + inspeção exata dos bits Float64; arredonda para **dentro** e bloqueia intervalos sem ponto Float64 com `NOT_RUN_FLOAT64_PRECISION`. Não transforma TLE em estado cartesiano, não cruza cenários RAAN concorrentes, nem rotula como prova Lean.
- Requer dados explícitos ausentes na saída da #43: unidade `km/s`, fonte do intervalo inicial, NORAD 527/529, época e referencial. Rejeita falso Lean `PASS` e domínios não-velocidade.
- Novo `tests/orbitDeclaredDomainBridge.test.mjs`: nove regressões sintéticas incluindo arredondamento adversarial, escala sub-ulp, contradição localizada, linhagem ausente e execução acoplada J2/seed. Workflow físico oficial inclui a bateria. Documentação `research/ORBIT_PHYSICS.md` atualizada.

## Evidência e validação
- HEAD do código testado no GitHub Actions: `b67fc15ce7151f72794af7766d1450f943b418ba`. Run `https://github.com/franklinbaldo/conde-incident/actions/runs/43159034722`, job `130985605274`; checkout de SHA exato, **64/64 PASS, 0 FAIL**.
- Comando: `node --experimental-strip-types --test tests/orbitPhysics.test.mjs tests/orbitHoldout.test.mjs tests/orbitConvergence.test.mjs tests/orbitAdmissibility.test.mjs tests/orbitEnergyAudit.test.mjs tests/orbitHoldoutAudit.test.mjs tests/orbitConditionalFit.test.mjs tests/orbitTrainingAudit.test.mjs tests/orbitAlternativeFits.test.mjs tests/orbitDeclaredDomainBridge.test.mjs`.
- Documentação complementada em commit `643865f30843d6ae65fc3c3fb18deb6459bae253`; verificar novo CI no HEAD após incluir esta memória, antes de qualquer integração.
- Fonte primária institucional já identificada C197: NASA/Goddard, *Satellite Situation Report*, vol. 3 nº 22, 15/11/1963, p. 8, NTRS 19640001198, `https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf`: somente decaimento 1963-003B no dia **08/11**. Não há UTC/posição terminal; cadeia NORAD/NASA pode ser compartilhada.
- C25/C179–C185 e C240/C241 são espelhos e auditorias derivados, **não** confirmação instrumental independente; conflito RAAN 198,5261° vs 284,1520° persiste.

## Resultado negativo / limites
- **NÃO** há restrição histórica certificada pelo Lean 4.35.0, nem export com SHA auditado; esta ponte conserva `leanProof=NOT_VERIFIED` e `unitFromAuditor=NOT_PRESENT`.
- **NOT_RUN**: holdout histórico 527/529 com época/frame/covariância independentes; SGP4 baseline no mesmo corte; densidade histórica F10.7/Ap e CdA/m; posição e hora de reentrada do 528.
- A discretização é subconjunto das caixas racionais, **não** enclosure global; não demonstra Conde incluído, excluído, reentrada física ou impacto.
- Verificação TypeScript global (tsc) **NOT_RUN**; GitHub Actions Node 22 confirma runtime de todos os testes sintéticos.

## Próximo trabalho
- Solicitar revisão independente 🦅 do conservadorismo de arredondamento, origem das caixas iniciais e rastreabilidade antes de qualquer integração 🐘.
- Aguardar certificado Lean e observações/cartesianos de origem verificada com épocas, frame e covariâncias; até lá não reinterpretar pontuação sintética como previsão de 1963.
- Sem merge, rebase, force-push, blog, comunicação externa ou fabricação de evidência.

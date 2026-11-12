# OKF — 🦫 Castor | 2026-11-12T10:00Z | estabilidade do rank a diferentes sondas

## Retomada
- Exclusivamente `franklinbaldo/conde-incident`, issue única #4, PR #5 `castor/coupled-rv-j2-drag-inverse-4`, mantida draft. `main/AGENTS.md`, `main/team/castor.md`, PRs/issues abertos e matriz cumulativa C001–C238 na draft #1 (blob `a7978c3a75a153b16ab70118a92c434bba674cb7`) consultados; contrato #28 ainda não integrado. Retomei a revisão pendente da identificabilidade local após o commit `7f73d51304718d5ee911c4f76456773356f143d9`.

## Implementação, contraprovas e resultado negativo
- `src/lib/orbitProbeStabilityAudit.ts`: três verificações independentes em sondas `h/2,h,2h`, cada uma reintegrando r/v com J2 opcional e convergência por redução de passo, exclusivamente nas épocas pré-corte. Exige spans de velocidade efetivamente distintos após clipping ao domínio. Não certifica Jacobiano, singular values, inferência histórica ou observabilidade global.
- `tests/orbitProbeStabilityAudit.test.mjs`: 6 regressões puramente sintéticas: rank igual para órbita sintética com posição posterior; rank que MUDA por amplitude em época curta (não esconder o resultado adverso); box estreita repetindo diferença numérica; velocidades fixas por premissas; falha Float64 e rejeição de vazamento temporal/unidades. Testes sempre rotulados como matemática sintética.
- Workflow `orbit-physics.yml` acrescenta teste no **head exato**. CI final deve ser consultado depois do commit de memória: até lá **PENDING/NOT_VERIFIED**, não alegar PASS. Sem alterações ao blog, sem contatos, sem merge/rebase/force-push.

## Cadeia documental
- Fonte original: NASA/Goddard, *Satellite Situation Report*, vol. 3 nº 22, 15 Nov 1963, p. impressa 8, NTRS 19640001198, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf ; matriz **C197** documenta só **08/11/1963** como dia de decaimento de 1963-003B, sem hora, posição, observação orbital instantânea ou evidência de impacto.
- C25/C179–C185 são TLEs derivativos/espelhados de possível ancestral NORAD comum, não sensores independentes. RAAN `198.5261°` e `284.1520°` seguem em conflito. Não acrescentar ocorrência histórica à matriz por testes sintéticos.
- **NOT_RUN:** prova Lean 4.35.0 de domínios históricos, posição original cega 527/529, SGP4 comparável, calibração atmosférica de 1963 e coordenadas de reentrada/impacto 528. Nenhuma probabilidade ou geolocalização inferida.

## Pergunta pendente
- Gavião deve verificar se estabilidade de rank em três amplitudes mascara não linearidade de posto ou pivôs diferentes; após observações independentes historicamente auditadas, testar holdout. Elefante integra após revisão. Código da sessão no commit 28dc05cdc8331af4037e569a21b74394bc346590, SHA e run final registrados no handoff da PR.

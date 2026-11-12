---
type: AgentMemory
agent: polvo
title: "Simulador real para Lean e provas de volta ao Castor"
description: "Issue #15/PR #17: gate epistêmico de saídas físicas, contagens monótonas e auditoria estática do legado"
date: "2026-11-12"
tags: [lean4, conde, simulator-bridge, castor, provenance, uncertainty, negative-results]
---

## Retomada, escopo e artefatos

- Retomada da issue [#15](https://github.com/franklinbaldo/conde-incident/issues/15), PR [#17](https://github.com/franklinbaldo/conde-incident/pull/17) sobre a base da PR #1. Lidas na `main` as regras `AGENTS.md` e `team/polvo.md`; conferidas PRs/issues e a matriz C01–C238 com 241 ocorrências, SHA Git blob `a7978c3a75a153b16ab70118a92c434bba674cb7`.
- Analisados os arquivos do simulador legado `src/lib/astrodynamics.ts`, `monteCarlo.ts`, `inverseSolver.ts`, `constants.ts`, `norad528_reconstruction.py` do [snapshot científico #1](https://github.com/franklinbaldo/conde-incident/tree/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b). `formal/scripts/simulation_bridge_audit.py` fixa SHA-1 Git verdadeiro de cada um e classifica 10 padrões limitantes; **é análise sintática, não execução da dinâmica ou prova de comportamento de todo o programa**.
- Lido o modelo acoplado na draft Castor [PR #5](https://github.com/franklinbaldo/conde-incident/pull/5) no SHA `3074ae0f014ce33a2c81dacb2a7400f92f4a4359`: `orbitPhysics.ts` (integração osculadora r/v, J2, arrasto com atmosfera fornecida, evento de altitude), `orbitAdmissibility.ts` (caixas condicionais), `orbitEnergyAudit.ts` (balanço de trabalho), `orbitHoldoutAudit.ts` (comparação condicionada sob refinamentos). O código Castor não foi executado neste CI nem copiado para a branch do Polvo.
- Novo módulo `formal/Conde1963/SimulatorBridge.lean`: `SimulationOrigin`, `NumericalEvent`, `SimulationAudit`, condições `HistoricallyAdmissible` e `GroundImpactAdmissible` e 12 teoremas sobre portas de admissibilidade, ausência de holdout/custódia, distinção entre limite atmosférico e impacto, monotonicidade de contagens em raios 50/100/250/500 km e sinal não positivo do arrasto em abstração aritmética inteira. Não é prova do programa TS, da integração RK4 em ponto flutuante ou da verdade das flags de certificação.
- Novo `formal/tests/test_simulation_bridge_audit.py`: 8 testes adversariais de deriva de fonte, alteração de comportamento, tentativa de concluir localização, e preservação dos limites.
- CI `.github/workflows/science.yml` passou a gerar `conde-simulation-bridge.json` com URLs, blob SHA-1, IDs de matriz e exigências para Castor. Publica no artifact de PR, junto com os 241 contratos documentais (sem publicação de site).

## Achados técnicos negativos com efeitos sobre a formalização

1. Legado `astrodynamics.ts` interrompe artificialmente propagação do 528 depois de **1963-11-08T23:59:59Z**; `C131/C197` registram **dia de decaimento publicado**, não instante UTC ou prova de queda. Não usar corte como observação.
2. Legado `monteCarlo.ts` sorteia argumento de latitude terminal independentemente da trajetória validada e usa RAAN 284,152°; fonte numérica derivada de `C179` fornece ~198,5261°. Frações sintéticas não são probabilidades históricas.
3. `astrodynamics.ts` constrói envelope com `sigmaKm` heurístico e `bracketingVerdict` de 527/529; ainda há fallback com `distanceToCondeKm: 0` quando não há ponto calculado. Não é corredor físico observado, nem localização de NORAD 528.
4. O acoplamento `r/v` de Castor separa forças e parâmetros, e suas auditorias exigem convergência, mas `historicalCalibration: NOT_RUN`, `observationAuthenticity: NOT_VERIFIED` e `rigorousErrorEnclosure: false` impedem inferência histórica. A travessia do evento de altitude escolhido NÃO equivale a material em solo.
5. Outros parâmetros de modelo, inclinação, `BSTAR=0`, época e RAAN do antigo TLE permanecem em conflito/linhagem secundária. Nenhuma inferência de Conde forçado, Conde excluído, hora, posição ou posterior foi produzida.

## Proveniência e fluxo científico

- NASA/Goddard, *Satellite Situation Report* 15/11/1963, p. impressa 8, [NTRS 19640001198](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), matriz C131 [L502](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L502) e C197 [L905](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L905): uma fonte histórica do *registro* do dia de decaimento, não observação independente do local.
- C25/C179–C185: TLEs em espelhos derivados de rastreamento comum, originais impressos de cada época **não recuperados**. C127–C130: holdouts anteriores mostram falha de extrapolações precisas; não apagados.
- Fac-símiles históricos não reinspecionados nesta fatia; ZIP antigo `Evidence.lean` 154 proposições/151 IDs, gerador, checksums e importação real **NOT_RUN**. Simulação física histórica completa e holdout cego 527/529 neste CI **NOT_RUN**.

## CI, falhas e próximos passos

- Falhas reais nas primeiras tentativas no novo `SimulatorBridge`: reescrita sobre definição ainda dobrada, prova aritmética não linear `Int.ofNat(a*b)`, ausência do lemma `mul_nonneg` no Lean core; corrigidas reescrevendo por projeções e provando sinal com construtores negativos de `Int`.
- **CI comprovado antes desta memória:** [run #43143618616](https://github.com/franklinbaldo/conde-incident/actions/runs/43143618616), commit `be990dc604ad78db4b02f89a5f51a26bc5cc3df4`: 2/2 jobs PASS, checkout HEAD real; Lean 4.35.0 `lake build` 11 jobs, `AxiomAudit.lean` sem `sorryAx`, **33/33** `unittest` Python, inventário 241/238, auditoria de 5 arquivos/10 achados, lint/build Web PASS. [Artifact](https://github.com/franklinbaldo/conde-incident/actions/runs/43143618616/artifacts/13910702470).
- **HEAD com esta memória deverá ser validado novamente**; não alegar PASS em SHA não executado.
- 🦅 Gavião: revisar a distinção demonstração simbólica vs. correção do código e as detecções estáticas; não confundir 10 padrões com 10 evidências instrumentais.
- 🦫 Castor: importar contrato de saída, remover/rotular cutoff fictício e fallback do legado na integração, só promover por fonte/holdout/error-bound com rastreabilidade e refazer revisão quando SHA das fontes mudar; nenhuma branch Castor alterada nesta sessão.
- 🐘 Elefante: integrar somente após revisão Gavião, bases reconciliadas e CI no HEAD exato. Implementador **não fez merge**, não publicou blog, não contatou arquivos/pessoas, não fez rebase ou force-push.

---
type: AgentMemory
title: "RAAN livre, única referência orbital rastreável e taxa J2"
description: "Retirada do vetor sem fonte da inferência; modelo J2 numérico para futuros limites via evidências e MCMC."
agent: polvo
date: "2026-11-12"
tags: [conde, lean, provenance, raan, j2, mcmc, fonte]
---

# Encerramento: correção científica, não geolocalização

## Decisão do proprietário
O antigo vetor manual do site (RAAN 284,1520°) não tem fonte orbital verificável; não pertence a cenário ativo nem a um estado físico de MCMC. Seu histórico permanece recuperável no Git. A PR #14 da 🐢 Tartaruga já removeu o vetor antigo das entradas operacionais do aplicativo, substituindo-o pelo literal secundário rastreável. O Polvo removeu o ramo legado também do **contrato ativo** exportado ao Castor.

## Fonte, identidade e dependências
- Matriz original da PR #1, blob Git `a7978c3a75a153b16ab70118a92c434bba674cb7`, **C25#1 linha 118** e **C179#1 linha 839**.
- Fonte secundária 528: https://www.itau.magnetic-declination.com/satellite/?s=528 ; par conservado https://github.com/franklinbaldo/conde-incident/blob/feature/tartaruga-tle-custody-1963/research/tle_custody/mirror_528_1963-10-27.tle; SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. Época `1963-10-27T14:40:16.132512Z`; RAAN 198,5261°, i 81,8615°, e 0,0017147 e n 15,74901460 revoluções/dia. O Parquet espelhado oxzoid SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` coincide dentro do arredondamento, **mesma linhagem**, não outra medição independente. O TLE original NORAD de 1963 e os erros instrumentais continuam não recuperados.
- NASA/Goddard *Satellite Situation Report*, 15/11/1963, página impressa 8, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf , C131#1/C197#1 = **mesma fonte** da data catalogada de decaimento, não de RAAN, hora/local de impacto. Fac-símile não reinspecionado nesta rodada.

## Fatia entregue
- Em `formal/scripts/evidence_registry.py`, `unresolved_element_scenarios_interface` v2 agora só exporta a fonte orbital secundária 528 como **referência** (`alternatives` com uma única entrada), não dois supostos conjuntos observacionais; os dados legados não entram no sampler. Mantém `raan_at_reference_epoch_deg` livre no círculo `[0°,360°)`, sem inventar priori ou desvio-padrão e sem promover 198,5261° a valor físico exato.
- O mesmo contrato explicita dependências: RAAN na época, `i`, `e`, `n`, precessão nodal J2, épocas da série 528, variações de arrasto/densidade e testes 527/529. Uma nova fonte independente poderá abrir novo ramo, mas valor manual do site não.
- Novo cálculo determinístico em Python `j2_nodal_rate_deg_per_day(i,e,n)`, com constantes de modelo da Terra `μ=398600.4418 km³/s²`, `J2=1.08262668e-3`, `R_E=6378.137 km`, fornece **−1,173124071 graus/dia** no proxy J2 de primeira ordem com os parâmetros secundários acima. É precessão calculada no modelo, **não medida histórica**, limite rígido ou trajetória terminal. Teste numérico e verificações de insumos inválidos em `formal/tests/test_evidence_registry.py`.
- Contrato de cenário `scenario_enclosure_interface` se ajustou à **única referência ativa**; `raan_epoch_contract.py` mantém a discrepância antiga apenas como **diagnóstico forense**, fora do estado MCMC. `formal/README.md`, `formal/scenario_alternatives.md`, `formal/scenario_enclosures.md` informam que a antiga descrição de dois ramos históricos está superada.
- Normas da PR #28 `AGENTS.md` e `team/polvo.md` atualizadas com a regra fonte-primeiro e variável angular livre. Handoff ao Castor em https://github.com/franklinbaldo/conde-incident/pull/5#issuecomment-6820784912; comentário na PR do Polvo https://github.com/franklinbaldo/conde-incident/pull/17#issuecomment-6820792833.

## Validação e resultado negativo
- CI da correção de representação antes do cálculo J2: https://github.com/franklinbaldo/conde-incident/actions/runs/43198056350 **SUCCESS** no SHA `3db1b693a6f148379dcc1d8f65c7ee51cf6c6eef`. Isso **não** prova o HEAD posterior com a taxa J2.
- Commit de código/teste de J2 `5afbdbe33f481d366ee617d98ccb540a1028e1b0`: execução CI https://github.com/franklinbaldo/conde-incident/actions/runs/43198626420 inicialmente **QUEUED**; confirmar o resultado antes de integrar. O commit desta memória torna-se o HEAD efetivo e exige sua própria checagem.
- **REDUCAO_FISICA_DE_DOMINIO=NOT_RUN; MCMC=NOT_RUN; erro observacional/likelihood=NOT_CALIBRATED; TLE primário=NOT_RECOVERED; holdout físico 527/529=NOT_RUN; ZIP Lean original 154/151=NOT_RUN; hora/local de reentrada=INDETERMINADO.** Testes de modelo, contratos e documentação não simulam observação física.
- Próximo avanço: usar épocas 528 do Parquet auditado para calcular diferenças **circulares** entre RAAN observada e Ω(t)=Ω₀+∫dotΩ_J2(i,e,n)dt com incertezas explicitadas; estimar quais i, e, n e arrasto reduzem o conjunto de Ω₀ admissíveis; controlar com 527/529 e comparar modelos sem priors inventados. Na falta de incerteza observacional, reportar resíduos e análise de sensibilidade, não posterior.

**Revisão:** 🦅 Gavião; **integração:** 🐘 Elefante. PR #17 permanece Draft, sem merge, rebase, publicação, blog ou contato externo.

---
type: AgentMemory
title: "Limiar TLE de 432 microssegundos e pista RAAN a 76 dias"
description: "Auditoria das 45 épocas do NORAD 528 encontra ângulo vizinho apenas em agosto; identidade documental segue não verificada."
agent: tartaruga
timestamp: "2026-11-11T22:39:46Z"
tags: [conde, tle, norad, custodia, raan, proveniencia]
---

# Retomada e fatos certificados

Li `AGENTS.md` e `team/tartaruga.md` na main, matriz C001–C238 na PR #1, issue #13 e PR #14; continuei exclusivamente [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14). Base científica ainda `research/scientific-integrity-foundation`; nenhuma alteração no blog, contato externo, rebase, force-push ou merge.

No script `tools/audit_norad_1963.py`, corrigi a correspondência de épocas: antes tolerava até 1 segundo; TLE de fração de dia com oito dígitos tem resolução de 864 µs, logo só se admite desvio de 432 µs e resultados próximos em separado (`NEAR_EPOCH_NOT_EQUAL`). Criei relatório `legacy_raan_temporal_audit` que procura 284,1520° entre as **épocas originais do espelho numérico preservadas**, mantendo separada a época literal de 27/10. Testes adversariais em `tests/test_audit_norad_1963.py` usam dados sintéticos, inclusive 432 versus 433 µs. Código no commit `49a833844e9476c23bcc990508838f2e582b0bce`.

**Prova executada:** [GitHub Actions #43113160100](https://github.com/franklinbaldo/conde-incident/actions/runs/43113160100) passou neste commit de código, **22/22 testes**, download Parquet pinado SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, 528 com 45 épocas e `MATCH_WITHIN_ROUNDING` em delta 0 µs. A busca angular pelo RAAN legado 284,1520° achou o melhor vizinho em **12/08/1963 13:35:30.863616 UTC**, linha 2998, RAAN 284,3310852050781°, distância 0,1790852050781°, **76,04496839 dias antes** do par de 27/10 (linha 3017, RAAN 198,52609252929688°). Isso refuta **mesma época para a melhor coincidência angular**, mas **não** prova que o legado foi transcrito de agosto; fontes NORAD primárias e frame permanecem desconhecidos. CSV de 45 linhas e seu SHA continuam gerados no workflow.

**Linhagem documental:** [HF oxzoid 1963](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet), espelho supostamente derivado de Space-Track; [TLE 528 literal secundário](https://www.itau.magnetic-declination.com/satellite/?s=528) SHA-256 `18cf11665e061b5ec8679242e10b00b82accf29bc6f0b9b7b6330b9c44e341cd`. São duas expressões potencialmente da **mesma cadeia instrumental**, não dois radares. [CelesTrak Historical Archives](https://celestrak.org/norad/archives/) orienta acesso a registros fora dos arquivos listados por *Special Data Request*; **nenhum pedido foi feito**, nem pares primários de 1963 obtidos.

**NOT_VERIFIED:** 45 pares TLE originais com checksum por linha; proveniência exata da RAAN 284,1520°; quadro orbital dos dados militares; tipo físico de S00528; estado terminal e lugar/hora de decaimento. NASA em 15/11/1963 p. impressa 8 atesta somente dia 08/11 para 1963-003B. O corpus numérico não converte a hipótese Conde em previsão.

Documentação adicionada em `research/tle_custody/README.md`, errata histórica e resultado em `research/evidence_matrix_C001-C238_2026-11-11.md` (C241-T1, sem tomar C242 de outro agente). HEAD documental antes desta memória `42d395f87278f714fed9c3c7c87799b7d4f2278e`; **checks no HEAD final ainda pendentes na hora da escrita**.

**Próxima pergunta falsificável:** recuperar arquivo primário com época/quadro/elemento do valor 284,1520°, para conferir se a diferença é erro de época ou outra fonte. Antes disso, Gavião deve revisar a metodologia de tolerância e dependência; Elefante somente integra após base #1 e CI no HEAD final. Não transformar a proximidade em conclusão.

## Achado operacional no encerramento

Os runs de PR antes desta correção tinham artefatos nomeados com `github.sha`, por exemplo `norad-1963-numeric-custody-f4e64e89...` no run #43113745007, que é SHA de merge de teste e **não** o HEAD da branch `6cee69e...`. Corrigi `.github/workflows/tle-custody.yml` para checkout/asserção exatos do SHA `github.event.pull_request.head.sha` (fallback para `workflow_dispatch`), artefato nomeado com esse SHA e teste de regressão adicional em `tests/test_audit_norad_1963.py`. Commits de correção: `e42de52b6cb9fce0db75415a0f9029444d5bb7ba`, `0d6d5a4dae00cda3a4792f94ca77dd53ebef859f`; documentação `6e6f44fcbdfd67f81a6fabdffd888cbac593e04f`. **CI com atestação do novo HEAD ainda não executado neste instante**, não herdar PASS do merge antigo. Próximo responsável deve verificar no log a linha `audited_source_head=` igual ao HEAD da PR, o download pinado e testes verdes antes de revisão. Sem merge.

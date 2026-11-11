---
type: AgentMemory
title: "Confronto adversarial de seis campos: TLE legado não é uma das 45 épocas"
description: "Checksum sintático não autentica; 0/45 correspondências do vetor legado com série numérica secundária pinada."
agent: tartaruga
timestamp: "2026-11-11T23:38:25Z"
tags: [conde, norad, tle, custodia, raan, falsificacao, proveniencia]
---

# Rodada da 🐢 Tartaruga, issue #13, PR #14

Retomada: li `AGENTS.md` e `team/tartaruga.md` na `main`, issue #13, PR #14 e as matrizes da branch empilhada sobre #1. Conferi que a PR #28 de fluxo científico ainda não estava integrada; mantive separadas observação documental, domínios de registro e premissa orbital. Não usei outros repositórios de trabalho, nem toquei no blog, nem contatei arquivos ou pesquisadores. Sem force-push/rebase/merge.

## Entrega verificável

- Script `tools/legacy_528_fingerprint.py` confronta **seis elementos simultâneos de cada época** do espelho 1963 com as antigas duas linhas TLE do app, preservadas no blob `0284f1217557b0ea891b5e51b6ac56bd13529d3f`. Aquelas linhas passam no algoritmo mod-10, mas **não** carregam prova de emissão NORAD.
- Guarda dos dados: Parquet oxzoid SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; CSV 528 derivado com 45 épocas SHA-256 `e3c946809d8e73d814bc1dfa424bf901a3b4331e63e4c85f82f81cf33b9c073e`. Referências: https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/main/data/tle_1963.parquet e https://www.itau.magnetic-declination.com/satellite/?s=528. Ambos são espelhos de possível **mesma linhagem instrumental**, não testemunhos independentes.
- Testes adversariais `tests/test_legacy_528_fingerprint.py` impedem combinar épocas, confundir checksum com autenticidade, aceitar CSV de SHA diferente, duplicar linhas, perder UTC ou alargar o limiar de 432 µs. `.github/workflows/tle-custody.yml` executa a comparação depois de extrair o Parquet pinado, e inclui `legacy_528_fingerprint.json` no artefato.
- **Dado observado no CI:** [run #43122019452](https://github.com/franklinbaldo/conde-incident/actions/runs/43122019452), HEAD exato `cb52253845f607d835f98839423b091d730cfda6`, SUCCESS, **30 testes PASS**, Parquet/CSV com hashes fixos, 45 épocas, **0/45 correspondências integrais** de seis elementos e zero coincidências de época literal. [Scientific checks #43122019297](https://github.com/franklinbaldo/conde-incident/actions/runs/43122019297) SUCCESS no mesmo HEAD. O próprio log imprime `audited_source_head=cb522538...`.
- Melhor candidato exclusivamente angular: `source_row=2998`, 1963-08-12 13:35:30.863616Z, RAAN 284.3310852050781°, ΔRAAN 0.179085205078°, mas Δe=0.005076799922, Δarg_perigee=97.491899°, Δmean_anomaly=97.025411°, Δmean_motion=0.30099865 rev/dia, Δinc=0.00770166°. Logo, não é o **vetor inteiro** legado dentro do espelho fixado. Não se conclui qual foi a verdadeira origem de 284,1520°.
- Registro cumulativo novo **C241-T2** (sem reatribuir C240/C241 entre agentes), README de custódia e dados de execução linkados. Commits de implementação: `8672176e40dbf81497f78c952dca0390405800ce`, `d7237337a9f7fee889141c6d4706388ed12b0412`, `cb52253845f607d835f98839423b091d730cfda6`; documentação `d583ef24a0c76f05faeebd5c25fb9460b1461887`, matriz `a26bbcb1ad84036bebe7aadd686e3b2c9e265b91`.

## Resultados negativos e próxima observação faltante

**NOT_RECOVERED:** as 45 duplas de linhas originais NORAD com checksum por época, processo institucional de conversão para os espelhos, frame/elemento médio declarado, observações instrumentais e ficha técnica que identifique a peça 00528; NASA documenta o dia 08/11 de decaimento, não hora/posição terminal. Não há coordenadas observadas de impacto, nem novas probabilidades. A nova contraprova limita apenas a hipótese *cópia do vetor completo do espelho*; não invalida o registro físico de um elemento de outro sistema até sua origem ser identificada.

**Próximo teste com potencial de reduzir o domínio físico:** obter fonte primária autoritativa de 1963 para pares TLE 527/528/529 com épocas, quadro, convenção de elementos e cadeia de custódia; somente depois entregar restrições verificáveis a Lean 4.35.0/Polvo, calibração/holdout e confronto de reentrada. Como a PR permanece em draft e empilhada sobre #1, 🦅 Gavião revisa e 🐘 Elefante integra apenas após todos os checks no HEAD final. Sem merge.

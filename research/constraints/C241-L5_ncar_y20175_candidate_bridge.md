---
type: Guide
title: "C241-L5: custódia de Y20175 conectada a nove consultas de perfis, não nove observações"
description: "Ponte de proveniência NCAR para variáveis latentes meteorológicas com exportação Lean tipada e testes."
---

# C241-L5: fonte Y20175 e consultas candidatas, sem inventar sondagens

**Responsável:** 🐙 Polvo, [issue #88](https://github.com/franklinbaldo/conde-incident/issues/88). **Origem documental:** custódia de 🦦 Lontra na [PR #139](https://github.com/franklinbaldo/conde-incident/pull/139) e [recado privado #3](https://github.com/franklinbaldo/polvo/issues/3), não reanálise do acervo. **Pergunta falsificável:** após decodificador NCAR ON20/CRAY RPTOUT comprovadamente compatível com **1963**, há registros utilizáveis dos códigos WMO **83229, 83096, 82900** em **7–9/11/1963**, com níveis, horários e controle de qualidade suficiente para testar um modelo meteorológico? **Resposta nesta rodada:** ainda NOT_DECODED. Nenhum valor de vento foi encontrado aqui.

## Nova conexão verificável

O arquivo público [GDEX d353000/Y20175](https://osdf-director.osg-htc.org/ncar-gdex/d353000/Y20175) possui **117.264.384 bytes** e SHA-256 afec7c443e0c912f8a742738bb82384197baecc7c743cfb00a2a8bda207b5de4, conforme manifesto de custódia integrado de Lontra em research/meteorology/nmc_y20175_1963_custody.json. Seu inventário administrativo é [grupo 2, resposta Y20175](https://gdex.ucar.edu/api/datasets/d353000/filelist/2/?filter_wfile=Y20175) (SHA-256 bruto e0d0403fe132578b4c244a8cb2ccce1d47ca166eff35bead134018d5cc47bf91). Esses hashes dizem respeito a **bytes custodiados**, não a nove observações identificadas.

A matriz congelada tem **241 ocorrências**; C151#1 refere-se a **NOAA IGRA Recife de 8/11/1963** (fonte e medição separadas, com fonte instrumental própria), sob snapshot Git blob a7978c3a75a153b16ab70118a92c434bba674cb7. A nova fonte Y20175 **não existe como linha da matriz congelada**, portanto usa MET-NMC-20261112-09 sem fabricar um identificador Cnn retroativo. O contrato cruza as duas fontes apenas como **candidatas a comparação futura**; sequer estabelece que Y20175 contém algum desses nove perfis, muito menos independência, coincidência de época ou medição em Conde.

A exportação research/constraints/nmc_y20175_pending_bridge.json contém o hash do binário, a linha e a versão da referência C151, o parâmetro latente de vento por tempo/altura/posição, o operador futuro e o produto cartesiano de **três códigos WMO × três datas**. São **nove consultas documentais**, não nove dados meteorológicos. formal/Conde1963/NmcCandidate.lean tipa as consultas e o hash da fonte sem teoremas novos de não identificabilidade ou queda. O gerador valida os limites de estado do manifesto e recusa mudar NOT_DECODED para perfil confirmado sem evidência; não há null novo nem valor meteorológico inventado.

## Separação de estados e métrica

| Medida | Antes | Depois |
|---|---|---|
| Fontes binárias NCAR com ponte tipada ao contexto C151 | 0 | **1** |
| Consultas WMO/data rastreáveis para eventual decodificação | 0 | **9** |
| Perfis efetivamente decodificados nesta entrega | 0 | **0** |
| Restrições físicas rígidas em Θ | 0 novas | **0 novas** |
| Holdouts e erros numéricos de vento (m/s) | Não avaliados | **NOT_RUN**, sem dados decodificados |
| Compatibilidade de quadros/épocas e covariância | Não verificada | **Não verificada** |

A redução de domínio orbital é **não avaliável**: não se declarou intervalo arbitrário nem testemunha nova de não vazio. A conexão poderá alimentar uma equação física somente quando houver decodificação validada, metadados tempo/altura/unidade, modelo espacial de transporte, erros/correlações e parâmetros do objeto. **Sondagem meteorológica não é observação orbital**. Os dados de Recife não autorizam extrapolação para Conde.

## Reprodução

Usar, nesta ordem:

1. python3 formal/scripts/compile_nmc_candidate.py --check
2. python3 -m unittest discover -s formal/tests -p 'test_nmc_candidate.py' -v
3. python3 tools/verify_nmc_y20175.py
4. No diretório formal: lake build; lake env lean Conde1963/CoreAxioms.lean

O CI Lean da PR executa o check, os testes e lake build em HEAD exato. Não baixar novamente o binário nem consultar pessoas ou arquivos. O próximo teste com potencial de **refutar** a presença desses perfis exige decodificador histórico auditado sobre os bytes SHA-256 acima e registro do número exato de hits por estação/data; só um resultado de busca integral validada poderia permitir NO_MATCH. Não há ligação física quantitativa entre estes candidatos e o RAAN 528 nesta entrega.

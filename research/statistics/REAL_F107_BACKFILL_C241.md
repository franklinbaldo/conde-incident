---
type: Experiment
title: 'C241-P33: recuperar 40 dias reais de F10.7 e fechar cobertura retrospectiva'
description: 'Recorte observado NRC com SHA, contraste trailing e ausência de versões as-of de 1963.'
experiment_id: C241-P33
model_ref: tools/audit_causal_flux_recovery.py
verification_status: RETROSPECTIVE_SOURCE_DERIVED_NO_ORBITAL_INFERENCE
---

# 🦌 C241-P33: fechamos a lacuna de cobertura, não a de publicação

**Pergunta verificável:** o [arquivo diário F10.7 de 1947–1996 do Natural Resources Canada](https://www.spaceweather.gc.ca/solar_flux_data/daily_flux_values/F107_1947_1996.txt) contém as 40 datas ausentes do extrato C241-P32? **Sim:** foram recuperadas as 40 linhas de 18/08 a 26/09/1963, coluna observada Obs. em unidades de fluxo solar (sfu). A versão integral baixada em 13/11/2026 tem **1.184.761 bytes**, SHA-256 60c51e8878dc70561e615b5cefb26315c201116fe4560799ec19237bed691c61, coincidente com a fonte já preservada no projeto. O recorte exato de 2.600 bytes tem SHA-256 26ee76e557dbe1ecf4eca35fa23e5f230b052c24bad15e21ffad3f408ca13351. Não é uma segunda fonte independente.

O recorte [F10.7](../meteorology/f107_1963_08_18_09_26_nrc_extract.txt) contém linhas originais, sem reformatar colunas. Para reproduzir sem rede, execute o script tools/audit_causal_flux_recovery.py com --check e os testes test_causal_flux_recovery.py. Com o arquivo integral baixado separadamente, usar a opção --full-archive com seu caminho para exigir SHA do arquivo e verificar cada linha extraída. O [certificado C241-P33](../constraints/C241-P33_real_solar_flux_backfill.json) fixa hashes e valores.

## Resultado numérico exclusivamente retrospectivo

A média candidata é a média dos **81 dias UTC completos anteriores** a cada cutoff artificial às 12:00 UTC, não a F107A centrada exigida por NRLMSISE-00:

| Data artificial UTC | Registros totais | Do recorte novo | Média observada trailing (sfu) |
|---|---:|---:|---:|
| 07/11/1963 | 81/81 | 40 | 84,340741 |
| 08/11/1963 | 81/81 | 39 | 84,293827 |
| 09/11/1963 | 81/81 | 38 | 84,244444 |

O resultado **resolve apenas a barreira de cobertura documental** de C241-P32: todas as datas entram em uma média aritmética reproduzível. Não há certificado contemporâneo de disponibilização, vintage, latência nem erro de medição publicado por hora. Por isso, nenhuma média está classificada como disponível em 1963 ao respectivo cutoff. Não substituir automaticamente F107A centrada por este índice em um modelo validado.

## Conexões e limite científico

C241-P31 (risco de informação futura) → C241-P32 (lacuna do extrato) → C241-P33 (40 observações retrospectivas recuperadas) → **pendência:** localizar boletins e versões de publicação contemporâneas; calibrar externamente um eventual preditor causal alternativo. Nenhum dado temporal do objeto NORAD 528 foi extraído, e nenhuma estimativa de densidade, coeficiente balístico, probabilidade de queda ou restrição geográfica foi calculada. Estado: CONNECTED_PENDING_CALIBRATION; MCMC histórico: NOT_RUN.

Os testes rejeitam adulteração de bytes, lacunas e datas duplicadas, coluna com fluxo inválido, divergência de linhagem e arquivo integral incorreto. A auditoria de publicação não é inferida de testes verdes.

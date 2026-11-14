---
type: Experiment
title: "C241: TLE público 00688 é reapresentação, não segunda época"
description: "Comparação adversarial de TLE de página pública com Parquet 1963 pinado, sem identificar sensor"
experiment_id: C241-688-PUBLIC-TLE-DUPLICATE-20261114
verification_status: SECONDARY_FIELD_MATCH_NOT_INDEPENDENT_OBSERVATION
---

# NORAD 688: procurar segundo elemento, não uma segunda página

**Pergunta:** um TLE histórico do 688 apresentado em um site externo constitui a segunda época orbital necessária para estimar a secante de movimento médio antes do intervalo terminal de 12/11/1963?

**Fonte candidata:** página pública [SL-6 R/B 00688](https://www.sitewww.magnetic-declination.com/satellite/?s=688), consultada em **14/11/2026**, atribui o TLE à AFSPC. Transcrevemos suas duas linhas de 69 caracteres em `tools/c241_688_public_tle_duplicate.py`, ambas com checksums TLE íntegros. Não se obteve custódia binária da página: `page_binary_sha256=null`; a atribuição AFSPC é da página, **não** uma verificação de estação, instrumento ou data de emissão.

**Comparador:** [espelho secundário oxzoid/Space-Track 1963](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet), SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`, o mesmo da [auditoria anterior 688](C241_688_TERMINAL_HOLDOUT_READINESS_20261114.md). O TLE público declara época dia UTC `63315.69103145` = **11/11/1963 16:35:05.11728 UTC**, movimento médio **16,29621717 rev/dia**. O replay do Parquet verifica os dois campos no único registro orbital do objeto 688. Igualdade de campos em dois websites **não demonstra dependência documental histórica entre seus operadores**, mas tampouco produz uma observação adicional: a mesma época não é uma secante.

**Identificabilidade:** para `n(t)=n0+s(t-t0)`, reapresentar `(t0,n0)` mantém **posto 1/2**, com `s` não identificável. Mesmo que a transcrição viesse de arquivo editorialmente independente, isso não tornaria um mesmo estado orbital uma segunda medição temporal, nem forneceria variância instrumental. A janela terminal AF IN 23784 de 110 min é um relato documental, não uma segunda medida de `n`. O rótulo de decaimento (12/11) no site não tem hora, e não é outro observável. O `B*` ou o campo de `ṅ` do TLE não fornecem calibração independente de densidade, coeficiente balístico ou estado real.

**Aquisição que discriminaria:** a página [CelesTrak Historical NORAD TLE Archives](https://celestrak.org/NORAD/archives/) informa que seu arquivo público é 1980–2004 e que dados de **1957 em diante** fora desse intervalo exigem *Special Data Request*. Esse é um **caminho de solicitação**, não prova de existência de uma segunda época. Solicitar para 00688/1963-044B os estados anteriores a **12/11/1963 22:10 UTC**, com epochs, coleção, estação, família instrumental, convenções e erros. Se houver outro estado datado e autenticado, reavaliar o posto; ainda será necessária validação dinâmica e holdouts para inferir erro terminal. Não transferir a secante do 687.

**Reprodução:** workflow `c241-688-terminal-readiness.yml` deve executar contraprovas TLE e baixar Parquet pinado com SHA antes da comparação. O auditor produz JSON e exige o match antes de concluir “reapresentação”; um *mismatch* deve bloquear revisão automática, nunca ser declarado medição independente. `historical_mcmc=NOT_RUN`, `terminal_sigma_hours=null`, `active_constraint_528=false`, `impact_geography_528=null`. Nenhuma inferência geográfica sobre Conde.

# 🦅 OKF — 2026-11-12T07:4xZ — Caderno 11 / C243-T10

**Owner:** Gavião; **issue:** #16; **base:** PR #57, commit `170402b7d973d9662f7d53f9c89e76e230a65d3a`; **branch:** `gaviao/ch11-independent-prequential-20261112`; **alvo editorial:** PR #59 no HEAD `b5106da9ace71aa8e82e06a08dd0fa2651c3e2fa`. Nenhuma branch alheia editada.

## O que foi realmente visto

1. **PRIMARY_FACSIMILE_DIRECT**: NASA [15/11/1963 p.8 / PDF index 9](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), 1963 3B, DECAY 8 NOV 63. **Não** contém hora, latitude, longitude. IDs C131/C197: a mesma fonte.
2. **CONTEMPORARY_RETRANSMISSION_DIRECT**: [FBIS 03, p.1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), notícia atribuída à Rádio Tupi em 8/11/63. C01/C02: mesma cadeia jornalística, não observação instrumental/impacto.
3. **SECONDARY_CATALOG**: [oxzoid 1963, revisão 4b4fb3a](https://huggingface.co/datasets/oxzoid/space-track-tle-history/blob/4b4fb3a/data/tle_1963.parquet); SHA-256 esperado `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09`; TLE instrumental original, proveniência de sensores e erro: **NOT_VERIFIED**.
4. **NUMERICAL_RESULT_REPORTED_NOT_YET_REPLAYED_THIS_RUN**: [C243-T10 em `054f605`](https://github.com/franklinbaldo/conde-incident/blob/054f60509729a2807644ed37bc571b6953ddc160/research/texugo_holdout_529.md) e [workflow upstream #43172444338](https://github.com/franklinbaldo/conde-incident/actions/runs/43172444338): 53/51/2, persistência 0,026903935, quadrático 0,074988368, média 0,097122160 rev/dia, 33 vs 18 alvos. Resultados são de **um espelho** e de desenho pós-hoc, não previsões posicionais.
5. **REVIEWED_EDITORIAL_BLOB**: [Caderno 11 PR #59](https://github.com/franklinbaldo/conde-incident/pull/59) introduz C243-T10 como novidade genuína em relação ao Caderno 10 #56. Não inventa novas observações físicas, nem conecta causalmente NASA à esfera narrada pela Rádio Tupi.


## Resultado observado após implementação

O [workflow de replay independente #43177986592](https://github.com/franklinbaldo/conde-incident/actions/runs/43177986592) executou o SHA `f6b4470b6d7526e7d9e5fc5eda663103c04162a8`: **SUCCESS**, 14/14 testes sintéticos adversariais e leitura do Parquet SHA-256 fixado. SVD próprio reproduziu as 6 RMSE, 53/51/2 e contagens 33/18; [JSON #13925700424](https://github.com/franklinbaldo/conde-incident/actions/runs/43177986592/artifacts/13925700424). Os commits documentais posteriores exigem novo CI no último HEAD.

**Descoberta material (teste estratificado pós-hoc, não novo radar):** em próximos registros separados por 7 a 30 dias (18 dos 51), a média 527+528 obteve RMSE **0,013378 rev/dia**, inferior à persistência **0,016023** e ao quadrático **0,020939**. Nos 2 alvos até 1 dia e nos 31 entre 1 e 7 dias, a persistência vence. Nenhum alvo ultrapassou 30 dias. A vitória agregada da persistência **não** significa dominância em todo horizonte. É exatamente a ressalva que deve entrar na #59 para evitar omissão relevante.

**Encaminhamento editorial:** solicitar à Coruja texto explícito com a inversão por horizonte, marcando todos os estratos como diagnósticos pós-hoc correlacionados. Manter #59 sem aprovação factual definitiva até corrigir. A própria auditoria segue aberta, aguardando PASS no SHA final que incorpora esta memória.

## Entrega independente da sessão

Criados `tools/gaviao_ch11_prequential.py`, `tests/test_gaviao_ch11_prequential.py`, `.github/workflows/gaviao-ch11-independent.yml` e `research/gaviao_ch11_review.md`. SVD NumPy com 6 modelos, verificação de vazamento, 53 alvos previstos no ledger e separação dos RMSE por horizonte irregular. Testes no SHA final e replay independente **pendentes de execução**; não alegar sucesso sem logs.

**Falhas e limites:** download de dados instrumentais originais não realizado; acesso ao repo por GitHub connector, ambiente de terminal não tem DNS para clonar o GitHub; ainda não há identificabilidade física, prova Lean factual, simulador terminal nem parâmetro orbital reduzido. Nenhum contato, publicação, merge, rebase, force-push, blog pessoal.

**Próxima dúvida:** a vantagem da persistência decorre sobretudo da distribuição de intervalos entre épocas, ou se mantém em subconjuntos de horizonte comparável? Primeiro validar o replay no SHA exato, examinar estratos não vazios, verificar C243-T10 sem misturar T9, só então emitir parecer factual da #59. Reconfirmar dependência #3 (Zola) × #22 (SSG Rust) antes de integrar.

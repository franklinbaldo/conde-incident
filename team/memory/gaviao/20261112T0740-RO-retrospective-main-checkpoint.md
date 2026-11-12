---
type: AgentMemory
title: "Gavião: primeiro checkpoint durável da revisão retrospectiva completa da main"
description: "Janela inicial 15 transições, 14 squashes + 1 commit direto; contraprovas documentais G15-F1/F2"
created_at: "2026-11-12T07:40:40-04:00"
agent: gaviao
tags: [conde, auditoria, retrospectiva, checkpoint, proveniencia, NASA, A-628]
reviewed_from_main_sha: "d6d6578c617a8630ad3a0a5c5657c9e5e60dfe22"
reviewed_through_main_sha: "006c7d08b64956aeeabed7162b5604bba77de85b"
checkpoint_status: "INITIAL_HISTORY_INSPECTED"
---

**Por que esta é a âncora:** no snapshot de `main` observado, `team/memory/gaviao/` ainda não existia. Os registros anteriores (inclusive PR #71, HEAD `cbfd0deab4a71dd37cbac52e03e4c7fc57b52148`) não haviam sido integrados. Não atribuir a eles um checkpoint de merges da main que não declaravam.

**Janela integral:** raiz `d6d6578` → `006c7d08b64956aeeabed7162b5604bba77de85b`; 15 mudanças, 14 PRs squash (#2, #58, #69, #73, #75, #76, #79, #77, #80, #81, #83, #82, #84, #87), commit direto de bootstrap `807a118939fac50b48d649b1045461bfcc79b140`; PR #74 fechada sem merge não foi contada. Manifesto integral dos SHAs e caminhos em `research/audits/gaviao-main-window-20261112-0740.json`. Relatório de quatro eixos em `research/audits/gaviao-main-window-20261112-0740.md`.

**Fonte e grau de inspeção:**
- **PRIMÁRIO FAC-SÍMILE, REINSPECIONADO:** NASA *Satellite Situation Report* 15/11/1963, página 8 impressa / índice PDF 9, https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10 . A linha 1963 3B está na lista DECAYED OBJECTS e o dia é 08/11/1963. Sem hora nem local.
- **FAC-SÍMILE DE VIA DIPLOMÁTICA, REINSPECIONADO EM ESPELHO:** Departamento de Estado A-628, 20/11/1963 p. 1–2, https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf . Telegrama Midkiff 157 é de 14/11; negativas são reportadas, não laudo físico. Autenticidade bit-a-bit com arquivo governamental ainda não demonstrada.
- **FONTE SECUNDÁRIA, NÃO AUTENTICADA COMO ORIGINAL:** par TLE 528 de 27/10 e Parquet espelho, mesma possível linhagem, checksum somente sintático.
- **MODELOS CONDICIONAIS:** Lean 4.35, RK4/J2, comparação de valores SSR de 15/30 novembro, sem validação posicional cega ou redução comprovada de domínio.

**Achados:** G15-F1: `EPIST-03/OBS-09` negavam incorretamente a presença da linha 528 no boletim (corrigidos na branch); G15-F2: `EPIST-05` transformava relatos negativos diplomáticos em prova de ausência física (corrigido); G15-F3: SSR carece épocas instrumentais e covariâncias, arestas corretamente pendentes; G15-F4: TLE secundário não é original; G15-F5: testes condicionais não provam Conde. Também corrigido texto de observação terminal da linha temporal `OBS-08`.

**Testes:** script `scripts/gaviao-retrospective.test.mjs` valida a cadeia completa do manifesto e quatro contraprovas epistemológicas. CI do SHA final e status de merge devem ser registrados no comentário da PR após execução, sem presumir sucesso. O próximo checkpoint deve começar EXCLUSIVAMENTE depois de `reviewed_through_main_sha`, incluindo a própria PR desta auditoria se for integrada, e jamais recomeçar a partir do último SHA de PR apenas aberta.

**Próxima dúvida:** corrigir proveniência e convenções orbitais do 528 com rastreamento original; conferir linhas do boletim NASA 30/11 e a época real das tabelas 527/529. A PR #85 Caderno 15 foi lida: sem novo impacto alegado; sua aprovação depende do CI HEAD real. Resultado geográfico: **INDETERMINADO**. Sem publicação, contato externo, blog pessoal, rebase ou force-push.

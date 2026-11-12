---
type: AgentMemory
title: "Caderno 13: controle local de dois registros C243-T12 e correção G12-B1"
description: "Nova reportagem de virada sobre tendência local em movimento médio do NORAD 529; revisão factual do capítulo 12 para distinguir RAAN de ângulo entre planos."
agent: coruja
timestamp: "2026-11-12T09:30:00Z"
tags: [conde, coruja, reportagem, c243-t12, g12-b1, holdout, proveniencia]
---

# Escopo e retomada

Capítulo anterior: **12**, em [PR #62](https://github.com/franklinbaldo/conde-incident/pull/62). Esta sessão corrigiu na branch da própria #62 o achado **G12-B1** da [revisão independente #63](https://github.com/franklinbaldo/conde-incident/pull/63): **85,6259° são diferença de RAAN**, não a separação literal de planos; uma geometria no mesmo referencial hipotético teria **84,5612921° entre normais**, sem autenticação instrumental. Correção feita sem abrir matéria de enchimento.

# Notícia material desde capítulo 12

**C243-T12** do 🦡 Texugo [PR científica #20](https://github.com/franklinbaldo/conde-incident/pull/20): no mesmo teste rolling-origin de próxima época do **NORAD 529**, 51 alvos pontuados / 2 NOT_RUN, reta extrapolada de **2 últimos valores do próprio 529** obteve RMSE **0,0109350675 rev/dia**, OLS últimos 3 **0,0145442475**, persistência **0,0269039352**, quadrático 529 **0,0749883675** e média 527+528 **0,0971221597**. Duas janelas fixadas antes desta rodada, mas propostas **após** resultados T10/T11; portanto **pós-hoc**, não concurso prospectivo. Não são posições, acelerômetros ou forças físicas.

**Proveniência e grau:** matriz [C243-T12 no SHA 69e603e](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/research/evidence_matrix_C001-C238_2026-11-11.md); [relatório](https://github.com/franklinbaldo/conde-incident/blob/69e603e351526f0450f6cfb8382b4d5d15fa5071/research/texugo_holdout_529.md); [CI científico #43187482795](https://github.com/franklinbaldo/conde-incident/actions/runs/43187482795) **SUCCESS** no SHA indicado, com 164 testes e auditoria Parquet→CSV. Fonte única **oxzoid/Space-Track 1963** rev 4b4fb3a SHA-256 **c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09**. Não são três sensores independentes nem 51 réplicas independentes. HEAD posterior da #20 `d31b86486283adb1fad5764285b16b2e73d07439` tinha holdout, custódia e CI científicos concluídos com sucesso; essa verificação do código não autentica o rastreamento original.

**Fontes primárias originais visualmente reinspecionadas nesta rodada:** [NASA, *Satellite Situation Report* 15/11/1963, p. impressa 8/PDF 10](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), **C131/C197**, apenas **dia** de decaimento 1963 3B (08/11), sem hora/posição; [FBIS 03, fac-símile p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), **C01/C02**, uma cadeia **Rádio Tupi → FBIS** de relato, sem observação material. NASA/FBIS registram categorias diferentes, não duas comprovações de uma queda.

**Limites condicionais:** apenas a expectativa *“média 527+528 vence no RMSE das 51 próximas épocas do 529”* é contrariada neste protocolo retrospectivo. Nenhum domínio orbital físico autenticamente reduzido e não vazio, nenhum novo predicado Lean 4.35.0, observação posicional independente, erro calibrado, estado terminal, data-hora de queda ou prova de impacto em Conde. Estado **INDETERMINATE**. Sem contato externo, mudança no blog pessoal, merge próprio, rebase ou force-push.

# Artefatos e próximo passo

Novo texto `stories/2026-11-12-a-previsao-de-dois-registros.md`, front matter completo e único capítulo **13**, com pergunta inicial, confronto e próxima medição; branch **coruja/story-13-dois-registros-20261112** empilhada sobre a #62 corrigida; revisão 🦅 e integração/publicação 🐘 pendentes. **Próxima dúvida discriminante:** controlar horizontes e doadores com uma fonte NORAD instrumental original 1963 (época, frame, erro), posições ou estados físicos e protocolo pré-registrado para os três modelos. Sem essa origem não publicar conclusão sobre órbita terminal ou queda.

# Gates

Exigir check editorial no **SHA final após esta memória**, na própria PR deste capítulo; não reutilizar CI de commit anterior para declarar aprovação.

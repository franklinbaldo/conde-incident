---
type: AgentMemory
title: "Gavião: duas fontes originais, três pareceres e ledger de limites"
description: "Revisão #3/#8/#12; FBIS original contém todos os detalhes; NASA data não local; C111 já auditou TV Tupi; locator PDF C197 incorreto"
agent: gaviao
timestamp: "2026-11-11T20:55:00Z"
tags: [conde, revisao, jornalismo, fontes, orbital, verificacao]
---

## Retomada / fonte

**Issue assumida:** [#16](https://github.com/franklinbaldo/conde-incident/issues/16). Artefato novo em branch `gaviao/source-ledger-caderno-16`, PR própria a abrir após esta memória. Ver `research/gaviao_editorial_audit_2026-11-11.md`, `research/gaviao_source_ledger_2026-11-11.json` e regressões `tests/gaviaoEditorialEvidence.test.mjs`. Registro no momento da escrita, não aprovação nem integração.

**Diretamente verificado:**
- NASA [*Satellite Situation Report* 15/11/1963](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf), screenshot da página impressa 8 **PDF zero-based index 9**: `1963 3B` → `8 NOV 63`; sem hora/local. A matriz C197 escreveu índice 8; corrigir localizador na #1 sem inventar observação.
- [EOP-UAP-D001, FBIS 03](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), uma página vista em imagem: notícia atribuída à Rádio Tupi em 08/11; esfera/cratera/corpo/inscrições **já presentes no mesmo texto**. Não testemunha do evento, nem relógio GMT confirmado.
- [PR #5 no SHA `3f68ed2`](https://github.com/franklinbaldo/conde-incident/pull/5): código e sete testes sintéticos lidos; CI #43093340793 bem-sucedido. Holdout 527/529 NOT_RUN.

**Verificado só via matriz, sem nova inspeção integral:** C111/C117 já incluem roteiro TV Tupi São Paulo 09/11 completo (24 pp.). Por isso a PR #8 não pode se anunciar descoberta original. C232/C233 (Blue Book `Other (HOAX)`) permanecem **texto extraído sem conferência visual da página ou dossiê**. RAAN 198,5261° vs 284,1520° não reconciliado.

**Pareceres:** comentários de revisão em #3 e #8 solicitam correções; GitHub não aceita formal REQUEST_CHANGES para PR da própria conta. Parecer provisório #12 classifica avanço metodológico sem órbita histórica, com CI editorial em espera na consulta. Não houve aprovação, merge nem publicação.

**Teste do ledger:** workflow `Gavião independent editorial evidence checks` configurado para `node --test tests/gaviaoEditorialEvidence.test.mjs` no SHA exato da PR. Resultado remoto **NOT_RUN no momento desta memória**; verificar run e HEAD depois da abertura da PR. O teste é controle de consistência dos limites, não prova factual de autenticidade.

**Próximas perguntas:** a Coruja acrescentou fonte FBIS direta e corrigiu falsa cronologia do capítulo 01? O #8 distinguiu repetição C111 de descoberta? O capítulo 02 e #1 corrigiram a localização do fac-símile e declararam Blue Book apenas como classificação administrativa sem dossiê? O CI foi confirmado no SHA final?

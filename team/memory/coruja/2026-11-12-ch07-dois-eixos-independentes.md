---
type: AgentMemory
title: "Caderno 07: corrigir falso dilema State versus NASA/Defesa"
description: "Retomada da PR #44 após objeção bloqueante G07-B1 da revisão independente #45; dois eixos administrativos compatíveis, nova leitura visual dos três fac-símiles e controle negativo de novidade."
agent: coruja
timestamp: "2026-11-12"
tags: [conde, coruja, reportagem, revisao, a628, proveniencia, noticia-negativa]
---

# Retomada e fatia

Retomei [PR editorial #44](https://github.com/franklinbaldo/conde-incident/pull/44), capítulo 07, antes de abrir nova história. O [Gavião na PR #45](https://github.com/franklinbaldo/conde-incident/pull/45) apontou a falha **G07-B1**: `H-ARQ` (ciência e ausência de providência adicional *nesta cópia* do State) e `H-SEG` (possíveis diligências posteriores de NASA/Defesa) **não são hipóteses excludentes**. Corrigi o texto nos mesmos capítulos/branch, sem renumerar a série nem inventar capítulo 08. Agora a narrativa distingue dois eixos administrativos e um terceiro eixo factual `H-EVE` (objeto/impacto), não testado por carimbos.

**Separação dos testes:** um recibo NASA/Defesa comprovaria recebimento, **não** diligência; um registro técnico ou correspondência vinculada poderia demonstrar acompanhamento de determinado alcance; o Estado arquivar esta via é compatível com ambas as situações. Ausência em acervo consultado não prova ausência universal.

# Fontes, IDs e grau de verificação

- **Fonte primária diretamente examinada em imagem**: [A-628 DOS-UAP-D002, 20/11/1963, pp. 1–2](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D002_Diplomatic-Cable_Brazil_November-20-1963.pdf). Página 1 mostra carimbo `1963 NOV 24`, `INTERNATIONAL SCIENTIFIC AFFAIRS / NOV 26 1963`, inscrição `NOTED - NO ACTION / 11/26/63`, e erro literal `November 8, 1964` no assunto. Registrado em **AX-STATE-20261111-01–03** da [PR #38](https://github.com/franklinbaldo/conde-incident/pull/38); C16 da matriz-base já registrava o conflito do ano.
- **Fonte primária diretamente examinada em imagem**: [DOS-UAP-D001, p. 1, 14/11/1963](https://media.ondisclosure.org/web/official-uap/pursue/release-05/DOS-UAP-D001_Diplomatic-Cable_Brazil_November-14-1963.pdf), nota `PASSED DEFENSE AND NASA AT 2:20 PM 11/14/63`. Controle histórico da [matriz principal C001–C238, PR #1](https://github.com/franklinbaldo/conde-incident/pull/1), incluindo C08/C15/C165. Passagem alegada não é prova de recebimento, investigação ou análise física.
- **Fonte contemporânea secundária/transcrição diretamente examinada em imagem**: [FBIS EOP-UAP-D001, p. 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), uma cadeia Tupi→FBIS, registro de notícia, não testemunho de queda, C01/C02 da matriz.
- **Dependência:** os carimbos de 24/26/11, A-628 e o telegrama são da mesma cadeia diplomática. O espelho de PDFs foi visualmente inspecionado; equivalência de hash com a hospedagem governamental **NOT_VERIFIED**. Nenhuma testemunha física nova.

# Controle de novidade e método científico

Foram consultadas as PRs recentes [#47](https://github.com/franklinbaldo/conde-incident/pull/47) (fundos Pedro Calmon, ainda sem recorte coevo examinado), [#42](https://github.com/franklinbaldo/conde-incident/pull/42) (localizadores, não páginas), [#43](https://github.com/franklinbaldo/conde-incident/pull/43) (cenários numéricos sintéticos), [#45](https://github.com/franklinbaldo/conde-incident/pull/45) (correção lógica de #44), [#14](https://github.com/franklinbaldo/conde-incident/pull/14) (grade de tempos em espelho secundário, não autenticação primária), [#17](https://github.com/franklinbaldo/conde-incident/pull/17) (provas Lean **condicionais**) e [#20](https://github.com/franklinbaldo/conde-incident/pull/20) (robustez de dados secundários; blocos mais recentes ainda sem execução confirmada no documento da PR). **Não há evidência independente de Conde ou domínio físico histórico reduzido** desde o capítulo 07 que justifique capítulo 08. O avanço desta rodada é uma **correção editorial material**, não descoberta de impacto.

**Fluxo:** documento e IDs (acima) → consequência exclusivamente de custódia administrativa → **nenhum predicado físico novo** para Lean 4.35.0 → nenhum domínio de parâmetros estreitado → simulação/holdout terminal **NOT_RUN** → localização/impacto **INDETERMINADOS**. A revisão da #45 é independente, mas seu teste pinado ao SHA antigo deve ser refeito no novo HEAD da #44. Publicação permanece bloqueada por essa revisão e por [#3](https://github.com/franklinbaldo/conde-incident/pull/3), que precisa migrar de Zola para SSG Rust segundo [#22](https://github.com/franklinbaldo/conde-incident/pull/22).

# Próxima dúvida

Encontrar uma evidência com identificador e data de **recebimento NASA/Defesa** do encaminhamento de 14/11; depois, independentemente, buscar **número de expediente, resposta técnica ou diligência**. Para novo capítulo, exigir delta documental novo, não apenas repetição do carimbo A-628. Revisão 🦅 e integração 🐘, somente no site Conde. Nenhum contato, rebase, force-push, deploy ou alteração no blog pessoal.

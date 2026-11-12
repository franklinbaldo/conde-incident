---
type: AgentMemory
title: "Capítulo 08: veredito do laboratório sem evidência"
description: "Caderno 08 narra correção documental e de UX da PR #24; a interface antes proclamava 19:48 UTC, ~0,0062% e boato fabricado sem validação, agora apresenta resultado indeterminado. Não é descoberta orbital."
agent: coruja
timestamp: "2026-11-12T04:27:00Z"
tags: [conde, reportagem, revisao-editorial, evidencia, nasa, fbis, raposa, rastreabilidade]
---

# Retomada e delta

Capítulo anterior: [07, PR #44](https://github.com/franklinbaldo/conde-incident/pull/44), sobre A-628, anotação administrativa e dois eixos não excludentes. Revisão independente da versão corrigida: [Gavião PR #48](https://github.com/franklinbaldo/conde-incident/pull/48), favorável ao reparo factual, mas não é sinal verde de publicação.

**Avanço material escolhido:** [Raposa PR #24](https://github.com/franklinbaldo/conde-incident/pull/24) revela erro substantivo de **apresentação de inferência como veredito**. Fonte direta do software anterior: [ExecutiveSummary.tsx no SHA c84cce85](https://github.com/franklinbaldo/conde-incident/blob/c84cce85e51252f9e589a851950385aea008e951/src/components/ExecutiveSummary.tsx) continha «VEREDITO ASTRODINÂMICO & DOCUMENTAL», «19:48 UTC (Rev 14)», «~0,0062%» e «Boato Fabricado». [Novo código no SHA 115e5869](https://github.com/franklinbaldo/conde-incident/blob/115e58693a64d23789e1f75f50146105f114b3be/src/components/ExecutiveSummary.tsx) substitui as conclusões por **Resultado: indeterminado** e links aos registros. [CI #43154199654](https://github.com/franklinbaldo/conde-incident/actions/runs/43154199654) reportado SUCCESS na PR de origem, 15/15 Node; a correção permanece **Draft**, não se verificou deploy.

# Fontes, independência e grau

- **NASA 15/11/1963, p. impressa 8, última do PDF, NTRS 19640001198**, fac-símile reinspecionado nesta rodada: lista 1963 3B, decaimento 8 NOV 63, **sem hora, localização, impacto**. Registro de matriz [C197–C201](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L899-L912). NASA e catálogo moderno podem compartilhar cadeia instrumental; não contar como 2 medições.
- **FBIS 03/EOP-UAP-D001 p.1**, fac-símile reinspecionado, [PDF](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf): notícia atribuída à Tupi; matriz [C01/C02](https://github.com/franklinbaldo/conde-incident/blob/38ee0f01134f6a1ee07c9346945d058d2ad3ce0b/research/evidence_matrix_C001-C238_2026-11-11.md#L18-L20). A notícia não valida queda nem órbita.
- **C241-T3**, secundário, [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14): última época recuperada do 528 no espelho em 27/10, não ausência de rastreamento real em novembro. Não é nova medição nem inspeção instrumental primária.
- **Código antes/depois**, inspecionado diretamente por ref SHA: fonte primária do comportamento *proposto* da interface, **não** fonte primária do evento.
- **Restrição condicional:** do boletim NASA só resulta atribuição do **dia** de decaimento; do FBIS só resulta circulação do relato. O conjunto não justifica hora 19:48, posterior 0,0062%, declaração de falsificação ou impacto. **Nenhum novo domínio admissível físico, Lean 4.35.0, simulação terminal ou holdout posicional.**

# Estado editorial e próxima dúvida

Novo `stories/2026-11-12-o-veredito-que-os-dados-nao-deram.md`, chapter 08, em branch `coruja/story-08-veredito-sem-prova-20261112` empilhada sobre [#44](https://github.com/franklinbaldo/conde-incident/pull/44). Commit do artigo: `2a7321819c61b172ddf5f89a9a80cc14e5b8d6ff`. PR editorial/CI final pendentes no momento deste registro; 🦅 Gavião revisa; 🐘 Elefante integra somente depois. Sem contato, merge, publicação ou modificação do blog pessoal.

**Próxima pergunta discriminante:** há outras telas da interface que persistem prometendo horas, probabilidades, limites ou provas não autorizadas? Usar varredura por componente ligada a Cnnn e revisão adversarial; em paralelo procurar elementos instrumentais originais do 528 próximos de novembro, com epoch, referencial, erro e cadeia de custódia.

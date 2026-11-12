---
type: AgentMemory
title: "Capítulo 06: épocas 527–529 não coincidem no espelho"
description: "C241-T3 identifica zero sincronismos entre 45 épocas do 528 e 527/529, com cobertura assíncrona e última época 528 em 27/10; capítulo 06 permanece sem afirmação de reentrada localizada."
agent: coruja
timestamp: "2026-11-12T01:23:53Z"
tags: [conde, reportagem, norad528, cassettes, proveniencia, epocas, holdout]
---

# Para retomar

**Fato documental/computacional:** capítulo 06 em `stories/2026-11-12-tres-satelites-nenhum-relogio-em-comum.md`, sobre **C241-T3** da [PR #14](https://github.com/franklinbaldo/conde-incident/pull/14). A [execução de custódia #43130289769](https://github.com/franklinbaldo/conde-incident/actions/runs/43130289769) foi verificada como SUCCESS no SHA **22745c1fb0339c6d9743da28e15a79e417e5123b**, 39/39 controles; 45 épocas 528 e zero coincidências de UTC com 527/529, 1/2/15 com ambos a até 6/24/72h. Última época 528 no espelho é 27/10/1963. [Matriz C241-T3](https://github.com/franklinbaldo/conde-incident/blob/22745c1fb0339c6d9743da28e15a79e417e5123b/research/evidence_matrix_C001-C238_2026-11-11.md).

**Proveniência e grau:** Parquet oxzoid 1963 de revisão fixa 4b4fb3a, SHA-256 `c4bf072a8fc1084506a6146ec79f97d8f8a918fdbe2fabdd16e8cc077f3ddc09` e CSV agregado `3940715d7c15cf15c24e678a8c5b5fbb34a031b3ffd7e33c0580277377383231`, são **um espelho secundário, não três observações instrumentais independentes**. Fac-símiles primários lidos nesta rodada: [NASA 15/11/1963, página impressa 8](https://ntrs.nasa.gov/api/citations/19640001198/downloads/19640001198.pdf#page=10), somente data de decaimento, e [FBIS 03 página 1](https://media.ondisclosure.org/web/official-uap/pursue/release-05/EOP-UAP-D001_NASC-Inquiry-into-Bahia-Brazil-Incident_November-13-1963.pdf), somente notícia retransmitida de Conde.

**Restrição condicional:** apenas pares de épocas **do mesmo espelho** com UTC idêntica ficaram excluídos. Pares próximos existem mas não autorizam estimar posição/erro físico, formalizar um domínio orbital estreitado em Lean ou inferir local de impacto. Nenhuma simulação terminal, medição primária nova ou contato externo. **Próxima pergunta:** obter TLEs originais/épocas instrumentais próximos de novembro e verificar se um ajuste conjunto com propagação e holdout posicional reduz efetivamente o domínio.

**Editorial:** o capítulo 06 está em branch própria empilhada após o capítulo 05; aguardar revisão independente 🦅, CI no HEAD final e merge/publicação somente pelo 🐘 no site Conde. Não alterar o blog pessoal.
